import asyncio
import json
import sys
from dataclasses import replace
from hashlib import sha256
from io import BytesIO
from uuid import UUID

import pytest

from aitm_usage.effort import Enrollment, Outcome, Role, UsageScope
from aitm_usage.effort.adapters.codex import CodexAdapter, CodexResume
from aitm_usage.effort.capture import (
    CaptureEvent,
    CaptureGap,
    HarnessCommand,
    capture,
    recover,
)
from aitm_usage.types import Availability, SourceRef, TokenCounts

BUILD = "0.171.0-alpha.13"
THREAD = str(UUID(int=20))
OTHER = str(UUID(int=21))
FIRST = str(UUID(int=31))
SECOND = str(UUID(int=32))
THIRD = str(UUID(int=33))
ENROLLMENT = Enrollment(UUID(int=1), UUID(int=2), UUID(int=3), Role.WORKER)
FIRST_USE = (19472, 13952, 9, 0)
SECOND_USE = (19502, 19328, 10, 2)
TOTAL_USE = (38974, 33280, 19, 2)


def ref(namespace, text):
    digest = sha256(f"{namespace}:{text}".encode()).hexdigest()
    return SourceRef(f"hmac-sha256:{digest}:{'0' * 64}")


ACCOUNT = ref("account", "fixture")


def lines(*rows):
    return b"".join(json.dumps(row).encode() + b"\n" for row in rows)


def row(kind, *, timestamp="2026-11-24T18:00:00.000Z", **payload):
    return {"type": kind, "timestamp": timestamp, "payload": payload}


def native(kind, **payload):
    return row("event_msg", type=kind, **payload)


def usage(counts, *, retained=False):
    gross, cached, output, reasoning = counts
    result = {
        "input_tokens": gross,
        "cached_input_tokens": cached,
        "cache_write_input_tokens": 0,
        "output_tokens": output,
    }
    if reasoning is not None:
        result["reasoning_output_tokens"] = reasoning
    if retained:
        result["total_tokens"] = gross + output
    return result


def header(session=THREAD, *, version=BUILD, surface="exec"):
    return lines(row("session_meta", id=session, cli_version=version, source=surface))


def turn(identifier, total=None, last=None, *, terminal="task_complete", error=None):
    bound = {"turn_id": identifier, "root_turn_id": identifier}
    start = lines(
        native("task_started", **bound, started_at=1795543200),
        row("turn_context", **bound, model="synthetic"),
        native("token_count", info=None),
    )
    counter = (
        b""
        if total is None
        else lines(
            native(
                "token_count",
                info={
                    "total_token_usage": usage(total, retained=True),
                    "last_token_usage": usage(last, retained=True),
                    "last_usage_includes_reasoning": True,
                },
            )
        )
    )
    return (
        start
        + counter
        + lines(
            native(
                terminal,
                **bound,
                completed_at=1795543201,
                timestamp="2026-11-24T18:00:01.000Z",
                **({} if error is None else {"error": error}),
            )
        )
    )


def stream(counts=FIRST_USE, *, session=THREAD, terminal="turn.completed"):
    return lines(
        {"type": "thread.started", "thread_id": session},
        {"type": "turn.started"},
        {"type": terminal, "usage": usage(counts)},
    )


def adapter(evidence=None, *, resume=None, max_bytes=1 << 20, **configuration):
    return CodexAdapter(
        ENROLLMENT.project_id,
        ACCOUNT,
        ref,
        open_rollout=None if evidence is None else lambda _: BytesIO(evidence),
        resume=resume,
        max_bytes=max_bytes,
        **configuration,
    )


def observe(codex, stdout, *, truncated=()):
    return codex.observe(CaptureEvent(ENROLLMENT, stdout, b"", frozenset(truncated)))


def exact(codex, evidence, identifier, *, session=THREAD, surface="exec"):
    return recover(
        codex,
        enrollment=ENROLLMENT,
        expected_turn=codex.native_turn(session, identifier, surface=surface),
        evidence=BytesIO(evidence),
    )


def tokens(counts):
    gross, cached, output, reasoning = counts
    return TokenCounts(gross, cached, None, None, output, reasoning, gross + output)


def test_fresh_headless_and_retrospective_receipt_are_identical():
    evidence = header() + turn(FIRST, FIRST_USE, FIRST_USE)
    codex = adapter(evidence)

    observation = observe(codex, stream())
    replay = exact(codex, evidence + turn(SECOND, TOTAL_USE, SECOND_USE), FIRST)

    assert observation == replay
    assert observation.gap is None
    assert observation.outcome is Outcome.COMPLETED
    assert observation.receipt.coverage is Availability.COMPLETE
    assert observation.receipt.tokens == tokens(FIRST_USE)
    assert observation.receipt.started_at is not None
    assert observation.receipt.ended_at > observation.receipt.started_at
    assert THREAD not in observation.receipt.to_json()


def test_resumed_headless_is_the_verified_delta_with_reasoning_and_cache():
    before = header() + turn(FIRST, FIRST_USE, FIRST_USE)
    evidence = before + turn(SECOND, TOTAL_USE, SECOND_USE)
    codex = adapter(evidence, resume=CodexResume(THREAD, before))

    observation = observe(codex, stream(TOTAL_USE))

    assert observation == exact(codex, evidence, SECOND)
    assert observation.receipt.tokens == tokens(SECOND_USE)


def test_prefixed_rollout_without_explicit_resume_is_not_fresh():
    evidence = header() + turn(FIRST, FIRST_USE, FIRST_USE)
    evidence += turn(SECOND, TOTAL_USE, SECOND_USE)
    assert observe(adapter(evidence), stream(TOTAL_USE)).gap is CaptureGap.WRONG_TURN


@pytest.mark.parametrize("mismatch", ["thread", "prefix", "counter", "last", "turn"])
def test_rejects_mismatched_resumed_evidence(mismatch):
    before = header() + turn(FIRST, FIRST_USE, FIRST_USE)
    suffix = turn(SECOND, TOTAL_USE, SECOND_USE)
    stdout = stream(TOTAL_USE)
    given_prefix = before
    if mismatch == "thread":
        stdout = stream(TOTAL_USE, session=OTHER)
    elif mismatch == "prefix":
        given_prefix = before.replace(b"synthetic", b"other")
    elif mismatch == "counter":
        stdout = stream((38975, 33280, 19, 2))
    elif mismatch == "last":
        suffix = turn(SECOND, TOTAL_USE, FIRST_USE)
    else:
        suffix += turn(THIRD, (38975, 33280, 19, 2), (1, 0, 0, 0))
    observation = observe(
        adapter(before + suffix, resume=CodexResume(THREAD, given_prefix)), stdout
    )
    assert observation.gap is not None
    assert observation.receipt is None


@pytest.mark.parametrize("partial", [False, True])
def test_interruption_retains_exact_turn_and_only_observed_usage(partial):
    counts = FIRST_USE if partial else None
    evidence = header() + turn(FIRST, counts, counts, terminal="turn_aborted")
    codex = adapter(evidence)
    stdout = b"\n".join(stream().splitlines()[:2]) + b"\n"

    observation = observe(codex, stdout)

    assert observation == exact(codex, evidence, FIRST)
    assert observation.outcome is Outcome.INTERRUPTED
    assert observation.receipt.coverage is (
        Availability.PARTIAL if partial else Availability.UNKNOWN
    )
    assert observation.gap is (None if partial else CaptureGap.MISSING)
    assert observation.receipt.tokens == (
        tokens(FIRST_USE) if partial else TokenCounts()
    )


def test_configured_interactive_exact_recovery_excludes_unassigned_baseline():
    evidence = header(surface="cli") + turn(FIRST, FIRST_USE, FIRST_USE)
    evidence += turn(SECOND, TOTAL_USE, SECOND_USE)
    codex = adapter()

    assert exact(codex, evidence, SECOND, surface="cli").receipt.tokens == tokens(
        SECOND_USE
    )
    assert exact(codex, evidence, SECOND).gap is CaptureGap.UNEXPECTED_HARNESS
    assert exact(codex, evidence, THIRD, surface="cli").gap is CaptureGap.WRONG_TURN
    assert (
        exact(codex, evidence, SECOND, session=OTHER, surface="cli").gap
        is CaptureGap.WRONG_TURN
    )


@pytest.mark.parametrize(
    ("evidence", "gap"),
    [
        (header(version="0.172.0"), CaptureGap.UNEXPECTED_HARNESS),
        (header() + b"{bad}\n", CaptureGap.MALFORMED),
        (
            header() + b'{"type": "ignored", "type": "turn_context"}\n',
            CaptureGap.MALFORMED,
        ),
    ],
)
def test_exact_rollout_rejects_invalid_or_unqualified_evidence(evidence, gap):
    assert exact(adapter(), evidence, FIRST).gap is gap


def test_headless_lookup_is_bounded_and_project_scoped():
    evidence = header() + turn(FIRST, FIRST_USE, FIRST_USE)

    assert observe(adapter(evidence, max_bytes=10), stream()).gap is (
        CaptureGap.EVIDENCE_LIMIT
    )
    event = CaptureEvent(
        replace(ENROLLMENT, project_id=UUID(int=9)), stream(), b"", frozenset()
    )
    assert adapter(evidence).observe(event).gap is CaptureGap.WRONG_ATTEMPT
    assert observe(adapter(), stream()).gap is CaptureGap.MISSING


def test_missing_reasoning_stays_unknown():
    native_counts = (25, 15, 9, None)
    evidence = header() + turn(FIRST, native_counts, native_counts)
    observation = observe(adapter(evidence), stream(native_counts))
    assert observation.receipt.coverage is Availability.PARTIAL
    assert observation.receipt.tokens == tokens(native_counts)


def test_bad_or_unbound_stdout_cannot_claim_an_exact_turn():
    evidence = header() + turn(FIRST, FIRST_USE, FIRST_USE)
    assert observe(adapter(evidence), b'{"type":9}\n').gap is CaptureGap.MALFORMED
    assert observe(adapter(evidence), b'{"type":"turn.started"}\n').gap is (
        CaptureGap.WRONG_TURN
    )


def test_failed_terminal_keeps_observed_partial_usage():
    evidence = header() + turn(
        FIRST, FIRST_USE, FIRST_USE, error={"message": "fixture"}
    )
    codex = adapter(evidence)
    result = observe(codex, stream(terminal="turn.failed"))
    assert result == exact(codex, evidence, FIRST)
    assert result.outcome is Outcome.FAILED
    assert result.receipt.coverage is Availability.PARTIAL
    assert result.receipt.tokens == tokens(FIRST_USE)


def test_truncated_stdout_retains_completed_exact_rollout():
    evidence = header() + turn(FIRST, FIRST_USE, FIRST_USE)
    codex = adapter(evidence)
    stdout = b"\n".join(stream().splitlines()[:2]) + b'\n{"type":"turn.comp'
    assert observe(codex, stdout, truncated=(1,)) == exact(codex, evidence, FIRST)


def test_recovery_distinguishes_an_open_turn_from_a_wrong_turn():
    evidence = header() + lines(native("task_started", turn_id=FIRST))
    codex = adapter()
    assert exact(codex, evidence, FIRST).gap is CaptureGap.MISSING
    assert exact(codex, evidence, SECOND).gap is CaptureGap.WRONG_TURN


def notification(session=THREAD, turn_id=SECOND, kind="agent-turn-complete"):
    return json.dumps({"type": kind, "thread-id": session, "turn-id": turn_id}).encode()


def test_armed_tui_notification_and_exact_recovery_agree():
    evidence = header(surface="cli") + turn(FIRST, FIRST_USE, FIRST_USE)
    evidence += turn(SECOND, TOTAL_USE, SECOND_USE)
    codex = adapter(evidence)

    observed = codex.observe_notification(
        ENROLLMENT,
        expected_turn=codex.native_turn(THREAD, SECOND, surface="cli"),
        notification=notification(),
    )

    assert observed == exact(codex, evidence, SECOND, surface="cli")
    assert observed.receipt.tokens == tokens(SECOND_USE)


@pytest.mark.parametrize(
    ("callback", "gap"),
    [
        (notification(session=OTHER), CaptureGap.WRONG_TURN),
        (notification(turn_id=FIRST), CaptureGap.WRONG_TURN),
        (notification(kind="other"), CaptureGap.MALFORMED),
        (b"broken", CaptureGap.MALFORMED),
    ],
)
def test_tui_notification_refuses_unbound_identity(callback, gap):
    evidence = header(surface="cli") + turn(FIRST, FIRST_USE, FIRST_USE)
    evidence += turn(SECOND, TOTAL_USE, SECOND_USE)

    codex = adapter(evidence)
    assert (
        codex.observe_notification(
            ENROLLMENT,
            expected_turn=codex.native_turn(THREAD, SECOND, surface="cli"),
            notification=callback,
        ).gap
        is gap
    )


def test_headless_cannot_bind_when_a_second_turn_is_still_open():
    evidence = header() + turn(FIRST, FIRST_USE, FIRST_USE)
    evidence += lines(native("task_started", turn_id=SECOND))
    assert observe(adapter(evidence), stream()).gap is CaptureGap.WRONG_TURN


def test_repeated_cumulative_quota_snapshot_does_not_double_count():
    initial = turn(FIRST, FIRST_USE, FIRST_USE)
    last_line = initial.splitlines(keepends=True)[-1]
    counter_line = initial.splitlines(keepends=True)[-2]
    evidence = header() + initial.removesuffix(last_line) + counter_line + last_line
    observation = observe(adapter(evidence), stream())
    assert observation.gap is None
    assert observation.receipt.tokens == tokens(FIRST_USE)


def test_changed_usage_in_an_unchanged_cumulative_snapshot_is_a_gap():
    initial = turn(FIRST, FIRST_USE, FIRST_USE)
    last_line = initial.splitlines(keepends=True)[-1]
    counter = json.loads(initial.splitlines(keepends=True)[-2])
    counter["payload"]["info"]["last_token_usage"] = usage(SECOND_USE, retained=True)
    evidence = header() + initial.removesuffix(last_line) + lines(counter) + last_line
    assert observe(adapter(evidence), stream()).gap is CaptureGap.MALFORMED


def explicit_record(identifier, cumulative, turn_counts, request_counts):
    return row(
        "token_usage_record",
        session_id=THREAD,
        thread_id=THREAD,
        turn_id=identifier,
        root_turn_id=identifier,
        response_id="synthetic-response",
        usage=usage(request_counts, retained=True),
        turn_token_usage=usage(turn_counts, retained=True),
        thread_token_usage=usage(cumulative, retained=True),
    )


def with_explicit_record(body, record, *, positional=True):
    *start, count, end = body.splitlines(keepends=True)
    return b"".join(start) + lines(record) + (count if positional else b"") + end


@pytest.mark.parametrize("positional", [True, False])
def test_explicit_native_witness_verifies_exact_turn_counts(positional):
    before = header() + turn(FIRST, FIRST_USE, FIRST_USE)
    body = turn(SECOND, TOTAL_USE, SECOND_USE)
    record = explicit_record(SECOND, TOTAL_USE, SECOND_USE, SECOND_USE)
    evidence = before + with_explicit_record(body, record, positional=positional)
    codex = adapter(evidence, resume=CodexResume(THREAD, before))
    observation = observe(codex, stream(TOTAL_USE))
    assert observation == exact(codex, evidence, SECOND)
    assert observation.receipt.tokens == tokens(SECOND_USE)


@pytest.mark.parametrize(
    ("field", "value", "gap"),
    [
        ("session_id", OTHER, CaptureGap.WRONG_TURN),
        ("thread_id", OTHER, CaptureGap.WRONG_TURN),
        ("turn_id", SECOND, CaptureGap.WRONG_TURN),
        ("root_turn_id", SECOND, CaptureGap.WRONG_TURN),
        ("turn_token_usage", usage(SECOND_USE, retained=True), CaptureGap.MALFORMED),
        ("thread_token_usage", usage(SECOND_USE, retained=True), CaptureGap.MALFORMED),
        ("usage", usage(SECOND_USE, retained=True), CaptureGap.MALFORMED),
    ],
    ids=[
        "session",
        "thread",
        "turn",
        "root",
        "turn-usage",
        "thread-usage",
        "request-usage",
    ],
)
def test_explicit_native_witness_must_agree_with_positional_evidence(field, value, gap):
    record = explicit_record(FIRST, FIRST_USE, FIRST_USE, FIRST_USE)
    record["payload"][field] = value
    evidence = header() + with_explicit_record(
        turn(FIRST, FIRST_USE, FIRST_USE), record
    )
    assert observe(adapter(evidence), stream()).gap is gap


@pytest.mark.parametrize(
    ("configuration", "scope"),
    [
        ({}, UsageScope.UNKNOWN),
        ({"scope": UsageScope.MIXED}, UsageScope.MIXED),
        ({"scope": UsageScope.BOUNDED}, UsageScope.BOUNDED),
    ],
    ids=["unknown-default", "mixed", "bounded"],
)
def test_scope_comes_from_caller_authority(configuration, scope):
    evidence = header() + turn(FIRST, FIRST_USE, FIRST_USE)
    assert observe(adapter(evidence, **configuration), stream()).receipt.scope is scope


def test_bounded_capture_and_exact_file_recovery_agree(tmp_path):
    rollout = tmp_path / "authorized.jsonl"
    evidence = header() + turn(FIRST, FIRST_USE, FIRST_USE)
    script = (
        "import sys; from pathlib import Path; "
        f"Path('authorized.jsonl').write_bytes({evidence!r}); "
        f"sys.stdout.buffer.write({stream()!r})"
    )
    codex = CodexAdapter(
        ENROLLMENT.project_id, ACCOUNT, ref, open_rollout=lambda _: rollout.open("rb")
    )

    result = asyncio.run(
        capture(
            codex,
            enrollment=ENROLLMENT,
            command=HarnessCommand((sys.executable, "-c", script), tmp_path),
        )
    )

    assert result.process.returncode == 0
    with rollout.open("rb") as selected:
        recovered = recover(
            codex,
            enrollment=ENROLLMENT,
            expected_turn=codex.native_turn(THREAD, FIRST, surface="exec"),
            evidence=selected,
        )
    assert result.observation == recovered
    assert result.observation.receipt.tokens == tokens(FIRST_USE)
