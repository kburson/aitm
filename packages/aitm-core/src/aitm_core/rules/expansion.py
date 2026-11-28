"""Reserve, finalize, and resolve an expansion against the current attempt."""

from dataclasses import dataclass, replace
from datetime import datetime
from hashlib import sha256
from typing import Literal
from uuid import uuid4

from aitm_core.events import StoryState, core_reducers, fold
from aitm_core.graduation import (
    CandidateFinalization,
    GraduationConflict,
    GraduationService,
    completed_record,
    graduation_path,
)
from aitm_core.models.attempts import AttemptRecord, AttemptState, ClockChanged
from aitm_core.models.common import CommandResult, LocalOutcome, PublicationOutcome
from aitm_core.models.config import DeliveryTarget
from aitm_core.models.evidence import (
    ExpansionCustody,
    ExpansionRecorded,
    ExpansionReservationResolved,
    ExpansionReserved,
    ExpansionResolved,
)
from aitm_core.models.identity import DraftSource, FrozenFinalization
from aitm_core.models.lifecycle import LinkChange
from aitm_core.models.operations import (
    AuthorityOrigin,
    EventAppend,
    FinalizationIntent,
    Operation,
    OperationCategory,
    OperationFact,
    Positive,
    PreflightOutcome,
    PreflightResult,
    ReadExpectation,
    RelatedWriteSet,
    story_event_path,
)
from aitm_core.providers.backlog import GraduationIntent, IssueRef
from aitm_core.providers.identity import (
    IdentityAuthority,
    IdentityConflict,
    reservation_root,
)
from aitm_core.providers.local import LocalBacklog
from aitm_core.reducers.evidence import EvidenceState
from aitm_core.relationships import EventContext, StoryGraph, read_graph
from aitm_core.services import mutate
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


def _origin_attempt(
    repository: Repository, snapshot: Snapshot, intent: GraduationIntent
):
    if intent.finalization is None or not isinstance(intent.source, DraftSource):
        raise IdentityConflict("Expansion needs its exact frozen draft and intent.")
    spec = _spec(intent.finalization.to_intent())
    path = story_event_path(spec.origin)
    raw = repository.read_blobs(snapshot.tree, (path,))[path]
    if raw is None:
        raise IdentityConflict("The exact expansion origin is unavailable.")
    state = fold(raw.splitlines(keepends=True), core_reducers())
    attempt_state = state.domains.get("attempts")
    if not isinstance(attempt_state, AttemptState):
        raise IdentityConflict("The origin has no retained attempt.")
    active = attempt_state.attempts.get(spec.attempt)
    if active is None or active.generation != spec.generation:
        raise IdentityConflict("Expansion attempt generation changed.")
    held = _reservation(state, active)
    if (
        held is None
        or held.reservation != spec.reservation
        or held.generation != spec.generation
        or spec.reservation != intent.operation_id
        or GraduationIntent.model_validate_json(held.intent) != intent
    ):
        raise IdentityConflict(
            "Expansion reservation is outside the exact held intent."
        )
    return path, raw, state, attempt_state, active, held


def expansion_claim_pin(
    repository: Repository,
    snapshot: Snapshot,
    intent: GraduationIntent,
) -> ReadExpectation | None:
    """Pin the authoritative live expansion origin for a new C20 claim."""
    if intent.finalization is None or intent.finalization.kind != EXPANSION_FINALIZER:
        return None
    path, raw, state, attempts, active, held = _origin_attempt(
        repository, snapshot, intent
    )
    spec = _spec(intent.finalization.to_intent())
    if (
        spec.issuer_route != "external"
        or active.closed
        or active.recovery_bound
        or attempts.current_attempt != held.attempt
        or active.clock_mode != "expansion-paused"
        or (active.binding is not None and held.holder != active.binding)
        or any(
            row.reservation == held.reservation
            for row in _facts(state, "core.expansion.reservation-resolved")
        )
    ):
        raise IdentityConflict(
            "The expansion origin is fenced from new issuer authority."
        )
    return ReadExpectation(path=path, digest=sha256(raw).hexdigest())


def stopped_expansion_claim(
    repository: Repository, snapshot: Snapshot, intent: GraduationIntent
):
    """Read the exact historical stopped origin, without reopening its clock."""
    path, raw, state, _, active, held = _origin_attempt(repository, snapshot, intent)
    if not active.closed or active.clock_mode != "terminal-closed":
        raise IdentityConflict(
            "Custody reconciliation requires the exact closed origin."
        )
    return path, raw, state, held


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


_CUSTODY_EVENT = "core.expansion.custody-recorded"
_CUSTODY_OPERATION = ("core.expansion.reconcile-stopped", 1)


def _append_custody(service, snapshot, policy_digest, intent, fact, evidence_paths):
    repository = service.installation.repository
    path, raw, state, _ = stopped_expansion_claim(repository, snapshot, intent)
    context = _context(service, policy_digest)
    reads = _pins(
        repository.read_blobs(
            snapshot.tree, tuple(dict.fromkeys((path, *evidence_paths)))
        )
    )
    append = _append(context, state, raw, ((_CUSTODY_EVENT, fact, "custody"),))
    operation = _operation(
        context,
        _CUSTODY_OPERATION[0],
        fact.model_dump_json().encode(),
        reads,
        (append,),
    ).model_copy(update={"category": OperationCategory.STOP_RECONCILIATION})

    def preflight(candidate):
        matches = candidate.operation == operation
        if matches:
            try:
                current_path, current_raw, _, _ = stopped_expansion_claim(
                    repository, candidate.snapshot, intent
                )
                matches = (current_path, current_raw) == (path, raw)
            except IdentityConflict:
                matches = False
        return PreflightResult(
            outcome=PreflightOutcome.PASSED if matches else PreflightOutcome.BLOCKED,
            origin=AuthorityOrigin.REGISTERED,
        )

    return mutate(
        service.installation,
        operation,
        snapshot,
        ports=replace(service.commit_ports(operation), attempt_preflight=preflight),
        categories={_CUSTODY_OPERATION: OperationCategory.STOP_RECONCILIATION},
    )


def reconcile_stopped_expansion(
    service: GraduationService,
    origin: int,
    reservation: str,
    *,
    external: IdentityAuthority | None = None,
) -> OperationResult:
    """Retain verified stopped-origin custody without granting a send or attaching a child."""
    prepared = service.policy()
    return _reconcile_custody(
        service, prepared, origin, reservation, external, refresh_after_fence=True
    )


def _reconcile_custody(
    service, prepared, origin, reservation, external, *, refresh_after_fence
):
    repository = service.installation.repository
    snapshot = service.snapshot(prepared)
    assert prepared.policy is not None
    policy = prepared.policy.source.digest
    context = _context(service, policy)
    graph = read_graph(repository, snapshot)
    state = graph.states.get(origin)
    held = (
        [
            row
            for row in _facts(state, "core.expansion.reserved")
            if row.reservation == reservation
        ]
        if state is not None
        else []
    )
    if len(held) != 1:
        raise IdentityConflict(
            "The exact stopped expansion reservation is unavailable."
        )
    intent = GraduationIntent.model_validate_json(held[0].intent)
    if (
        intent.finalization is None
        or intent.source is None
        or intent.delivery_target is None
    ):
        raise IdentityConflict("Stopped custody requires a complete frozen intent.")
    spec = _spec(intent.finalization.to_intent())
    if spec.origin != origin or spec.reservation != reservation:
        raise IdentityConflict(
            "Custody cannot match a different origin or reservation."
        )
    if (
        service.owner.extension is not None
        or service.owner.binding != held[0].holder
        or service.owner.generation != spec.generation
    ):
        raise IdentityConflict(
            "Custody requires the exact authorized reservation holder."
        )
    service.check_target(intent.delivery_target)
    _, _, state, _ = stopped_expansion_claim(repository, snapshot, intent)
    key = intent.source.semantic_key
    graduated = graduation_path(intent.source)
    external_reservation = f"{reservation_root(key)}/reservation.json"
    if completed_record(repository, snapshot, intent.source) is not None:
        raise IdentityConflict("The expansion already has a finalized child.")
    existing = tuple(
        row for row in _facts(state, _CUSTODY_EVENT) if row.reservation == reservation
    )
    terminal = next(
        (row for row in existing if row.disposition != "sender-fenced"), None
    )
    basis = dict(
        attempt=spec.attempt,
        generation=spec.generation,
        reservation=reservation,
        semantic_key=key,
    )

    def retained(message):
        return service.result(
            context.operation,
            snapshot,
            LocalOutcome.COMPLETED,
            message,
            PublicationOutcome.VERIFIED
            if intent.shared
            else PublicationOutcome.NOT_APPLICABLE,
        )

    if spec.issuer_route == "local":
        if (
            external is not None
            or repository.read_blobs(snapshot.tree, (external_reservation,))[
                external_reservation
            ]
            is not None
        ):
            raise IdentityConflict(
                "Local no-child authority cannot consume external custody."
            )
        if terminal is not None:
            if (
                terminal.authority != "local-allocation"
                or terminal.disposition != "no-child"
            ):
                raise IdentityConflict(
                    "The retained local custody contradicts the expected authority."
                )
            return retained("Verified the retained local no-child disposition.")
        fact = ExpansionCustody(
            **basis,
            disposition="no-child",
            authority="local-allocation",
            verified_at=snapshot.revision,
            proof_refs=(f"local-allocation-fenced:{snapshot.revision}",),
        )
        return _append_custody(
            service, snapshot, policy, intent, fact, (graduated, external_reservation)
        )

    if external is None or external.installation != service.installation:
        raise IdentityConflict(
            "Stopped external custody requires the anchored identity authority."
        )
    observed = external.observe_stopped(intent)
    # C20 may have published positive issuance after the first planning read.
    prepared = service.policy()
    snapshot = service.snapshot(prepared)
    assert prepared.policy is not None
    if snapshot != observed.snapshot or prepared.policy.source.digest != policy:
        raise IdentityConflict(
            "Custody observation is stale against authoritative planning."
        )
    _, _, current, _ = stopped_expansion_claim(repository, snapshot, intent)
    if _facts(current, _CUSTODY_EVENT) != _facts(state, _CUSTODY_EVENT):
        raise IdentityConflict("Custody history changed during observation.")
    paths = (graduated, *observed.reads)
    claim = observed.claim
    if observed.issue is not None:
        assert claim is not None
        if terminal is not None:
            if (
                terminal.disposition != "issued"
                or terminal.claim != claim.token
                or terminal.issue != observed.issue.number
            ):
                raise IdentityConflict(
                    "Confirmed issuance contradicts retained terminal custody. The exact issue is retained."
                )
            return retained("Verified the retained issued identity without attachment.")
        fact = ExpansionCustody(
            **basis,
            disposition="issued",
            authority="provider-claim",
            claim=claim.token,
            issue=observed.issue.number,
            verified_at=snapshot.revision,
            proof_refs=(f"issued-ownership:{snapshot.revision}",),
        )
        return _append_custody(service, snapshot, policy, intent, fact, paths)
    absence = observed.absence
    if terminal is not None:
        if (
            terminal.disposition == "no-child"
            and claim is not None
            and terminal.claim == claim.token
            and absence is not None
            and terminal.fence == absence.fence_proof
        ):
            return retained("Verified the retained terminal claim disposition.")
        raise IdentityConflict(
            "Current issuer evidence cannot confirm the retained terminal custody."
        )
    if claim is None or absence is None:
        return service.result(
            context.operation,
            snapshot,
            LocalOutcome.UNAVAILABLE,
            "Expansion custody remains unknown. No uniform writer or provider fence was verified.",
            PublicationOutcome.PENDING,
        )

    fence = next((row for row in existing if row.disposition == "sender-fenced"), None)
    fence_proof = absence.fence_proof
    assert fence_proof is not None
    if fence is None:
        fact = ExpansionCustody(
            **basis,
            disposition="sender-fenced",
            authority="provider-claim",
            claim=claim.token,
            fence=fence_proof,
            verified_at=snapshot.revision,
            proof_refs=(f"provider-fence:{fence_proof}",),
        )
        published = _append_custody(service, snapshot, policy, intent, fact, paths)
        expected = (
            PublicationOutcome.VERIFIED
            if intent.shared
            else PublicationOutcome.NOT_APPLICABLE
        )
        if (
            refresh_after_fence
            and published.command.local == LocalOutcome.COMPLETED
            and published.command.publication == expected
        ):
            return _reconcile_custody(
                service,
                service.policy(),
                origin,
                reservation,
                external,
                refresh_after_fence=False,
            )
        return published
    if (fence.claim, fence.fence) != (claim.token, fence_proof):
        raise IdentityConflict(
            "The provider fence differs from the retained claim proof."
        )
    fact = ExpansionCustody(
        **basis,
        disposition="no-child",
        authority="provider-claim",
        claim=claim.token,
        fence=fence_proof,
        absence=absence.model_dump_json(),
        verified_at=snapshot.revision,
        proof_refs=(f"ordered-provider-observation:{snapshot.revision}",),
    )
    return _append_custody(service, snapshot, policy, intent, fact, paths)
