"""Exact planning and source coverage retained at child pickup."""

from collections.abc import Iterable
from pathlib import PurePosixPath
from typing import Annotated, Literal

from pydantic import AfterValidator, model_validator

from aitm_core.models.attempts import AttemptFact, Positive, SourceSnapshot, Text
from aitm_core.models.events import DIGEST
from aitm_core.models.lifecycle import DocumentAcceptance, JitEvidence
from aitm_core.models.operations import repository_path


class Baseline(AttemptFact):
    kind: Literal["source", "deliverable"]
    snapshot: SourceSnapshot


class Coverage(AttemptFact):
    baseline: Baseline
    plan_digest: DIGEST
    plan_generation: Positive
    attempt: Text
    attempt_generation: Positive
    paths: tuple[Annotated[str, AfterValidator(repository_path)], ...]
    complete: bool = True

    @model_validator(mode="after")
    def unique_paths(self):
        if len(set(self.paths)) != len(self.paths):
            raise ValueError("coverage paths must be unique")
        return self


def assess_jit(
    coverage: Coverage,
    baseline: Baseline,
    *,
    plan_digest: str,
    plan_generation: int,
    attempt: str,
    attempt_generation: int,
    descendant: bool = False,
    changed_paths: Iterable[str] | None = None,
) -> bool:
    """Accept identical inputs or a proven descendant with no covered changes."""
    if (
        not coverage.complete
        or coverage.plan_digest != plan_digest
        or coverage.plan_generation != plan_generation
        or coverage.attempt != attempt
        or coverage.attempt_generation != attempt_generation
        or coverage.baseline.kind != baseline.kind
    ):
        return False
    if coverage.baseline == baseline:
        return True
    if (
        coverage.baseline.snapshot.commit == baseline.snapshot.commit
        or not descendant
        or changed_paths is None
    ):
        return False
    tracked = tuple(PurePosixPath(path) for path in coverage.paths)
    for raw in changed_paths:
        path = PurePosixPath(repository_path(raw))
        if any(
            path.is_relative_to(item) or item.is_relative_to(path) for item in tracked
        ):
            return False
    return True


def record_jit(coverage: Coverage, plan: DocumentAcceptance) -> JitEvidence:
    """Prepare a replayable record for the current accepted plan and exact baseline."""
    if (
        plan.role != "plan"
        or plan.canonical_digest != coverage.plan_digest
        or plan.plan_generation != coverage.plan_generation
    ):
        raise ValueError("JIT evidence requires the current accepted plan")
    baseline = coverage.baseline
    return JitEvidence(
        plan_digest=coverage.plan_digest,
        plan_generation=coverage.plan_generation,
        attempt=coverage.attempt,
        code_baseline=baseline.snapshot.commit,
        coverage_paths=coverage.paths,
        coverage_status="complete" if coverage.complete else "partial",
        outcome="accepted" if coverage.complete else "hold",
        reviewed_revisions=(baseline.snapshot.commit,),
        baseline_kind=baseline.kind,
        baseline_snapshot=baseline.snapshot,
        attempt_generation=coverage.attempt_generation,
    )
