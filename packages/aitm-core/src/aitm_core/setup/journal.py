"""Durable bootstrap proposals in the clone's common Git directory."""

from os import fsdecode, fsync, link
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictStr

from aitm_core.models.common import StoreAnchor
from aitm_core.models.config import BacklogIssuer, Name, Oid
from aitm_core.store.gate import _atomic_write
from aitm_core.store.objects import Repository


class ReplacementBasis(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    anchor: StoreAnchor
    revision: Oid


class BootstrapProposal(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["aitm.bootstrap/v1"] = "aitm.bootstrap/v1"
    operation_id: Annotated[StrictStr, Field(pattern=r"^[a-f0-9]{32}$")]
    anchor: StoreAnchor
    initial_tip: Oid
    code_repository: Name
    planning_repository: Name
    issuer: BacklogIssuer
    config: Name
    workflow: Name
    code_remote: Name | None = None
    activated_revision: Oid | None = None
    replacement: ReplacementBasis | None = None


def state_directory(repository: Repository) -> Path:
    common = repository._git("rev-parse", "--path-format=absolute", "--git-common-dir")
    return Path(fsdecode(common.removesuffix(b"\n"))) / "aitm"


def read_proposal(repository: Repository) -> BootstrapProposal | None:
    path = state_directory(repository) / "bootstrap.json"
    try:
        return BootstrapProposal.model_validate_json(path.read_bytes())
    except FileNotFoundError:
        return None


def record_proposal(repository: Repository, proposal: BootstrapProposal) -> None:
    _atomic_write(
        state_directory(repository) / "bootstrap.json", proposal.model_dump(mode="json")
    )


def prepare_file(path: Path, content: bytes) -> None:
    """Install complete bytes atomically and refuse to replace existing files."""
    with NamedTemporaryFile(dir=path.parent, delete=False) as temp:
        temporary = Path(temp.name)
        try:
            temp.write(content)
            temp.flush()
            fsync(temp.fileno())
            try:
                link(temporary, path)
            except FileExistsError:
                if (
                    path.is_symlink()
                    or not path.is_file()
                    or path.read_bytes() != content
                ):
                    raise ValueError(f"Existing {path.name} differs from the proposal.")
        finally:
            temporary.unlink()
