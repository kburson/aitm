"""Construct and finalize a numbered story without provisioning work resources."""

from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from hashlib import sha256
from json import dumps
from pathlib import PurePosixPath
from types import MappingProxyType
from typing import Callable, Literal, Mapping
from uuid import uuid4

from aitm_core.description import (
    DescriptionInput,
    DescriptionTarget,
    describe,
    description_path,
)
from aitm_core.documents import DocumentSchema
from aitm_core.drafts import Intake, _graduated
from aitm_core.entities import (
    BindingDisposition,
    entity_matches,
    finalize_entity_binding,
)
from aitm_core.events import StoryState, core_reducers, fold
from aitm_core.machine.profile import load_profile
from aitm_core.models.attempts import SourceSnapshot
from aitm_core.models.common import CommandResult, LocalOutcome, PublicationOutcome
from aitm_core.models.events import DIGEST
from aitm_core.models.identity import (
    DeliveryTarget,
    DraftSource,
    FrozenSource,
    IdentityFact,
    PlanEntrySource,
)
from aitm_core.models.lifecycle import (
    Graduation,
    LifecycleState,
    Relationships,
    StoryKind,
    WorkflowObservation,
)
from aitm_core.models.operations import (
    AuthorityOrigin,
    BlobWrite,
    EventAppend,
    FinalizationIntent,
    Operation,
    OperationCategory,
    OperationOwner,
    ReadExpectation,
    RelatedWriteSet,
    WriteAuthorization,
    story_event_path,
)
from aitm_core.providers.backlog import GraduationIntent, IdentityReservation, IssueRef
from aitm_core.providers.identity import IdentityAuthority, reservation_root
from aitm_core.relationships import (
    EventContext,
    GraphConflict,
    LinkRequest,
    StoryGraph,
    checked_relations,
    link_changes,
    read_graph,
    reciprocal_events,
)
from aitm_core.services import PolicyPreflight, ServicePorts, mutate, preflight_policy
from aitm_core.store.backend import OperationResult, Snapshot
from aitm_core.store.continuity import ContinuityStatus
from aitm_core.store.fetch import Freshness
from aitm_core.store.installation import Installation
from aitm_core.store.objects import Repository
from aitm_core.store.render import ViewState, render
from aitm_core.store.validation import _entries
from aitm_core.store.workspace import BindingConflict, Workspace


class GraduationConflict(ValueError):
    """The pinned graduation intent or its candidate cannot finalize."""


def ordinary_finalization() -> FinalizationIntent:
    return FinalizationIntent(
        kind="core.graduation.ordinary",
        version=1,
        related_preconditions=(),
        payload=b"{}",
    )


def _check_finalization(
    intent: GraduationIntent, finalization: FinalizationIntent
) -> None:
    expected = (
        intent.finalization.to_intent()
        if intent.finalization is not None
        else ordinary_finalization()
    )
    if expected != finalization:
        raise GraduationConflict("The finalization differs from the frozen intent.")


@dataclass(frozen=True, slots=True)
class CandidateFinalization:
    """The authoritative event tails after the base graduation appends."""

    child: int
    snapshot: Snapshot
    events: EventContext
    tails: Mapping[int, StoryState]


Finalizer = Callable[[FinalizationIntent, int, Snapshot], RelatedWriteSet]
CandidateFinalizer = Callable[
    [FinalizationIntent, CandidateFinalization], RelatedWriteSet
]


@dataclass(frozen=True, slots=True)
class FinalizerRegistry:
    handlers: Mapping[tuple[str, int], Finalizer] = field(
        default_factory=lambda: MappingProxyType({})
    )
    candidate_handlers: Mapping[tuple[str, int], CandidateFinalizer] = field(
        default_factory=lambda: MappingProxyType({})
    )

    def _registration_key(self, kind: str, version: int) -> tuple[str, int]:
        key = kind, version
        if (
            not kind.strip()
            or version < 1
            or key in self.handlers
            or key in self.candidate_handlers
            or key == ("core.graduation.ordinary", 1)
        ):
            raise ValueError("Invalid or duplicate finalizer registration.")
        return key

    def register_finalizer(
        self, kind: str, version: int, handler: Finalizer
    ) -> "FinalizerRegistry":
        key = self._registration_key(kind, version)
        return replace(self, handlers=MappingProxyType({**self.handlers, key: handler}))

    def register_candidate_finalizer(
        self, kind: str, version: int, handler: CandidateFinalizer
    ) -> "FinalizerRegistry":
        key = self._registration_key(kind, version)
        return replace(
            self,
            candidate_handlers=MappingProxyType(
                {**self.candidate_handlers, key: handler}
            ),
        )

    def materialize_finalization(
        self,
        intent: FinalizationIntent,
        chosen_child: int,
        pinned_snapshot: Snapshot,
        *,
        candidate: CandidateFinalization | None = None,
    ) -> RelatedWriteSet:
        self.require_finalizer(intent)
        key = intent.kind, intent.version
        handler = self.candidate_handlers.get(key)
        if handler is not None:
            if (
                candidate is None
                or candidate.child != chosen_child
                or candidate.snapshot != pinned_snapshot
            ):
                raise GraduationConflict(
                    "The finalizer requires matching candidate context."
                )
            return RelatedWriteSet.model_validate(handler(intent, candidate))
        legacy = self.handlers.get(key)
        if legacy is not None:
            return RelatedWriteSet.model_validate(
                legacy(intent, chosen_child, pinned_snapshot)
            )
        return RelatedWriteSet(read_set=())

    def require_finalizer(
        self, intent: FinalizationIntent
    ) -> Finalizer | CandidateFinalizer | None:
        if intent == ordinary_finalization():
            return None
        key = intent.kind, intent.version
        handler = self.handlers.get(key, self.candidate_handlers.get(key))
        if handler is None:
            raise GraduationConflict("The semantic finalizer is unregistered.")
        return handler


class GraduatedRecord(IdentityFact):
    schema_version: Literal["aitm.graduated-identity/v1"] = "aitm.graduated-identity/v1"
    intent: GraduationIntent
    issue: IssueRef
    operation: str
    workflow_digest: DIGEST
    binding_disposition: BindingDisposition | None = None


def graduation_path(source: FrozenSource) -> str:
    return f"{reservation_root(source.semantic_key)}/graduated.json"


def validate_graduated_record(path: str, content: bytes) -> None:
    record = GraduatedRecord.model_validate_json(content)
    if (
        record.intent.source is None
        or path != graduation_path(record.intent.source)
        or record.issue.issuer != record.intent.issuer
        or record.intent.delivery_target is None
    ):
        raise ValueError(
            "The graduated identity does not match its declared source or issuer."
        )
    disposition = record.binding_disposition
    if disposition is not None and (
        not isinstance(record.intent.source, DraftSource)
        or disposition.source != record.intent.source.entity
        or disposition.source_digest != record.intent.source.document_digest
        or disposition.outcome != "graduated"
    ):
        raise ValueError(
            "The graduation binding disposition does not match the frozen source."
        )


def completed_record(
    repo: Repository, snapshot: Snapshot, source: FrozenSource
) -> GraduatedRecord | None:
    path = graduation_path(source)
    raw = repo.read_blobs(snapshot.tree, (path,))[path]
    if raw is None:
        return None
    validate_graduated_record(path, raw)
    return GraduatedRecord.model_validate_json(raw)


def _draft_paths(
    repo: Repository, snapshot: Snapshot, source: DraftSource
) -> tuple[str, ...]:
    document = source.entity.document
    folder = str(PurePosixPath(document).parent)
    raw = repo.read_blobs(snapshot.tree, (document,))[document]
    actual = repo._run("rev-parse", "--verify", f"{snapshot.tree}:{folder}")
    if (
        raw is None
        or not entity_matches(source.entity, raw)
        or sha256(raw).hexdigest() != source.document_digest
        or actual.returncode
        or actual.stdout.decode().strip() != source.draft_tree
    ):
        raise GraduationConflict(
            "The current draft folder differs from the frozen source."
        )
    return tuple(
        sorted(
            path for path in _entries(repo, snapshot) if path.startswith(folder + "/")
        )
    )


def graduation_replay_conflict(
    repo: Repository, snapshot: Snapshot, operation: Operation
) -> str | None:
    record = GraduatedRecord.model_validate_json(operation.intent.payload)
    source = record.intent.source
    if isinstance(source, DraftSource):
        try:
            _draft_paths(repo, snapshot, source)
            if _graduated(repo, snapshot, source.identity, _entries(repo, snapshot)):
                return "The frozen draft has already graduated."
        except GraduationConflict as error:
            return str(error)
    story = story_event_path(record.issue.number).removesuffix("events.jsonl")
    if any(path.startswith(story) for path in _entries(repo, snapshot)):
        return "The candidate number is already occupied."
    return None


@dataclass(frozen=True, slots=True)
class CandidateIdentity:
    issue: IssueRef
    snapshot: Snapshot
    repository: Repository
    context: EventContext
    initial: WorkflowObservation
    binding_disposition: BindingDisposition | None = None
    authority_paths: tuple[str, ...] = ()


def _pin(bodies: Mapping[str, bytes | None]) -> tuple[ReadExpectation, ...]:
    return tuple(
        ReadExpectation(
            path=path, digest=sha256(raw).hexdigest() if raw is not None else None
        )
        for path, raw in sorted(bodies.items())
    )


def _fold_append(graph: StoryGraph, append: EventAppend) -> StoryState:
    before = graph.logs.get(append.path) or b""
    if before and not before.endswith(b"\n"):
        before += b"\n"
    records = tuple(raw.removesuffix(b"\n") + b"\n" for raw in append.records)
    return fold((*before.splitlines(keepends=True), *records), core_reducers())


def _merge_related_events(
    base: tuple[EventAppend, ...], related: tuple[EventAppend, ...]
) -> tuple[EventAppend, ...]:
    streams = {append.story: append for append in base}
    for append in related:
        earlier = streams.get(append.story)
        streams[append.story] = (
            EventAppend(story=append.story, records=earlier.records + append.records)
            if earlier is not None
            else append
        )
    return tuple(streams.values())


def build_graduation(
    intent: GraduationIntent,
    source: FrozenSource,
    candidate: CandidateIdentity,
    finalization: FinalizationIntent,
    registry: FinalizerRegistry = FinalizerRegistry(),
) -> Operation:
    """Read pinned data and construct the entire CAS without committing any effects."""
    _check_finalization(intent, finalization)
    if (
        source != intent.source
        or intent.delivery_target is None
        or candidate.issue.issuer != intent.issuer
    ):
        raise GraduationConflict(
            "Candidate authority differs from the prepared graduation intent."
        )
    if candidate.initial.terminal:
        raise GraduationConflict(
            "Graduation requires a nonterminal configured entry state."
        )
    repo, snapshot, context = (
        candidate.repository,
        candidate.snapshot,
        candidate.context,
    )
    if repo.read_tree(snapshot.revision) != snapshot:
        raise GraduationConflict("Invalid planning snapshot.")
    number = candidate.issue.number
    event_path = story_event_path(number)
    root = event_path.removesuffix("events.jsonl")
    occupied = _entries(repo, snapshot)
    if any(path.startswith(root) for path in occupied):
        raise GraduationConflict("The candidate number is already occupied.")
    if completed_record(repo, snapshot, source) is not None:
        raise GraduationConflict("The source already has a permanent identity.")
    graph = read_graph(repo, snapshot)
    parent = intent.parent
    if isinstance(source, PlanEntrySource):
        if parent not in {None, source.parent}:
            raise GraduationConflict("The parent differs from the accepted plan entry.")
        parent = source.parent
    changes = {}
    if parent is not None:
        if parent not in graph.stories:
            raise GraphConflict("Graduation requires an initialized epic parent.")
        facts = graph.stories[parent].relationships
        changes[parent] = facts.model_copy(
            update={"children": tuple(sorted((*facts.children, number)))}
        )
    checked_relations(
        graph, {**changes, number: Relationships(parent=parent)}, (number, intent.kind)
    )
    issue = candidate.issue
    graduation = Graduation(
        kind=intent.kind,
        source_kind=source.kind,
        source_id=source.identity,
        source_digest=source.digest,
        issue=f"{issue.issuer.backlog}:{issue.issuer.backlog_repository}#{number}",
        parent=parent,
        source_intent=intent.operation_id,
        initial_state=candidate.initial,
        delivery_target=intent.delivery_target,
    )
    first = context.encode(
        number, "core.story.graduated", StoryState(), graduation, "graduation"
    )
    story_events = (first,)
    writes = {}
    description = {}
    if isinstance(source, DraftSource):
        original = repo.read_tree(source.snapshot.commit)
        if (
            original.tree != source.snapshot.tree
            or repo._run(
                "merge-base", "--is-ancestor", original.revision, snapshot.revision
            ).returncode
        ):
            raise GraduationConflict(
                "The draft snapshot is outside retained planning history."
            )
        _draft_paths(repo, original, source)
        if _graduated(repo, snapshot, source.identity, occupied):
            raise GraduationConflict("The draft already graduated.")
        original_folder = str(PurePosixPath(source.entity.document).parent) + "/"
        for path, data in repo.read_blobs(
            snapshot.tree, _draft_paths(repo, snapshot, source)
        ).items():
            writes[path] = None
            writes[root + path.removeprefix(original_folder)] = data
    else:
        descriptor = source.descriptor
        path = description_path(number)
        if descriptor.actor and descriptor.want and descriptor.so_that:
            authored = describe(
                DescriptionTarget(
                    number,
                    {event_path: first + b"\n", path: None},
                    context.owner,
                    context.policy_digest,
                    context.operation,
                    context.stamp,
                ),
                DescriptionInput(
                    title=descriptor.title,
                    actor=descriptor.actor,
                    want=descriptor.want,
                    so_that=descriptor.so_that,
                    scope=descriptor.scope,
                ),
            )
            story_events += authored.change.events[0].records
            description[path] = authored.change.writes[0].content
        else:
            header = dumps(
                {
                    "schema": DocumentSchema().name,
                    "story": number,
                    "role": "description",
                    "title": descriptor.title,
                }
            )
            writes[path] = f"---\n{header}\n---\n{descriptor.scope}\n".encode()
    record = GraduatedRecord(
        intent=intent,
        issue=issue,
        operation=context.operation,
        workflow_digest=candidate.initial.revision,
        binding_disposition=candidate.binding_disposition,
    )
    payload = record.model_dump_json().encode()
    marker = graduation_path(source)
    validate_graduated_record(marker, payload)
    writes[marker] = payload
    events = (
        EventAppend(story=number, records=story_events),
        *reciprocal_events(graph, changes, context),
    )
    origin_paths = tuple(item.path for item in finalization.related_preconditions)
    origin = {
        item.path: item.digest
        for item in _pin(repo.read_blobs(snapshot.tree, origin_paths))
    }
    if any(
        origin[item.path] != item.digest for item in finalization.related_preconditions
    ):
        raise GraduationConflict("The related finalization requirements are fenced.")
    candidate_scoped = (
        finalization.kind,
        finalization.version,
    ) in registry.candidate_handlers
    child_state = _fold_append(graph, events[0])
    candidate_context = None
    if candidate_scoped:
        tails = {**graph.states, number: child_state}
        tails.update(
            {append.story: _fold_append(graph, append) for append in events[1:]}
        )
        candidate_context = CandidateFinalization(
            number, snapshot, context, MappingProxyType(tails)
        )
    related = registry.materialize_finalization(
        finalization, number, snapshot, candidate=candidate_context
    )
    if candidate_scoped:
        events = _merge_related_events(events, related.events)
        if related.events:
            final_states = {
                append.story: _fold_append(graph, append) for append in events
            }
            child_state = final_states[number]
            related_relationships = {}
            for story, final_state in final_states.items():
                life = final_state.domains.get("lifecycle")
                if (
                    not isinstance(life, LifecycleState)
                    or final_state.story_id != story
                ):
                    raise GraduationConflict(
                        "Related events require an initialized story stream."
                    )
                related_relationships[story] = life.relationships
            checked_relations(graph, related_relationships, (number, intent.kind))
    else:
        if {append.path for append in related.events} & {
            append.path for append in events
        }:
            raise GraduationConflict(
                "Related finalization overlaps the base graduation."
            )
        events += related.events
    writes.update(render(ViewState(child_state), description, DocumentSchema()))
    if {write.path for write in related.writes} & writes.keys():
        raise GraduationConflict("Related finalization overlaps the base graduation.")
    writes.update({write.path: write.content for write in related.writes})
    expected = (*finalization.related_preconditions, *related.read_set)
    paths = {
        *graph.logs,
        *writes,
        *candidate.authority_paths,
        *(append.path for append in events),
        *(item.path for item in expected),
    }
    reads = _pin(repo.read_blobs(snapshot.tree, tuple(sorted(paths))))
    pinned = {item.path: item.digest for item in reads}
    if any(pinned[item.path] != item.digest for item in expected):
        raise GraduationConflict("The related finalization requirements are fenced.")
    return Operation(
        operation_id=context.operation,
        owner=context.owner,
        policy_digest=context.policy_digest,
        category=OperationCategory.NORMAL,
        intent=FinalizationIntent(
            kind="core.graduated",
            version=1,
            related_preconditions=reads,
            payload=payload,
        ),
        change=RelatedWriteSet(
            read_set=reads,
            writes=tuple(
                BlobWrite(path=path, content=raw)
                for path, raw in sorted(writes.items())
            ),
            events=events,
        ),
        pending_actions=(f"project-backlog:{intent.operation_id}",),
    )


@dataclass(frozen=True, slots=True)
class GraduationService:
    installation: Installation
    owner: OperationOwner
    stamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    registry: FinalizerRegistry = FinalizerRegistry()
    ports: ServicePorts = ServicePorts()

    def policy(self) -> PolicyPreflight:
        prepared = preflight_policy(self.installation, ports=self.ports)
        if (
            prepared.outcome != LocalOutcome.COMPLETED
            or prepared.policy is None
            or prepared.views.code_freshness
            not in {Freshness.FRESH, Freshness.LOCAL_ONLY}
        ):
            raise GraduationConflict(
                prepared.reason or "The current committed policy is unavailable."
            )
        return prepared

    def snapshot(
        self, prepared: PolicyPreflight, *, authoritative: bool = True
    ) -> Snapshot:
        ref = prepared.views.planning.observed_commit
        if authoritative and self.installation.store.planning_remote is not None:
            shared = prepared.views.shared
            if shared is None or shared.status != ContinuityStatus.VERIFIED:
                raise GraduationConflict(
                    "Verified shared planning authority is unavailable."
                )
            ref = shared.valid_tip
        if ref is None:
            raise GraduationConflict("Planning history is unavailable.")
        return self.installation.repository.read_tree(ref)

    def check_target(self, delivery: DeliveryTarget) -> None:
        repo = self.installation.repository
        if delivery.repository != self.installation.code_repository:
            raise GraduationConflict(
                "The delivery target is outside the anchored code repository."
            )
        repo._git("check-ref-format", delivery.ref)
        if (
            delivery.ref
            not in {
                self.installation.code_remote_ref,
                self.installation.store.code_default_ref,
            }
            and repo._run("show-ref", "--verify", "--quiet", delivery.ref).returncode
        ):
            raise GraduationConflict(
                "The selected delivery target has no bound branch."
            )

    def prepare_draft(
        self,
        handle: str,
        operation: str,
        delivery: DeliveryTarget,
        *,
        kind: StoryKind = "story",
        parent: int | None = None,
    ) -> GraduationIntent:
        self.check_target(delivery)
        repo = self.installation.repository
        prepared = self.policy()
        assert prepared.policy is not None
        snapshot = self.snapshot(prepared)
        intake = Intake(
            self.installation,
            snapshot,
            prepared.policy.source.digest,
            self.owner,
            datetime.fromisoformat(self.stamp),
        )
        entity = intake.resolve_entity("draft", handle)
        folder = PurePosixPath(entity.document).parent
        raw = repo.read_blobs(snapshot.tree, (entity.document,))[entity.document]
        assert raw is not None
        source = DraftSource(
            entity=entity,
            snapshot=SourceSnapshot(commit=snapshot.revision, tree=snapshot.tree),
            draft_tree=repo._git("rev-parse", f"{snapshot.tree}:{folder}")
            .decode()
            .strip(),
            document_digest=sha256(raw).hexdigest(),
        )
        return GraduationIntent(
            operation_id=operation,
            issuer=self.installation.issuer,
            shared=self.installation.store.planning_remote is not None,
            source=source,
            delivery_target=delivery,
            kind=kind,
            parent=parent,
        )

    def build(
        self,
        intent: GraduationIntent,
        issue: IssueRef,
        snapshot: Snapshot,
        prepared: PolicyPreflight,
        finalization: FinalizationIntent,
        workspace: Workspace,
        *,
        operation: str,
        authority_paths: tuple[str, ...] = (),
    ) -> Operation:
        assert prepared.policy is not None
        if intent.source is None or intent.issuer != self.installation.issuer:
            raise GraduationConflict(
                "The prepared source or anchored issuer is missing."
            )
        if intent.delivery_target is None:
            raise GraduationConflict("A declared delivery target is required.")
        self.check_target(intent.delivery_target)
        profile = load_profile(prepared.policy)
        initial = profile.states[0]
        context = EventContext(
            operation, self.owner, self.stamp, prepared.policy.source.digest
        )
        disposition = (
            finalize_entity_binding(
                workspace,
                intent.source.entity,
                "graduated",
                snapshot,
                operation_id=operation,
            )
            if isinstance(intent.source, DraftSource)
            else None
        )
        proposed = CandidateIdentity(
            issue,
            snapshot,
            self.installation.repository,
            context,
            WorkflowObservation(
                workflow_id=profile.id,
                revision=profile.source.digest,
                state_id=initial.id,
                label=initial.label,
                terminal=initial.id == profile.lifecycle.terminal,
            ),
            disposition,
            authority_paths,
        )
        return build_graduation(
            intent, intent.source, proposed, finalization, self.registry
        )

    def commit_ports(self, operation: Operation) -> ServicePorts:
        def authorize(
            owner: OperationOwner, change: RelatedWriteSet
        ) -> WriteAuthorization:
            return WriteAuthorization(
                allowed=owner == operation.owner and change == operation.change,
                origin=AuthorityOrigin.REGISTERED,
            )

        return replace(self.ports, write_authorization=authorize)

    def commit(self, operation: Operation, snapshot: Snapshot) -> OperationResult:
        return mutate(
            self.installation,
            operation,
            snapshot,
            ports=self.commit_ports(operation),
        )

    def result(
        self,
        identity: str,
        snapshot: Snapshot,
        local: LocalOutcome,
        message: str,
        publication: PublicationOutcome = PublicationOutcome.NOT_APPLICABLE,
    ) -> OperationResult:
        return OperationResult(
            CommandResult(
                operation_id=identity,
                local=local,
                publication=publication,
                evidence=(message,),
            ),
            snapshot,
            message,
        )

    def finalize_external_identity(
        self,
        authority: IdentityAuthority,
        reservation: IdentityReservation,
        finalization: FinalizationIntent,
    ) -> OperationResult:
        intent = reservation.intent
        if authority.installation != self.installation or intent.source is None:
            raise GraduationConflict(
                "The reservation belongs to a different installation or source."
            )
        _check_finalization(intent, finalization)
        self.registry.require_finalizer(finalization)
        if intent.delivery_target is None:
            raise GraduationConflict("A declared delivery target is required.")
        self.check_target(intent.delivery_target)
        observed = authority.dispatch_or_observe(reservation)
        prepared = self.policy()
        snapshot = self.snapshot(prepared)
        if observed.issue is None:
            return self.result(
                intent.operation_id,
                snapshot,
                LocalOutcome.UNAVAILABLE,
                "External issuance remains pending.",
                PublicationOutcome.PENDING,
            )
        existing = completed_record(
            self.installation.repository, snapshot, intent.source
        )
        if existing is not None:
            if existing.issue != observed.issue or existing.intent != intent:
                raise GraduationConflict(
                    "The source already finalized under another identity."
                )
            return self.result(
                intent.operation_id,
                snapshot,
                LocalOutcome.COMPLETED,
                "Verified the retained graduation.",
                PublicationOutcome.VERIFIED
                if intent.shared
                else PublicationOutcome.NOT_APPLICABLE,
            )
        workspace = Workspace(self.installation)
        try:
            with workspace.lock():
                pins = authority.issued_reads(snapshot, reservation, observed.issue)
                operation = self.build(
                    intent,
                    observed.issue,
                    snapshot,
                    prepared,
                    finalization,
                    workspace,
                    operation=uuid4().hex,
                    authority_paths=pins,
                )
                result = self.commit(operation, snapshot)
        except (GraduationConflict, GraphConflict, BindingConflict) as error:
            return self.result(
                intent.operation_id,
                snapshot,
                LocalOutcome.CONFLICT,
                str(error),
                PublicationOutcome.PENDING,
            )
        return OperationResult(
            result.command.model_copy(update={"operation_id": intent.operation_id}),
            result.snapshot,
            result.reason,
            result.guards,
            result.preflight,
            result.authorization,
        )

    def link(self, request: LinkRequest) -> OperationResult:
        prepared = self.policy()
        assert prepared.policy is not None
        snapshot = self.snapshot(prepared)
        graph = read_graph(self.installation.repository, snapshot)
        changes = link_changes(graph, request)
        identity = uuid4().hex
        if not changes:
            return self.result(
                identity,
                snapshot,
                LocalOutcome.COMPLETED,
                "The reciprocal links already match.",
            )
        context = EventContext(
            identity, self.owner, self.stamp, prepared.policy.source.digest
        )
        reads = _pin(graph.logs)
        operation = Operation(
            operation_id=identity,
            owner=self.owner,
            policy_digest=context.policy_digest,
            category=OperationCategory.NORMAL,
            intent=FinalizationIntent(
                kind="core.link",
                version=1,
                related_preconditions=reads,
                payload=request.model_dump_json().encode(),
            ),
            change=RelatedWriteSet(
                read_set=reads, events=reciprocal_events(graph, changes, context)
            ),
        )
        return self.commit(operation, snapshot)
