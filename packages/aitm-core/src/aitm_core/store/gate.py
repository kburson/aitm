"""Serialize Core ref updates and check the literal target's checkout exclusion."""

import json
import os
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4

from aitm_core.models.common import LocalOutcome
from aitm_core.store.backend import Snapshot
from aitm_core.store.git_backend import ValidationRejected
from aitm_core.store.objects import GitCommandError, Repository
from aitm_core.store.validation import ValidationReport

COOPERATIVE_LIMIT = "The clone lock covers supported Core operations. External Git commands operate independently of it."


@dataclass(frozen=True, slots=True)
class RefIdentity:
    name: str

    def __post_init__(self) -> None:
        if not self.name.startswith("refs/"):
            raise ValueError("a fully qualified literal ref is required")


class RefMutationKind(StrEnum):
    PLANNING = "planning"
    DELIVERY = "delivery"


type HistoryCheck = Callable[[str], ValidationReport]
type DeliveryCheck = Callable[[Snapshot, Snapshot], None]


def _worktrees(repository: Repository, target: RefIdentity) -> tuple[str, ...]:
    raw = repository._git("worktree", "list", "--porcelain", "-z")
    branch = b"branch " + target.name.encode("utf-8")
    locations = []
    path = None
    for field in raw.split(b"\0"):
        if field.startswith(b"worktree "):
            path = os.fsdecode(field.removeprefix(b"worktree "))
        elif field == branch and path is not None:
            locations.append(path)
    return tuple(locations)


def _target_revision(repository: Repository, target: RefIdentity) -> str | None:
    observed = repository._run("rev-parse", "--quiet", "--verify", target.name)
    if observed.returncode == 1:
        return None
    if observed.returncode:
        raise GitCommandError("rev-parse", observed.stderr)
    return repository._oid(observed.stdout.strip().decode("ascii"))


def _receipt_path(state: Path, target: RefIdentity) -> Path:
    return (
        state
        / "ref-fences"
        / (sha256(target.name.encode("utf-8")).hexdigest() + ".json")
    )


def _atomic_write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(
        "w", dir=path.parent, encoding="utf-8", delete=False
    ) as temp:
        temporary = Path(temp.name)
        json.dump(value, temp, sort_keys=True)
        temp.write("\n")
        temp.flush()
        os.fsync(temp.fileno())
    os.replace(temporary, path)


class Gate:
    def __init__(
        self,
        repository: Repository,
        target: RefIdentity,
        purpose: RefMutationKind,
        state: Path,
        planning_validation: HistoryCheck | None,
        delivery_validation: DeliveryCheck | None,
    ) -> None:
        self.repository = repository
        self.target = target
        self.purpose = RefMutationKind(purpose)
        self.fence = _receipt_path(state, target)
        self.planning_validation = planning_validation
        self.delivery_validation = delivery_validation
        self.before: Snapshot | None = None
        self.candidate: Snapshot | None = None

    def assert_excluded(self) -> None:
        if self.fence.exists():
            raise ValidationRejected(
                f"{self.target.name} is fenced pending explicit checkout reconciliation. {COOPERATIVE_LIMIT}"
            )
        locations = _worktrees(self.repository, self.target)
        if locations:
            raise ValidationRejected(
                f"{self.target.name} is checked out. {COOPERATIVE_LIMIT}"
            )

    def __call__(self, before: Snapshot, candidate: Snapshot | None) -> None:
        self.before = before
        self.candidate = candidate
        if self.purpose == RefMutationKind.PLANNING:
            if self.planning_validation is None:
                raise ValidationRejected("configured planning validation is required")
            target = before if candidate is None else candidate
            report = self.planning_validation(target.revision)
            if (
                report.outcome != LocalOutcome.COMPLETED
                or report.tip != target.revision
            ):
                raise ValidationRejected(
                    report.reason or "planning history validation refused"
                )
        elif candidate is not None:
            if self.delivery_validation is None:
                raise ValidationRejected("delivery content validation is required")
            self.delivery_validation(before, candidate)
        self.assert_excluded()

    def postcheck(self) -> None:
        locations = _worktrees(self.repository, self.target)
        if not locations:
            return
        prefix = f"refs/aitm/recovery/checkout-{uuid4().hex}"
        old = self.before.revision if self.before else None
        new = _target_revision(self.repository, self.target)
        refs = {
            f"{prefix}/{label}": tip
            for label, tip in (("old", old), ("observed", new))
            if tip is not None
        }
        receipt = {
            "schema": "aitm.checkout-fence/v1",
            "ref": self.target.name,
            "old": old,
            "observed": new,
            "candidate": self.candidate.revision if self.candidate else None,
            "recovery_refs": list(refs),
            "worktrees": list(locations),
        }
        _atomic_write(self.fence, receipt)
        if refs:
            create = "".join(f"create {name} {rev}\n" for name, rev in refs.items())
            self.repository._git(
                "update-ref",
                "--stdin",
                data=f"start\n{create}prepare\ncommit\n".encode("ascii"),
            )
        raise ValidationRejected(
            f"An external checkout of {self.target.name} was observed. "
            f"Publication requires explicit checkout reconciliation. {COOPERATIVE_LIMIT}"
        )


@contextmanager
def ref_gate(
    repository: Repository,
    target_ref: RefIdentity,
    purpose: RefMutationKind,
    *,
    planning_validation: HistoryCheck | None = None,
    delivery_validation: DeliveryCheck | None = None,
) -> Iterator[Gate]:
    """Hold a clone-common lock across the caller's supported ref operation."""
    try:
        import fcntl
    except ImportError as error:
        raise ValidationRejected(
            "The clone lock is unavailable on this host."
        ) from error

    repository._git("check-ref-format", target_ref.name)
    common = repository._git("rev-parse", "--path-format=absolute", "--git-common-dir")
    state = Path(os.fsdecode(common.removesuffix(b"\n"))) / "aitm"
    state.mkdir(parents=True, exist_ok=True)
    with (state / "ref-mutation.lock").open("a+b") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        gate = Gate(
            repository,
            target_ref,
            purpose,
            state,
            planning_validation,
            delivery_validation,
        )
        gate.assert_excluded()
        observed = _target_revision(repository, target_ref)
        if observed is not None:
            gate.before = repository.read_tree(observed)
        try:
            yield gate
        finally:
            try:
                gate.postcheck()
            except GitCommandError as error:
                raise ValidationRejected(
                    f"Could not verify checkout exclusion. {COOPERATIVE_LIMIT}"
                ) from error
