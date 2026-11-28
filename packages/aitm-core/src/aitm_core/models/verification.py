"""Immutable identities shared by capture, preparation and verification."""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Literal, Self

import rfc8785
from pydantic import Field, model_validator

from aitm_core.models.attempts import (
    AttemptFact,
    ExecutionCandidate,
    Positive,
    SourceSnapshot,
    Text,
)
from aitm_core.models.events import DIGEST
from aitm_core.models.lifecycle import RepositoryPath


class CapturedInput(AttemptFact):
    path: RepositoryPath
    origin: Literal["tracked", "extra"]
    digest: DIGEST
    executable: bool


class CaptureManifest(AttemptFact):
    schema_version: Literal["aitm.capture-manifest/v1"] = Field(
        default="aitm.capture-manifest/v1", alias="schema"
    )
    authority_store: Text
    story: Positive
    attempt: Text
    binding: Text
    generation: Positive
    branch: Text
    source: SourceSnapshot
    policy: SourceSnapshot
    policy_digest: DIGEST
    declarations: tuple[Text, ...]
    output_roots: tuple[RepositoryPath, ...]
    entries: tuple[CapturedInput, ...]

    @model_validator(mode="after")
    def unique_ordered_inputs(self) -> Self:
        paths = tuple(entry.path for entry in self.entries)
        if paths != tuple(sorted(set(paths))):
            raise ValueError("Captured paths must be unique and sorted.")
        return self

    @property
    def content(self) -> bytes:
        return rfc8785.dumps(self.model_dump(mode="json", by_alias=True))

    @property
    def digest(self) -> str:
        return sha256(self.content).hexdigest()


@dataclass(frozen=True, slots=True)
class CapturedInputs:
    directory: Path
    manifest: CaptureManifest

    @property
    def source_directory(self) -> Path:
        return self.directory / "source"

    @property
    def candidate(self) -> ExecutionCandidate:
        return ExecutionCandidate(
            source=self.manifest.source, capture_manifest=self.manifest.digest
        )
