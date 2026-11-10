"""Native Grok evidence replay and conservative failure cases."""

import json
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

import pytest
from test_monitor_adapters import Evidence

from aitm_usage import monitor_types
from aitm_usage.ledger import Ledger
from aitm_usage.sources import adapter
from aitm_usage.types import (
    DiagnosticCode,
    Provider,
    ProviderCheckpoint,
    SourceCheckpoint,
    SourceCursor,
    SourceRef,
    _decode,
    _encode,
)

FIXTURES = Path(__file__).parent / "fixtures" / "grok"
SESSION = "10000000-0000-4000-8000-000000000115"
PROMPT_A = "20000000-0000-4000-8000-000000000001"
PROMPT_B = "20000000-0000-4000-8000-000000000002"
GROK_BINARY = "197c66a63e5ac46e07450b0ca21d141ce665050a412180f185dadfae1c7a5b2a"


@pytest.fixture
def grok_source(tmp_path, monkeypatch):
    from aitm_usage.sources import grok

    monkeypatch.setattr("aitm_usage.ledger._control_root", lambda: tmp_path / "control")
    key = Ledger.initialize(tmp_path / "evidence", UUID(int=115))
    approved_root = tmp_path / "private-approved-root"
    directory = approved_root / SESSION
    directory.mkdir(parents=True)
    checkout = key.pseudonymize("grok-checkout", "verified-checkout")
    origin = grok.GrokOrigin(
        session_id=SESSION,
        system="Darwin",
        architecture="arm64",
        version="1.0.77",
        build="50ca579fa996",
        executable_digest=GROK_BINARY,
        format_version=1,
        lineage_id=SESSION,
        incarnation=key.pseudonymize("grok-incarnation", "incarnation-1"),
        checkout=checkout,
    )
    root = adapter.SourceRoot(
        approved_root, datetime(2026, 1, 1, tzinfo=UTC), (), Evidence(key)
    )
    pending_receipts = {
        (SESSION, PROMPT_A, "synthetic-event-1"): key.pseudonymize("grok-receipt", "a"),
        (SESSION, PROMPT_B, "synthetic-event-7"): key.pseudonymize("grok-receipt", "b"),
    }
    rows = (FIXTURES / "updates.jsonl").read_bytes().splitlines(keepends=True)
    snapshot = json.loads((FIXTURES / "usage.json").read_text())
    headless = json.loads((FIXTURES / "headless.json").read_text())

    def disallow_project_access(*args):
        pytest.fail("adapter attempted destination access")

    monkeypatch.setattr(Ledger, "open", disallow_project_access)
    monkeypatch.setattr(Ledger, "writer", disallow_project_access)
    return SimpleNamespace(
        key=key,
        root=root,
        directory=directory,
        origin=origin,
        rows=rows,
        snapshot=snapshot,
        headless=headless,
        pending_receipts=pending_receipts,
        module=grok,
        checkout=checkout,
    )


def _batch(
    source,
    rows,
    snapshot=None,
    cursor=None,
    *,
    origin=None,
    verifier=None,
    headless=None,
):
    (source.directory / "updates.jsonl").write_bytes(b"".join(rows))
    snapshot_path = source.directory / "usage.json"
    if snapshot is None:
        snapshot_path.unlink(missing_ok=True)
    else:
        snapshot_path.write_text(json.dumps(snapshot))
    reader = source.module.GrokAdapter(
        lambda _: source.origin if origin is None else origin,
        verifier
        if verifier is not None
        else lambda *parts: source.pending_receipts.get(parts),
        headless,
    )
    (locator,) = reader.discover(source.root)
    return reader.read_delta(locator, cursor)


def _set_usage(row, **values):
    envelope = json.loads(row)
    envelope["params"]["update"]["usage"].update(values)
    return json.dumps(envelope).encode() + b"\n"


def _second_snapshot(source):
    return {"sessionId": SESSION, "turns": [source.snapshot["turns"][1]]}


def _codes(batch):
    return {entry.code for entry in batch.diagnostics}


def test_grok_surface_is_separate_from_the_legacy_provider():
    assert getattr(monitor_types.MonitorProvider, "GROK", None) is not None
    with pytest.raises((ValueError, TypeError)):
        _decode('"grok"', Provider)


@pytest.mark.parametrize("provider", [Provider.CODEX, Provider.CLAUDE])
def test_pre_grok_stream_cursor_bytes_still_round_trip(grok_source, provider):
    ref = grok_source.key.pseudonymize("old-cursor", "fixture")
    checkpoint = SourceCheckpoint(
        SourceCursor(ref, ref, ref, 0, ref),
        ProviderCheckpoint(provider),
    )
    old = '{"checkpoint":' + _encode(checkpoint, SourceCheckpoint) + "}"
    decoded = _decode(old, adapter.StreamCursor)
    assert decoded == adapter.StreamCursor(checkpoint)
    assert _encode(decoded, adapter.StreamCursor) == old


def test_grok_observation_round_trips_in_the_versioned_payload(grok_source):
    s = grok_source
    first = _batch(s, s.rows, s.snapshot).observations[0]
    revision = monitor_types.MonitorRevision(first.key, first.revision, first.usage)
    encoded = _encode(revision, monitor_types.MonitorRevision)
    assert _decode(encoded, monitor_types.MonitorRevision) == revision
    assert json.loads(encoded)["observation"]["provider"] == "grok"


def test_resume_and_snapshot_replay_count_two_distinct_turns(grok_source):
    s = grok_source
    single = _batch(s, s.rows, s.snapshot)
    assert single.diagnostics == ()
    assert len(single.observations) == len(single.boundaries) == 2
    assert len({item.key for item in single.observations}) == 2
    assert single.observations[0].usage.observed_at == datetime.fromtimestamp(
        1793491200.010, UTC
    )
    first = _batch(
        s, s.rows[:5], {"sessionId": SESSION, "turns": s.snapshot["turns"][:1]}
    )
    assert len(first.observations) == 1
    restored = _decode(
        _encode(first.cursor, adapter.StreamCursor), adapter.StreamCursor
    )
    second = _batch(s, s.rows, s.snapshot, restored)
    assert (*first.observations, *second.observations) == single.observations
    assert second.observations[0].project_context == s.checkout
    repeat = _batch(s, s.rows, s.snapshot, second.cursor)
    assert repeat.observations == repeat.diagnostics == ()
    assert repeat.cursor == second.cursor


def test_cold_restart_at_every_native_row_and_with_partial_tail(grok_source):
    s = grok_source
    complete = _batch(s, s.rows, s.snapshot)
    for cut in range(len(s.rows) + 1):
        prior = _batch(s, s.rows[:cut], s.snapshot)
        wire = adapter.StreamCursor | None
        restored = _decode(_encode(prior.cursor, wire), wire)
        later = _batch(s, s.rows, s.snapshot, restored)
        assert (*prior.observations, *later.observations) == complete.observations
    partial = _batch(s, [*s.rows[:4], s.rows[4][:20]], s.snapshot)
    assert not partial.observations and not partial.cursor


def test_hookless_eligible_completion_keeps_native_interval(grok_source):
    s = grok_source
    result = _batch(
        s, s.rows[1:5], {"sessionId": SESSION, "turns": s.snapshot["turns"][:1]}
    )
    (item,) = result.observations
    assert not result.boundaries
    assert item.time_basis is monitor_types.ObservationTimeBasis.NATIVE_COMPLETION
    assert item.project_context == s.checkout
    absent = _batch(s, s.rows[1:5], origin=replace(s.origin, checkout=None))
    assert absent.observations[0].project_context is None


def test_fork_excludes_inherited_turns(grok_source):
    s = grok_source
    origin = replace(s.origin, inherited_prompt_ids=frozenset({PROMPT_A}))
    result = _batch(s, s.rows, _second_snapshot(s), origin=origin)
    assert len(result.observations) == 1
    assert result.observations[0].usage.tokens.output_tokens == 38


@pytest.mark.parametrize("fork", [False, True])
def test_nearby_excluded_turn_does_not_dispute_an_eligible_turn(grok_source, fork):
    s = grok_source
    followup = []
    for row, tick in zip(s.rows[6:], (150, 160, 190, 200), strict=True):
        envelope = json.loads(row)
        meta = envelope["params"]["_meta"]
        meta["agentTimestampMs"] = 1793491200000 + tick
        envelope["timestamp"] = meta["agentTimestampMs"] // 1000
        followup.append(json.dumps(envelope).encode() + b"\n")
    s.snapshot["turns"][1]["endedAt"] = "2026-11-01T00:00:00.185000+00:00"
    if fork:
        s.origin = replace(s.origin, inherited_prompt_ids=frozenset({PROMPT_A}))
    else:
        s.root = replace(s.root, cutoff=datetime.fromtimestamp(1793491200.100, UTC))
    prefix = _batch(s, s.rows[:5])
    assert not prefix.observations
    wire = adapter.StreamCursor
    prior = _decode(_encode(prefix.cursor, wire), wire)
    result = _batch(s, [*s.rows[:5], *followup], s.snapshot, prior)
    (eligible,) = result.observations
    assert eligible.usage.tokens.output_tokens == 38
    assert DiagnosticCode.IDENTITY_CONFLICT not in _codes(result)


def test_late_folded_parent_never_adds_to_child(grok_source):
    s = grok_source
    child = _batch(s, s.rows[:5])
    (prior,) = child.observations
    folded = _set_usage(s.rows[4], modelCalls=2)
    after = _batch(s, [*s.rows[:5], folded], cursor=child.cursor)
    assert not after.observations and after.cursor == child.cursor
    (gap,) = after.diagnostics
    assert gap.code is DiagnosticCode.OVERLAP_UNVERIFIED
    assert gap.observation_key == prior.key


def test_snapshot_conflict_and_cache_categories(grok_source):
    s = grok_source
    result = _batch(s, s.rows, s.snapshot)
    tokens = result.observations[0].usage.tokens
    assert (
        tokens.uncached_input_tokens,
        tokens.cache_read_tokens,
        tokens.cache_creation_tokens,
    ) == (12789, 1152, 0)
    changed = json.loads(json.dumps(s.snapshot))
    turn = changed["turns"][0]
    turn["inputTokens"] += 1
    turn["totalTokens"] += 1
    turn["modelUsage"]["grok-4.7-build"]["inputTokens"] += 1
    turn["modelUsage"]["grok-4.7-build"]["totalTokens"] += 1
    conflict = _batch(s, s.rows, changed, result.cursor)
    assert not conflict.observations and conflict.cursor == result.cursor
    assert any(
        gap.code is DiagnosticCode.IDENTITY_CONFLICT
        and gap.observation_key == result.observations[0].key
        for gap in conflict.diagnostics
    )


def test_native_cache_creation_uses_its_own_bucket(grok_source):
    s = grok_source
    row = json.loads(s.rows[4])
    usage = row["params"]["update"]["usage"]
    usage["cacheCreationTokens"] = 120
    usage["modelUsage"]["grok-4.7-build"]["cacheCreationTokens"] = 120
    native = json.dumps(row).encode() + b"\n"
    result = _batch(s, [*s.rows[:4], native])
    (item,) = result.observations
    assert item.usage.tokens.uncached_input_tokens == 12669
    assert item.usage.tokens.cache_read_tokens == 1152
    assert item.usage.tokens.cache_creation_tokens == 120
    assert item.usage.tokens.total_tokens == 14140


def test_internally_conflicting_snapshot_disputes_the_matched_turn(grok_source):
    s = grok_source
    before = _batch(s, s.rows, s.snapshot)
    s.snapshot["turns"][0]["modelUsage"]["grok-4.7-build"]["costUsdTicks"] += 1
    cold = _batch(s, s.rows, s.snapshot)
    resumed = _batch(s, s.rows, s.snapshot, before.cursor)
    for result in (cold, resumed):
        assert not result.observations
        (dispute,) = result.diagnostics
        assert dispute.code is DiagnosticCode.IDENTITY_CONFLICT
        assert dispute.observation_key == before.observations[0].key
    assert resumed.cursor == before.cursor


def test_duplicate_prompt_with_conflicting_verified_marker_disputes_after_restart(
    grok_source,
):
    s = grok_source
    before = _batch(s, s.rows[:5])
    restored = _decode(
        _encode(before.cursor, adapter.StreamCursor), adapter.StreamCursor
    )
    hook = json.loads(s.rows[0])
    hook["params"]["_meta"]["eventId"] = "another-verified-marker"
    s.pending_receipts[(SESSION, PROMPT_A, "another-verified-marker")] = (
        s.key.pseudonymize("grok-receipt", "different-scope")
    )
    replay = [*s.rows[:5], json.dumps(hook).encode() + b"\n", *s.rows[1:5]]
    result = _batch(s, replay, cursor=restored)
    assert not result.observations and not result.boundaries
    (dispute,) = result.diagnostics
    assert dispute.code is DiagnosticCode.IDENTITY_CONFLICT
    assert dispute.observation_key == before.observations[0].key
    assert result.cursor == restored


def test_late_hook_cannot_backdate_a_receipt(grok_source):
    s = grok_source
    before = _batch(s, s.rows[1:5])
    late = _batch(s, [*s.rows[1:5], s.rows[0], s.rows[4]], cursor=before.cursor)
    assert not late.observations and not late.boundaries and not late.diagnostics
    assert late.cursor.checkpoint.offset > before.cursor.checkpoint.offset


def test_duplicate_cannot_evade_dispute_by_crossing_the_cutoff(grok_source):
    s = grok_source
    s.root = replace(s.root, cutoff=datetime.fromtimestamp(1793491200, UTC))
    before = _batch(s, s.rows[:5])
    duplicate = json.loads(s.rows[4])
    duplicate["timestamp"] -= 1
    duplicate["params"]["_meta"]["agentTimestampMs"] -= 1000
    revised = _batch(
        s, [*s.rows[:5], json.dumps(duplicate).encode() + b"\n"], cursor=before.cursor
    )
    assert not revised.observations and revised.cursor == before.cursor
    (dispute,) = revised.diagnostics
    assert dispute.code is DiagnosticCode.IDENTITY_CONFLICT
    assert dispute.observation_key == before.observations[0].key


def test_bounded_snapshot_reports_all_keyed_disputes_without_advancing(grok_source):
    s = grok_source
    before = _batch(s, s.rows, s.snapshot)
    for row in s.snapshot["turns"]:
        row["costUsdTicks"] += 1
    replay = _batch(s, s.rows, s.snapshot, before.cursor)
    assert not replay.observations and replay.cursor == before.cursor
    assert {item.observation_key for item in replay.diagnostics} == {
        item.key for item in before.observations
    }
    assert _codes(replay) == {DiagnosticCode.IDENTITY_CONFLICT}
    held = _batch(
        s, s.rows, {**s.snapshot, "padding": "x" * (2 * 1024 * 1024)}, before.cursor
    )
    assert not held.observations and held.cursor == before.cursor
    assert _codes(held) == {DiagnosticCode.COVERAGE_GAP}


def test_conflicting_native_turn_counts_hold_overlap(grok_source):
    s = grok_source
    native = _set_usage(s.rows[4], numTurns=1, turnCount=2)
    result = _batch(s, [*s.rows[:4], native])
    assert not result.observations and not result.cursor
    assert _codes(result) == {DiagnosticCode.OVERLAP_UNVERIFIED}


def test_complete_native_only_counts_with_corroboration_gap(grok_source):
    s = grok_source
    result = _batch(s, s.rows)
    assert len(result.observations) == 2
    assert _codes(result) == {DiagnosticCode.UNRECONCILED_USAGE}
    too_old = json.loads(json.dumps(s.snapshot))
    too_old["turns"][0]["endedAt"] = "2026-01-01T00:00:00+00:00"
    replay = _batch(s, s.rows, too_old)
    assert replay.observations == result.observations
    assert DiagnosticCode.UNRECONCILED_USAGE in _codes(replay)
    assert DiagnosticCode.IDENTITY_CONFLICT not in _codes(replay)


def test_snapshot_only_does_not_charge(grok_source):
    s = grok_source
    result = _batch(s, [], s.snapshot)
    assert not result.observations
    assert DiagnosticCode.UNRECONCILED_USAGE in _codes(result)


def test_headless_projection_is_only_corroboration(grok_source):
    s = grok_source
    verified = {entry["requestId"]: entry for entry in s.headless}
    baseline = _batch(
        s, s.rows, s.snapshot, headless=lambda _session, prompt: verified[prompt]
    )
    assert len(baseline.observations) == 2 and not baseline.diagnostics
    verified[PROMPT_A]["usage"]["input_tokens"] += 1152
    forged = _batch(
        s, s.rows, s.snapshot, headless=lambda _session, prompt: verified[prompt]
    )
    assert DiagnosticCode.IDENTITY_CONFLICT in _codes(
        forged
    ) or DiagnosticCode.MALFORMED_USAGE in _codes(forged)
    assert not any(
        item.key == baseline.observations[0].key for item in forged.observations
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"system": "Linux"},
        {"architecture": "x86_64"},
        {"version": "1.0.78"},
        {"build": "unknown"},
        {"executable_digest": "a" * 64},
        {"format_version": 2},
    ],
)
def test_unsupported_source_never_emits_usage(grok_source, changes):
    s = grok_source
    result = _batch(s, s.rows, s.snapshot, origin=replace(s.origin, **changes))
    assert not result.observations and not result.cursor
    assert _codes(result) == {DiagnosticCode.UNSUPPORTED_FORMAT}


def test_receipts_only_carry_verified_keyed_evidence(grok_source):
    s = grok_source
    baseline = _batch(s, s.rows, s.snapshot)
    absent = _batch(s, s.rows, s.snapshot, verifier=lambda *_: None)
    forged_ref = SourceRef("hmac-sha256:" + "0" * 64 + ":" + "0" * 64)
    forged = _batch(s, s.rows, s.snapshot, verifier=lambda *_: forged_ref)
    assert not absent.boundaries
    assert absent.observations == baseline.observations
    assert forged == absent
    assert (
        baseline.boundaries[0].boundary.receipt_ref
        == s.pending_receipts[(SESSION, PROMPT_A, "synthetic-event-1")]
    )
    for evidence in baseline.cursor, *baseline.boundaries, *baseline.observations:
        encoded = _encode(evidence, type(evidence))
        assert not any(
            secret in encoded
            for secret in (
                SESSION,
                PROMPT_A,
                PROMPT_B,
                "private-approved-root",
                "synthetic-marker",
            )
        )


def test_cancellation_concurrent_turns_and_invalid_clock_fail_closed(grok_source):
    s = grok_source
    cancelled = json.loads(s.rows[4])
    cancelled["params"]["update"]["stop_reason"] = "cancelled"
    bad_clock = json.loads(s.rows[4])
    bad_clock["timestamp"] += 5
    for mutation in (
        [s.rows[0], json.dumps(cancelled).encode() + b"\n"],
        [s.rows[0], s.rows[6], s.rows[4]],
        [json.dumps(bad_clock).encode() + b"\n"],
    ):
        result = _batch(s, mutation)
        assert not result.observations and not result.cursor


def test_rewind_and_copy_cannot_add_a_second_identity(grok_source):
    s = grok_source
    first = _batch(s, s.rows[:5])
    assert len(first.observations) == 1
    rewind = _batch(s, s.rows[1:5], cursor=first.cursor)
    assert not rewind.observations and rewind.cursor == first.cursor
    assert DiagnosticCode.SOURCE_REPLACED in _codes(rewind)
    copy = s.root.path / "archive" / SESSION
    copy.mkdir(parents=True)
    (s.directory / "updates.jsonl").unlink()
    s.directory = copy
    fresh = _batch(s, s.rows[:5])
    assert fresh.observations[0].key == first.observations[0].key
    unproven = _batch(s, s.rows[:5], origin=replace(s.origin, lineage_id=None))
    assert not unproven.observations and not unproven.cursor
