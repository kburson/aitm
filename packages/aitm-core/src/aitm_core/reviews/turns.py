"""Persist immutable review capsules and normalized review facts through C09."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import PurePosixPath
from typing import Literal

from aitm_core.documents import _parse, canonicalize
from aitm_core.events import StoryState, core_reducers, fold
from aitm_core.models.common import CommandResult, LocalOutcome
from aitm_core.models.documents import DocumentSchema
from aitm_core.models.events import EventEnvelope, validate_envelope
from aitm_core.models.evidence import (
    DocumentReviewCompleted,
    DocumentReviewFact,
    DocumentReviewOpened,
    DocumentReviewTurn,
    ReviewLevel,
    ReviewParticipant,
)
from aitm_core.models.operations import (
    BlobWrite,
    EventAppend,
    FinalizationIntent,
    Operation,
    OperationCategory,
    OperationOwner,
    ReadExpectation,
    RelatedWriteSet,
    repository_path,
    story_event_path,
    story_scope,
)
from aitm_core.reducers.evidence import DocumentReview, EvidenceState
from aitm_core.reviews.native import ValidatedBundle
from aitm_core.reviews.policy import _decision, _TurnClaims
from aitm_core.reviews.portable import (
    Original,
    PortableResponse,
    ReviewError,
    _parse_record,
)
from aitm_core.store.backend import Backend, OperationResult, Snapshot


class ReviewConflict(ReviewError):
    """The retained review identity refers to different source evidence."""


@dataclass(frozen=True, slots=True)
class ReviewContext:
    backend: Backend
    snapshot: Snapshot
    owner: OperationOwner
    policy_digest: str
    operation_id: str
    at: str
    publish: Callable[[Operation, Snapshot], OperationResult]


@dataclass(frozen=True, slots=True)
class OpenReviewRequest:
    context: ReviewContext
    story: int
    path: str
    level: ReviewLevel
    document: bytes


@dataclass(frozen=True, slots=True)
class LevelRecord:
    context: ReviewContext
    story: int
    record_id: str
    path: str
    level: ReviewLevel
    result: OperationResult | None = None

    @property
    def capsule(self) -> str:
        store_story = PurePosixPath(story_event_path(self.story)).parent
        return f"{store_story}/evidence/reviews/{self.record_id}"


def _story(context: ReviewContext, story: int) -> tuple[bytes, StoryState]:
    path = story_event_path(story)
    raw = context.backend.read(context.snapshot, (path,))[path]
    if raw is None:
        raise ReviewError("review story is unavailable")
    state = fold(raw.splitlines(keepends=True), core_reducers())
    if state.story_id != story or "lifecycle" not in state.domains:
        raise ReviewError("review target is not an initialized story")
    return raw, state


def _reviews(state: StoryState) -> dict[str, DocumentReview]:
    evidence = state.domains.get("evidence")
    return evidence.document_reviews if isinstance(evidence, EvidenceState) else {}


def _document(raw: bytes, story: int, path: str):
    repository_path(path)
    header = _parse(raw).header
    if (
        story_scope(path) != story
        or header.get("story") != story
        or header.get("role") not in ("design", "plan")
    ):
        raise ReviewError(
            "review document must be an authored design or plan of the selected story"
        )
    return canonicalize(raw, DocumentSchema())


def load_level(context: ReviewContext, story: int, record_id: str) -> LevelRecord:
    _, state = _story(context, story)
    record = _reviews(state).get(record_id)
    if record is None:
        raise ReviewError("review capsule is unavailable")
    return LevelRecord(context, story, record_id, record.path, record.level)


def _existing(level: LevelRecord, state: StoryState) -> DocumentReview:
    entry = _reviews(state).get(
        level.record_id, DocumentReview(level.level, level.path)
    )
    if entry.level != level.level or entry.path != level.path:
        raise ReviewConflict("review identity belongs to another document or level")
    return entry


def _events(
    level: LevelRecord,
    raw: bytes,
    state: StoryState,
    facts: tuple[tuple[str, str, DocumentReviewFact], ...],
) -> tuple[bytes, ...]:
    # The event fold suppresses exact repeated event IDs. Hash that same
    # unique causal prefix when appending several facts as one operation.
    prefix = sha256()
    seen = set()
    for line in raw.splitlines(keepends=True):
        identity = validate_envelope(line).id
        if identity not in seen:
            prefix.update(line.removesuffix(b"\n") + b"\n")
            seen.add(identity)
    ctx = level.context
    records = []
    for index, (event_type, occurred, fact) in enumerate(facts):
        event = (
            EventEnvelope(
                v=1,
                id=f"{ctx.operation_id}:review-{index}",
                story=level.story,
                type=f"core.doc-review.{event_type}",
                ts=occurred,
                recorded_at=ctx.at,
                actor=ctx.owner.actor,
                operation_id=ctx.operation_id,
                sequence=state.next_sequence + index,
                prior_log_digest=prefix.hexdigest(),
                policy_digest=ctx.policy_digest,
                data=fact.model_dump(mode="json"),
            )
            .model_dump_json(exclude_none=True)
            .encode()
        )
        prefix.update(event + b"\n")
        records.append(event)
    return tuple(records)


def _persist(
    level: LevelRecord,
    raw: bytes,
    state: StoryState,
    files: dict[str, bytes],
    facts: tuple[tuple[str, str, DocumentReviewFact], ...],
    *,
    intent: Literal["open", "turn", "complete"],
    additional_reads: tuple[str, ...] = (),
) -> OperationResult:
    ctx = level.context
    event_path = story_event_path(level.story)
    paths = tuple(dict.fromkeys((event_path, *files, *additional_reads)))
    old = ctx.backend.read(ctx.snapshot, paths)
    if old[event_path] != raw:
        raise ReviewConflict("review event stream changed")
    changes = []
    for path, data in files.items():
        if old[path] is None:
            changes.append(BlobWrite(path=path, content=data))
        elif old[path] != data:
            raise ReviewConflict(f"immutable review evidence differs at {path}")
    if not changes and not facts:
        return OperationResult(
            CommandResult(operation_id=ctx.operation_id, local=LocalOutcome.COMPLETED),
            ctx.snapshot,
        )
    reads = tuple(
        ReadExpectation(
            path=path,
            digest=sha256(old[path]).hexdigest() if old[path] is not None else None,
        )
        for path in paths
    )
    records = _events(level, raw, state, facts)
    operation = Operation(
        operation_id=ctx.operation_id,
        owner=ctx.owner,
        policy_digest=ctx.policy_digest,
        category=OperationCategory.NORMAL,
        intent=FinalizationIntent(
            kind=f"review.{intent}",
            version=1,
            related_preconditions=reads,
            payload=b"{}",
        ),
        change=RelatedWriteSet(
            read_set=reads,
            writes=tuple(changes),
            events=(EventAppend(story=level.story, records=records),)
            if records
            else (),
        ),
    )
    return ctx.publish(operation, ctx.snapshot)


def open_review(request: OpenReviewRequest) -> LevelRecord:
    ctx = request.context
    document = _document(request.document, request.story, request.path)
    record_id = (
        f"review-{request.story}-{sha256(ctx.operation_id.encode()).hexdigest()[:24]}"
    )
    level = LevelRecord(ctx, request.story, record_id, request.path, request.level)
    raw, state = _story(ctx, request.story)
    existing = _existing(level, state).opening
    if existing is not None and existing.raw_digest != document.raw_sha256:
        raise ReviewConflict("opened capsule is bound to different raw bytes")
    opening = DocumentReviewOpened(
        record_id=record_id,
        level=level.level,
        path=level.path,
        raw_digest=document.raw_sha256,
        content_digest=document.canonical_sha256,
        opened_at=ctx.at,
        opened_by=ctx.owner.actor,
        source_operation=ctx.operation_id,
    )
    result = _persist(
        level,
        raw,
        state,
        {f"{level.capsule}/base.md": request.document},
        () if existing else (("opened", ctx.at, opening),),
        intent="open",
    )
    return LevelRecord(ctx, level.story, record_id, level.path, level.level, result)


def _turn_path(level: LevelRecord, turn: PortableResponse) -> str:
    return f"{level.capsule}/{turn.role}-response-{turn.round}.md"


def _predecessor_name(response: PortableResponse) -> str | None:
    if response.role == "author":
        return f"reviewer-response-{response.round}.md"
    if response.round > 1:
        return f"author-response-{response.round - 1}.md"
    return None


def _fact(
    level: LevelRecord,
    response: PortableResponse,
    original: Original,
    predecessor: Original | None = None,
    native_anchor=None,
) -> DocumentReviewTurn:
    if (response.story, response.level, response.artifact_path) != (
        level.story,
        level.level,
        level.path,
    ):
        raise ReviewConflict("review response belongs to another capsule")
    if response.agent is None or response.submitted_at is None:
        raise ReviewError(
            "submitted review evidence requires participant and submission time"
        )
    document = _parse(original.raw)
    header = document.header
    path = _turn_path(level, response)
    decision = None
    if response.role == "reviewer":
        verdict = _decision(document, _TurnClaims.model_validate(header))
        if verdict is None:
            raise ReviewError("reviewer response lacks an explicit decision")
        decision = "pass" if verdict == "accepted" else "changes"
    elif response.patch != f"patch-{response.round:03d}.diff":
        raise ReviewError("author response lacks its own numbered patch reference")
    session = getattr(response, f"{response.role}_session")
    identity_kind = header.get("session_identity_kind")
    basis, started, reference = "unknown", None, None
    if native_anchor is not None and native_anchor.source is not None:
        basis, started = native_anchor.basis, native_anchor.started_at
        reference = (
            f"{level.capsule}/{native_anchor.source.path}#{native_anchor.source.digest}"
        )
        if native_anchor.claim_id:
            reference += f"/{native_anchor.claim_id}"
    elif response.start_basis == "recorded" and response.started_at is not None:
        basis, started = "recorded", response.started_at
        reference = f"{path}#{original.raw_digest}/started_at"
    elif response.start_basis == "prior-submit" and predecessor is not None:
        prior = _parse_record(predecessor.raw, PortableResponse, predecessor.name)
        if (
            response.start_source == predecessor.name
            and response.started_at == prior.submitted_at
            and prior.submitted_at is not None
        ):
            basis, started = "prior-submit", prior.submitted_at
            reference = f"{level.capsule}/{predecessor.name}#{predecessor.raw_digest}"
    if started is not None and datetime.fromisoformat(started) > datetime.fromisoformat(
        response.submitted_at
    ):
        raise ReviewError("review start follows submission")
    agent = response.agent
    digest = response.artifact_digest.removeprefix("sha256:")
    return DocumentReviewTurn(
        record_id=level.record_id,
        level=level.level,
        path=level.path,
        round=response.round,
        role=response.role,
        agent=ReviewParticipant(
            host=agent.host,
            provider=agent.provider,
            model_id=agent.model_id,
            effort=agent.effort,
            session_id=session,
            session_id_kind="native"
            if identity_kind == "native-fingerprint"
            else "adapter"
            if session
            else "unknown",
        ),
        started_at=started,
        submitted_at=response.submitted_at,
        start_basis=basis,
        start_ref=reference,
        input_digest=digest if response.role == "reviewer" else None,
        output_digest=digest if response.role == "author" else None,
        patch_path=f"{level.capsule}/{response.patch}" if response.patch else None,
        response_path=path,
        source_digest=original.raw_digest.removeprefix("sha256:"),
        finding_ids=response.finding_ids
        if response.role == "reviewer"
        else response.answered_finding_ids,
        decision=decision,
    )


def record_turn(level: LevelRecord, response: bytes) -> OperationResult:
    raw, state = _story(level.context, level.story)
    existing = _existing(level, state)
    parsed = _parse_record(response, PortableResponse, "provisional response")
    path = _turn_path(level, parsed)
    original = Original(PurePosixPath(path).name, response)
    prior = existing.turns.get((parsed.round, parsed.role))
    if prior is not None and prior.source_digest != original.raw_digest.removeprefix(
        "sha256:"
    ):
        raise ReviewConflict("review turn identity has different source bytes")
    if existing.completion is not None and prior is None:
        raise ReviewConflict("completed review cannot acquire a new provisional turn")
    predecessor_name = _predecessor_name(parsed)
    predecessor = None
    if predecessor_name is not None:
        absolute = f"{level.capsule}/{predecessor_name}"
        value = level.context.backend.read(level.context.snapshot, (absolute,))[
            absolute
        ]
        predecessor = Original(predecessor_name, value) if value is not None else None
    fact = _fact(level, parsed, original, predecessor)
    return _persist(
        level,
        raw,
        state,
        {path: response},
        () if prior is not None else (("submitted", fact.submitted_at, fact),),
        intent="turn",
        additional_reads=(f"{level.capsule}/{predecessor_name}",)
        if predecessor_name
        else (),
    )


def complete_review(
    level: LevelRecord,
    bundle: ValidatedBundle,
    *,
    additional_reads: tuple[str, ...] = (),
) -> OperationResult:
    """Reuse immutable live turns while adding verified closure and any timing derivation."""
    raw, state = _story(level.context, level.story)
    declared = bundle.record.manifest
    if (declared.story, declared.level, declared.artifact_path) != (
        level.story,
        level.level,
        level.path,
    ):
        raise ReviewConflict("review bundle belongs to another document or level")
    existing = _existing(level, state)
    base = _document(bundle.record.base_bytes, level.story, level.path)
    final = _document(bundle.record.final_bytes, level.story, level.path)
    if existing.opening is not None and existing.opening.raw_digest != base.raw_sha256:
        raise ReviewConflict("review bundle base differs from the opened capsule")
    originals = {item.name: item for item in bundle.record.originals}
    files = {}
    for name, original in originals.items():
        repository_path(name)
        path = f"{level.capsule}/{name}"
        files[path] = original.raw
    if existing.opening is not None:
        files[f"{level.capsule}/base.md"] = bundle.record.base_bytes
    native = {
        (turn.response.round, turn.response.role): turn.anchor
        for turn in (bundle.native.turns if bundle.native is not None else ())
    }
    pending = []
    observed = set()
    ends = []
    for round_ in bundle.record.rounds:
        for turn in (round_.reviewer, round_.author):
            key = (turn.round, turn.role)
            observed.add(key)
            name = f"{turn.role}-response-{turn.round}.md"
            fact = _fact(
                level,
                turn,
                originals[name],
                originals.get(_predecessor_name(turn)),
                native.get(key),
            )
            ends.append(fact.submitted_at)
            prior = existing.turns.get(key)
            if prior is None:
                pending.append(("submitted", fact.submitted_at, fact))
            elif prior != fact:
                if (
                    prior.model_copy(
                        update={
                            "start_basis": fact.start_basis,
                            "started_at": fact.started_at,
                            "start_ref": fact.start_ref,
                        }
                    )
                    != fact
                ):
                    raise ReviewConflict(
                        "verified turn disagrees with retained source evidence"
                    )
                # Additional public timing proof does not replace the source
                # turn or count it a second time.
                files[f"{level.capsule}/timing/{name}.json"] = (
                    fact.model_dump_json().encode()
                )
    if set(existing.turns).difference(observed):
        raise ReviewConflict("completion omits retained live turns")
    opened = existing.opening.opened_at if existing.opening is not None else None
    completed = DocumentReviewCompleted(
        record_id=level.record_id,
        level=level.level,
        path=level.path,
        rounds=declared.rounds,
        outcome="exhausted",
        base_digest=base.canonical_sha256,
        final_digest=final.canonical_sha256,
        started_at=opened,
        start_basis="recorded" if opened else "unknown",
        ended_at=max(ends, key=datetime.fromisoformat),
        manifest_path=f"{level.capsule}/review-manifest.md",
    )
    if existing.completion is not None and existing.completion != completed:
        raise ReviewConflict("review already has a different completion")
    if existing.completion is None:
        pending.append(("completed", completed.ended_at, completed))
    return _persist(
        level,
        raw,
        state,
        files,
        tuple(pending),
        intent="complete",
        additional_reads=additional_reads,
    )
