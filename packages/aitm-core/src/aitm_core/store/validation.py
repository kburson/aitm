"""Validate planning history against the independently supplied store anchor."""

import json
import re
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from pathlib import PurePosixPath
from typing import Protocol

from pydantic import JsonValue

from aitm_core.events import UnavailableReducer, core_reducers, fold
from aitm_core.models.common import CommandResult, LocalOutcome, StoreAnchor
from aitm_core.models.operations import WriteAuthorization, repository_path, story_scope
from aitm_core.store.backend import Snapshot
from aitm_core.store.objects import GitCommandError, Repository

_ROOT_MARKER = b"aitm-planning-root: v1"
_ALLOWED_DATA = frozenset(
    {
        ".csv",
        ".diff",
        ".jpeg",
        ".jpg",
        ".json",
        ".jsonl",
        ".md",
        ".patch",
        ".pdf",
        ".png",
        ".toml",
        ".tsv",
        ".txt",
        ".yaml",
        ".yml",
    }
)
_MONTH = re.compile(r"[0-9]{4}-(?:0[1-9]|1[0-2])")
_SCHEMA = re.compile(r"aitm\.[a-z0-9.-]+/v1")
_EXTENSION_DIRECTORY = re.compile(r"[a-z][a-z0-9-]*")
CORE_ROOT_NAMES = frozenset(
    {"README.md", "store.json", "operations", "repairs", "ideas", "drafts"}
)
CORE_STORY_NAMES = frozenset(
    {
        "description.md",
        "draft.md",
        "story.md",
        "events.jsonl",
        "attachments",
        "design",
        "evidence",
        "plan",
        "retro",
        "operations",
    }
)


class PlanningPath(StrEnum):
    DATA = "data"
    EXTENSION_DATA = "extension-data"
    STORE = "store"
    OPERATION = "operation"
    REPAIR = "repair"
    EVENTS = "events"


@dataclass(frozen=True, slots=True)
class ValidationReport:
    outcome: LocalOutcome
    tip: str
    reason: str | None = None
    valid_prefix: str | None = None
    first_invalid: str | None = None


@dataclass(frozen=True, slots=True)
class DiagnosedHistory:
    valid_prefix: Snapshot
    first_invalid: str
    bad_tip: Snapshot
    reason: str


class ForwardRepairVerifier(Protocol):
    def __call__(
        self,
        anchor: StoreAnchor,
        diagnosed_history: DiagnosedHistory,
        candidate: Snapshot,
    ) -> ValidationReport: ...


@dataclass(frozen=True, slots=True)
class _Entry:
    mode: str
    kind: str
    oid: str


def classify_planning_path(path: str) -> PlanningPath:
    normalized = PurePosixPath(repository_path(path))
    parts = normalized.parts
    suffix = normalized.suffix.lower()
    if parts[0] != ".aitm" or any(part.casefold() == ".git" for part in parts):
        raise ValueError(f"outside planning data paths: {path}")
    if parts == (".aitm", "README.md"):
        return PlanningPath.DATA
    if parts == (".aitm", "store.json"):
        return PlanningPath.STORE
    if len(parts) == 3 and suffix == ".json":
        if parts[1] == "operations":
            return PlanningPath.OPERATION
        if parts[1] == "repairs":
            return PlanningPath.REPAIR
    if story_scope(path) is not None:
        tail = parts[4:]
        if tail == ("events.jsonl",):
            return PlanningPath.EVENTS
        if len(tail) == 1 and tail[0] in {"description.md", "draft.md", "story.md"}:
            return PlanningPath.DATA
        if len(tail) >= 2 and suffix in _ALLOWED_DATA:
            if tail[0] in {"attachments", "design", "evidence", "plan", "retro"}:
                return PlanningPath.DATA
            if tail[0] == "operations" and suffix == ".json":
                return PlanningPath.OPERATION
            if tail[0] not in CORE_STORY_NAMES | {
                "core"
            } and _EXTENSION_DIRECTORY.fullmatch(tail[0]):
                return PlanningPath.EXTENSION_DATA
    if len(parts) >= 4 and suffix in _ALLOWED_DATA:
        if (
            parts[1] == "ideas"
            and _MONTH.fullmatch(parts[2])
            and len(parts) == 4
            and suffix == ".md"
        ):
            return PlanningPath.DATA
        if parts[1] == "drafts":
            if parts[2] == "discarded" and len(parts) == 4 and suffix == ".json":
                return PlanningPath.DATA
            if _MONTH.fullmatch(parts[2]) and len(parts) >= 5:
                if parts[4:] == ("draft.md",) or (
                    len(parts) >= 6 and parts[4] == "attachments"
                ):
                    return PlanningPath.DATA
    if (
        len(parts) >= 3
        and suffix in _ALLOWED_DATA
        and parts[1] not in CORE_ROOT_NAMES | {"core", "stories"}
        and _EXTENSION_DIRECTORY.fullmatch(parts[1])
    ):
        return PlanningPath.EXTENSION_DATA
    raise ValueError(f"unauthorized planning data path: {path}")


def _entries(repository: Repository, snapshot: Snapshot) -> dict[str, _Entry]:
    raw = repository._git("ls-tree", "-r", "-z", "--full-tree", snapshot.tree)
    entries = {}
    for line in raw.split(b"\0"):
        if line:
            header, name = line.split(b"\t", 1)
            mode, kind, oid = header.decode("ascii").split()
            path = name.decode("utf-8")
            if path in entries:
                raise ValueError(f"duplicate planning path: {path}")
            entries[path] = _Entry(mode, kind, oid)
    return entries


def _unique_fields(pairs: list[tuple[str, JsonValue]]) -> dict[str, JsonValue]:
    row = {}
    for name, value in pairs:
        if name in row:
            raise ValueError(f"duplicate planning field: {name}")
        row[name] = value
    return row


def _typed_json(data: bytes, path: str) -> dict[str, JsonValue]:
    row = json.loads(data, object_pairs_hook=_unique_fields)
    if not isinstance(row, dict):
        raise ValueError(f"expected a planning object in {path}")
    version = row.get("schema", row.get("schema_version"))
    if not isinstance(version, str) or _SCHEMA.fullmatch(version) is None:
        raise ValueError(f"unsupported planning schema in {path}")
    return row


def _check_tree(
    repository: Repository,
    anchor: StoreAnchor,
    before: Snapshot,
    candidate: Snapshot,
    old: dict[str, _Entry],
    new: dict[str, _Entry],
) -> None:
    typed = {}
    extension_changes = set()
    extension_authorizations = set()
    for path, entry in new.items():
        if entry.mode != "100644" or entry.kind != "blob":
            raise ValueError(
                f"planning data requires a regular non-executable blob: {path}"
            )
        role = classify_planning_path(path)
        if old.get(path) != entry:
            if role is PlanningPath.EXTENSION_DATA:
                extension_changes.add(path)
            elif role is not PlanningPath.DATA:
                typed[path] = role

    retained = {}
    for path, entry in old.items():
        if new.get(path) == entry:
            continue
        role = classify_planning_path(path)
        if role is PlanningPath.EXTENSION_DATA:
            extension_changes.add(path)
        if role in {PlanningPath.OPERATION, PlanningPath.REPAIR}:
            raise ValueError(f"retained planning record changed: {path}")
        if role == PlanningPath.EVENTS:
            if path not in new:
                raise ValueError(f"event stream removed: {path}")
            retained[path] = role

    blobs = repository.read_blobs(candidate.tree, tuple(typed))
    prefix = repository.read_blobs(before.tree, tuple(retained))
    for path, role in typed.items():
        content = blobs[path]
        if content is None:
            raise ValueError(f"missing planning blob: {path}")
        if role == PlanningPath.EVENTS:
            previous = prefix.get(path)
            if previous:
                boundary = previous if previous.endswith(b"\n") else previous + b"\n"
                if not content.startswith(boundary):
                    raise ValueError(f"event stream is not append-only: {path}")
            state = fold(content.splitlines(keepends=True), core_reducers())
            if state.story_id not in (None, story_scope(path)):
                raise ValueError(f"event stream belongs to a different story: {path}")
            continue
        row = _typed_json(content, path)
        if role == PlanningPath.STORE:
            if (
                row.get("schema") != "aitm.store/v1"
                or row.get("store_uuid") != anchor.store_uuid
            ):
                raise ValueError(
                    f"planning store identity or schema disagrees with its anchor: {path}"
                )
        if role == PlanningPath.OPERATION:
            if row.get("schema_version") != "aitm.operation-record/v1":
                raise ValueError(f"unsupported transaction record: {path}")
            command = CommandResult.model_validate(row.get("command"))
            identity = sha256(command.operation_id.encode("utf-8")).hexdigest()
            request = row.get("request_digest")
            story = story_scope(path)
            declared_story = row.get("story")
            if story is None:
                if declared_story is not None:
                    raise ValueError(
                        f"story record requires its owning story path: {path}"
                    )
                directory = ".aitm/operations"
            else:
                if type(declared_story) is not int or declared_story != story:
                    raise ValueError(
                        f"operation record does not match its owning story: {path}"
                    )
                directory = f".aitm/stories/{story // 100:03d}/{story}/operations"
            if (
                path != f"{directory}/{identity}.json"
                or row.get("base") != before.revision
                or not isinstance(request, str)
                or re.fullmatch(r"[0-9a-f]{64}", request) is None
            ):
                raise ValueError(f"unbound transaction record: {path}")
            authority = row.get("authorization")
            if isinstance(authority, dict) and (
                "extension" in authority or "owned_paths" in authority
            ):
                receipt = WriteAuthorization.model_validate_json(json.dumps(authority))
                if (
                    receipt.extension is None
                    or command.local is not LocalOutcome.COMPLETED
                ):
                    raise ValueError(f"invalid extension operation receipt: {path}")
                for owned in receipt.owned_paths:
                    if (
                        classify_planning_path(owned) is not PlanningPath.EXTENSION_DATA
                        or owned in extension_authorizations
                    ):
                        raise ValueError(f"ambiguous extension write receipt: {owned}")
                    extension_authorizations.add(owned)
    unproven = extension_changes - extension_authorizations
    if unproven:
        raise ValueError(
            f"extension data lacks a matching operation receipt: {min(unproven)}"
        )


def _commit_parents(repository: Repository, revision: str) -> tuple[str, ...]:
    raw = repository._git("cat-file", "commit", repository._oid(revision))
    headers = raw.partition(b"\n\n")[0]
    return tuple(
        line.removeprefix(b"parent ").decode("ascii")
        for line in headers.splitlines()
        if line.startswith(b"parent ")
    )


def _walk(
    anchor: StoreAnchor,
    tip: str,
    repository: Repository,
    forward_repair_verifier: ForwardRepairVerifier | None,
) -> ValidationReport:
    if anchor.planning_ref != repository.ref or not anchor.code_default_ref.startswith(
        "refs/"
    ):
        raise ValueError(
            "anchor does not identify the configured planning and code refs"
        )
    revision = repository._oid(tip)
    if repository._git("rev-parse", "--is-shallow-repository").strip() == b"true":
        return ValidationReport(
            LocalOutcome.UNAVAILABLE, revision, "complete-planning-history-required"
        )
    anchor_root = repository._oid(anchor.root_commit)
    code = (
        repository._git(
            "rev-parse", "--verify", f"{anchor.code_default_ref}^{{commit}}"
        )
        .strip()
        .decode("ascii")
    )
    shared = repository._run("merge-base", revision, code)
    if shared.returncode == 0:
        return ValidationReport(LocalOutcome.INTEGRITY_ERROR, revision, "code-ancestry")
    if shared.returncode != 1:
        raise GitCommandError("merge-base", shared.stderr)

    history = [
        row.split()
        for row in repository._git(
            "rev-list", "--reverse", "--topo-order", "--parents", revision
        )
        .decode("ascii")
        .splitlines()
    ]
    if (
        not history
        or history[0] != [anchor_root]
        or _commit_parents(repository, anchor_root)
    ):
        return ValidationReport(
            LocalOutcome.INTEGRITY_ERROR, revision, "planning-root-mismatch"
        )
    root = repository.read_tree(anchor_root)
    if _entries(repository, root):
        return ValidationReport(
            LocalOutcome.INTEGRITY_ERROR, revision, "nonempty-planning-root"
        )
    message = repository._git("show", "-s", "--format=%B", root.revision)
    if _ROOT_MARKER not in message.splitlines():
        return ValidationReport(
            LocalOutcome.INTEGRITY_ERROR, revision, "planning-root-marker-missing"
        )

    previous = valid = root
    last_tree: dict[str, _Entry] = {}
    valid_tree: dict[str, _Entry] = {}
    first_invalid = reason = None
    for commit, *parents in history[1:]:
        if parents != [previous.revision] or _commit_parents(repository, commit) != (
            previous.revision,
        ):
            return ValidationReport(
                LocalOutcome.INTEGRITY_ERROR,
                revision,
                "planning-history-must-be-linear",
                valid.revision,
                commit,
            )
        candidate = repository.read_tree(commit)
        tree = _entries(repository, candidate)
        added_repair = any(
            path.startswith(".aitm/repairs/") and last_tree.get(path) != entry
            for path, entry in tree.items()
        )
        if first_invalid is not None:
            if added_repair:
                if not callable(forward_repair_verifier):
                    return ValidationReport(
                        LocalOutcome.UNAVAILABLE,
                        revision,
                        "forward-repair-verifier-unavailable",
                        valid.revision,
                        first_invalid,
                    )
                diagnosis = DiagnosedHistory(
                    valid, first_invalid, previous, reason or "invalid-planning-data"
                )
                proof = forward_repair_verifier(anchor, diagnosis, candidate)
                if (
                    not isinstance(proof, ValidationReport)
                    or proof.outcome != LocalOutcome.COMPLETED
                    or proof.tip != commit
                ):
                    return ValidationReport(
                        LocalOutcome.INTEGRITY_ERROR,
                        revision,
                        "forward-repair-proof-refused",
                        valid.revision,
                        first_invalid,
                    )
                _check_tree(repository, anchor, valid, candidate, valid_tree, tree)
                first_invalid = reason = None
                valid, valid_tree = candidate, tree
        else:
            try:
                if added_repair:
                    raise ValueError(
                        "forward repair requires a diagnosed invalid history"
                    )
                _check_tree(repository, anchor, valid, candidate, valid_tree, tree)
            except ValueError as error:
                first_invalid, reason = commit, str(error)
            else:
                valid, valid_tree = candidate, tree
        previous, last_tree = candidate, tree

    if first_invalid is not None:
        return ValidationReport(
            LocalOutcome.INTEGRITY_ERROR,
            revision,
            reason,
            valid.revision,
            first_invalid,
        )
    return ValidationReport(
        LocalOutcome.COMPLETED, revision, valid_prefix=valid.revision
    )


def validate_history(
    anchor: StoreAnchor,
    tip: str,
    *,
    repository: Repository,
    forward_repair_verifier: ForwardRepairVerifier | None = None,
) -> ValidationReport:
    """Read and validate without moving refs, checking out trees or editing the index."""
    try:
        return _walk(anchor, tip, repository, forward_repair_verifier)
    except (GitCommandError, OSError, UnavailableReducer) as error:
        return ValidationReport(LocalOutcome.UNAVAILABLE, tip, str(error))
    except ValueError as error:
        return ValidationReport(LocalOutcome.INTEGRITY_ERROR, tip, str(error))
