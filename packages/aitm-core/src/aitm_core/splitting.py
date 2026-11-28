"""Bounded Refine split and pre-implementation Design recovery."""

from dataclasses import dataclass
from hashlib import sha256

from pydantic import BaseModel

from aitm_core.description import (
    DescriptionInput,
    DescriptionTarget,
    describe,
    description_path,
)
from aitm_core.documents import canonicalize
from aitm_core.events import UnavailableReducer, core_reducers, fold
from aitm_core.machine.obligations import validate_profile
from aitm_core.machine.transitions import (
    TransitionRequest,
    _read,
    _snapshot,
    event_records,
)
from aitm_core.models.attempts import AttemptState
from aitm_core.models.common import CommandResult, LocalOutcome
from aitm_core.models.documents import DocumentSchema
from aitm_core.models.events import validate_envelope
from aitm_core.models.lifecycle import (
    Description,
    DesignInvalidated,
    KindSplit,
    LifecycleState,
    StateChange,
    WorkflowEdge,
    WorkflowObservation,
)
from aitm_core.models.operations import (
    EventAppend,
    FinalizationIntent,
    Operation,
    OperationCategory,
    ReadExpectation,
    RelatedWriteSet,
    story_event_path,
)
from aitm_core.reducers.evidence import EvidenceState
from aitm_core.services import UnavailablePort
from aitm_core.store.backend import OperationResult


@dataclass(frozen=True, slots=True)
class SplitRequest:
    transition: TransitionRequest
    scope: str
    reason: str
    leaf_hours: float


class SplitRefusal(ValueError):
    """Current story facts place it outside the bounded operation."""


def _pending_authority(state) -> bool:
    evidence = state.domains.get("evidence")
    if not isinstance(evidence, EvidenceState):
        return False
    prefixes = (
        "core.execution.",
        "core.pr.",
        "core.dev.",
        "core.identity.",
        "core.story.graduat",
    )
    return any(
        record.pending.action_id.startswith(prefixes)
        and (
            record.result is None
            or getattr(record.result, "outcome", "") in {"uncertain", "unavailable"}
        )
        for record in evidence.actions.values()
    )


def _parent_read(request, snapshot, story) -> ReadExpectation | None:
    parent = story.relationships.parent
    if parent is None:
        return None
    location = story_event_path(parent)
    raw = request.backend.read(snapshot, (location,))[location]
    if not raw:
        raise SplitRefusal("Parent relationship evidence is unavailable.")
    pinned = fold(raw.splitlines(keepends=True), core_reducers())
    lifecycle = pinned.domains.get("lifecycle")
    if (
        pinned.story_id != parent
        or not isinstance(lifecycle, LifecycleState)
        or story.story_id not in lifecycle.relationships.children
    ):
        raise SplitRefusal("Parent and child relationships are inconsistent.")
    evidence = pinned.domains.get("evidence")
    if isinstance(evidence, EvidenceState) and any(
        row.envelope.data.get("child") == story.story_id
        for label in ("core.expansion.recorded", "core.expansion.reservation-resolved")
        for row in evidence.facts.get(label, ())
    ):
        raise SplitRefusal("An expansion child cannot be split.")
    return ReadExpectation(path=location, digest=sha256(raw).hexdigest())


def _scope_change(request, snapshot, path, raw, story, scope):
    current = story.description
    if current is None:
        raise SplitRefusal("The existing authored description is required.")
    authored_path = description_path(request.story)
    authored = request.backend.read(snapshot, (authored_path,))[authored_path]
    if (
        authored is not None
        and canonicalize(authored, DocumentSchema()).canonical_sha256
        != current.content_hash
    ):
        raise SplitRefusal(
            "The authored description changed since the structured scope was recorded."
        )
    operation = describe(
        DescriptionTarget(
            request.story,
            {path: raw, authored_path: authored},
            request.owner,
            request.policy_digest,
            request.operation_id,
            request.at,
        ),
        DescriptionInput(
            title=current.title,
            actor=current.actor,
            want=current.want,
            so_that=current.so_that,
            scope=scope,
        ),
    )
    event = validate_envelope(operation.change.events[0].records[0])
    fact = Description.model_validate(event.data)
    return operation.change, fact


def _move(
    request: TransitionRequest, reason: str, split: SplitRequest | None
) -> OperationResult:
    snapshot = _snapshot(request)
    try:
        path, raw, state, story = _read(request, snapshot)
        current = story.workflow_state
        profile = request.profile
        validity = validate_profile(profile, request.registry, request.contract)
        if (
            not validity.valid
            or current.workflow_id != profile.id
            or current.revision != profile.source.digest
        ):
            raise ValueError("The story requires a valid current workflow profile.")
        if not reason.strip():
            raise SplitRefusal("Provide a reason for Design rework.")
        if isinstance(state.domains.get("attempts"), AttemptState):
            raise SplitRefusal("A retained attempt fences Design rework and split.")
        if _pending_authority(state):
            raise SplitRefusal(
                "An unresolved execution or identity operation fences this change."
            )
        target_id = profile.recovery.design_rework
        if request.target not in (None, target_id):
            raise SplitRefusal(
                "The requested state differs from the configured Design destination."
            )
        recovered = next(item for item in profile.states if item.id == target_id)
        if current.terminal or current.state_id == target_id:
            raise SplitRefusal(
                "Design rework requires an eligible nonterminal source state."
            )

        facts: list[tuple[str, str, BaseModel]] = []
        reads = (ReadExpectation(path=path, digest=sha256(raw).hexdigest()),)
        writes = ()
        invalidations = {
            "invalidated_acceptances": tuple(
                sorted(
                    item.canonical_digest for item in story.accepted_documents.values()
                )
            ),
            "invalidated_estimates": tuple(sorted(story.estimates)),
        }
        if split is not None:
            if current.state_id != "refine":
                raise SplitRefusal("An oversized leaf can split only in Refine.")
            if story.kind == "epic":
                raise SplitRefusal("Only a leaf can be split into an epic.")
            if story.relationships.children:
                raise SplitRefusal("A leaf with existing children cannot be split.")
            parent_read = _parent_read(request, snapshot, story)
            estimate = story.estimates.get("refine")
            if estimate is None or estimate.agent_hours <= split.leaf_hours:
                raise SplitRefusal(
                    "Split requires a current oversized Refine estimate."
                )
            if story.description is not None and split.scope == story.description.scope:
                raise SplitRefusal("Split requires revised authored scope.")
            change, description = _scope_change(
                request, snapshot, path, raw, story, split.scope
            )
            reads = change.read_set + ((parent_read,) if parent_read else ())
            writes = change.writes
            kind = KindSplit(
                **{"from": story.kind, "to": "epic"},
                reason=reason,
                scope_digest=description.content_hash,
                decomposition_required=True,
                **invalidations,
            )
            facts.extend(
                [
                    (
                        "core.description.set",
                        f"{request.operation_id}:description",
                        description,
                    ),
                    ("core.kind.changed", f"{request.operation_id}:kind", kind),
                ]
            )
            operation = "state.split"
        else:
            if current.state_id not in {
                "refine",
                "ready-for-plan",
                profile.lifecycle.reopen_plan,
            }:
                raise SplitRefusal(
                    "Design rework applies to Refine or planning before implementation."
                )
            facts.append(
                (
                    "core.design.invalidated",
                    f"{request.operation_id}:invalidate",
                    DesignInvalidated(reason=reason, **invalidations),
                )
            )
            operation = "state.design-rework"
        destination = WorkflowObservation(
            workflow_id=profile.id,
            revision=profile.source.digest,
            state_id=target_id,
            label=recovered.label,
        )
        move = StateChange(
            **{"from": current, "to": destination},
            edge=WorkflowEdge(
                id=operation,
                workflow_id=profile.id,
                revision=profile.source.digest,
                source=current.state_id,
                target=target_id,
                kind="rework",
            ),
            mode=request.mode,
            reason=reason,
        )
        facts.append(("core.state.changed", f"{request.operation_id}:state", move))
        read_digest = RelatedWriteSet(read_set=reads).read_set_digest
        records = event_records(request, raw, state, read_digest, facts)
        op = Operation(
            operation_id=request.operation_id,
            owner=request.owner,
            policy_digest=request.policy_digest,
            category=OperationCategory.NORMAL,
            intent=FinalizationIntent(
                kind=operation,
                version=1,
                related_preconditions=reads,
                payload=move.model_dump_json(by_alias=True).encode(),
            ),
            change=RelatedWriteSet(
                read_set=reads,
                events=(EventAppend(story=request.story, records=records),),
                writes=writes,
            ),
        )
        return (request.transact or request.backend.transact)(op, snapshot)
    except SplitRefusal as error:
        outcome, reason = LocalOutcome.REFUSED, str(error)
    except (UnavailablePort, UnavailableReducer) as error:
        outcome, reason = LocalOutcome.UNAVAILABLE, str(error)
    except ValueError as error:
        outcome, reason = LocalOutcome.INTEGRITY_ERROR, str(error)
    return OperationResult(
        CommandResult(
            operation_id=request.operation_id, local=outcome, evidence=(reason,)
        ),
        snapshot,
        reason,
    )


def split_leaf(request: SplitRequest) -> OperationResult:
    """Convert an eligible numbered Refine leaf and atomically invalidate old scope."""
    return _move(request.transition, request.reason, request)


def rework_design(request: TransitionRequest) -> OperationResult:
    """Reopen the configured pre-implementation Design route with a retained reason."""
    return _move(request, request.reason or "", None)
