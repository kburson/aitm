import asyncio
import json
import sys
from dataclasses import replace
from datetime import UTC, datetime
from io import BytesIO
from uuid import UUID

import pytest

from aitm_usage.effort import (
    Disposition,
    EffortStore,
    Enrollment,
    NativeTurn,
    Outcome,
    Role,
    UsageReceipt,
)
from aitm_usage.effort import capture as effort_capture
from aitm_usage.types import Availability, SourceRef, TokenCounts


def source_ref(digit):
    return SourceRef(f"hmac-sha256:{'0' * 64}:{digit * 64}")


ENROLLMENT = Enrollment(UUID(int=1), UUID(int=2), UUID(int=3), Role.WORKER)
TURN = NativeTurn(
    "fixture", "1", "headless", source_ref("1"), source_ref("2"), source_ref("3")
)


class FixtureAdapter:
    def observe(self, event):
        line = event.stdout.splitlines()[0] if event.stdout else b""
        return self.decode(event.enrollment, line)

    def recover(self, exact_ref):
        return self.decode(exact_ref.enrollment, exact_ref.evidence)

    def decode(self, enrollment, evidence):
        if not evidence:
            return effort_capture.Observation(gap=effort_capture.CaptureGap.MISSING)
        data = json.loads(evidence)
        outcome = Outcome(data["terminal"])
        receipt = UsageReceipt(
            project_id=enrollment.project_id,
            attempt_id=enrollment.attempt_id,
            turn=TURN,
            source_sha256="4" * 64,
            observed_at=datetime(2026, 11, 24, tzinfo=UTC),
            revision=1,
            coverage=Availability.PARTIAL,
            outcome=outcome,
            tokens=TokenCounts(total_tokens=data["tokens"]),
        )
        return effort_capture.Observation(outcome, receipt)


def launch(tmp_path, script, **kwargs):
    return asyncio.run(
        effort_capture.capture(
            FixtureAdapter(),
            enrollment=ENROLLMENT,
            command=effort_capture.HarnessCommand(
                (sys.executable, "-c", script), cwd=tmp_path
            ),
            **kwargs,
        )
    )


@pytest.mark.parametrize(
    ("terminal", "returncode", "tokens"),
    [("interrupted", 0, 8), ("failed", 9, 12)],
)
def test_terminal_outcome_and_usage_survive_process_exit(
    tmp_path, terminal, returncode, tokens
):
    line = json.dumps({"terminal": terminal, "tokens": tokens})
    result = launch(tmp_path, f"print({line!r}); raise SystemExit({returncode})")

    assert result.process.state is effort_capture.ProcessState.EXITED
    assert result.process.returncode == returncode
    assert result.observation.outcome is Outcome(terminal)
    assert result.observation.receipt.tokens.total_tokens == tokens
    assert line not in repr(result)


def test_stream_limit_preserves_prior_terminal_receipt(tmp_path):
    line = '{"terminal":"failed","tokens":12}'
    result = launch(
        tmp_path,
        f"import sys; print({line!r}, flush=True); sys.stderr.write('x' * 16384)",
        limits=effort_capture.CaptureLimits(stdout_bytes=128, stderr_bytes=64),
    )

    assert result.process.state is effort_capture.ProcessState.OUTPUT_LIMIT
    assert result.observation.outcome is Outcome.FAILED
    assert result.observation.receipt.tokens.total_tokens == 12


def test_timeout_is_independent_of_unobserved_terminal_outcome(tmp_path):
    result = launch(
        tmp_path,
        "import time; time.sleep(10)",
        limits=effort_capture.CaptureLimits(timeout_seconds=0.05),
    )

    assert result.process.state is effort_capture.ProcessState.TIMED_OUT
    assert result.process.returncode is not None
    assert result.observation.outcome is Outcome.UNKNOWN
    assert result.observation.gap is effort_capture.CaptureGap.MISSING


def test_configured_launch_inherits_only_selected_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("AITM_FIXTURE_SIGN_IN", "fixture-profile")
    monkeypatch.setenv("AITM_FIXTURE_UNRELATED", "fixture-secret")
    script = (
        "from os import environ; "
        f"assert environ['HOME'] == {str(tmp_path)!r}; "
        "assert environ['AITM_FIXTURE_SIGN_IN'] == 'fixture-profile'; "
        "assert 'AITM_FIXTURE_UNRELATED' not in environ; "
        'print(\'{"terminal":"completed","tokens":0}\')'
    )
    command = effort_capture.HarnessCommand(
        (sys.executable, "-c", script),
        cwd=tmp_path,
        inherit_env=frozenset({"AITM_FIXTURE_SIGN_IN"}),
    )
    result = asyncio.run(
        effort_capture.capture(FixtureAdapter(), enrollment=ENROLLMENT, command=command)
    )

    assert result.process.returncode == 0
    assert result.observation.outcome is Outcome.COMPLETED


def test_exact_recovery_replays_live_observation(tmp_path):
    line = '{"terminal":"completed","tokens":23}'
    store = EffortStore(tmp_path / "effort.sqlite3", ENROLLMENT.project_id)
    store.enroll(ENROLLMENT)
    live = launch(tmp_path, f"print({line!r})").observation
    assert store.ingest(live.receipt) is Disposition.INSERTED

    recovered = effort_capture.recover(
        FixtureAdapter(),
        enrollment=ENROLLMENT,
        expected_turn=replace(TURN, surface="retained"),
        evidence=BytesIO(line.encode()),
    )

    assert recovered.receipt.observation_id == live.receipt.observation_id
    assert store.ingest(recovered.receipt) is Disposition.REPLAYED


@pytest.mark.parametrize("field", ["account", "session", "turn"])
def test_recovery_rejects_evidence_for_another_native_turn(field):
    result = effort_capture.recover(
        FixtureAdapter(),
        enrollment=ENROLLMENT,
        expected_turn=replace(TURN, **{field: source_ref("5")}),
        evidence=BytesIO(b'{"terminal":"completed","tokens":23}'),
    )

    assert result.gap is effort_capture.CaptureGap.WRONG_TURN
    assert result.receipt is None
    assert result.outcome is Outcome.UNKNOWN


def test_recovery_reads_only_up_to_evidence_limit():
    evidence = BytesIO(b"z" * 30)
    result = effort_capture.recover(
        FixtureAdapter(),
        enrollment=ENROLLMENT,
        expected_turn=TURN,
        evidence=evidence,
        max_bytes=8,
    )

    assert evidence.tell() == 9
    assert result.gap is effort_capture.CaptureGap.EVIDENCE_LIMIT
