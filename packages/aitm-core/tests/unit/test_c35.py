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
