"""Pinned Git object reads and isolated index writes for the planning store."""

import os
import re
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from aitm_core.models.operations import repository_path
from aitm_core.store.backend import Blobs, Snapshot

_REPOSITORY_ENV = {
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_COMMON_DIR",
    "GIT_DIR",
    "GIT_INDEX_FILE",
    "GIT_NAMESPACE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_PREFIX",
    "GIT_WORK_TREE",
}


class GitCommandError(RuntimeError):
    def __init__(self, command: str, stderr: bytes) -> None:
        detail = stderr.decode("utf-8", errors="replace").strip()
        super().__init__(f"git {command} failed: {detail}")


class UnknownTree(ValueError):
    """The requested Git object does not identify a tree."""


@dataclass(frozen=True, slots=True)
class Repository:
    root: Path
    ref: str
    identity: str = field(init=False)
    oid_length: int = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "root", self.root.resolve())
        if not self.ref.startswith("refs/heads/"):
            raise ValueError("planning target must be a fully qualified local branch")
        self._git("check-ref-format", self.ref)
        common = self._git("rev-parse", "--path-format=absolute", "--git-common-dir")
        object_format = self._git("rev-parse", "--show-object-format").strip()
        lengths = {b"sha1": 40, b"sha256": 64}
        if object_format not in lengths:
            raise ValueError("unsupported Git object format")
        object.__setattr__(self, "oid_length", lengths[object_format])
        directory = Path(os.fsdecode(common.removesuffix(b"\n"))).resolve()
        object.__setattr__(self, "identity", f"{directory}:{self.ref}")

    def _run(
        self, *args: str, data: bytes | None = None, index: Path | None = None
    ) -> subprocess.CompletedProcess[bytes]:
        env = {
            key: value
            for key, value in os.environ.items()
            if key not in _REPOSITORY_ENV
        }
        env["GIT_NO_REPLACE_OBJECTS"] = "1"
        if index is not None:
            env["GIT_INDEX_FILE"] = str(index)
        return subprocess.run(
            ("git", "-C", str(self.root), *args),
            input=data,
            env=env,
            capture_output=True,
            check=False,
        )

    def _git(
        self, *args: str, data: bytes | None = None, index: Path | None = None
    ) -> bytes:
        result = self._run(*args, data=data, index=index)
        if result.returncode:
            raise GitCommandError(args[0], result.stderr)
        return result.stdout

    def _oid(self, value: str) -> str:
        if re.fullmatch(rf"[0-9a-f]{{{self.oid_length}}}", value) is None:
            raise ValueError("expected a full Git object identity")
        return value

    def tip(self) -> Snapshot:
        symbolic = self._run("symbolic-ref", "-q", self.ref)
        if symbolic.returncode == 0:
            raise ValueError("planning target must be a direct ref")
        if symbolic.returncode != 1:
            raise GitCommandError("symbolic-ref", symbolic.stderr)
        revision = self._git("rev-parse", "--verify", f"{self.ref}^{{commit}}")
        return self.read_tree(revision.strip().decode("ascii"))

    def read_tree(self, oid: str) -> Snapshot:
        revision = self._oid(oid)
        resolved = self._run("rev-parse", "--quiet", "--verify", f"{revision}^{{tree}}")
        if resolved.returncode == 1:
            raise UnknownTree("requested revision does not resolve to a local tree")
        if resolved.returncode:
            raise GitCommandError("rev-parse", resolved.stderr)
        return Snapshot(
            self.identity, revision, self._oid(resolved.stdout.strip().decode("ascii"))
        )

    def read_blobs(self, tree: str, paths: Sequence[str]) -> Blobs:
        oid = self._oid(tree)
        requests = {
            path: f"{oid}:{repository_path(path)}".encode("utf-8") for path in paths
        }
        if not requests:
            return {}

        response = self._git(
            "cat-file", "--batch", data=b"\n".join(requests.values()) + b"\n"
        )
        reader = BytesIO(response)
        result: dict[str, bytes | None] = {}
        for path, request in requests.items():
            header = reader.readline()
            if header == request + b" missing\n":
                result[path] = None
                continue
            parts = header.split()
            if len(parts) != 3 or parts[1] not in (b"blob", b"tree"):
                raise ValueError("Git returned an unsupported planning object")
            size = int(parts[2])
            if size < 0:
                raise ValueError("Git returned an invalid object size")
            content = reader.read(size)
            if len(content) != size or reader.read(1) != b"\n":
                raise ValueError("incomplete Git batch object")
            result[path] = content if parts[1] == b"blob" else None
        if reader.read(1):
            raise ValueError("unexpected data after the Git batch response")
        return result

    def create_commit(
        self, base: Snapshot, writes: Blobs, operation_id: str
    ) -> Snapshot:
        with TemporaryDirectory(prefix="aitm-planning-index-") as temp:
            index = Path(temp) / "index"
            self._git("read-tree", self._oid(base.tree), index=index)
            entries = []
            for path, content in writes.items():
                name = repository_path(path).encode("utf-8")
                if content is None:
                    header = b"0 " + (b"0" * self.oid_length)
                else:
                    blob = self._git(
                        "hash-object", "-w", "--stdin", data=content
                    ).strip()
                    header = b"100644 " + blob
                entries.append(header + b"\t" + name + b"\0")
            self._git(
                "update-index",
                "-z",
                "--index-info",
                data=b"".join(entries),
                index=index,
            )
            tree = self._oid(
                self._git("write-tree", index=index).strip().decode("ascii")
            )

        changed = self._git(
            "diff-tree",
            "-r",
            "--no-renames",
            "--no-commit-id",
            "--name-only",
            "-z",
            base.tree,
            tree,
        )
        changed_paths = {path.decode("utf-8") for path in changed.split(b"\0") if path}
        if (
            not changed_paths.issubset(writes)
            or self.read_blobs(tree, tuple(writes)) != writes
        ):
            raise ValueError("staged Git tree differs from the approved writes")

        commit = self._git(
            "commit-tree",
            tree,
            "-p",
            self._oid(base.revision),
            "-m",
            f"AITM operation {operation_id}",
        )
        return Snapshot(self.identity, self._oid(commit.strip().decode("ascii")), tree)

    def compare_and_swap(self, new: str, expected: str) -> bool:
        result = self._run(
            "update-ref", "--no-deref", self.ref, self._oid(new), self._oid(expected)
        )
        if not result.returncode:
            return True
        if self.tip().revision != expected:
            return False
        raise GitCommandError("update-ref", result.stderr)

    def record_origin(self, snapshot: Snapshot, path: str) -> Snapshot:
        revision = self._git(
            "log",
            "-1",
            "--format=%H",
            self._oid(snapshot.revision),
            "--",
            repository_path(path),
        )
        return self.read_tree(revision.strip().decode("ascii"))

    def parent(self, snapshot: Snapshot) -> str:
        data = self._git(
            "rev-list", "--parents", "-n", "1", self._oid(snapshot.revision)
        )
        values = data.decode("ascii").split()
        if len(values) != 2:
            raise ValueError("operation commit must have exactly one parent")
        return self._oid(values[1])
