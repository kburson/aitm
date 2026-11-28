"""Bind public native review provenance to C24 replay and C57 acceptance."""

import json
import os
import re
from contextlib import ExitStack
from dataclasses import dataclass, replace
from hashlib import sha1, sha256
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError

from aitm_core.documents import DocumentError, _parse
from aitm_core.models.evidence import UtcText
from aitm_core.models.lifecycle import Commit, Positive, Text
from aitm_core.reviews.anchors import (
    PublicClaim,
    Role,
    SourceReference,
    SubmittedTurn,
    TimingAnchor,
    derive_anchor,
)
from aitm_core.reviews.policy import (
    ReviewPolicy,
    ValidatedReview,
    _decision,
    _TurnClaims,
    validate_review,
)
from aitm_core.reviews.portable import (
    FindingIds,
    Original,
    PortableResponse,
    RawDigest,
    ReconstructedReview,
    ReviewError,
    ReviewPath,
    _read_original,
    reconstruct_bundle,
)

_REVIEW_ID = Annotated[str, Field(pattern=r"^review-[a-z0-9-]+$")]
_PATH = TypeAdapter(ReviewPath)
_COMMIT = TypeAdapter(Commit)
_JSON_BLOCK = re.compile(rb"(?ms)^```json[ \t]*\r?\n(.*?)\r?\n^```[ \t]*\r?$")
_FRONTMATTER = re.compile(rb"(?m)^---\r?\n")


class _PublicRecord(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="ignore")


class _Agent(_PublicRecord):
    host: Text
    provider: Text
    model_id: Text
    session_fingerprint: RawDigest


class _Response(_PublicRecord):
    schema_version: Literal["ai-peer-review.response/v1"] = Field(alias="schema")
    review_id: _REVIEW_ID
    role: Role
    turn: Positive
    commit_mode: Literal["normal"]
    authority_assurance: Literal["unavailable"]
    artifact_path: ReviewPath
    artifact_commit: Commit
    artifact_blob: Commit
    artifact_digest: RawDigest
    agent: _Agent
    submitted_at: UtcText
    finding_ids: FindingIds = ()
    answered_finding_ids: FindingIds = ()


class _Artifact(_PublicRecord):
    path: ReviewPath
    blob: Commit
    digest: RawDigest


class _Revision(_Artifact):
    turn: Annotated[int, Field(ge=0)]
    commit: Commit


class _Reference(_PublicRecord):
    path: ReviewPath
    digest: RawDigest


class _Turn(_PublicRecord):
    turn: Positive
    decision: Literal["accepted", "revisions-requested"]
    finding_ids: FindingIds
    reviewer_response: _Reference
    author_response: _Reference | None
    artifact: _Artifact | None
    commit: Commit | None


class _Runtime(_PublicRecord):
    classification: Literal["SAR", "SPR", "XPR"]


class _Manifest(_PublicRecord):
    schema_version: Literal["ai-peer-review.manifest/v1"] = Field(alias="schema")
    review_id: _REVIEW_ID
    status: Literal["accepted"]
    commit_mode: Literal["normal"]
    acceptance_basis: Literal["reviewer-consensus"]
    authority_assurance: Literal["unavailable"]
    artifact_path: ReviewPath
    startup_commit: Commit
    final_commit: Commit
    runtime: _Runtime
    artifact_history: list[_Revision]
    claims: list[PublicClaim] = Field(default_factory=list)
    turns: Annotated[list[_Turn], Field(min_length=1)]


@dataclass(frozen=True, slots=True)
class NativeTurn:
    response: SubmittedTurn
    anchor: TimingAnchor
    provider: str
    model_id: str
    input_commit: str
    input_blob: str
    input_digest: str
    finding_ids: tuple[str, ...]
    answered_finding_ids: tuple[str, ...]

    @property
    def source_digest(self) -> str:
        return self.response.source.digest


@dataclass(frozen=True, slots=True)
class PortableFacts:
    review_id: str
    classification: str
    manifest: SourceReference
    revisions: tuple[_Revision, ...]
    turns: tuple[NativeTurn, ...]
    finalization_commit: str | None = None

    @property
    def revision_commit(self) -> str:
        return self.revisions[-1].commit


@dataclass(frozen=True, slots=True)
class ValidatedBundle(ValidatedReview):
    native: PortableFacts | None = None


def _strict_json(pairs):
    values = {}
    for key, value in pairs:
        if key in values:
            raise ReviewError(f"duplicate native manifest field {key}")
        values[key] = value
    return values


def _manifest(original: Original) -> _Manifest:
    blocks = _JSON_BLOCK.findall(original.raw)
    if len(blocks) != 1:
        raise ReviewError("native manifest requires one public JSON block")
    try:
        manifest = _Manifest.model_validate(
            json.loads(blocks[0], object_pairs_hook=_strict_json),
        )
    except (ValidationError, ValueError) as error:
        raise ReviewError("invalid or unaccepted native manifest") from error
    if not original.name.endswith(f"{manifest.review_id}-review-manifest.md"):
        raise ReviewError("native manifest filename conflicts with the review ID")
    return manifest


def _native_response(
    original: Original, reference: _Reference, decision: str | None
) -> _Response:
    if original.raw_digest != reference.digest:
        raise ReviewError(f"native response hash mismatch: {original.name}")
    fence = _FRONTMATTER.search(original.raw)
    if fence is None:
        raise ReviewError(f"missing native protected frontmatter: {original.name}")
    try:
        document = _parse(original.raw[fence.start() :])
        response = _Response.model_validate(document.header)
        if decision is not None and _decision(document, _TurnClaims()) != decision:
            raise ReviewError(
                "native reviewer response disagrees with the manifest decision"
            )
        return response
    except (DocumentError, ValidationError) as error:
        raise ReviewError(
            f"invalid or unsubmitted native response: {original.name}"
        ) from error


def _source(originals: tuple[Original, ...], reference: _Reference) -> Original:
    matches = tuple(
        item
        for item in originals
        if reference.path == item.name or reference.path.endswith("/" + item.name)
    )
    if len(matches) != 1:
        raise ReviewError(f"missing or ambiguous native original: {reference.path}")
    return matches[0]


def map_native(originals: tuple[Original, ...]) -> PortableFacts:
    """Map a supported public native bundle; acceptance still requires byte replay."""
    try:
        for item in originals:
            _PATH.validate_python(item.name, strict=True)
    except ValidationError as error:
        raise ReviewError("unsafe native original path") from error
    if len({item.name for item in originals}) != len(originals):
        raise ReviewError("duplicate native original")
    manifests = tuple(
        item for item in originals if item.name.endswith("-review-manifest.md")
    )
    if len(manifests) != 1:
        raise ReviewError("expected exactly one native manifest")
    original = manifests[0]
    manifest = _manifest(original)
    source = SourceReference(original.name, original.raw_digest)
    history = tuple(manifest.artifact_history)
    if (
        len(history) != len(manifest.turns)
        or history[0].commit != manifest.startup_commit
        or history[-1].commit != manifest.final_commit
        or any(
            item.path != manifest.artifact_path or item.turn != i
            for i, item in enumerate(history)
        )
    ):
        raise ReviewError("native revision lineage conflicts with the manifest")
    mapped = []
    preceding = None
    for index, turn in enumerate(manifest.turns, 1):
        final = index == len(manifest.turns)
        if turn.turn != index or (turn.decision == "accepted") != final:
            raise ReviewError("native decisions do not establish ordered consensus")
        if final:
            if any(
                (turn.author_response, turn.artifact, turn.commit, turn.finding_ids)
            ):
                raise ReviewError(
                    "native consensus cannot contain an outgoing revision or findings"
                )
        else:
            outgoing = history[index]
            if (
                turn.author_response is None
                or turn.artifact
                != _Artifact(
                    path=outgoing.path, blob=outgoing.blob, digest=outgoing.digest
                )
                or turn.commit != outgoing.commit
            ):
                raise ReviewError(
                    "native outgoing artifact conflicts with revision lineage"
                )
        incoming = history[index - 1]
        for role, reference in (
            ("reviewer", turn.reviewer_response),
            ("author", turn.author_response),
        ):
            if reference is None:
                continue
            item = _source(originals, reference)
            response = _native_response(
                item, reference, turn.decision if role == "reviewer" else None
            )
            if (
                response.review_id != manifest.review_id
                or response.role != role
                or response.turn != index
                or response.artifact_path != incoming.path
                or response.artifact_commit != incoming.commit
                or response.artifact_blob != incoming.blob
                or response.artifact_digest != incoming.digest
            ):
                raise ReviewError(
                    "native response input disagrees with revision lineage"
                )
            if role == "reviewer" and (
                response.finding_ids != turn.finding_ids
                or response.answered_finding_ids
            ):
                raise ReviewError("native reviewer findings conflict with the manifest")
            if role == "author" and (
                response.finding_ids
                or set(response.answered_finding_ids) != set(turn.finding_ids)
                or len(response.answered_finding_ids) != len(turn.finding_ids)
            ):
                raise ReviewError(
                    "native author dispositions conflict with the manifest"
                )
            submitted = SubmittedTurn(
                index,
                response.role,
                response.agent.host,
                response.agent.session_fingerprint,
                response.submitted_at,
                SourceReference(item.name, item.raw_digest),
            )
            anchor = derive_anchor(submitted, preceding, tuple(manifest.claims), source)
            mapped.append(
                NativeTurn(
                    submitted,
                    anchor,
                    response.agent.provider,
                    response.agent.model_id,
                    incoming.commit,
                    incoming.blob,
                    incoming.digest,
                    response.finding_ids,
                    response.answered_finding_ids,
                )
            )
            preceding = submitted
    return PortableFacts(
        manifest.review_id,
        manifest.runtime.classification,
        source,
        history,
        tuple(mapped),
    )


def _read_nested(root: Path, path: str) -> Original:
    components = _PATH.validate_python(path, strict=True).split("/")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    try:
        with ExitStack() as stack:
            fd = os.open(root, flags)
            stack.callback(os.close, fd)
            for component in components[:-1]:
                fd = os.open(component, flags, dir_fd=fd)
                stack.callback(os.close, fd)
            raw = _read_original(fd, components[-1], [])
            return Original(path, raw)
    except OSError as error:
        raise ReviewError(f"unsafe or missing native source: {path}") from error


def _git_blob_matches(content: bytes, expected: str) -> bool:
    prefix = f"blob {len(content)}\0".encode()
    digest = sha1(usedforsecurity=False) if len(expected) == 40 else sha256()
    digest.update(prefix)
    digest.update(content)
    return digest.hexdigest() == expected


def _bind_turn(
    response: PortableResponse,
    header: dict,
    native: NativeTurn,
    originals: dict[str, dict] | None = None,
) -> None:
    agent = response.agent
    if (
        agent is None
        or (agent.host, agent.provider, agent.model_id)
        != (native.response.host, native.provider, native.model_id)
        or header.get("session_identity_kind") != "native-fingerprint"
        or header.get(f"{response.role}_session") != native.response.fingerprint
        or header.get("native_source") != native.response.source.path
        or header.get("native_source_digest") != native.source_digest
        or response.finding_ids != native.finding_ids
        or response.answered_finding_ids != native.answered_finding_ids
        or response.submitted_at != native.response.submitted_at
    ):
        raise ReviewError("portable response disagrees with its native provenance")
    if response.start_basis is None:
        return
    anchor = native.anchor
    if response.start_basis != anchor.basis or response.started_at != anchor.started_at:
        raise ReviewError("portable timing contradicts its native anchor")
    stated_hash = header.get("start_source_digest")
    if anchor.source is None:
        matches = response.start_source is None and stated_hash is None
    elif anchor.basis == "claim":
        expected_source = f"{anchor.source.path}#claim-{anchor.claim_id}"
        matches = response.start_source == expected_source and stated_hash in (
            None,
            anchor.source.digest,
        )
    else:
        role = "reviewer" if response.role == "author" else "author"
        index = response.round if response.role == "author" else response.round - 1
        alias = f"{role}-response-{index}.md"
        predecessor = originals.get(alias) if originals is not None else None
        # Legacy aliases are read through their retained native source identity.
        matches = (
            response.start_source == anchor.source.path
            and stated_hash == anchor.source.digest
        ) or (
            response.start_source == alias
            and predecessor is not None
            and predecessor.get("native_source") == anchor.source.path
            and predecessor.get("native_source_digest") == anchor.source.digest
            and stated_hash in (None, anchor.source.digest)
        )
    if not matches:
        raise ReviewError("portable start source disagrees with its native anchor")


def _bind_bundle(
    root: Path, record: ReconstructedReview, header: dict
) -> tuple[ReconstructedReview, PortableFacts]:
    originals = {item.name: item for item in record.originals}
    turns = []
    for item in record.rounds:
        for response in (item.reviewer, item.author):
            name = f"{response.role}-response-{response.round}.md"
            turns.append((response, _parse(originals[name].raw).header))
    first = next(
        (value.get("native_source") for _, value in turns if "native_source" in value),
        None,
    )
    if not isinstance(first, str):
        raise ReviewError("native provenance requires retained response references")
    first = _PATH.validate_python(first, strict=True)
    review_id = TypeAdapter(_REVIEW_ID).validate_python(
        header.get("native_review_id"), strict=True
    )
    path = str(Path(first).with_name(f"{review_id}-review-manifest.md"))
    manifest = _read_nested(root, path)
    if header.get("native_manifest_digest", manifest.raw_digest) != manifest.raw_digest:
        raise ReviewError("native manifest hash mismatch")
    native_originals = {path: manifest}
    for _, value in turns:
        if "native_source" in value:
            source = _PATH.validate_python(value["native_source"], strict=True)
            if source in native_originals:
                raise ReviewError("ambiguous native response reference")
            native_originals[source] = _read_nested(root, source)
    facts = map_native(tuple(native_originals.values()))
    finalization = header.get("native_finalization_commit")
    if finalization is not None:
        finalization = _COMMIT.validate_python(finalization, strict=True)
    if (
        facts.review_id != review_id
        or facts.classification.lower() != record.manifest.level
        or facts.revision_commit != header.get("native_revision_commit")
        or finalization == facts.revision_commit
        or len(facts.revisions) != len(record.rounds)
        or facts.revisions[0].commit != record.manifest.artifact_base_commit
        or facts.revisions[-1].digest != record.manifest.final_digest
    ):
        raise ReviewError("portable manifest disagrees with native revision provenance")
    native_turns = {
        (turn.response.round, turn.response.role): turn for turn in facts.turns
    }
    headers = {
        f"{response.role}-response-{response.round}.md": value
        for response, value in turns
    }
    for response, value in turns:
        index = response.round
        native = native_turns.get((index, response.role))
        incoming = facts.revisions[index - 1]
        if native is not None:
            _bind_turn(response, value, native, headers)
        elif (
            index != len(record.rounds)
            or response.role != "author"
            or "native_source" in value
        ):
            raise ReviewError("missing native turn lineage")
        if response.role == "reviewer":
            data = record.rounds[index - 1].input_bytes
            if (
                incoming.path != record.manifest.artifact_path
                or incoming.digest != response.artifact_digest
                or not _git_blob_matches(data, incoming.blob)
            ):
                raise ReviewError("native Git blob disagrees with replayed input bytes")
    return replace(
        record, originals=record.originals + tuple(native_originals.values())
    ), replace(
        facts,
        finalization_commit=finalization,
    )


def validate_bundle(folder: Path | str, policy: ReviewPolicy) -> ValidatedBundle:
    """Validate portable evidence and any claimed native origin without mutating originals."""
    root = Path(folder)
    record = reconstruct_bundle(root)
    try:
        manifest = next(
            item for item in record.originals if item.name == "review-manifest.md"
        )
        claims = _parse(manifest.raw).header
        native = None
        if "native_review_id" in claims or claims.get("native_status") is not None:
            record, native = _bind_bundle(root, record, claims)
        validated = validate_review(record, policy)
    except (DocumentError, ValidationError) as error:
        raise ReviewError("invalid native source or timing provenance") from error
    return ValidatedBundle(
        validated.record, validated.level, validated.assurance, native
    )
