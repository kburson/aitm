"""Protect the verification command and assurance boundaries."""

import os
from pathlib import Path

import pytest

from aitm_core.verification.lanes import capture_command, select_lane


def test_uv_run_uses_pinned_installer_and_offline_no_sync():
    installer = Path("/trusted/bin/uv")
    assert capture_command("uv run python 'check inputs.py'", installer) == (
        os.fspath(installer),
        "--no-config",
        "run",
        "--no-sync",
        "--offline",
        "--no-python-downloads",
        "--",
        "python",
        "check inputs.py",
    )


@pytest.mark.parametrize(
    "command", ["sh -c 'echo test'", "uv sync", "uv run", "uv run --online x"]
)
def test_unmanaged_command_cannot_bypass_the_locked_launcher(command):
    with pytest.raises(ValueError, match="verification command"):
        capture_command(command, Path("/trusted/bin/uv"))


def test_contained_never_uses_export_adapter_on_unknown_platform():
    assert select_lane("contained", "unsupported").probe().assurance is None
    assert (
        select_lane("captured-export", "unsupported").probe().assurance
        == "captured-export"
    )


def test_pre_review_requires_an_exact_hosted_candidate():
    from aitm_core.models.attempts import ExecutionCandidate, SourceSnapshot
    from aitm_core.verification.guards import (
        HostedCandidate,
        LocalCandidateProof,
        VerificationBasis,
        candidate_guard,
    )

    source = SourceSnapshot(commit="a" * 40, tree="b" * 40)
    tested = SourceSnapshot(commit="c" * 40, tree="d" * 40)
    candidate = ExecutionCandidate(source=source, capture_manifest="e" * 64)
    basis = VerificationBasis(
        story=42,
        attempt="attempt-1",
        generation=1,
        candidate=candidate,
        policy="f" * 64,
        source_proof="story-tagged",
        expansion_resolved=True,
        hosted=HostedCandidate(
            "owner/repo", 601, "refs/heads/trunk", "1" * 40, source, tested
        ),
    )
    calls = []

    def local(current):
        return LocalCandidateProof(
            current.story,
            current.attempt,
            current.generation,
            current.candidate,
            current.policy,
            "passed",
        )

    def hosted(stale):
        def read(target):
            calls.append(target)
            return (stale, "passed")

        return read

    assert candidate_guard(basis, local, hosted(basis.hosted)).status == "pass"
    from dataclasses import replace

    stale = replace(basis.hosted, base="2" * 40)
    assert candidate_guard(basis, local, hosted(stale)).status == "blocked"
    assert candidate_guard(basis, local, None).status == "unavailable"
    assert (
        candidate_guard(
            replace(basis, expansion_resolved=False), local, hosted(stale)
        ).status
        == "blocked"
    )
    assert calls == [basis.hosted, basis.hosted]


def test_recording_an_unknown_launch_does_not_report_verification_complete():
    from aitm_core.execution.executor import ExecutionResult
    from aitm_core.models.common import CommandResult, LocalOutcome, PublicationOutcome
    from aitm_core.verification.run import verification_command

    observed = ExecutionResult(
        CommandResult(
            operation_id="execution",
            local=LocalOutcome.COMPLETED,
            publication=PublicationOutcome.VERIFIED,
        ),
    )
    result = verification_command(observed, None)
    assert result.local == LocalOutcome.UNAVAILABLE
    assert result.publication == PublicationOutcome.VERIFIED


def test_configured_candidate_guard_retains_code_and_story_read():
    from datetime import datetime
    from hashlib import sha256

    from aitm_core.events import core_reducers, fold
    from aitm_core.machine.guards import GuardCall, core_guard
    from aitm_core.machine.profile import WorkflowEdge
    from aitm_core.models.attempts import (
        AttemptStarted,
        ClockChanged,
        ExecutionCandidate,
        SourceSnapshot,
    )
    from aitm_core.models.operations import ReadExpectation, story_event_path
    from aitm_core.relationships import EventContext
    from aitm_core.rules.trips import _append
    from aitm_core.services import ServicePorts
    from aitm_core.store.memory_backend import MemoryBackend
    from aitm_core.verification.guards import (
        CandidateVerification,
        HostedCandidate,
        LocalCandidateProof,
        VerificationBasis,
    )
    from tests.unit.test_c15 import OWNER, STAMP, graduated

    policy = "f" * 64
    source = SourceSnapshot(commit="a" * 40, tree="b" * 40)
    candidate = ExecutionCandidate(source=source, capture_manifest="e" * 64)
    tested = SourceSnapshot(commit="c" * 40, tree="d" * 40)
    target = HostedCandidate(
        "owner/repo", 601, "refs/heads/trunk", "1" * 40, source, tested
    )
    raw = graduated()
    reducers = core_reducers()
    state = fold([raw], reducers)
    attempt = AttemptStarted(
        attempt="attempt-1",
        generation=1,
        plan_generation=1,
        source=source,
        binding="binding-1",
        allowance_millis=1000,
    )
    clock = ClockChanged(
        attempt=attempt.attempt,
        generation=attempt.generation,
        cause_event_id="attempt-open:started:16",
        **{"from": None, "to": "active"},
        observed_at=datetime.fromisoformat(STAMP),
        used_millis=0,
    )
    appended = _append(
        EventContext("attempt-open", OWNER, STAMP, policy),
        state,
        raw,
        [
            ("core.attempt.started", attempt, "started"),
            ("core.attempt.clock.changed", clock, "clock"),
        ],
        include_null_data=True,
    )
    raw += b"".join(record + b"\n" for record in appended.records)
    path = story_event_path(16)
    backend = MemoryBackend({path: raw})
    lifecycle = fold(raw.splitlines(keepends=True), reducers).domains["lifecycle"]
    call = GuardCall(
        "core.dev.review-candidate-current",
        1,
        "onEnter",
        backend.snapshot(),
        lifecycle,
        WorkflowEdge.model_validate({"from": "dev", "to": "review"}),
        {path: raw},
        policy,
    )

    port = CandidateVerification(
        basis=lambda _: VerificationBasis(
            16,
            attempt.attempt,
            attempt.generation,
            candidate,
            policy,
            "story-tagged",
            True,
            target,
        ),
        local=lambda _: LocalCandidateProof(
            16, attempt.attempt, attempt.generation, candidate, policy, "passed"
        ),
        hosted=lambda observed: (observed, "passed"),
    )
    kind, exit_guard = ServicePorts(candidate_verification=port).workflow_guard_ports(
        source
    )
    result = core_guard(
        call, leaf_hours=4, kind_requirements=kind, story_exit_guards=exit_guard
    )
    assert (result.status, result.code) == (
        "pass",
        "exact-candidate-verification-current",
    )
    assert result.reads == (ReadExpectation(path=path, digest=sha256(raw).hexdigest()),)
