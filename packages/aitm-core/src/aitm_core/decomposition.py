"""Freeze reviewed decomposition and evaluate issued child provenance."""

import json
from dataclasses import dataclass
from hashlib import sha256
from types import MappingProxyType

from aitm_core.documents import _parse, canonicalize
from aitm_core.events import UnavailableReducer, core_reducers, fold
from aitm_core.graduation import (
    GraduatedRecord,
    graduation_path,
    validate_graduated_record,
)
from aitm_core.models.binding import StoryRef, allows_authored
from aitm_core.models.decomposition import DecompositionMap, PlanEntry
from aitm_core.models.documents import DocumentSchema
from aitm_core.models.identity import PlanEntrySource
from aitm_core.models.lifecycle import DocumentAcceptance, Graduation, LifecycleState
from aitm_core.models.operations import ReadExpectation, story_event_path
from aitm_core.reviews.acceptance import ApplicabilityResult, DocumentInput
from aitm_core.reviews.turns import ReviewContext
from aitm_core.store.backend import Backend, Snapshot


class DecompositionUnavailable(ValueError):
    """A typed, reviewed decomposition input is unavailable."""


@dataclass(frozen=True, slots=True)
class FrozenDecomposition:
    snapshot: Snapshot
    parent: int
    design_digest: str
    plan_digest: str
    _entries: MappingProxyType[str, PlanEntry]
    reads: tuple[ReadExpectation, ...]

    def entry(self, key: str) -> PlanEntry:
        try:
            return self._entries[key]
        except KeyError as error:
            raise ValueError("decomposition entry is unavailable") from error

    def identity(self, key: str) -> tuple[str, int, str]:
        self.entry(key)
        return self.snapshot.store, self.parent, key


@dataclass(frozen=True, slots=True)
class EntryReconciliation:
    child: int
    identity: tuple[str, int, str]
    previous: PlanEntrySource
    current: PlanEntrySource
    reads: tuple[ReadExpectation, ...]


def _accepted_inputs(
    store: Backend,
    snapshot: Snapshot,
    parent: int,
    policy_digest: str,
) -> tuple[DocumentAcceptance, DocumentAcceptance, tuple[ReadExpectation, ...]]:
    path = story_event_path(parent)
    raw = store.read(snapshot, (path,))[path]
    if not raw:
        raise DecompositionUnavailable("parent acceptance evidence is unavailable")
    state = fold(raw.splitlines(keepends=True), core_reducers())
    lifecycle = state.domains.get("lifecycle")
    if (
        state.story_id != parent
        or not isinstance(lifecycle, LifecycleState)
        or lifecycle.kind != "epic"
    ):
        raise ValueError("decomposition requires the declared parent epic")
    design = lifecycle.accepted_documents.get("design")
    plan = lifecycle.accepted_documents.get("plan")
    if (
        design is None
        or plan is None
        or any(doc.policy_digest != policy_digest for doc in (design, plan))
    ):
        raise DecompositionUnavailable(
            "current accepted parent design and plan are required"
        )
    return design, plan, (ReadExpectation(path=path, digest=sha256(raw).hexdigest()),)


def _document(
    parent: int, doc: DocumentAcceptance, raw: bytes | None
) -> tuple[dict, ReadExpectation]:
    if raw is None:
        raise DecompositionUnavailable("accepted parent document is unavailable")
    header = _parse(raw).header
    if (
        not allows_authored(StoryRef(story=parent), doc.path)
        or doc.path.split("/")[4] != doc.role
        or (header.get("story"), header.get("role")) != (parent, doc.role)
    ):
        raise ValueError("accepted parent document identity disagrees with its scope")
    digest = canonicalize(raw, DocumentSchema())
    if digest.canonical_sha256 != doc.canonical_digest:
        raise ValueError("current parent document differs from accepted content")
    return header, ReadExpectation(path=doc.path, digest=digest.raw_sha256)


def prepare_decomposition(
    store: Backend,
    snapshot: Snapshot,
    parent: int,
    expected_plan: str,
    policy_digest: str,
) -> FrozenDecomposition:
    """Read one exact snapshot and freeze the accepted semantic map and coverage."""
    design, plan, event_reads = _accepted_inputs(store, snapshot, parent, policy_digest)
    if plan.canonical_digest != expected_plan:
        raise ValueError("expected plan disagrees with the accepted parent plan")
    documents = store.read(snapshot, (design.path, plan.path))
    _, design_read = _document(parent, design, documents[design.path])
    plan_header, plan_read = _document(parent, plan, documents[plan.path])
    fields = plan_header.get("decomposition")
    if fields is None:
        raise DecompositionUnavailable(
            "accepted plan lacks a v1 semantic decomposition map"
        )
    descriptors = DecompositionMap.model_validate_json(json.dumps(fields))
    return FrozenDecomposition(
        snapshot,
        parent,
        design.canonical_digest,
        plan.canonical_digest,
        MappingProxyType(descriptors.root),
        (*event_reads, design_read, plan_read),
    )


def prepare_plan_entry(parent: FrozenDecomposition, key: str) -> PlanEntrySource:
    entry = parent.entry(key)
    return PlanEntrySource(
        parent=parent.parent,
        entry_key=key,
        design_digest=parent.design_digest,
        plan_digest=parent.plan_digest,
        entry_digest=entry.digest,
        descriptor=entry.description,
    )


def assess_decomposition(
    child: PlanEntrySource, parent: FrozenDecomposition, *, design_coverage: str | None
) -> ApplicabilityResult:
    if design_coverage != "own-document":
        return ApplicabilityResult(
            "unavailable", reason="own-document design coverage is required"
        )
    if child.parent != parent.parent:
        return ApplicabilityResult("stale", reason="child belongs to another parent")
    try:
        source = prepare_plan_entry(parent, child.entry_key)
    except ValueError as error:
        return ApplicabilityResult("stale", reason=str(error))
    if child != source:
        return ApplicabilityResult(
            "stale", reason="parent or child entry provenance changed"
        )
    return ApplicabilityResult("current", parent.reads)


def reconcile_plan_entry(
    child: int,
    prior: PlanEntrySource,
    parent: FrozenDecomposition,
    *,
    store: str,
) -> EntryReconciliation:
    """Prepare updated source for an existing identity. Issuance is owned by C75."""
    if (
        child < 1
        or child == parent.parent
        or prior.parent != parent.parent
        or store != parent.snapshot.store
    ):
        raise ValueError("existing child identity is outside the pinned parent/store")
    current = prepare_plan_entry(parent, prior.entry_key)
    return EntryReconciliation(
        child, parent.identity(prior.entry_key), prior, current, parent.reads
    )


def plan_entry_applicability(
    context: ReviewContext,
    graduation: Graduation,
    document: DocumentInput,
    *,
    design_coverage: str | None,
) -> ApplicabilityResult:
    """C26 port: qualify frozen issuance plus its current reviewed parent inputs."""
    if design_coverage != "own-document":
        return ApplicabilityResult(
            "unavailable", reason="own-document design coverage is required"
        )
    if graduation.source_kind != "plan-entry" or graduation.parent is None:
        return ApplicabilityResult(
            "stale", reason="child has no declared plan entry source"
        )
    parent_id, _, key = graduation.source_id.partition(":")
    if parent_id != str(graduation.parent) or not key:
        return ApplicabilityResult(
            "stale", reason="malformed child plan entry identity"
        )
    try:
        _, plan, _ = _accepted_inputs(
            context.backend, context.snapshot, graduation.parent, context.policy_digest
        )
        parent = prepare_decomposition(
            context.backend,
            context.snapshot,
            graduation.parent,
            plan.canonical_digest,
            context.policy_digest,
        )
        source = prepare_plan_entry(parent, key)
        path = graduation_path(source)
        raw = context.backend.read(context.snapshot, (path,))[path]
        if raw is None:
            raise DecompositionUnavailable("retained child issuance is unavailable")
        validate_graduated_record(path, raw)
        record = GraduatedRecord.model_validate_json(raw)
        issued = record.intent.source
        if (
            not isinstance(issued, PlanEntrySource)
            or record.issue.number != document.story
            or record.intent.kind != graduation.kind
            or record.intent.parent != graduation.parent
            or issued.identity != graduation.source_id
            or issued.entry_digest != graduation.source_digest
        ):
            return ApplicabilityResult(
                "stale", reason="retained child issuance disagrees with graduation"
            )
        decision = assess_decomposition(issued, parent, design_coverage=design_coverage)
        if decision.status != "current":
            return decision
        return ApplicabilityResult(
            "current",
            (
                *decision.reads,
                ReadExpectation(path=path, digest=sha256(raw).hexdigest()),
            ),
        )
    except (DecompositionUnavailable, UnavailableReducer) as error:
        return ApplicabilityResult("unavailable", reason=str(error))
    except ValueError as error:
        return ApplicabilityResult("stale", reason=str(error))
