"""Read portable v0 evidence and reconstruct its exact document revisions."""

import os
import re
import stat
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, ValidationError

from aitm_core.documents import DocumentError, _parse
from aitm_core.models.evidence import ReviewLevel, UtcText
from aitm_core.models.lifecycle import Commit, Positive, RepositoryPath, Text
from aitm_core.reviews.patches import apply_patch, validate_patch


class ReviewError(ValueError):
    """A portable record is incomplete, unsafe, or inconsistent."""


def _portable_path(value: str) -> str:
    if any(
        part.casefold() in {"", ".", "..", ".git"} for part in value.split("/")
    ) or any(ord(char) < 32 or ord(char) == 127 or char in '\\":' for char in value):
        raise ValueError("expected a portable repository-relative path")
    return value


ReviewPath = Annotated[RepositoryPath, AfterValidator(_portable_path)]
RawDigest = Annotated[str, Field(pattern=r"^sha256:[0-9a-f]{64}$")]
FindingIds = Annotated[tuple[Text, ...], Field(strict=False)]
_PATCH_NAME = re.compile(r"patch-([0-9]+)\.diff")
_RESPONSE_NAME = re.compile(r"(?:reviewer|author)-response-([0-9]+)\.md")


class PortableIdentity(BaseModel):
    # Optional historical extensions are retained verbatim in Original, for
    # later topology and native-lineage consumers.
    model_config = ConfigDict(strict=True, frozen=True, extra="ignore")

    level: ReviewLevel
    story: Positive
    artifact_path: ReviewPath
    artifact_base_commit: Commit | None = None


class PortableManifest(PortableIdentity):
    schema_version: Literal["aitm.review-manifest/v0"] = Field(alias="schema")
    base_digest: RawDigest
    final_digest: RawDigest
    rounds: Positive
    outcome: Text
    verified_at: UtcText | None = None


class PortableAgent(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="ignore")

    host: Text
    provider: Text
    model_id: Text
    effort: Text


class PortableResponse(PortableIdentity):
    schema_version: Literal["aitm.review-response/v0"] = Field(alias="schema")
    role: Literal["reviewer", "author"]
    round: Positive
    artifact_digest: RawDigest
    patch: ReviewPath | None = None
    agent: PortableAgent | None = None
    reviewer_session: Text | None = None
    author_session: Text | None = None
    started_at: UtcText | None = None
    submitted_at: UtcText | None = None
    start_basis: Text | None = None
    start_source: Text | None = None
    finding_ids: FindingIds = ()
    answered_finding_ids: FindingIds = ()


def _digest(raw: bytes) -> str:
    return "sha256:" + sha256(raw).hexdigest()


@dataclass(frozen=True, slots=True)
class Original:
    name: str
    raw: bytes

    @property
    def raw_digest(self) -> str:
        return _digest(self.raw)


@dataclass(frozen=True, slots=True)
class ReconstructedRound:
    reviewer: PortableResponse
    author: PortableResponse
    input_bytes: bytes
    output_bytes: bytes


@dataclass(frozen=True, slots=True)
class ReconstructedReview:
    manifest: PortableManifest
    base_bytes: bytes
    final_bytes: bytes
    rounds: tuple[ReconstructedRound, ...]
    originals: tuple[Original, ...]


def _read_original(directory: int, name: str, originals: list[Original]) -> bytes:
    try:
        fd = os.open(
            name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory
        )
        with os.fdopen(fd, "rb") as stream:
            mode = os.fstat(stream.fileno()).st_mode
            if not stat.S_ISREG(mode) or mode & 0o111:
                raise ReviewError(f"{name} must be a regular nonexecutable file")
            raw = stream.read()
    except OSError as error:
        raise ReviewError(f"cannot read review original {name}") from error
    originals.append(Original(name, raw))
    return raw


def _check_inventory(directory: int, rounds: int) -> None:
    for name in sorted(os.listdir(directory)):
        if match := _PATCH_NAME.fullmatch(name):
            index = int(match[1])
            if index > rounds or match[1] != f"{index:03d}":
                raise ReviewError(f"undeclared numbered patch: {name}")
        elif match := _RESPONSE_NAME.fullmatch(name):
            index = int(match[1])
            if not 1 <= index <= rounds or match[1] != str(index):
                raise ReviewError(f"undeclared numbered response: {name}")


def _parse_record[T: PortableIdentity](raw: bytes, model: type[T], name: str) -> T:
    try:
        raw.decode("utf-8")
        return model.model_validate(_parse(raw).header)
    except (UnicodeError, DocumentError, ValidationError) as error:
        raise ReviewError(f"invalid portable record {name}: {error}") from error


def _response(
    directory: int,
    manifest: PortableManifest,
    role: Literal["reviewer", "author"],
    index: int,
    originals: list[Original],
) -> PortableResponse:
    name = f"{role}-response-{index}.md"
    response = _parse_record(
        _read_original(directory, name, originals), PortableResponse, name
    )
    if (
        response.story != manifest.story
        or response.level != manifest.level
        or response.artifact_path != manifest.artifact_path
        or response.artifact_base_commit != manifest.artifact_base_commit
        or response.role != role
        or response.round != index
    ):
        raise ReviewError(f"{name} conflicts with the bundle identity")
    return response


def _replay(
    workspace: Path, artifact: str, index: int, patch: bytes, previous: bytes
) -> bytes:
    try:
        validate_patch(patch, artifact, create=index == 0)
        if not patch:
            return previous
        apply_patch(workspace, artifact, patch)
        return (workspace / artifact).read_bytes()
    except (OSError, ValueError) as error:
        raise ReviewError(f"cannot replay patch-{index:03d}.diff: {error}") from error


def _match_digest(raw: bytes, expected: str, label: str) -> None:
    if _digest(raw) != expected:
        raise ReviewError(f"{label} digest mismatch")


def reconstruct_bundle(folder: Path | str) -> ReconstructedReview:
    """Verify a single portable review's byte chain and retain its originals."""
    try:
        directory = os.open(Path(folder), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError as error:
        raise ReviewError("cannot open portable review directory") from error

    originals: list[Original] = []
    rounds: list[ReconstructedRound] = []
    try:
        name = "review-manifest.md"
        manifest = _parse_record(
            _read_original(directory, name, originals), PortableManifest, name
        )
        _check_inventory(directory, manifest.rounds)
        artifact = manifest.artifact_path
        with TemporaryDirectory(prefix="aitm-review-") as scratch:
            workspace = Path(scratch).resolve()
            base_patch = _read_original(directory, "patch-000.diff", originals)
            base = _replay(workspace, artifact, 0, base_patch, b"")
            _match_digest(base, manifest.base_digest, "base")
            current = base
            for index in range(1, manifest.rounds + 1):
                reviewer = _response(directory, manifest, "reviewer", index, originals)
                _match_digest(
                    current, reviewer.artifact_digest, f"round {index} reviewer input"
                )
                author = _response(directory, manifest, "author", index, originals)
                name = f"patch-{index:03d}.diff"
                if author.patch != name or reviewer.patch is not None:
                    raise ReviewError(f"round {index} has an invalid patch reference")
                patch = _read_original(directory, name, originals)
                output = _replay(workspace, artifact, index, patch, current)
                _match_digest(
                    output, author.artifact_digest, f"round {index} author output"
                )
                rounds.append(ReconstructedRound(reviewer, author, current, output))
                current = output
        _match_digest(current, manifest.final_digest, "final")
        return ReconstructedReview(
            manifest, base, current, tuple(rounds), tuple(originals)
        )
    finally:
        os.close(directory)
