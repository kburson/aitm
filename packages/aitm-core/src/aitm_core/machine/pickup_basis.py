"""Read the three current pickup bases from one pinned planning snapshot."""

from dataclasses import dataclass
from hashlib import sha256
from typing import Literal

from aitm_core.decomposition import (
    DecompositionUnavailable,
    assess_issued_entry,
    pin_accepted_document,
    prepare_decomposition,
    prepare_plan_entry,
)
from aitm_core.events import UnavailableReducer, core_reducers, fold
from aitm_core.jit import Baseline, Coverage, assess_jit
from aitm_core.models.attempts import SourceSnapshot
from aitm_core.models.decomposition import PlanEntry
from aitm_core.models.identity import PlanEntrySource
from aitm_core.models.lifecycle import LifecycleState
from aitm_core.models.operations import ReadExpectation, story_event_path
from aitm_core.store.backend import Backend, Snapshot

BasisKind = Literal["standalone", "epic", "child-jit"]


@dataclass(frozen=True, slots=True)
class SourceObservation:
    """Current source from the source adapter, with optional qualified change coverage."""

    current: Baseline
    descendant_of: Baseline | None = None
    changed_paths: tuple[str, ...] | None = None


@dataclass(frozen=True, slots=True)
class StandaloneBasis:
    plan_digest: str
    source: SourceObservation


@dataclass(frozen=True, slots=True)
class EpicBasis:
    plan_digest: str


@dataclass(frozen=True, slots=True)
class ChildJitBasis:
    entry: PlanEntrySource
    coverage: Coverage
    source: SourceObservation
    attempt: str
    attempt_generation: int
    checklist: str


@dataclass(frozen=True, slots=True)
class PickupBasisRequest:
    story: int
    policy_digest: str
    basis: StandaloneBasis | EpicBasis | ChildJitBasis


@dataclass(frozen=True, slots=True)
class PickupBasisResult:
    kind: BasisKind
    status: Literal["current", "hold", "unavailable"]
    reads: tuple[ReadExpectation, ...] = ()
    source: SourceSnapshot | None = None
    entry: PlanEntry | None = None
    scope_required: bool = False
    reason: str | None = None


def _lifecycle(store: Backend, snapshot: Snapshot, story: int):
    path = story_event_path(story)
    raw = store.read(snapshot, (path,))[path]
    if not raw:
        raise DecompositionUnavailable("story history is unavailable")
    state = fold(raw.splitlines(keepends=True), core_reducers())
    lifecycle = state.domains.get("lifecycle")
    if state.story_id != story or not isinstance(lifecycle, LifecycleState):
        raise ValueError("planning snapshot does not identify the requested story")
    return lifecycle, ReadExpectation(path=path, digest=sha256(raw).hexdigest())


def _standalone(
    store: Backend,
    snapshot: Snapshot,
    request: PickupBasisRequest,
    state: LifecycleState,
    proof: ReadExpectation,
) -> PickupBasisResult:
    basis = request.basis
    if not isinstance(basis, StandaloneBasis):
        return PickupBasisResult(
            "standalone", "hold", reason="standalone plan basis is required"
        )
    plan = state.accepted_documents.get("plan")
    if plan is None or plan.policy_digest != request.policy_digest:
        return PickupBasisResult(
            "standalone", "unavailable", reason="current accepted plan is unavailable"
        )
    if plan.canonical_digest != basis.plan_digest:
        return PickupBasisResult(
            "standalone", "hold", reason="accepted plan digest changed"
        )
    raw = store.read(snapshot, (plan.path,))[plan.path]
    header, read = pin_accepted_document(request.story, plan, raw)
    baseline = basis.source.current
    source = baseline.snapshot
    # The existing semantic source field is authenticated by the accepted plan.
    if header.get("source") != f"{baseline.kind}:{source.commit}:{source.tree}":
        return PickupBasisResult(
            "standalone", "hold", reason="accepted plan source is stale or missing"
        )
    if (state.kind == "spike") != (baseline.kind == "deliverable"):
        return PickupBasisResult(
            "standalone", "hold", reason="wrong baseline kind for story"
        )
    return PickupBasisResult("standalone", "current", (proof, read), source=source)


def _child(
    store: Backend,
    snapshot: Snapshot,
    request: PickupBasisRequest,
    state: LifecycleState,
    proof: ReadExpectation,
) -> PickupBasisResult:
    basis = request.basis
    if not isinstance(basis, ChildJitBasis):
        return PickupBasisResult(
            "child-jit", "hold", reason="child JIT basis is required"
        )
    graduation = state.graduation
    if (
        state.relationships.parent != basis.entry.parent
        or graduation.parent != basis.entry.parent
        or graduation.source_id != basis.entry.identity
        or graduation.source_digest != basis.entry.entry_digest
        or not basis.checklist.strip()
    ):
        return PickupBasisResult(
            "child-jit", "hold", reason="JIT does not identify the issued child entry"
        )
    parent = prepare_decomposition(
        store,
        snapshot,
        basis.entry.parent,
        basis.entry.plan_digest,
        request.policy_digest,
    )
    if prepare_plan_entry(parent, basis.entry.entry_key) != basis.entry:
        return PickupBasisResult(
            "child-jit", "hold", reason="JIT is pinned to a stale parent entry"
        )
    issued = assess_issued_entry(
        store,
        parent,
        graduation,
        request.story,
        design_coverage="own-document",
    )
    if issued.status != "current":
        status = "unavailable" if issued.status == "unavailable" else "hold"
        return PickupBasisResult("child-jit", status, reason=issued.reason)
    if (state.kind == "spike") != (basis.source.current.kind == "deliverable"):
        return PickupBasisResult(
            "child-jit", "hold", reason="wrong baseline kind for child"
        )
    freshness = assess_jit(
        basis.coverage,
        basis.source.current,
        plan_digest=parent.plan_digest,
        plan_generation=parent.plan_generation,
        attempt=basis.attempt,
        attempt_generation=basis.attempt_generation,
        descendant=basis.source.descendant_of == basis.coverage.baseline,
        changed_paths=basis.source.changed_paths,
    )
    if not freshness.applicable:
        return PickupBasisResult("child-jit", "hold", reason=freshness.reason)
    return PickupBasisResult(
        "child-jit",
        "current",
        (proof, *issued.reads),
        source=basis.source.current.snapshot,
        entry=parent.entry(basis.entry.entry_key),
        scope_required=True,
    )


def evaluate_pickup_basis(
    store: Backend,
    snapshot: Snapshot,
    request: PickupBasisRequest,
) -> PickupBasisResult:
    """Resolve source and plan applicability. The child scope decision is separate."""
    kind: BasisKind = "standalone"
    try:
        state, proof = _lifecycle(store, snapshot, request.story)
        if state.kind == "epic":
            kind = "epic"
            if not isinstance(request.basis, EpicBasis):
                return PickupBasisResult(
                    kind, "hold", reason="epic plan basis is required"
                )
            parent = prepare_decomposition(
                store,
                snapshot,
                request.story,
                request.basis.plan_digest,
                request.policy_digest,
            )
            return PickupBasisResult(kind, "current", parent.reads)
        if state.graduation.source_kind == "plan-entry":
            kind = "child-jit"
            return _child(store, snapshot, request, state, proof)
        if state.relationships.parent is not None:
            parent, parent_proof = _lifecycle(
                store, snapshot, state.relationships.parent
            )
            if parent.kind == "epic":
                return PickupBasisResult(
                    "child-jit", "hold", reason="epic child requires issued plan entry"
                )
            result = _standalone(store, snapshot, request, state, proof)
            if result.status == "current":
                return PickupBasisResult(
                    kind,
                    "current",
                    (*result.reads, parent_proof),
                    source=result.source,
                )
            return result
        return _standalone(store, snapshot, request, state, proof)
    except (DecompositionUnavailable, UnavailableReducer) as error:
        return PickupBasisResult(kind, "unavailable", reason=str(error))
    except ValueError as error:
        return PickupBasisResult(kind, "hold", reason=str(error))
