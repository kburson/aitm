"""Typed lifecycle records for the C02 event reducer."""

from pathlib import PurePosixPath
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

from aitm_core.models.config import DeliveryTarget
from aitm_core.models.events import EventActor

Text = Annotated[str, Field(min_length=1)]
Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Commit = Annotated[str, Field(pattern=r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")]
Positive = Annotated[int, Field(gt=0)]
StoryKind = Literal["story", "epic", "defect", "spike"]
EstimatePhase = Literal["decomposition", "refine", "plan", "jit"]
DocumentRole = Literal["design", "plan"]
Disposition = Literal["delivered", "abandoned", "superseded", "duplicate", "unverified"]


def _repository_path(value: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or ".." in path.parts or "\x00" in value:
        raise ValueError("expected a repository-relative path")
    return value


RepositoryPath = Annotated[Text, AfterValidator(_repository_path)]


class LifecycleFact(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class CapabilityObservation(LifecycleFact):
    id: Text
    version: Text
    status: Literal["available", "unavailable", "unknown"]


class WorkflowObservation(LifecycleFact):
    workflow_id: Text
    revision: Digest
    state_id: Text
    label: Text
    terminal: bool = False
    capability: CapabilityObservation | None = None


class WorkflowEdge(LifecycleFact):
    id: Text
    workflow_id: Text
    revision: Digest
    source: Text
    target: Text
    kind: Literal["normal", "rework", "reopen", "terminal"]


class Graduation(LifecycleFact):
    kind: StoryKind
    source_kind: Literal["draft", "plan-entry"]
    source_id: Text
    source_digest: Digest
    issue: Text
    parent: Positive | None = None
    source_intent: Text | None = None
    initial_state: WorkflowObservation
    delivery_target: DeliveryTarget | None = None


class KindSplit(LifecycleFact):
    from_kind: Literal["story"] = Field(alias="from")
    to_kind: Literal["epic"] = Field(alias="to")
    reason: Text
    scope_digest: Digest
    invalidated_acceptances: tuple[Digest, ...]
    invalidated_estimates: tuple[EstimatePhase, ...]
    decomposition_required: bool


class StateChange(LifecycleFact):
    from_state: WorkflowObservation = Field(alias="from")
    to_state: WorkflowObservation = Field(alias="to")
    edge: WorkflowEdge
    mode: Literal["enforce", "advisory"]
    reason: Text | None = None
    attempt: Text | None = None
    disposition: Disposition | None = None
    replacement_story: Positive | None = None


class Relationships(LifecycleFact):
    parent: Positive | None = None
    children: tuple[Positive, ...] = ()
    blocked_by: tuple[Positive, ...] = ()
    blocking: tuple[Positive, ...] = ()


class LinkChange(LifecycleFact):
    before: Relationships
    after: Relationships


class Description(LifecycleFact):
    title: Text
    actor: Text = Field(alias="as")
    want: Text
    so_that: Text
    scope: Text
    content_hash: Digest


class Estimate(LifecycleFact):
    phase: EstimatePhase
    agent_hours: Annotated[float, Field(ge=0, allow_inf_nan=False)]
    size: Text
    priority: Literal["P0", "P1", "P2", "P3"]


class DocumentAcceptance(LifecycleFact):
    role: DocumentRole
    path: RepositoryPath
    canonical_version: Literal["aitm.authored-content/v1"]
    canonical_digest: Digest
    raw_digest: Digest
    review_refs: Annotated[tuple[Text, ...], Field(min_length=1)]
    levels: Annotated[tuple[Literal["sar", "spr", "xpr"], ...], Field(min_length=1)]
    policy_digest: Digest
    source_planning_sha: Commit
    plan_generation: Positive


class JitEvidence(LifecycleFact):
    plan_digest: Digest
    plan_generation: Positive
    attempt: Text
    code_baseline: Commit
    coverage_paths: tuple[RepositoryPath, ...]
    coverage_status: Literal["complete", "partial", "unavailable"]
    outcome: Literal["accepted", "hold", "requires-review"]
    reviewed_revisions: tuple[Commit, ...]


class Deliverable(LifecycleFact):
    deliverable_id: Text
    path: RepositoryPath
    raw_digest: Digest
    canonical_digest: Digest | None = None
    attempt: Text
    source_snapshot: Commit


class SigningAgent(EventActor):
    kind: Literal["agent"]


class Signoff(LifecycleFact):
    retro: RepositoryPath
    confidence: Annotated[int, Field(ge=1, le=5)]
    verdict: Literal["delivered", "not-delivered"]
    by: SigningAgent


class LifecycleState(LifecycleFact):
    story_id: Positive
    graduation: Graduation
    kind: StoryKind
    relationships: Relationships = Field(default_factory=Relationships)
    split: KindSplit | None = None
    transitions: tuple[StateChange, ...] = ()
    description: Description | None = None
    estimates: dict[EstimatePhase, Estimate] = Field(default_factory=dict)
    accepted_documents: dict[DocumentRole, DocumentAcceptance] = Field(
        default_factory=dict
    )
    jit: JitEvidence | None = None
    deliverables: dict[str, Deliverable] = Field(default_factory=dict)
    signoffs: tuple[Signoff, ...] = ()

    @property
    def state_history(self) -> tuple[WorkflowObservation, ...]:
        return (
            self.graduation.initial_state,
            *(change.to_state for change in self.transitions),
        )

    @property
    def workflow_state(self) -> WorkflowObservation:
        return (
            self.transitions[-1].to_state
            if self.transitions
            else self.graduation.initial_state
        )

    @property
    def signoff(self) -> Signoff | None:
        return self.signoffs[-1] if self.signoffs else None
