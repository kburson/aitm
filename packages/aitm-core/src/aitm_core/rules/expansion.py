"""Reserve, finalize, and resolve an expansion against the current attempt."""

from dataclasses import dataclass, replace
from datetime import datetime
from hashlib import sha256
from typing import Literal
from uuid import uuid4

from aitm_core.events import StoryState
from aitm_core.graduation import (
    CandidateFinalization,
    GraduationConflict,
    GraduationService,
    completed_record,
)
from aitm_core.models.attempts import AttemptRecord, AttemptState, ClockChanged
from aitm_core.models.common import CommandResult, LocalOutcome, PublicationOutcome
from aitm_core.models.config import DeliveryTarget
from aitm_core.models.evidence import (
    ExpansionRecorded,
    ExpansionReservationResolved,
    ExpansionReserved,
    ExpansionResolved,
)
from aitm_core.models.identity import DraftSource, FrozenFinalization
from aitm_core.models.lifecycle import LinkChange
from aitm_core.models.operations import (
    EventAppend,
    FinalizationIntent,
    Operation,
    OperationCategory,
    OperationFact,
    Positive,
    PreflightOutcome,
    ReadExpectation,
    RelatedWriteSet,
    story_event_path,
)
from aitm_core.providers.backlog import GraduationIntent, IssueRef
from aitm_core.providers.identity import IdentityAuthority, reservation_root
from aitm_core.providers.local import LocalBacklog
from aitm_core.reducers.evidence import EvidenceState
from aitm_core.relationships import EventContext, StoryGraph, read_graph
from aitm_core.store.backend import (
    OperationContext,
    OperationResult,
    Snapshot,
    _preflight,
)
from aitm_core.store.objects import Repository

EXPANSION_FINALIZER = "core.graduation.expansion"
ExpansionKind = Literal["defect", "story"]


class ExpansionAuthority(OperationFact):
    origin: Positive
    attempt: str
    generation: Positive
    reservation: str
    kind: ExpansionKind
    draft_handle: str
    reason: str
    issuer_route: Literal["local", "external"]


@dataclass(frozen=True, slots=True)
class ExpansionResult:
    command: CommandResult
    issue: IssueRef | None = None


@dataclass(frozen=True, slots=True)
class ExpansionView:
    snapshot: Snapshot
    graph: StoryGraph
    state: StoryState
    attempt: AttemptRecord
    policy_digest: str
    allowance: int


def _attempt(state: StoryState, context: EventContext) -> AttemptRecord:
    attempts = state.domains.get("attempts")
    if not isinstance(attempts, AttemptState) or attempts.current_attempt is None:
        raise GraduationConflict("Expansion requires a current implementation attempt.")
    active = attempts.attempts[attempts.current_attempt]
    if (
        active.closed
        or active.recovery_bound
        or (
            active.binding is not None
            and (active.binding, active.generation)
            != (context.owner.binding, context.owner.generation)
        )
    ):
        raise GraduationConflict("Expansion is fenced from this attempt generation.")
    return active


def _facts(state, kind):
    evidence = state.domains.get("evidence")
    if isinstance(evidence, EvidenceState):
        return tuple(fact.payload for fact in evidence.facts.get(kind, ()))
    return ()


def _reservation(state, attempt):
    facts = [
        fact
        for fact in _facts(state, "core.expansion.reserved")
        if fact.attempt == attempt.started.attempt
    ]
    if len(facts) > 1:
        raise GraduationConflict(
            "The attempt has contradictory expansion reservations."
        )
    return facts[0] if facts else None


def _spec(finalization):
    if finalization.kind != EXPANSION_FINALIZER or finalization.version != 1:
        raise GraduationConflict("Unsupported expansion finalization.")
    return ExpansionAuthority.model_validate_json(finalization.payload)


def _view(service, origin):
    prepared = service.policy()
    policy = prepared.policy
    assert policy is not None
    snapshot = service.snapshot(prepared)
    graph = read_graph(service.installation.repository, snapshot)
    state = graph.states.get(origin)
    if state is None or graph.stories[origin].kind not in {"story", "defect"}:
        raise GraduationConflict("Expansion requires an initialized story or defect.")
    context = _context(service, policy.source.digest)
    active = _attempt(state, context)
    return ExpansionView(
        snapshot,
        graph,
        state,
        active,
        policy.source.digest,
        policy.config.limits.expansions_per_attempt,
    )


def _context(service, digest):
    return EventContext(uuid4().hex, service.owner, service.stamp, digest)


def _pins(blobs):
    return tuple(
        ReadExpectation(
            path=path, digest=sha256(raw).hexdigest() if raw is not None else None
        )
        for path, raw in sorted(blobs.items())
    )


def _append(context, state, raw, facts):
    """Encode a batch against the actual retained stream, including causal clocks."""
    story = state.story_id
    assert story is not None
    prefix = sha256(raw if raw.endswith(b"\n") else raw + b"\n")
    rows = []
    for name, fact, label in facts:
        row = context.encode(story, name, state, fact, label)
        rows.append(row)
        prefix.update(row + b"\n")
        state = replace(
            state,
            next_sequence=state.next_sequence + 1,
            prior_log_digest=prefix.hexdigest(),
        )
    return EventAppend(story=story, records=tuple(rows))


def _clock(context, active, cause, before, after):
    return ClockChanged(
        attempt=active.started.attempt,
        generation=active.generation,
        cause_event_id=cause,
        **{"from": before, "to": after},
        observed_at=datetime.fromisoformat(context.stamp),
        used_millis=active.used_millis,
    )


def _operation(context, kind, payload, reads, events=()):
    return Operation(
        operation_id=context.operation,
        owner=context.owner,
        policy_digest=context.policy_digest,
        category=OperationCategory.NORMAL,
        intent=FinalizationIntent(
            kind=kind, version=1, related_preconditions=reads, payload=payload
        ),
        change=RelatedWriteSet(read_set=reads, events=events),
    )


def _hold(service, view, context, outcome, reason):
    publication = (
        PublicationOutcome.PENDING
        if service.installation.store.planning_remote
        else PublicationOutcome.NOT_APPLICABLE
    )
    return service.result(
        context.operation, view.snapshot, outcome, reason, publication
    )


def _check_request(service, view, context, payload):
    operation = _operation(context, "expand", payload, _pins(view.graph.logs))
    checked = _preflight(
        OperationContext(operation, view.snapshot, (view.attempt,)), service.ports
    )
    if checked.outcome is PreflightOutcome.PASSED:
        return None
    outcome = (
        LocalOutcome.REFUSED
        if checked.outcome is PreflightOutcome.BLOCKED
        else LocalOutcome.UNAVAILABLE
    )
    return _hold(
        service,
        view,
        context,
        outcome,
        checked.reason or "Expansion preflight unavailable.",
    )


def _frozen(state, active, spec):
    held = _reservation(state, active)
    if held is None or (held.reservation, held.attempt, held.generation) != (
        spec.reservation,
        spec.attempt,
        spec.generation,
    ):
        raise GraduationConflict(
            "The exact expansion reservation is no longer current."
        )
    return GraduationIntent.model_validate_json(held.intent)


def reserve_expansion(
    service: GraduationService, origin: int, intent: GraduationIntent
) -> OperationResult:
    """Publish the allowance reservation and its pause before identity can act."""
    if intent.finalization is None or not isinstance(intent.source, DraftSource):
        raise GraduationConflict("Expansion requires a frozen draft and finalization.")
    finalization = intent.finalization.to_intent()
    spec = _spec(finalization)
    view = _view(service, origin)
    context = _context(service, view.policy_digest)
    if (origin, view.attempt.started.attempt, view.attempt.generation, intent.kind) != (
        spec.origin,
        spec.attempt,
        spec.generation,
        spec.kind,
    ):
        raise GraduationConflict("Expansion intent does not match the current attempt.")
    previous = _reservation(view.state, view.attempt)
    if (
        previous is not None
        or view.allowance != 1
        or view.attempt.clock_mode != "active"
    ):
        denied = _check_request(service, view, context, finalization.payload)
        if denied is not None:
            return denied
        return _hold(
            service,
            view,
            context,
            LocalOutcome.REFUSED,
            "The expansion allowance is unavailable.",
        )
    if spec.reservation != intent.operation_id or intent.parent is not None:
        raise GraduationConflict(
            "Expansion cannot allocate a different intent or an epic child."
        )
    # The graph projection also prevents a second origin from taking this draft
    # out of custody before its first origin has resolved the reservation.
    for state in view.graph.states.values():
        for held in _facts(state, "core.expansion.reserved"):
            other = GraduationIntent.model_validate_json(held.intent)
            if (
                other.source is not None
                and other.source.identity == intent.source.identity
            ):
                denied = _check_request(service, view, context, finalization.payload)
                if denied is not None:
                    return denied
                return _hold(
                    service,
                    view,
                    context,
                    LocalOutcome.CONFLICT,
                    "Another expansion already holds this draft.",
                )
    service.registry.require_finalizer(finalization)
    path = story_event_path(origin)
    fact = ExpansionReserved(
        attempt=spec.attempt,
        generation=spec.generation,
        reservation=spec.reservation,
        intent=intent.model_dump_json(),
        holder=service.owner.binding or context.operation,
    )
    label = "expansion-reserved"
    appended = _append(
        context,
        view.state,
        view.graph.logs[path],
        (
            ("core.expansion.reserved", fact, label),
            (
                "core.attempt.clock.changed",
                _clock(
                    context,
                    view.attempt,
                    f"{context.operation}:{label}:{origin}",
                    "active",
                    "expansion-paused",
                ),
                "clock-paused",
            ),
        ),
    )
    candidate = _operation(
        context, "expand", finalization.payload, _pins(view.graph.logs), (appended,)
    )
    return service.commit(candidate, view.snapshot)


def build_expansion_related(
    repository: Repository,
    finalization: FinalizationIntent,
    candidate: CandidateFinalization,
) -> RelatedWriteSet:
    """Bind the chosen child to the still-live reservation under graduation CAS."""
    spec = _spec(finalization)
    origin, child = spec.origin, candidate.child
    left = candidate.tails.get(origin)
    right = candidate.tails[child]
    if left is None:
        raise GraduationConflict("Expansion origin is unavailable.")
    active = _attempt(left, candidate.events)
    frozen = _frozen(left, active, spec)
    if frozen.finalization is None or frozen.finalization.to_intent() != finalization:
        raise GraduationConflict(
            "The expansion finalization differs from its reservation."
        )
    if active.clock_mode != "expansion-paused" or any(
        fact.reservation == spec.reservation
        for fact in _facts(left, "core.expansion.reservation-resolved")
    ):
        raise GraduationConflict("The expansion reservation is no longer pending.")
    if (active.started.attempt, active.generation, right.domains["lifecycle"].kind) != (
        spec.attempt,
        spec.generation,
        spec.kind,
    ):
        raise GraduationConflict(
            "Expansion no longer matches the attempt or chosen child."
        )

    proposed = right.domains["lifecycle"].graduation
    source = frozen.source
    if not isinstance(source, DraftSource) or (
        proposed.source_kind,
        proposed.source_id,
        proposed.source_digest,
    ) != (source.kind, source.identity, source.digest):
        raise GraduationConflict(
            "The chosen child does not carry the frozen expansion draft."
        )

    paths = (story_event_path(origin), story_event_path(child))
    bodies = repository.read_blobs(candidate.snapshot.tree, paths)
    left_links = left.domains["lifecycle"].relationships
    right_links = right.domains["lifecycle"].relationships
    origin_link = LinkChange(
        before=left_links,
        after=left_links.model_copy(
            update={"blocked_by": tuple(sorted((*left_links.blocked_by, child)))}
        ),
    )
    child_link = LinkChange(
        before=right_links,
        after=right_links.model_copy(update={"blocking": (origin,)}),
    )
    resolved = ExpansionReservationResolved(
        attempt=spec.attempt,
        generation=spec.generation,
        reservation=spec.reservation,
        disposition="linked",
        child=child,
        proof_refs=(f"graduation:{candidate.events.operation}",),
    )
    recorded = ExpansionRecorded(
        attempt=spec.attempt,
        generation=spec.generation,
        reservation=spec.reservation,
        child=child,
        kind=spec.kind,
        reason=spec.reason,
    )
    origin_append = _append(
        candidate.events,
        left,
        bodies[paths[0]],
        (
            ("core.expansion.reservation-resolved", resolved, "expansion-linked"),
            ("core.expansion.recorded", recorded, "expansion-child"),
            ("core.link.changed", origin_link, "expansion-block"),
        ),
    )
    child_append = EventAppend(
        story=child,
        records=(
            candidate.events.encode(
                child, "core.link.changed", right, child_link, "expansion-origin"
            ),
        ),
    )
    return RelatedWriteSet(read_set=_pins(bodies), events=(origin_append, child_append))


def expand(
    service: GraduationService,
    origin: int,
    draft: str,
    kind: ExpansionKind,
    reason: str,
    *,
    external: IdentityAuthority | None = None,
) -> ExpansionResult:
    """Graduate only from a verified, live pause reservation."""
    view = _view(service, origin)
    context = _context(service, view.policy_digest)
    reason = reason.strip()
    if not reason or not draft.strip():
        raise GraduationConflict("Expansion requires a draft and a nonempty reason.")
    route = "external" if external is not None else "local"
    held = _reservation(view.state, view.attempt)
    if held is not None:
        intent = GraduationIntent.model_validate_json(held.intent)
        assert (
            isinstance(intent.source, DraftSource) and intent.finalization is not None
        )
        finalization = intent.finalization.to_intent()
        spec = _spec(finalization)
        same_request = draft in {
            spec.draft_handle,
            intent.source.identity,
            intent.source.entity.document,
        } and (kind, reason, route) == (spec.kind, spec.reason, spec.issuer_route)
        requested = (
            spec
            if same_request
            else spec.model_copy(
                update={
                    "kind": kind,
                    "reason": reason,
                    "draft_handle": draft,
                    "reservation": context.operation,
                    "issuer_route": route,
                }
            )
        )
        denied = _check_request(
            service, view, context, requested.model_dump_json().encode()
        )
        if denied is not None:
            return ExpansionResult(denied.command)
        if not same_request:
            return ExpansionResult(
                _hold(
                    service,
                    view,
                    context,
                    LocalOutcome.REFUSED,
                    "The attempt has already reserved a different expansion.",
                ).command
            )
        if (origin, view.attempt.started.attempt, view.attempt.generation) != (
            spec.origin,
            spec.attempt,
            spec.generation,
        ):
            raise GraduationConflict(
                "The retained expansion belongs to a fenced attempt generation."
            )
        if any(
            fact.reservation == spec.reservation and fact.disposition == "no-child"
            for fact in _facts(view.state, "core.expansion.reservation-resolved")
        ):
            return ExpansionResult(
                _hold(
                    service,
                    view,
                    context,
                    LocalOutcome.REFUSED,
                    "The expansion reservation was closed without a child.",
                ).command
            )
        published = completed_record(
            service.installation.repository, view.snapshot, intent.source
        )
        if published is not None:
            if published.intent != intent:
                raise GraduationConflict(
                    "The draft graduated under a different reservation."
                )
            receipt = service.result(
                intent.operation_id,
                view.snapshot,
                LocalOutcome.COMPLETED,
                "Verified the retained expansion.",
                PublicationOutcome.VERIFIED
                if intent.shared
                else PublicationOutcome.NOT_APPLICABLE,
            )
            return ExpansionResult(receipt.command, published.issue)
        if view.attempt.clock_mode != "expansion-paused":
            raise GraduationConflict("The retained expansion is no longer paused.")
    else:
        if route == "local" and service.installation.issuer.backlog != "local":
            return ExpansionResult(
                _hold(
                    service,
                    view,
                    context,
                    LocalOutcome.UNAVAILABLE,
                    "External identity authority is unavailable.",
                ).command
            )
        target = view.graph.stories[origin].graduation.delivery_target
        if target is None:
            installation = service.installation
            target = DeliveryTarget(
                repository=installation.code_repository,
                ref=installation.code_remote_ref or installation.store.code_default_ref,
            )
        intent = service.prepare_draft(draft, context.operation, target, kind=kind)
        spec = ExpansionAuthority(
            origin=origin,
            attempt=view.attempt.started.attempt,
            generation=view.attempt.generation,
            reservation=intent.operation_id,
            kind=kind,
            draft_handle=draft,
            reason=reason,
            issuer_route=route,
        )
        finalization = FinalizationIntent(
            kind=EXPANSION_FINALIZER,
            version=1,
            related_preconditions=(),
            payload=spec.model_dump_json().encode(),
        )
        try:
            service.registry.require_finalizer(finalization)
        except GraduationConflict as error:
            return ExpansionResult(
                _hold(
                    service, view, context, LocalOutcome.UNAVAILABLE, str(error)
                ).command
            )
        intent = intent.model_copy(
            update={"finalization": FrozenFinalization.from_intent(finalization)}
        )
        reserved = reserve_expansion(service, origin, intent).command
        authority = (
            PublicationOutcome.VERIFIED
            if intent.shared
            else PublicationOutcome.NOT_APPLICABLE
        )
        if (
            reserved.local is not LocalOutcome.COMPLETED
            or reserved.publication is not authority
        ):
            return ExpansionResult(reserved)
    if external is None:
        result = LocalBacklog(service).graduate(intent, finalization)
        return ExpansionResult(result.command, result.issue)
    reservation = external.reserve_identity(intent)
    result = service.finalize_external_identity(external, reservation, finalization)
    authoritative = (
        PublicationOutcome.VERIFIED
        if intent.shared
        else PublicationOutcome.NOT_APPLICABLE
    )
    if (
        result.command.local is not LocalOutcome.COMPLETED
        or result.command.publication is not authoritative
    ):
        return ExpansionResult(result.command)
    child = completed_record(
        service.installation.repository, result.snapshot, intent.source
    )
    if child is None or child.intent != intent:
        raise GraduationConflict(
            "The verified expansion has no matching child receipt."
        )
    return ExpansionResult(result.command, child.issue)


def resolve_expansion(
    service: GraduationService,
    origin: int,
    reservation: str,
    *,
    child: int | None = None,
) -> OperationResult:
    """Resolve a terminal child or atomically fence a provably unissued local candidate."""
    view = _view(service, origin)
    context = _context(service, view.policy_digest)
    held = _reservation(view.state, view.attempt)
    if (
        held is None
        or held.reservation != reservation
        or view.attempt.clock_mode != "expansion-paused"
    ):
        raise GraduationConflict("No live paused expansion matches the reservation.")
    intent = GraduationIntent.model_validate_json(held.intent)
    assert intent.finalization is not None and intent.source is not None
    spec = _spec(intent.finalization.to_intent())
    if (spec.origin, spec.attempt, spec.generation) != (
        origin,
        view.attempt.started.attempt,
        view.attempt.generation,
    ):
        raise GraduationConflict("Expansion resolution belongs to another attempt.")
    repo = service.installation.repository
    existing = completed_record(repo, view.snapshot, intent.source)
    reads = dict(view.graph.logs)
    related = ()
    if child is None:
        reservation_path = (
            f"{reservation_root(intent.source.semantic_key)}/reservation.json"
        )
        external_pin = repo.read_blobs(view.snapshot.tree, (reservation_path,))
        reads.update(external_pin)
        if (
            spec.issuer_route != "local"
            or existing is not None
            or external_pin[reservation_path] is not None
        ):
            return _hold(
                service,
                view,
                context,
                LocalOutcome.REFUSED,
                "A no-child disposition needs terminal non-issuance authority.",
            )
        fact = ExpansionReservationResolved(
            attempt=spec.attempt,
            generation=spec.generation,
            reservation=reservation,
            disposition="no-child",
            proof_refs=(f"local-allocation-fenced:{view.snapshot.revision}",),
        )
        name = "core.expansion.reservation-resolved"
        links = ()
    else:
        if (
            existing is None
            or existing.intent != intent
            or existing.issue.number != child
        ):
            raise GraduationConflict("The child is outside this expansion reservation.")
        other = view.graph.stories[child]
        terminal = other.transitions[-1] if other.transitions else None
        if (
            not other.workflow_state.terminal
            or terminal is None
            or terminal.disposition in (None, "unverified")
        ):
            return _hold(
                service,
                view,
                context,
                LocalOutcome.REFUSED,
                "The child has no terminal disposition.",
            )
        left_links = view.graph.stories[origin].relationships
        right_links = other.relationships
        if child not in left_links.blocked_by or origin not in right_links.blocking:
            raise GraduationConflict("The expansion dependency is not intact.")
        links = (
            (
                "core.link.changed",
                LinkChange(
                    before=left_links,
                    after=left_links.model_copy(
                        update={
                            "blocked_by": tuple(
                                item for item in left_links.blocked_by if item != child
                            )
                        }
                    ),
                ),
                "remove-child-block",
            ),
        )
        child_path = story_event_path(child)
        related = (
            _append(
                context,
                view.graph.states[child],
                reads[child_path],
                (
                    (
                        "core.link.changed",
                        LinkChange(
                            before=right_links,
                            after=right_links.model_copy(
                                update={
                                    "blocking": tuple(
                                        item
                                        for item in right_links.blocking
                                        if item != origin
                                    )
                                }
                            ),
                        ),
                        "remove-origin-link",
                    ),
                ),
            ),
        )
        fact = ExpansionResolved(
            attempt=spec.attempt,
            generation=spec.generation,
            child=child,
            dependency=child,
            disposition=terminal.disposition,
            proof_refs=(f"terminal-child:{child}:{view.snapshot.revision}",),
        )
        name = "core.expansion.resolved"
    origin_path = story_event_path(origin)
    origin_append = _append(
        context,
        view.state,
        reads[origin_path],
        (
            *links,
            (name, fact, "expansion-resolved"),
            (
                "core.attempt.clock.changed",
                _clock(
                    context,
                    view.attempt,
                    f"{context.operation}:expansion-resolved:{origin}",
                    "expansion-paused",
                    "active",
                ),
                "clock-resumed",
            ),
        ),
    )
    operation = _operation(
        context,
        "expand.resolve",
        intent.finalization.to_intent().payload,
        _pins(reads),
        (origin_append, *related),
    )
    return service.commit(operation, view.snapshot)
