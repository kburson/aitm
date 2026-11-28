"""Import exact review evidence under a planning authoring reservation."""

import re
from dataclasses import dataclass, replace
from datetime import datetime
from hashlib import sha256
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory

from aitm_core.documents import _GENERATED_KEYS, _parse, rewrite_metadata
from aitm_core.models.attempts import BindingPurpose
from aitm_core.models.binding import Binding, StoryRef, allows_authored
from aitm_core.models.common import LocalOutcome, PublicationOutcome
from aitm_core.models.documents import Metadata
from aitm_core.models.evidence import DocumentReviewCompleted
from aitm_core.models.operations import (
    BlobWrite,
    FinalizationIntent,
    Operation,
    OperationCategory,
    ReadExpectation,
    RelatedWriteSet,
    repository_path,
    story_event_path,
)
from aitm_core.reviews.native import ValidatedBundle
from aitm_core.reviews.policy import _decision, _findings, _TurnClaims
from aitm_core.reviews.portable import (
    ReconstructedReview,
    ReviewError,
    reconstruct_bundle,
)
from aitm_core.reviews.turns import (
    LevelRecord,
    ReviewConflict,
    ReviewContext,
    _document,
    _existing,
    _persist,
    _reviews,
    _story,
    complete_review,
)
from aitm_core.store.backend import OperationResult, Snapshot
from aitm_core.store.objects import GitCommandError
from aitm_core.store.sync import _pin
from aitm_core.store.validation import PlanningPath, classify_planning_path
from aitm_core.store.workspace import (
    BindingConflict,
    Workspace,
    _materialize,
    digest,
    read_workspace,
)


@dataclass(frozen=True, slots=True)
class ReviewImport:
    context: ReviewContext
    workspace: Workspace
    story: int
    path: str
    binding_id: str
    generation: int
    session: str
    record_id: str | None = None
    project_authored: bool = True
    observed_publication: PublicationOutcome = PublicationOutcome.PENDING


def _revised_document(
    story: int, path: str, shared: bytes | None, base: bytes, final: bytes
) -> bytes | None:
    before = _document(base, story, path)
    after = _document(final, story, path)
    current = _document(shared, story, path) if shared is not None else None
    header = _parse(shared).header if shared is not None else {}
    role = PurePosixPath(path).parts[4]
    if any(
        value.get("role", role) != role
        for value in (_parse(base).header, _parse(final).header, header)
    ):
        raise ReviewError("review document role must match its authored directory")
    if current is not None and (
        current.canonical_sha256 != before.canonical_sha256
        or current.canonical_sha256 == after.canonical_sha256
    ):
        return None
    # Retain generated values from the refreshed planning FUR. The reviewed
    # raw bytes are retained in the immutable patch chain.
    generated = Metadata.model_validate(
        {key: header.get(key) for key in _GENERATED_KEYS}
    )
    return rewrite_metadata(final, generated)


def _originals(
    record: ReconstructedReview, bundle: ValidatedBundle | None
) -> dict[str, bytes]:
    inventory = {"review-manifest.md", "patch-000.diff"}
    if record.manifest.rounds != len(record.rounds):
        raise ReviewError("review manifest and replay have different round counts")
    for index in range(1, len(record.rounds) + 1):
        inventory.update(
            (
                f"patch-{index:03d}.diff",
                f"reviewer-response-{index}.md",
                f"author-response-{index}.md",
            )
        )
    sources = ()
    if bundle is not None and bundle.native is not None:
        native = bundle.native
        sources = (native.manifest, *(turn.response.source for turn in native.turns))
        for source in sources:
            if source.path in inventory:
                raise ReviewError("native provenance overlaps a review original")
            inventory.add(source.path)
    originals = {item.name: item.raw for item in record.originals}
    if len(originals) != len(record.originals) or set(originals) != inventory:
        raise ReviewError("review original inventory differs from the verified inputs")
    if any(
        f"sha256:{digest(originals[source.path])}" != source.digest
        for source in sources
    ):
        raise ReviewError("native original bytes differ from their verified reference")
    if bundle is None:
        header = _parse(originals["review-manifest.md"]).header
        if (
            "native_review_id" in header
            or header.get("native_status") is not None
            or header.get("authority_assurance")
            in ("unavailable", "native-consensus-authority-unavailable")
        ):
            raise ReviewError("native provenance for a capped review is unsupported")
        # Capped evidence carries no policy receipt. Replay the exact originals
        # before recording it, including the claimed cap and the final bytes.
        with TemporaryDirectory(prefix="aitm-capped-review-") as folder:
            for name, raw in originals.items():
                (Path(folder) / name).write_bytes(raw)
            observed = reconstruct_bundle(folder)
        if replace(observed, originals=record.originals) != record:
            raise ReviewError("capped review does not match the retained byte chain")
        for index, round_ in enumerate(record.rounds, 1):
            _findings(round_.reviewer, round_.author, index)
            response = _parse(originals[f"reviewer-response-{index}.md"])
            if (
                _decision(response, _TurnClaims.model_validate(response.header))
                == "accepted"
            ):
                raise ReviewError("capped review contains an acceptance decision")
    return originals


def _capsule(
    request: ReviewImport,
    record: ReconstructedReview,
    originals: dict[str, bytes],
    bundle: ValidatedBundle | None,
) -> tuple[LevelRecord, tuple[str, ...]]:
    ctx = request.context
    _, state = _story(ctx, request.story)
    levels = _reviews(state)
    identity = request.record_id
    source_name = (
        bundle.native.manifest.path
        if bundle is not None and bundle.native is not None
        else "review-manifest.md"
    )
    candidates = {}
    for candidate, entry in levels.items():
        if (entry.path, entry.level) != (request.path, record.manifest.level):
            continue
        other = _level(request, candidate, record)
        if entry.completion is not None:
            candidates[candidate] = {
                f"{other.capsule}/{source_name}": originals[source_name]
            }
        elif entry.opening is not None and entry.turns:
            if entry.opening.raw_digest != digest(record.base_bytes):
                continue
            turns = {
                f"{role}-response-{index}.md": turn.source_digest
                for (index, role), turn in entry.turns.items()
            }
            if all(
                name in originals and digest(originals[name]) == raw
                for name, raw in turns.items()
            ):
                candidates[candidate] = {
                    f"{other.capsule}/base.md": record.base_bytes,
                    **{f"{other.capsule}/{name}": originals[name] for name in turns},
                }
    checked = tuple(path for expected in candidates.values() for path in expected)
    retained = ctx.backend.read(ctx.snapshot, checked)
    matches = [
        candidate
        for candidate, expected in candidates.items()
        if all(retained[path] == raw for path, raw in expected.items())
    ]
    if len(matches) > 1 or (
        matches and identity is not None and identity != matches[0]
    ):
        raise ReviewConflict(
            "review evidence matches a different or ambiguous live capsule"
        )
    if identity is not None and identity not in levels:
        raise ReviewConflict("the named review capsule is unavailable")
    if identity is None:
        source_digest = sha256(originals[source_name]).hexdigest()
        identity = (
            matches[0] if matches else f"review-{request.story}-{source_digest[:24]}"
        )
    return _level(request, identity, record), checked


def _level(
    request: ReviewImport, identity: str, record: ReconstructedReview
) -> LevelRecord:
    if re.fullmatch(rf"review-{request.story}-[0-9a-f]{{24}}", identity) is None:
        raise ReviewConflict("the review capsule identity is outside the story scope")
    return LevelRecord(
        request.context, request.story, identity, request.path, record.manifest.level
    )


def _cap(
    level: LevelRecord,
    record: ReconstructedReview,
    originals: dict[str, bytes],
    additional_reads: tuple[str, ...],
) -> OperationResult:
    raw, state = _story(level.context, level.story)
    existing = _existing(level, state)
    base = _document(record.base_bytes, level.story, level.path)
    final = _document(record.final_bytes, level.story, level.path)
    if existing.opening is not None and existing.opening.raw_digest != base.raw_sha256:
        raise ReviewConflict("capped review base differs from the opened capsule")
    for index, role in existing.turns:
        body = originals.get(f"{role}-response-{index}.md")
        if body is None or digest(body) != existing.turns[(index, role)].source_digest:
            raise ReviewConflict("capped review disagrees with a retained live turn")
    observed = [
        turn.submitted_at
        for round_ in record.rounds
        for turn in (round_.reviewer, round_.author)
        if turn.submitted_at is not None
    ]
    ended = record.manifest.verified_at or (
        max(observed, key=datetime.fromisoformat) if observed else None
    )
    if ended is None:
        raise ReviewError("capped review requires a retained end timestamp")
    opened = existing.opening.opened_at if existing.opening is not None else None
    completed = DocumentReviewCompleted(
        record_id=level.record_id,
        level=level.level,
        path=level.path,
        rounds=record.manifest.rounds,
        outcome="round-cap",
        base_digest=base.canonical_sha256,
        final_digest=final.canonical_sha256,
        started_at=opened,
        start_basis="recorded" if opened else "unknown",
        ended_at=ended,
        manifest_path=f"{level.capsule}/review-manifest.md",
    )
    if existing.completion is not None and existing.completion != completed:
        raise ReviewConflict("review already has a different completion")
    files = {f"{level.capsule}/{name}": body for name, body in originals.items()}
    if existing.opening is not None:
        files[f"{level.capsule}/base.md"] = record.base_bytes
    pending = (("completed", ended, completed),) if existing.completion is None else ()
    return _persist(
        level,
        raw,
        state,
        files,
        pending,
        intent="complete",
        additional_reads=additional_reads,
    )


def _publish(
    context: ReviewContext,
    expected: Snapshot,
    path: str,
    revised: bytes | None,
    operation: Operation,
) -> OperationResult:
    changes = operation.change
    if revised is not None:
        changes = RelatedWriteSet(
            read_set=changes.read_set,
            writes=(*changes.writes, BlobWrite(path=path, content=revised)),
            events=changes.events,
        )
    return context.publish(
        operation.model_copy(
            update={
                "change": changes,
                "intent": operation.intent.model_copy(update={"kind": "review.import"}),
            }
        ),
        expected,
    )


def _projection_admitted(publication: PublicationOutcome, shared: bool) -> bool:
    required = (
        PublicationOutcome.VERIFIED if shared else PublicationOutcome.NOT_APPLICABLE
    )
    return publication == required


def _project(
    request: ReviewImport, binding: Binding, before: bytes | None, revised: bytes
) -> None:
    workspace = request.workspace
    current = workspace.repo.tip()
    if (
        workspace.repo.read_blobs(current.tree, (request.path,))[request.path]
        != revised
    ):
        raise BindingConflict("The planning ref advanced before workspace projection.")
    _materialize(Path(binding.worktree), request.path, revised, observed=before)
    pinned = _pin(workspace, binding, (request.path,))
    selected = next(item for item in pinned.paths if item.path == request.path)
    if selected.digest != digest(revised):
        raise BindingConflict("The workspace projection could not be pinned.")


def import_review(
    binding: ReviewImport,
    bundle: ValidatedBundle | ReconstructedReview,
    expected_base: str | None,
) -> OperationResult:
    """CAS a reviewed FUR and immutable evidence in one planning-store operation."""
    request = binding
    context = request.context
    workspace = request.workspace
    qualified = bundle if isinstance(bundle, ValidatedBundle) else None
    replay = qualified.record if qualified is not None else bundle
    if not isinstance(replay, ReconstructedReview):
        raise ReviewError("unsupported review evidence input")
    manifest = replay.manifest
    scope = StoryRef(story=request.story)
    path = repository_path(request.path)
    if (
        (manifest.story, manifest.artifact_path) != (request.story, path)
        or not allows_authored(scope, path)
        or PurePosixPath(path).parts[4] not in ("design", "plan")
        or PurePosixPath(path).suffix != ".md"
    ):
        raise ReviewError(
            "review import requires the selected story's authored design or plan"
        )
    if (
        expected_base is not None
        and re.fullmatch(r"[0-9a-f]{64}", expected_base) is None
    ):
        raise ReviewError("expected base must be a raw SHA-256 or an absent file")
    if qualified is None and manifest.outcome != "round-cap":
        raise ReviewError("review import requires a validated bundle or capped replay")
    if qualified is not None and (
        qualified.level != manifest.level or manifest.outcome != "exhausted"
    ):
        raise ReviewError("validated bundle does not prove this completed review level")
    originals = _originals(replay, qualified)
    with workspace.lock():
        held = workspace.require(
            scope, request.binding_id, request.generation, request.session
        )
        pinned_path = next((item for item in held.paths if item.path == path), None)
        if (
            held.purpose != BindingPurpose.PLANNING
            or pinned_path is None
            or (context.owner.binding, context.owner.generation)
            != (held.identity, held.generation)
            or context.owner.actor.session != held.session
            or context.owner.extension is not None
        ):
            raise ReviewConflict(
                "review import requires the current planning binding for this path"
            )
        if workspace.repo.tip() != context.snapshot:
            raise ReviewConflict("the planning snapshot changed before review import")
        before = context.backend.read(context.snapshot, (path,))[path]
        root = Path(held.worktree)
        local = read_workspace(root, path)
        retry_projection = False
        if (
            qualified is not None
            and request.project_authored
            and before is not None
            and pinned_path.revision is not None
            and pinned_path.digest == expected_base
            and (digest(before) != expected_base or local != before)
        ):
            bound = context.backend.read_tree(pinned_path.revision)
            original = context.backend.read(bound, (path,))[path]
            retry_projection = (
                digest(original) == expected_base
                and local in (original, before)
                and _revised_document(
                    request.story, path, original, replay.base_bytes, replay.final_bytes
                )
                == before
            )
        if not retry_projection and (
            digest(before) != expected_base
            or pinned_path.digest != expected_base
            or local != before
        ):
            raise ReviewConflict(
                "the expected authored base differs from the store or workspace"
            )
        revised = (
            _revised_document(
                request.story, path, before, replay.base_bytes, replay.final_bytes
            )
            if qualified is not None
            and request.project_authored
            and not retry_projection
            else None
        )
        level, collateral = _capsule(request, replay, originals, qualified)
        additional_reads = (path, *collateral)
        for name in originals:
            if classify_planning_path(f"{level.capsule}/{name}") != PlanningPath.DATA:
                raise ReviewError("review original is outside the capsule data paths")

        published = False

        def publish(operation: Operation, expected: Snapshot) -> OperationResult:
            nonlocal published
            if retry_projection:
                raise ReviewConflict(
                    "projection recovery requires the completed exact capsule"
                )
            if read_workspace(root, path) != before:
                raise ReviewConflict("the workspace changed before review publication")
            published = True
            return _publish(context, expected, path, revised, operation)

        level = replace(level, context=replace(context, publish=publish))
        if qualified is None:
            result = _cap(level, replay, originals, additional_reads)
        else:
            result = complete_review(
                level, qualified, additional_reads=additional_reads
            )
            if revised is not None and not published:
                # A previously completed capsule may still apply to this FUR.
                # The replayed originals and completion remain immutable.
                paths = (
                    *additional_reads,
                    story_event_path(request.story),
                    f"{level.capsule}/base.md",
                    *(f"{level.capsule}/{name}" for name in originals),
                    *(
                        f"{level.capsule}/timing/{name}.json"
                        for name in originals
                        if re.fullmatch(
                            r"(?:reviewer|author)-response-[0-9]+\.md", name
                        )
                    ),
                )
                pinned = context.backend.read(
                    context.snapshot, tuple(dict.fromkeys(paths))
                )
                reads = tuple(
                    ReadExpectation(path=key, digest=digest(data))
                    for key, data in pinned.items()
                )
                result = publish(
                    Operation(
                        operation_id=context.operation_id,
                        owner=context.owner,
                        policy_digest=context.policy_digest,
                        category=OperationCategory.NORMAL,
                        intent=FinalizationIntent(
                            kind="review.import",
                            version=1,
                            related_preconditions=reads,
                            payload=b"{}",
                        ),
                        change=RelatedWriteSet(read_set=reads),
                    ),
                    context.snapshot,
                )
        if result.command.local != LocalOutcome.COMPLETED:
            return result
        evidence = (*result.command.evidence, f"Review record {level.record_id}.")
        if not published:
            evidence = (
                *evidence,
                "Matching review evidence already exists in the local store.",
            )
        if revised is None and not retry_projection:
            evidence = (*evidence, "The authored document was preserved.")
        pending = result.command.pending
        shared = workspace.installation.store.planning_remote is not None
        projection = before if retry_projection else revised
        publication = (
            request.observed_publication
            if retry_projection
            else result.command.publication
        )
        if projection is not None and not _projection_admitted(publication, shared):
            pending = (*pending, "review-workspace-projection")
            evidence = (*evidence, "Workspace projection awaits verified publication.")
        elif projection is not None:
            try:
                _project(request, held, local, projection)
            except (OSError, ValueError, GitCommandError) as error:
                pending = (*pending, "review-workspace-projection")
                evidence = (
                    *evidence,
                    f"Review import committed. Workspace projection pending: {error}",
                )
        return replace(
            result,
            command=result.command.model_copy(
                update={
                    "evidence": evidence,
                    "pending": tuple(dict.fromkeys(pending)),
                    "publication": publication,
                }
            ),
        )
