"""Qualify the pinned planning producer against the unchanged v1 receiver."""

import json
import subprocess
import sys
from hashlib import sha256
from importlib.resources import files

import pytest
from fixtures.receiver import ImportInterrupted, Receiver, ReceiverConflict
from test_effort_pinned_inputs import add_receipt, at, pin, write
from test_effort_session_publication import PROJECT, STORY
from test_effort_session_publication import repo_pair as repo_pair

from aitm_usage.effort.cli import main
from aitm_usage.effort.pinned_amounts import load_comparison_rates
from aitm_usage.effort.pinned_coverage import canonical as canonical_record
from aitm_usage.effort.pinned_inputs import read_inputs
from aitm_usage.effort.pinned_report import (
    build_pinned_report,
    freeze_report,
    report_path,
    validate_envelope,
)
from aitm_usage.effort.receipts import Outcome, UsageScope
from aitm_usage.effort.store import EffortError
from aitm_usage.types import Availability, TokenCounts

CARD = files("aitm_usage").joinpath("rates/effort/2026-11-25-sol-standard.json")
STORY_ID = 457
SOURCE = "hmac-sha256:" + "a" * 64
ATTEMPT = "5" * 64
SECRET = b"fixed-sensitive-core-fixture-key"
ACTOR = "ACTOR-PRIVATE-CANARY"
WINDOW = {
    "window_start_utc": "2026-11-25T00:00:00Z",
    "window_end_utc": "2026-11-25T01:00:00Z",
    "cutoff_utc": "2026-11-25T02:00:00Z",
}


def registration(repo, kind, relative, payload, stamp, **data):
    write(repo, f"{STORY}/{relative}", payload)
    fact = {
        "v": 0,
        "ts": stamp.isoformat(),
        "story": STORY_ID,
        "type": "core.evidence.recorded",
        "actor": {"kind": "agent"},
        "provenance": {"route": "manual-bootstrap", "runtime_transition": False},
        "data": {
            "kind": kind,
            "path": relative,
            "sha256": sha256(payload).hexdigest(),
            **data,
        },
    }
    with (repo / STORY / "events.jsonl").open("ab") as output:
        output.write(canonical_record(fact) + b"\n")


def exact_receipt(repo, *, revision=1, previous=None, **overrides):
    tokens = TokenCounts(
        input_tokens=100,
        cached_input_tokens=10,
        output_tokens=20,
        reasoning_output_tokens=1,
        total_tokens=120,
    )
    fields = {
        "model": "gpt-6.2-sol",
        "rate_inputs": (tokens,),
        "tokens": tokens,
        "coverage": Availability.COMPLETE,
        "outcome": Outcome.COMPLETED,
        **overrides,
    }
    return add_receipt(repo, rev=revision, prev=previous, **fields)


def roster(
    repo,
    *,
    window=WINDOW,
    phase="implement",
    state="observed",
    admission="closed",
    supersedes=None,
    additional=(),
):
    scope = {"project": str(PROJECT), "story": STORY_ID}
    record = {
        "schema": "aitm.story-effort-coverage/v1",
        **scope,
        "window": window,
        "admission": admission,
        "attempts": [{"attempt": ATTEMPT, "state": state}, *additional],
        "unattributed": 0 if admission == "closed" else None,
        "verified_no_work": False,
        "supersedes": supersedes,
        "attestation_sha256": "2" * 64 if admission == "closed" else None,
    }
    if phase is not None:
        path = f"attachments/timing/fixture-{STORY_ID}.json"
        timing = canonical_record(
            {
                "schema": "aitm.story-timing-receipt/v1",
                "project": "aitm",
                "subject": STORY_ID,
                "batch": "fixture",
                "recorded_at_utc": at(1, 5).isoformat(),
                "source": {"ref": "manual:fixture"},
                "observations": [
                    {
                        "observation_id": "fixture.turn",
                        "kind": "agent-turn",
                        "coverage": "complete",
                        "basis": "verified-turn-boundaries",
                        "actor": ACTOR,
                        "phase": phase,
                        "start_utc": at(0, 5).isoformat(),
                        "end_utc": at(1).isoformat(),
                    }
                ],
            }
        )
        registration(
            repo,
            "story-timing-receipt",
            path,
            timing,
            at(1, 5),
            scope={"project": "aitm", "story": STORY_ID},
        )
        record["timing"] = [
            {
                "attempt": ATTEMPT,
                "path": path,
                "sha256": sha256(timing).hexdigest(),
                "project": "aitm",
                "observation": "fixture.turn",
                "clock": "f" * 64,
                "waits": [],
            }
        ]
    payload = canonical_record(record)
    digest = sha256(payload).hexdigest()
    registration(
        repo,
        "story-effort-coverage",
        f"attachments/effort/coverage/{digest}.json",
        payload,
        at(2, 10),
        scope=scope,
        window=window,
    )
    return digest


def artifact(repo, *, window=WINDOW, rate_card=CARD, forged=False, source_pin=None):
    source_pin = source_pin or pin(repo)
    rates = load_comparison_rates(rate_card, sha256(rate_card.read_bytes()).hexdigest())
    inputs = read_inputs(repo, PROJECT, STORY_ID, source_pin, window)
    raw = build_pinned_report(inputs, rates)
    value = validate_envelope(raw)
    if forged:
        raw = freeze_report(
            value["manifest"], value["report"] | {"api_estimate_usd": "99"}
        )
        value = validate_envelope(raw)
    report_id = value["report_id"]
    write(repo, report_path(STORY_ID, report_id), raw)
    return pin(repo), report_id, raw


def export(repo, pair, rate_card=CARD, key=SECRET):
    from aitm_usage.effort.core_export import build_core_export

    return build_core_export(repo, pair[0], PROJECT, STORY_ID, pair[1], rate_card, key)


def materialize(path, outputs):
    path.mkdir()
    for name in ("manifest.json", "usage.jsonl"):
        (path / name).write_bytes(outputs[name])
    return path


def test_core_export_derives_pinned_rows_and_provenance(repo_pair, tmp_path):
    repo, _ = repo_pair
    receipt_digest = exact_receipt(repo)
    roster(repo)
    pair = artifact(repo)
    out = export(repo, pair)
    assert out == export(repo, pair)
    assert {b"\r\n" in raw for raw in out.values()} == {False}
    assert all(
        marker not in raw
        for raw in out.values()
        for marker in (ACTOR.encode(), SECRET, b"fixture.turn", str(repo).encode())
    )
    manifest = json.loads(out["manifest.json"])
    row = json.loads(out["usage.jsonl"])
    proof = json.loads(out["provenance.json"])
    assert manifest["schema"] == "aitm.usage.export/v1"
    assert manifest["cutoff"] == 1_795_572_000_000_000
    assert row["source"] == SOURCE and row["scope"]["phase"] == "development"
    assert row["model"] == row["client_version"] == "unknown"
    assert row["price"]["usd"] == "0.000381"
    assert proof["rows"][0]["receipt_sha256"] == receipt_digest
    assert proof["rows"][0]["model"] == "gpt-6.2-sol"
    assert proof["report_sha256"] == sha256(pair[2]).hexdigest()
    assert proof["cost_eligible"] is True
    assert proof["wire_sha256"]["usage.jsonl"] == sha256(out["usage.jsonl"]).hexdigest()
    snapshot = materialize(tmp_path / "snapshot", out)
    with Receiver(tmp_path / "receiver.db", PROJECT) as receiver:
        assert receiver.import_snapshot(snapshot) == "imported"
        assert receiver.accepted.keys() == {SOURCE}
        assert receiver.import_snapshot(snapshot) == "duplicate"


@pytest.mark.parametrize(
    "mode",
    [
        "unscoped",
        "unknown-phase",
        "partial",
        "inclusive",
        "grok",
        "disputed",
        "duplicate",
    ],
)
def test_core_export_preserves_held_evidence(repo_pair, tmp_path, mode):
    repo, _ = repo_pair
    overrides = {}
    if mode == "partial":
        overrides = {"coverage": Availability.PARTIAL, "outcome": Outcome.INTERRUPTED}
    elif mode == "inclusive":
        overrides = {"usage_scope": UsageScope.INCLUSIVE}
    elif mode == "grok":
        overrides = {
            "provider": "grok",
            "version": "1.0.92",
            "surface": "usage",
            "model": "grok-4.7-build-fast",
            "rate_inputs": None,
        }
    exact_receipt(repo, **overrides)
    if mode == "duplicate":
        add_receipt(repo, "b" * 64)
    roster(
        repo,
        phase=None
        if mode in ("unscoped", "disputed")
        else "unknown-phase"
        if mode == "unknown-phase"
        else "implement",
        state="disputed" if mode == "disputed" else "observed",
        admission="open" if mode == "unscoped" else "closed",
    )
    if mode == "duplicate":
        with pytest.raises(EffortError, match="Multiple pinned receipt identities"):
            artifact(repo)
        return
    out = export(repo, artifact(repo))
    proof = json.loads(out["provenance.json"])
    with Receiver(tmp_path / "receiver.db", PROJECT) as receiver:
        assert (
            receiver.import_snapshot(materialize(tmp_path / "snapshot", out))
            == "imported"
        )
        assert not receiver.accepted
        if mode in ("disputed", "grok", "duplicate"):
            assert not receiver.pending and not out["usage.jsonl"]
            assert proof["rows"][0]["status"] == "held"
        else:
            assert receiver.pending == {SOURCE}
            assert proof["rows"][0]["status"] == "pending"


def test_core_export_refuses_foreign_forged_and_wrong_rate(repo_pair, tmp_path):
    repo, _ = repo_pair
    exact_receipt(repo)
    roster(repo)
    pair = artifact(repo)
    with pytest.raises(EffortError, match="report"):
        export(repo, (pair[0], "b" * 64, pair[2]))
    with pytest.raises(EffortError, match="reproduce"):
        export(
            repo,
            artifact(
                repo,
                forged=True,
                source_pin=json.loads(pair[2])["manifest"]["planning_commit"],
            ),
        )
    other_rate = tmp_path / "other.json"
    other_rate.write_bytes(CARD.read_bytes().replace(b'"2"', b'"3"'))
    with pytest.raises(EffortError, match="rate card"):
        export(repo, pair, other_rate)
    with pytest.raises(EffortError, match="32 bytes"):
        export(repo, pair, key=SECRET + b"\n")


def test_fixture_reprices_and_refuses_scope_key_change_at_same_cutoff(
    repo_pair, tmp_path
):
    repo, _ = repo_pair
    exact_receipt(repo)
    roster(repo)
    pair = artifact(repo)
    original = export(repo, pair)
    pinned = json.loads(pair[2])["manifest"]["planning_commit"]
    revised_rate = tmp_path / "rate.json"
    revised_rate.write_bytes(
        CARD.read_bytes().replace(
            b'"uncached_input_per_million":"2"', b'"uncached_input_per_million":"3"'
        )
    )
    repriced_pair = artifact(repo, source_pin=pinned, rate_card=revised_rate)
    repriced = export(repo, repriced_pair, revised_rate)
    assert json.loads(repriced["usage.jsonl"])["price"]["usd"] == "0.000471"
    different_key = export(repo, pair, key=b"c" * 32)
    assert json.loads(different_key["usage.jsonl"])["source"] == SOURCE
    assert (
        json.loads(different_key["usage.jsonl"])["scope"]
        != json.loads(original["usage.jsonl"])["scope"]
    )
    first = materialize(tmp_path / "first", original)
    second = materialize(tmp_path / "repriced", repriced)
    wrong = materialize(tmp_path / "wrong", different_key)
    with Receiver(tmp_path / "receiver.db", PROJECT) as receiver:
        assert receiver.import_snapshot(first) == "imported"
        accepted = receiver.accepted
        with pytest.raises(ReceiverConflict, match="projection"):
            receiver.import_snapshot(wrong)
        assert receiver.accepted == accepted and not receiver.reconciliation
        assert receiver.import_snapshot(second) == "imported"
        assert receiver.accepted == accepted and receiver.reconciliation == {SOURCE: 1}
        assert (
            receiver.import_snapshot(first)
            == receiver.import_snapshot(second)
            == "duplicate"
        )


def test_fixture_reconciles_correction_and_retains_acceptance_after_dispute(
    repo_pair, tmp_path
):
    repo, _ = repo_pair
    digest = exact_receipt(repo)
    roster(repo)
    original = export(repo, artifact(repo))
    revision_window = WINDOW | {"cutoff_utc": "2026-11-25T02:05:00Z"}
    exact_receipt(repo, revision=2, previous=digest, observed_at=at(2, 5))
    late_attempt = "6" * 64
    add_receipt(repo, "b" * 64, attempt=late_attempt, observed_at=at(2, 5))
    roster(
        repo,
        window=revision_window,
        additional=({"attempt": late_attempt, "state": "observed"},),
    )
    revised = export(repo, artifact(repo, window=revision_window))
    rows = [json.loads(raw) for raw in revised["usage.jsonl"].splitlines()]
    assert rows[0]["source"] == SOURCE and rows[0]["observation_revision"] == 2
    assert any(
        row["source"] == "hmac-sha256:" + "b" * 64 and row["status"] == "pending"
        for row in json.loads(revised["provenance.json"])["rows"]
    )

    dispute_window = WINDOW | {"cutoff_utc": "2026-11-25T02:10:00Z"}
    roster(
        repo,
        window=dispute_window,
        state="disputed",
        phase=None,
        additional=({"attempt": late_attempt, "state": "observed"},),
    )
    disputed = export(repo, artifact(repo, window=dispute_window))
    assert any(
        row.get("reason") == "disputed"
        for row in json.loads(disputed["provenance.json"])["rows"]
    )
    initial = materialize(tmp_path / "first", original)
    with Receiver(tmp_path / "receiver.db", PROJECT) as receiver:
        assert receiver.import_snapshot(initial) == "imported"
        accepted = receiver.accepted
        assert (
            receiver.import_snapshot(materialize(tmp_path / "revised", revised))
            == "imported"
        )
        assert receiver.accepted == accepted and receiver.reconciliation == {SOURCE: 1}
        assert receiver.pending == {"hmac-sha256:" + "b" * 64}
        assert receiver.import_snapshot(initial) == "stale"
        assert (
            receiver.import_snapshot(materialize(tmp_path / "disputed", disputed))
            == "imported"
        )
        assert receiver.accepted == accepted and receiver.reconciliation == {SOURCE: 1}


def test_fixture_proves_ambiguous_acceptance_or_absence_before_identical_retry(
    repo_pair, tmp_path
):
    repo, _ = repo_pair
    exact_receipt(repo)
    roster(repo)
    pair = artifact(repo)
    original = export(repo, pair)
    row = original["usage.jsonl"].rstrip(b"\n")
    original_digest = sha256(row).hexdigest()
    snapshot = materialize(tmp_path / "snapshot", original)
    landed = tmp_path / "committed-before-lost-ack.db"
    with Receiver(landed, PROJECT) as receiver:
        receiver.import_snapshot(snapshot)
        # Simulate losing the response after the receiver committed.
    with Receiver(landed, PROJECT) as reopened:
        assert reopened.accepted[SOURCE] == original_digest
        assert reopened.ingest_usage(SOURCE, row) == "duplicate"
        altered = json.loads(row)
        altered["tokens"]["input_tokens"] += 1
        with pytest.raises(ReceiverConflict, match="source provenance"):
            reopened.ingest_usage(SOURCE, canonical_record(altered))
        assert reopened.accepted == {SOURCE: original_digest}

    rolled_back = tmp_path / "controlled-rollback.db"
    with Receiver(rolled_back, PROJECT) as receiver:
        with pytest.raises(ImportInterrupted):
            receiver.import_snapshot(snapshot, interrupt_after=1)
    with Receiver(rolled_back, PROJECT) as reopened:
        assert SOURCE not in reopened.accepted and SOURCE not in reopened.pending
        assert reopened.watermark is None
        assert (retry := export(repo, pair)) == original
        assert (
            reopened.import_snapshot(materialize(tmp_path / "retry", retry))
            == "imported"
        )
        assert reopened.accepted == {SOURCE: original_digest}


def core_cli(repo, pair, key):
    return [
        "--project",
        str(PROJECT),
        "story-core-export",
        str(STORY_ID),
        pair[1],
        "--repository",
        str(repo),
        "--artifact-commit",
        pair[0],
        "--rate-card",
        str(CARD),
        "--scope-key",
        str(key),
    ]


def test_core_export_cli_emits_exact_files_and_sanitizes_key_errors(
    repo_pair, tmp_path, capsys
):
    repo, _ = repo_pair
    exact_receipt(repo)
    roster(repo)
    pair = artifact(repo)
    key = tmp_path / "KEY-PATH-PRIVATE-CANARY"
    args = core_cli(repo, pair, key)
    assert main(args) == 2
    capture = capsys.readouterr()
    assert (
        "scope key" in capture.err and key.name not in capture.err and not capture.out
    )
    key.write_bytes(SECRET + b"\n")
    assert main(args) == 2
    assert "32 bytes" in capsys.readouterr().err
    key.write_bytes(SECRET)
    assert main(core_cli(repo, (pair[0], "b" * 64), key)) == 2
    assert "report unavailable" in capsys.readouterr().err
    command = [sys.executable, "-m", "aitm_usage.effort.cli", *args]
    raw = subprocess.check_output(command)
    bundle = json.loads(raw)
    assert raw == subprocess.check_output(command) and raw.endswith(b"\n")
    assert bundle["schema"] == "aitm.story-core-export-bundle/v1"
    assert {
        name: rendered.encode() for name, rendered in bundle["files"].items()
    } == export(repo, pair)


def test_oversized_cli_bundle_writes_no_stdout(
    repo_pair, tmp_path, capsys, monkeypatch
):
    from aitm_usage.effort import core_export

    repo, _ = repo_pair
    exact_receipt(repo)
    roster(repo)
    pair = artifact(repo)
    key = tmp_path / "key"
    key.write_bytes(SECRET)
    monkeypatch.setattr(core_export, "MAX_BUNDLE_BYTES", 1024)
    assert main(core_cli(repo, pair, key)) == 2
    output = capsys.readouterr()
    assert not output.out and "Core export bundle exceeds its byte limit" in output.err
