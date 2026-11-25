"""Publish immutable, sanitized turn receipts to the approved planning ref."""

import os
import re
import subprocess
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path, PurePosixPath
from uuid import UUID, uuid4

_PLANNING = "refs/heads/planning"
_MAX_BLOB = 2 * 1024 * 1024
_MAX_PUSHES = 3
_GIT_TIMEOUT = 30
_RECEIPT_PATH = re.compile(
    rb"\.aitm/stories/([0-9]+)/([1-9][0-9]*)/attachments/effort/session/"
    rb"([a-f0-9]{64})-r[1-9][0-9]*\.json"
)


class PublicationHold(ValueError):
    """A receipt batch has not been verified on the approved remote."""


@dataclass(frozen=True, slots=True)
class PublicationEntry:
    story: int
    identity: str
    revision: int
    data: bytes

    @property
    def story_root(self) -> str:
        return f".aitm/stories/{self.story // 100:03d}/{self.story}"

    @property
    def path(self) -> str:
        return self._revision_path(self.revision)

    def _revision_path(self, revision: int) -> str:
        directory = f"{self.story_root}/attachments/effort/session"
        return f"{directory}/{self.identity}-r{revision}.json"


def _decode_receipt(data: bytes) -> dict:
    from .session import validate_public_receipt

    return validate_public_receipt(data)


def _git(
    repository: Path,
    *args: str,
    index: Path | None = None,
    data: bytes | None = None,
) -> subprocess.CompletedProcess:
    env = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    env.update(
        GIT_NO_REPLACE_OBJECTS="1",
        GIT_TERMINAL_PROMPT="0",
        GIT_ALLOW_PROTOCOL="file:https:ssh",
    )
    if index is not None:
        env["GIT_INDEX_FILE"] = str(index)
    command = ["git", "-C", str(repository), *args]
    try:
        return subprocess.run(
            command, env=env, input=data, capture_output=True, timeout=_GIT_TIMEOUT
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(command, 124, b"", b"")


def _read(
    repository: Path,
    *args: str,
    index: Path | None = None,
    data: bytes | None = None,
) -> bytes:
    result = _git(repository, *args, index=index, data=data)
    if result.returncode:
        # Git can report local paths or credentials in stderr.
        raise PublicationHold(f"Git {args[0]} failed during planning publication")
    return result.stdout


def _require_remote(repository: Path, remote_url: str) -> None:
    fetch = _read(repository, "remote", "get-url", "--all", "origin").splitlines()
    push = _read(
        repository, "remote", "get-url", "--push", "--all", "origin"
    ).splitlines()
    if not remote_url or fetch != [remote_url.encode()] or push != fetch:
        raise PublicationHold("Configured publication remote does not match origin")


def _validated_batch(
    project_id: UUID, receipts: Sequence[PublicationEntry]
) -> dict[str, PublicationEntry]:
    if type(project_id) is not UUID:
        raise PublicationHold("Expected a publication project UUID")
    entries = {}
    assignments = {}
    for entry in receipts:
        if (
            type(entry.story) is not int
            or entry.story < 1
            or type(entry.revision) is not int
            or not 1 <= entry.revision < 2**63
            or not isinstance(entry.identity, str)
            or not re.fullmatch("[a-f0-9]{64}", entry.identity)
            or type(entry.data) is not bytes
            or not 0 < len(entry.data) <= _MAX_BLOB
        ):
            raise PublicationHold("Invalid publication entry")
        payload = _decode_receipt(entry.data)
        if (
            payload["schema"] != "aitm.session-turn/v1"
            or payload["project"] != str(project_id)
            or payload["story"] != entry.story
            or payload["identity"] != entry.identity
            or payload["revision"] != entry.revision
        ):
            raise PublicationHold("Receipt scope does not match the publication entry")
        existing = entries.setdefault(entry.path, entry)
        if existing.data != entry.data:
            raise PublicationHold("Refused conflicting immutable receipts in one batch")
        if assignments.setdefault(entry.identity, entry.story) != entry.story:
            raise PublicationHold("A receipt identity is assigned to another story")
    return entries


class _PlanningTree:
    def __init__(self, repository: Path, tip: str) -> None:
        self.repository = repository
        self.tip = tip
        self.entries: dict[str, tuple[bytes, str] | None] = {}

    def entry(self, path: str) -> tuple[bytes, str] | None:
        if path not in self.entries:
            raw = _read(self.repository, "ls-tree", "-z", self.tip, "--", path)
            if raw:
                details, name = raw[:-1].split(b"\t", 1)
                mode, _, object_id = details.split(b" ")
                if name != path.encode():
                    raise PublicationHold("Unexpected name in planning tree")
                self.entries[path] = (mode, object_id.decode("ascii"))
            else:
                self.entries[path] = None
        return self.entries[path]

    def blob(self, object_id: str) -> bytes:
        size = int(_read(self.repository, "cat-file", "-s", object_id))
        if size > _MAX_BLOB:
            raise PublicationHold("Planning file exceeds the publication size limit")
        return _read(self.repository, "cat-file", "blob", object_id)

    def require_story(self, entry: PublicationEntry) -> None:
        story_file = self.entry(f"{entry.story_root}/story.md")
        if story_file is None or story_file[0] != b"100644":
            raise PublicationHold(
                "Planning story file is missing or has an unexpected mode"
            )
        lines = self.blob(story_file[1]).splitlines()
        if lines and lines[0] == b"---" and b"---" in lines[1:]:
            end = lines.index(b"---", 1)
            identifiers = [line for line in lines[1:end] if line.startswith(b"id:")]
            if (
                len(identifiers) == 1
                and identifiers[0][3:].strip() == str(entry.story).encode()
            ):
                return
        raise PublicationHold("Planning story does not match the receipt scope")

    def require_stable_assignments(self, entries: dict[str, PublicationEntry]) -> None:
        if not entries:
            return
        assignments = {
            item.identity.encode(): item.story_root.encode()
            for item in entries.values()
        }
        # Read names from the pinned planning tree only. No other stories' blobs are opened.
        paths = _read(
            self.repository,
            "ls-tree",
            "-rz",
            "--name-only",
            self.tip,
            "--",
            ".aitm/stories",
        )
        for path in paths.split(b"\0"):
            match = _RECEIPT_PATH.fullmatch(path)
            if match is None:
                continue
            bucket, story, identity = match.groups()
            assignment = assignments.get(identity)
            if assignment is not None and assignment != b"/".join(
                (b".aitm/stories", bucket, story)
            ):
                raise PublicationHold(
                    "A receipt identity is published under another story"
                )

    def require_predecessor(
        self, entry: PublicationEntry, entries: dict[str, PublicationEntry]
    ) -> None:
        if entry.revision == 1:
            return
        path = entry._revision_path(entry.revision - 1)
        candidate = entries.get(path)
        if candidate is not None:
            previous = candidate.data
        else:
            published = self.entry(path)
            if published is None or published[0] != b"100644":
                raise PublicationHold("Expected the exact public receipt predecessor")
            previous = self.blob(published[1])
        current_payload = _decode_receipt(entry.data)
        predecessor = _decode_receipt(previous)
        if (
            sha256(previous).hexdigest() != current_payload["previous_receipt_sha256"]
            or predecessor["revision"] != entry.revision - 1
            or any(
                predecessor[key] != current_payload[key]
                for key in (
                    "project",
                    "story",
                    "identity",
                    "attempt",
                    "provider",
                    "role",
                )
            )
        ):
            raise PublicationHold(
                "Public receipt predecessor does not match revision lineage"
            )

    def missing(self, entries: dict[str, PublicationEntry]) -> list[PublicationEntry]:
        self.require_stable_assignments(entries)
        missing = []
        checked_stories = set()
        for path, entry in entries.items():
            parents = reversed(PurePosixPath(path).parents)
            for parent in parents:
                if parent == PurePosixPath("."):
                    continue
                existing = self.entry(parent.as_posix())
                if existing is not None and existing[0] != b"040000":
                    raise PublicationHold(
                        "Publication requires normal planning tree directories"
                    )
            if entry.story not in checked_stories:
                self.require_story(entry)
                checked_stories.add(entry.story)
            self.require_predecessor(entry, entries)
            existing = self.entry(path)
            if existing is None:
                missing.append(entry)
            elif existing[0] != b"100644" or self.blob(existing[1]) != entry.data:
                raise PublicationHold("Refused conflicting immutable planning receipt")
        return missing


def _commit(
    repository: Path, index: Path, tip: str, entries: list[PublicationEntry]
) -> str:
    _read(repository, "read-tree", tip, index=index)
    updates = []
    for entry in entries:
        object_id = _read(repository, "hash-object", "-w", "--stdin", data=entry.data)
        updates.append(
            b"100644 " + object_id.strip() + b"\t" + entry.path.encode() + b"\0"
        )
    _read(
        repository,
        "update-index",
        "-z",
        "--index-info",
        index=index,
        data=b"".join(updates),
    )
    tree = _read(repository, "write-tree", index=index).decode("ascii").strip()
    return (
        _read(
            repository,
            "commit-tree",
            tree,
            "-p",
            tip,
            "-m",
            "Publish session turn receipts",
        )
        .decode("ascii")
        .strip()
    )


def publish_receipts(
    repository: Path,
    remote_url: str,
    project_id: UUID,
    receipts: Sequence[PublicationEntry],
) -> str:
    """Use one nonforced planning commit and return a tip with verified receipts.

    Git runs from the caller's authorized checkout. Its branch and index are
    untouched. The caller keeps the private batch when publication is on hold.
    """
    entries = _validated_batch(project_id, receipts)
    fetch_ref = f"refs/aitm/session-publication/{uuid4().hex}"
    try:
        with tempfile.TemporaryDirectory(
            prefix="aitm-session-publication-"
        ) as directory:
            index = Path(directory) / "index"
            for attempt in range(_MAX_PUSHES + 1):
                _require_remote(repository, remote_url)
                fetch = _git(
                    repository,
                    "fetch",
                    "--no-tags",
                    "--no-write-fetch-head",
                    "--no-auto-maintenance",
                    "--refmap=",
                    "origin",
                    f"{_PLANNING}:{fetch_ref}",
                )
                if fetch.returncode:
                    continue
                tip = _read(
                    repository, "rev-parse", "--verify", f"{fetch_ref}^{{commit}}"
                )
                tip = tip.decode("ascii").strip()
                missing = _PlanningTree(repository, tip).missing(entries)
                if not missing:
                    return tip
                if attempt == _MAX_PUSHES:
                    break
                commit = _commit(repository, index, tip, missing)
                _require_remote(repository, remote_url)
                # Any result, including a lost acknowledgement, needs remote readback.
                _git(
                    repository, "push", "--porcelain", "origin", f"{commit}:{_PLANNING}"
                )
        raise PublicationHold(
            "Planning publication remains unverified after bounded retries"
        )
    finally:
        _git(repository, "update-ref", "-d", fetch_ref)
