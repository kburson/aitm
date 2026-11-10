"""Exact Git endpoints for test impact analysis."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import selectors
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from bisect import bisect_left
from collections.abc import Callable
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path

_GIT_TIMEOUT = 30
_GIT_OUTPUT_LIMIT = 128 * 1024 * 1024
_ENTRY_LIMIT = 200_000
_WORKTREE_LIMIT = 256 * 1024 * 1024
_BLOB_MODES = frozenset({"100644", "100755", "120000"})
_GITLINK = "160000"
_DIFF_FLAGS = (
    "--raw",
    "--no-abbrev",
    "-z",
    "--no-ext-diff",
    "--no-textconv",
    "-O/dev/null",
    "--no-relative",
    "--ignore-submodules=none",
    "--find-renames=50%",
    "-l1000",
)
_GIT_FLAGS = (
    "--no-replace-objects",
    "--no-lazy-fetch",
    "--no-optional-locks",
    "-c",
    "core.fsmonitor=false",
    "-c",
    "core.untrackedCache=false",
    "-c",
    "core.ignoreCase=false",
    "-c",
    "core.precomposeUnicode=false",
    "-c",
    "protocol.allow=never",
)


class SnapshotUncertain(Exception):
    """An exact observation could not be established."""

    def __init__(self, mode: str, reason: str):
        self.mode = mode
        self.reason = reason
        super().__init__(f"{mode}: {reason}")


@dataclass(frozen=True)
class HostedBinding:
    repository: str
    ref: str
    run_id: int
    run_attempt: int
    base_commit: str | None
    tested_commit: str
    tested_tree: str
    pr_head: str | None = None


@dataclass(frozen=True)
class HostedRequest:
    repository: str
    ref_role: str
    ref: str
    run_id: int
    run_attempt: int
    base_commit: str | None
    tested_commit: str
    tested_tree: str
    pr_head: str | None
    binding: HostedBinding | None


@dataclass(frozen=True)
class LocalRequest:
    repository: str
    ref_role: str
    base_commit: str | None
    relevant_ignored: tuple[bytes, ...] = ()


@dataclass(frozen=True)
class GitEndpoint:
    commit: str
    tree: str


@dataclass(frozen=True)
class Entry:
    path: bytes
    mode: str
    content_id: str


@dataclass(frozen=True)
class Change:
    status: str
    old: Entry | None
    new: Entry | None


@dataclass(frozen=True)
class GitProfile:
    version: str
    object_format: str
    config_scope: str = "repository-only"
    flags: tuple[str, ...] = _GIT_FLAGS
    diff_flags: tuple[str, ...] = _DIFF_FLAGS


@dataclass(frozen=True)
class HostedProvenance:
    binding: HostedBinding
    git: GitProfile


@dataclass(frozen=True)
class WorktreeEndpoint:
    worktree_digest: str


@dataclass(frozen=True)
class LocalObservation:
    head: GitEndpoint
    head_ref: bytes
    index_entries: tuple[Entry, ...]
    untracked_paths: tuple[bytes, ...]
    relevant_ignored: tuple[bytes, ...]
    ignore_sources: tuple[tuple[bytes, str | None], ...]
    observed_absent: tuple[bytes, ...]
    effective_entries: tuple[Entry, ...]
    symlink_targets: tuple[tuple[bytes, bytes], ...]


@dataclass(frozen=True)
class LocalProvenance:
    git: GitProfile
    observation: LocalObservation
    committed_changes: tuple[Change, ...]
    staged_changes: tuple[Change, ...]
    unstaged_changes: tuple[Change, ...]


@dataclass(frozen=True)
class Snapshot:
    repository: str
    mode: str
    ref_role: str
    endpoint_identity: GitEndpoint | WorktreeEndpoint
    baseline_identity: GitEndpoint
    entries: tuple[Entry, ...]
    changes: tuple[Change, ...]
    provenance: HostedProvenance | LocalProvenance
    _reader: Callable[[Entry], bytes] = field(repr=False, compare=False)

    def read_content(self, path: bytes) -> bytes:
        """Read original bytes bound to an entry in this endpoint."""
        _check_path(path, self.mode)
        index = bisect_left(self.entries, path, key=lambda entry: entry.path)
        if index == len(self.entries) or self.entries[index].path != path:
            raise SnapshotUncertain(self.mode, "absent_path")
        return self._reader(self.entries[index])

    def canonical_bytes(self) -> bytes:
        return _canonical(
            {
                "version": 1,
                "repository": self.repository,
                "mode": self.mode,
                "ref_role": self.ref_role,
                "endpoint_identity": self.endpoint_identity,
                "baseline_identity": self.baseline_identity,
                "entries": self.entries,
                "changes": self.changes,
                "provenance": self.provenance,
            }
        )

    @property
    def digest(self) -> str:
        return _sha256(self.canonical_bytes())


def _json_value(value):
    if isinstance(value, bytes):
        return base64.b64encode(value).decode("ascii")
    if is_dataclass(value):
        return {
            item.name: _json_value(getattr(value, item.name)) for item in fields(value)
        }
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    return value


def _canonical(record: dict) -> bytes:
    return json.dumps(
        _json_value(record), sort_keys=True, separators=(",", ":")
    ).encode("ascii")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _check_path(path: bytes, mode: str) -> None:
    if (
        not isinstance(path, bytes)
        or b"\0" in path
        or any(part.lower() in (b"", b".", b"..", b".git") for part in path.split(b"/"))
    ):
        raise SnapshotUncertain(mode, "unsafe_path")


def _run_git(repo, command, env, data=None):
    """Drain both pipes within one timeout and output budget."""
    with tempfile.TemporaryFile() as input_file:
        if data is not None:
            input_file.write(data)
            input_file.seek(0)
        with (
            subprocess.Popen(
                command,
                cwd=repo,
                env=env,
                stdin=input_file if data is not None else subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ) as process,
            selectors.DefaultSelector() as selector,
        ):
            output = bytearray()
            errors = bytearray()
            selector.register(process.stdout, selectors.EVENT_READ, output)
            selector.register(process.stderr, selectors.EVENT_READ, errors)
            deadline = time.monotonic() + _GIT_TIMEOUT
            try:
                while selector.get_map():
                    events = selector.select(max(0, deadline - time.monotonic()))
                    if not events or time.monotonic() >= deadline:
                        raise subprocess.TimeoutExpired(command, _GIT_TIMEOUT)
                    for key, _ in events:
                        chunk = os.read(key.fd, 65536)
                        if not chunk:
                            selector.unregister(key.fd)
                            continue
                        if len(output) + len(errors) + len(chunk) > _GIT_OUTPUT_LIMIT:
                            raise OverflowError
                        key.data.extend(chunk)
                code = process.wait(timeout=max(0, deadline - time.monotonic()))
            except BaseException:
                process.kill()
                raise
        return subprocess.CompletedProcess(command, code, bytes(output), bytes(errors))


class _Git:
    def __init__(self, repo: Path, mode: str):
        self.mode = mode
        try:
            self.root = repo.resolve(strict=True)
        except (OSError, RuntimeError, ValueError):
            self.refuse("unreadable_input")
        # Apple Git on the qualified macOS lane has the offline control. PATH may
        # instead name a separate installation that lacks it.
        executable = "/usr/bin/git" if sys.platform == "darwin" else shutil.which("git")
        if executable is None:
            self.refuse("unsupported_profile")
        self.command = (os.path.abspath(executable), *_GIT_FLAGS)
        self.env = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("GIT_")
        }
        self.env.update(
            GIT_CONFIG_NOSYSTEM="1",
            GIT_CONFIG_SYSTEM=os.devnull,
            GIT_CONFIG_GLOBAL=os.devnull,
            GIT_TERMINAL_PROMPT="0",
            LC_ALL="C",
        )
        version = self.run("--version", failure="unsupported_profile")
        if not re.fullmatch(rb"git version [0-9]+\.[^\x00\n]+\n", version):
            self.refuse("unsupported_profile")
        root = self.run("rev-parse", "--show-toplevel", failure="unreadable_input")
        if not root.endswith(b"\n") or os.path.realpath(root[:-1]) != os.fsencode(
            self.root
        ):
            self.refuse("unsafe_path")
        object_format = self.run("rev-parse", "--show-object-format")
        if object_format not in (b"sha1\n", b"sha256\n"):
            self.refuse("unsupported_profile")
        self.profile = GitProfile(
            version[:-1].decode("ascii"), object_format[:-1].decode("ascii")
        )
        self.oid_size = hashlib.new(self.profile.object_format).digest_size
        self.oid_pattern = re.compile(rf"[0-9a-f]{{{self.oid_size * 2}}}")

    def refuse(self, reason: str):
        raise SnapshotUncertain(self.mode, reason)

    def run(
        self, *args: str, data: bytes | None = None, failure: str = "command_failure"
    ) -> bytes:
        try:
            result = _run_git(self.root, (*self.command, *args), self.env, data)
        except subprocess.TimeoutExpired:
            self.refuse("command_timeout")
        except OverflowError:
            self.refuse("output_limit")
        except OSError:
            self.refuse(failure)
        if result.returncode:
            self.refuse(failure)
        if result.stderr:
            if b"rename detection" in result.stderr.lower():
                self.refuse("rename_limit")
            self.refuse(failure)
        return result.stdout

    def oid(self, value: str, reason: str = "malformed_data") -> str:
        if not isinstance(value, str) or not self.oid_pattern.fullmatch(value):
            self.refuse(reason)
        return value

    def text(self, value: bytes) -> str:
        try:
            return value.decode("ascii")
        except UnicodeDecodeError:
            self.refuse("malformed_data")

    def object(self, oid: str, kind: str) -> bytes:
        data = self.run("cat-file", "--batch", data=oid.encode("ascii") + b"\n")
        header, sep, body = data.partition(b"\n")
        if sep and not body and header == f"{oid} missing".encode("ascii"):
            self.refuse("missing_object")
        expected = f"{oid} {kind} {len(body) - 1}".encode("ascii")
        if not body.endswith(b"\n") or header != expected:
            if (
                header.startswith(f"{oid} ".encode("ascii"))
                and len(header.split()) == 3
            ):
                if header.split()[1] != kind.encode("ascii"):
                    self.refuse("unsupported_object")
            self.refuse("malformed_data")
        payload = body[:-1]
        if self.object_id(kind, payload) != oid:
            self.refuse("identity_mismatch")
        return payload

    def object_id(self, kind: str, payload: bytes) -> str:
        digest = hashlib.new(self.profile.object_format)
        digest.update(f"{kind} {len(payload)}\0".encode("ascii"))
        digest.update(payload)
        return digest.hexdigest()

    def commit(self, oid: str) -> tuple[GitEndpoint, tuple[str, ...]]:
        data = self.object(oid, "commit")
        headers, separator, _ = data.partition(b"\n\n")
        lines = headers.split(b"\n")
        if not separator or not lines[0].startswith(b"tree "):
            self.refuse("malformed_data")
        tree = self.oid(self.text(lines[0][5:]))
        parents = []
        parent_end = 1
        while parent_end < len(lines) and lines[parent_end].startswith(b"parent "):
            parents.append(self.oid(self.text(lines[parent_end][7:])))
            parent_end += 1
        if any(line.startswith((b"tree ", b"parent ")) for line in lines[parent_end:]):
            self.refuse("malformed_data")
        return GitEndpoint(oid, tree), tuple(parents)

    def tree_entries(self, oid: str) -> tuple[Entry, ...]:
        # Read native trees by identity so even a successful valid-prefix result
        # cannot omit an entry. Validate each directory before descending.
        pending = [(b"", oid)]
        entries = []
        total = 0
        while pending:
            prefix, oid = pending.pop()
            data = self.object(oid, "tree")
            names = set()
            prior = b""
            start = 0
            while start < len(data):
                separator = data.find(b" ", start)
                end = data.find(b"\0", separator + 1)
                if separator < 0 or end < 0 or end + 1 + self.oid_size > len(data):
                    self.refuse("malformed_data")
                mode = self.text(data[start:separator])
                name = data[separator + 1 : end]
                path = prefix + name
                _check_path(path, self.mode)
                if b"/" in name or name in names:
                    self.refuse("malformed_data")
                order = name + b"/" if mode == "40000" else name
                if order <= prior:
                    self.refuse("malformed_data")
                prior = order
                names.add(name)
                start = end + 1 + self.oid_size
                child = data[end + 1 : start].hex()
                total += 1
                if total > _ENTRY_LIMIT:
                    self.refuse("output_limit")
                if mode == "40000":
                    pending.append((path + b"/", child))
                elif mode in _BLOB_MODES or mode == _GITLINK:
                    entries.append(Entry(path, mode, child))
                else:
                    self.refuse("unsupported_object")
        return tuple(sorted(entries, key=lambda entry: entry.path))

    def require_blobs(self, *endpoints: tuple[Entry, ...]) -> None:
        objects = sorted(
            {
                entry.content_id
                for entries in endpoints
                for entry in entries
                if entry.mode in _BLOB_MODES
            }
        )
        if not objects:
            return
        data = b"".join(oid.encode("ascii") + b"\n" for oid in objects)
        result = self.run("cat-file", "--batch-check", data=data)
        lines = result.split(b"\n")
        if len(lines) != len(objects) + 1 or lines[-1]:
            self.refuse("malformed_data")
        for oid, line in zip(objects, lines, strict=False):
            oid = oid.encode("ascii")
            if line == oid + b" missing":
                self.refuse("missing_object")
            if not re.fullmatch(oid + rb" blob (?:0|[1-9][0-9]*)", line):
                self.refuse("unsupported_object")

    def read_blob(self, entry: Entry) -> bytes:
        if entry.mode not in _BLOB_MODES:
            self.refuse("unsupported_object")
        return self.object(entry.content_id, "blob")

    def changes(
        self, data: bytes, before: tuple[Entry, ...], after: tuple[Entry, ...]
    ) -> tuple[Change, ...]:
        old = {entry.path: entry for entry in before}
        new = {entry.path: entry for entry in after}
        changed = {
            path for path in old.keys() | new.keys() if old.get(path) != new.get(path)
        }
        remaining_old = changed & old.keys()
        remaining_new = changed & new.keys()
        result = []
        records = iter(self.nul_records(data))
        for raw in records:
            header = raw.split(b" ")
            if len(header) != 5 or not header[0].startswith(b":"):
                self.refuse("malformed_data")
            old_mode, new_mode, old_oid, new_oid, status = map(self.text, header)
            old_mode = old_mode[1:]
            self.oid(old_oid)
            self.oid(new_oid)
            zero = "0" * (self.oid_size * 2)
            path = next(records, None)
            if path is None:
                self.refuse("malformed_data")
            _check_path(path, self.mode)
            old_entry = new_entry = None
            if re.fullmatch(r"R(?:0[5-9][0-9]|100)", status):
                new_path = next(records, None)
                if new_path is None:
                    self.refuse("malformed_data")
                _check_path(new_path, self.mode)
                status = "R"
                if path in new or new_path in old or old_mode[:3] != new_mode[:3]:
                    self.refuse("malformed_data")
            elif status in ("A", "D", "M", "T"):
                new_path = path
            else:
                self.refuse("malformed_data")
            if status == "A":
                if path in old or (old_mode, old_oid) != ("000000", zero):
                    self.refuse("malformed_data")
            else:
                old_entry = Entry(path, old_mode, old_oid)
                if path not in remaining_old or old_entry != old[path]:
                    self.refuse("malformed_data")
                remaining_old.remove(path)
            if status == "D":
                if path in new or (new_mode, new_oid) != ("000000", zero):
                    self.refuse("malformed_data")
            else:
                new_entry = Entry(new_path, new_mode, new_oid)
                if new_path not in remaining_new or new_entry != new[new_path]:
                    self.refuse("malformed_data")
                remaining_new.remove(new_path)
            if _GITLINK in (old_mode, new_mode):
                self.refuse("unsupported_object")
            if status in ("M", "T") and status != _modified(old_mode, new_mode):
                self.refuse("malformed_data")
            result.append(Change(status, old_entry, new_entry))
        if remaining_old or remaining_new:
            self.refuse("malformed_data")
        return _sorted_changes(result)

    def nul_records(self, data: bytes) -> tuple[bytes, ...]:
        if not data:
            return ()
        if not data.endswith(b"\0"):
            self.refuse("malformed_data")
        records = data[:-1].split(b"\0")
        if not all(records):
            self.refuse("malformed_data")
        return tuple(records)

    def tree_changes(
        self,
        base: GitEndpoint,
        tested: GitEndpoint,
        before: tuple[Entry, ...],
        after: tuple[Entry, ...],
    ) -> tuple[Change, ...]:
        data = self.run(
            "diff-tree", "--no-commit-id", "-r", *_DIFF_FLAGS, base.tree, tested.tree
        )
        return self.changes(data, before, after)


def _modified(old_mode: str, new_mode: str) -> str:
    return "M" if old_mode[:3] == new_mode[:3] else "T"


def _sorted_changes(changes: list[Change]) -> tuple[Change, ...]:
    return tuple(
        sorted(
            changes,
            key=lambda item: (
                item.old.path if item.old else item.new.path,
                item.new.path if item.new else b"",
            ),
        )
    )


def _hosted(repo: Path, request: HostedRequest) -> tuple[Snapshot, Snapshot]:
    binding = request.binding
    if (
        binding is None
        or not request.repository
        or not request.ref
        or type(request.run_id) is not int
        or request.run_id < 1
        or type(request.run_attempt) is not int
        or request.run_attempt < 1
    ):
        raise SnapshotUncertain("hosted", "missing_authority")
    if not request.base_commit:
        raise SnapshotUncertain("hosted", "missing_baseline")
    if not request.tested_commit or not request.tested_tree:
        raise SnapshotUncertain("hosted", "missing_authority")
    is_pr = request.ref_role == "pr-tested"
    if (
        binding
        != HostedBinding(
            request.repository,
            request.ref,
            request.run_id,
            request.run_attempt,
            request.base_commit,
            request.tested_commit,
            request.tested_tree,
            request.pr_head,
        )
        or type(binding.run_id) is not int
        or type(binding.run_attempt) is not int
        or not isinstance(request.repository, str)
        or not re.fullmatch(r"[^/\s]+/[^/\s]+", request.repository)
        or not isinstance(request.ref, str)
        or (is_pr and not re.fullmatch(r"refs/pull/[1-9][0-9]*/merge", request.ref))
        or (
            not is_pr
            and (
                request.ref_role != "trunk-tested"
                or request.ref != "refs/heads/trunk"
                or request.pr_head is not None
            )
        )
    ):
        raise SnapshotUncertain("hosted", "identity_mismatch")
    if is_pr and not request.pr_head:
        raise SnapshotUncertain("hosted", "missing_authority")
    git = _Git(repo, "hosted")
    baseline, _ = git.commit(git.oid(request.base_commit, "identity_mismatch"))
    tested, parents = git.commit(git.oid(request.tested_commit, "identity_mismatch"))
    if tested.tree != request.tested_tree or (
        is_pr and parents != (baseline.commit, request.pr_head)
    ):
        git.refuse("identity_mismatch")
    if is_pr:
        git.commit(git.oid(request.pr_head, "identity_mismatch"))
    old_entries = git.tree_entries(baseline.tree)
    new_entries = (
        git.tree_entries(tested.tree) if tested.tree != baseline.tree else old_entries
    )
    git.require_blobs(old_entries, new_entries)
    changes = git.tree_changes(baseline, tested, old_entries, new_entries)
    provenance = HostedProvenance(binding, git.profile)
    return (
        Snapshot(
            request.repository,
            "hosted",
            "baseline",
            baseline,
            baseline,
            old_entries,
            changes,
            provenance,
            git.read_blob,
        ),
        Snapshot(
            request.repository,
            "hosted",
            request.ref_role,
            tested,
            baseline,
            new_entries,
            changes,
            provenance,
            git.read_blob,
        ),
    )


def _witness(info: os.stat_result) -> tuple[int, ...]:
    return (
        info.st_dev,
        info.st_ino,
        info.st_mode,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
    )


@dataclass(frozen=True)
class _LocalFile:
    mode: str
    data: bytes
    witness: tuple[int, ...]


class _CheckedTree:
    """Read by exact directory-entry spelling beneath a pinned descriptor."""

    def __init__(self, root: Path, fd: int):
        self.root = root
        self.fd = fd
        self.names: dict[tuple[int, ...], frozenset[bytes]] = {}
        self.accessed: dict[bytes, tuple[int, ...] | None] = {}

    def check_root(self) -> None:
        by_name = self.root.stat(follow_symlinks=False)
        if not os.path.samestat(by_name, os.fstat(self.fd)):
            raise SnapshotUncertain("local", "observation_drift")

    def _names(self, directory: int) -> frozenset[bytes]:
        witness = _witness(os.fstat(directory))
        if witness not in self.names:
            names = frozenset(map(os.fsencode, os.listdir(directory)))
            if _witness(os.fstat(directory)) != witness:
                raise SnapshotUncertain("local", "observation_drift")
            if len(names) > _ENTRY_LIMIT:
                raise SnapshotUncertain("local", "output_limit")
            self.names[witness] = names
        return self.names[witness]

    def _stat(self, directory: int, name: bytes) -> os.stat_result | None:
        exact = name in self._names(directory)
        try:
            info = os.stat(name, dir_fd=directory, follow_symlinks=False)
        except FileNotFoundError:
            if exact:
                raise SnapshotUncertain("local", "observation_drift") from None
            return None
        if not exact:
            raise SnapshotUncertain("local", "unsafe_path")
        return info

    @contextmanager
    def _directory(self, path: bytes):
        with ExitStack() as stack:
            parent = self.fd
            guards = []
            prefix = b""
            for name in path.split(b"/") if path else ():
                prefix = prefix + b"/" + name if prefix else name
                info = self._stat(parent, name)
                if info is None:
                    self._remember(prefix, None)
                    parent = None
                    break
                witness = _witness(info)
                self._remember(prefix, witness)
                guards.append((parent, name, witness))
                if stat.S_ISREG(info.st_mode):
                    parent = None
                    break
                if not stat.S_ISDIR(info.st_mode):
                    raise SnapshotUncertain("local", "unsafe_path")
                child = os.open(
                    name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent
                )
                stack.callback(os.close, child)
                if _witness(os.fstat(child)) != witness:
                    raise SnapshotUncertain("local", "observation_drift")
                parent = child
            yield parent
            for directory, name, witness in guards:
                current = self._stat(directory, name)
                if current is None or _witness(current) != witness:
                    raise SnapshotUncertain("local", "observation_drift")

    def _remember(self, path: bytes, witness: tuple[int, ...] | None) -> None:
        if path in self.accessed and self.accessed[path] != witness:
            raise SnapshotUncertain("local", "observation_drift")
        self.accessed[path] = witness

    def read(self, path: bytes) -> _LocalFile | None:
        _check_path(path, "local")
        parent, _, name = path.rpartition(b"/")
        with self._directory(parent) as directory:
            if directory is None:
                return None
            info = self._stat(directory, name)
            if info is None:
                return None
            witness = _witness(info)
            if stat.S_ISLNK(info.st_mode):
                data = os.readlink(name, dir_fd=directory)
                mode = "120000"
            elif stat.S_ISREG(info.st_mode):
                mode = "100755" if info.st_mode & stat.S_IXUSR else "100644"
                if info.st_size > _GIT_OUTPUT_LIMIT:
                    raise SnapshotUncertain("local", "output_limit")
                descriptor = os.open(
                    name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory
                )
                with os.fdopen(descriptor, "rb") as stream:
                    if _witness(os.fstat(descriptor)) != witness:
                        raise SnapshotUncertain("local", "observation_drift")
                    data = stream.read(info.st_size + 1)
                    if (
                        len(data) != info.st_size
                        or _witness(os.fstat(descriptor)) != witness
                    ):
                        raise SnapshotUncertain("local", "observation_drift")
            elif stat.S_ISDIR(info.st_mode):
                mode, data = "040000", b""
                self._remember(path, witness)
            else:
                raise SnapshotUncertain("local", "unsupported_object")
            current = self._stat(directory, name)
            if current is None or _witness(current) != witness:
                raise SnapshotUncertain("local", "observation_drift")
            return _LocalFile(mode, data, witness)

    def catalog(
        self, pruned: set[bytes], covered: set[bytes]
    ) -> tuple[tuple[bytes, tuple[int, ...]], ...]:
        """Check membership and find every directory with consulted ignore rules."""
        remaining = set(pruned)
        visited = {}
        pending = [b""]
        total = 0
        while pending:
            path = pending.pop()
            with self._directory(path) as directory:
                if directory is None:
                    raise SnapshotUncertain("local", "observation_drift")
                witness = _witness(os.fstat(directory))
                visited[path] = witness
                for name in self._names(directory):
                    if not path and name == b".git":
                        continue
                    child = path + b"/" + name if path else name
                    _check_path(child, "local")
                    info = self._stat(directory, name)
                    if info is None:
                        raise SnapshotUncertain("local", "observation_drift")
                    total += 1
                    if total > _ENTRY_LIMIT:
                        raise SnapshotUncertain("local", "output_limit")
                    if stat.S_ISDIR(info.st_mode):
                        if child in pruned:
                            remaining.remove(child)
                        else:
                            pending.append(child)
                    elif child not in covered:
                        if not (
                            stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode)
                        ):
                            raise SnapshotUncertain("local", "unsupported_object")
                        raise SnapshotUncertain("local", "observation_drift")
                if _witness(os.fstat(directory)) != witness:
                    raise SnapshotUncertain("local", "observation_drift")
        if remaining:
            raise SnapshotUncertain("local", "observation_drift")
        return tuple(sorted(visited.items()))


@dataclass(frozen=True)
class _LocalCapture:
    observation: LocalObservation
    head_entries: tuple[Entry, ...]
    staged: tuple[Change, ...]
    witnesses: tuple
    contents: dict[bytes, _LocalFile] = field(compare=False)


def _index(git: _Git) -> tuple[Entry, ...]:
    result = {}
    for record in git.nul_records(git.run("ls-files", "--stage", "-z")):
        header, separator, path = record.partition(b"\t")
        if not separator or len(header.split(b" ")) != 3:
            git.refuse("malformed_data")
        mode, oid, stage = map(git.text, header.split(b" "))
        _check_path(path, git.mode)
        if stage in ("1", "2", "3"):
            git.refuse("unmerged_index")
        if stage != "0" or path in result:
            git.refuse("malformed_data")
        if mode not in _BLOB_MODES:
            git.refuse("unsupported_object")
        result[path] = Entry(path, mode, git.oid(oid))
    return tuple(result[path] for path in sorted(result))


def _ancestors(paths: set[bytes]) -> set[bytes]:
    result = set()
    for path in paths:
        parent = path.rpartition(b"/")[0]
        while parent and parent not in result:
            result.add(parent)
            parent = parent.rpartition(b"/")[0]
    return result


def _membership(git: _Git) -> tuple[set[bytes], set[bytes], set[bytes]]:
    options = ("ls-files", "--others", "--exclude-per-directory=.gitignore", "-z")
    untracked_records = git.nul_records(git.run(*options))
    ignored_records = git.nul_records(git.run(*options, "--ignored", "--directory"))
    untracked, ignored, ignored_dirs = set(), set(), set()
    for record in untracked_records:
        if record.endswith(b"/"):
            git.refuse("unsupported_object")
        _check_path(record, git.mode)
        if record in untracked:
            git.refuse("malformed_data")
        untracked.add(record)
    for record in ignored_records:
        directory = record.endswith(b"/")
        path = record[:-1] if directory else record
        _check_path(path, git.mode)
        target = ignored_dirs if directory else ignored
        if path in target:
            git.refuse("malformed_data")
        target.add(path)
    if untracked & (ignored | ignored_dirs) or ignored & ignored_dirs:
        git.refuse("malformed_data")
    return untracked, ignored, ignored_dirs


def _link_target(
    path: bytes, payload: bytes, directories: dict[bytes, tuple[int, ...] | None]
) -> bytes:
    """Resolve only an in-root relative target through observed real directories."""
    parts = path.split(b"/")[:-1]
    names = payload.split(b"/")
    for index, name in enumerate(names):
        if name == b"..":
            if not parts:
                raise SnapshotUncertain("local", "unsafe_path")
            parts.pop()
        elif name != b".":
            _check_path(name, "local")
            parts.append(name)
        if parts and index < len(names) - 1:
            witness = directories.get(b"/".join(parts))
            if witness is None or not stat.S_ISDIR(witness[2]):
                raise SnapshotUncertain("local", "unsafe_path")
    return b"/".join(parts)


def _observe_local(
    git: _Git, worktree: _CheckedTree, request: LocalRequest
) -> _LocalCapture:
    worktree.names.clear()
    worktree.accessed.clear()
    worktree.check_root()
    head_id = git.run("rev-parse", "--verify", "HEAD", failure="missing_object")
    if not head_id.endswith(b"\n"):
        git.refuse("malformed_data")
    head, _ = git.commit(git.oid(git.text(head_id[:-1])))
    head_ref = git.run("rev-parse", "--symbolic-full-name", "HEAD")
    if not head_ref.endswith(b"\n") or not head_ref[:-1] or b"\n" in head_ref[:-1]:
        git.refuse("malformed_data")
    head_entries = git.tree_entries(head.tree)
    index = _index(git)
    git.require_blobs(head_entries, index)
    staged = git.changes(
        git.run(
            "diff-index",
            "--cached",
            "--ita-visible-in-index",
            "-r",
            *_DIFF_FLAGS,
            head.tree,
        ),
        head_entries,
        index,
    )
    untracked, ignored, ignored_dirs = _membership(git)
    tracked = {entry.path for entry in (*head_entries, *index)}
    covered = tracked | untracked | ignored
    pruned = ignored_dirs - _ancestors(covered | ignored_dirs)
    directories = worktree.catalog(pruned, covered)
    ignore_sources = {}
    ignore_witnesses = []
    for directory, _ in directories:
        path = directory + b"/.gitignore" if directory else b".gitignore"
        rule = worktree.read(path)
        if rule is None:
            ignore_sources[path] = None
        else:
            if rule.mode not in ("100644", "100755"):
                git.refuse("unreadable_input")
            ignore_sources[path] = _sha256(rule.data)
            ignore_witnesses.append((path, rule.witness))

    contents = {}
    effective = []
    absent = []
    inodes = set()
    total_bytes = 0
    requested = set(request.relevant_ignored)
    for path in sorted(tracked | untracked | requested):
        captured = worktree.read(path)
        if captured is not None and captured.mode == "040000":
            if path in requested:
                git.refuse("unsupported_object")
            captured = None
        if captured is None:
            if path in untracked:
                git.refuse("observation_drift")
            absent.append(path)
            continue
        inode = captured.witness[:2]
        if inode in inodes:
            git.refuse("unsafe_path")
        inodes.add(inode)
        total_bytes += len(captured.data)
        if total_bytes > _WORKTREE_LIMIT:
            git.refuse("output_limit")
        identity = _sha256(captured.data)
        if path in ignore_sources and identity != ignore_sources[path]:
            git.refuse("observation_drift")
        contents[path] = captured
        effective.append(Entry(path, captured.mode, identity))

    symlinks = []
    for path, captured in contents.items():
        if captured.mode != "120000":
            continue
        target = _link_target(path, captured.data, worktree.accessed)
        if target not in contents or contents[target].mode == "120000":
            git.refuse("unsafe_path")
        symlinks.append((path, target))

    worktree.check_root()
    observation = LocalObservation(
        head,
        head_ref[:-1],
        index,
        tuple(sorted(untracked)),
        tuple(sorted(requested)),
        tuple(sorted(ignore_sources.items())),
        tuple(absent),
        tuple(effective),
        tuple(symlinks),
    )
    witnesses = (
        directories,
        tuple(sorted(worktree.accessed.items())),
        tuple(sorted(ignore_witnesses)),
        tuple((path, capture.witness) for path, capture in contents.items()),
        tuple(sorted(ignored)),
        tuple(sorted(ignored_dirs)),
    )
    return _LocalCapture(observation, head_entries, staged, witnesses, contents)


def _rename_origins(*layers: tuple[Change, ...]) -> dict[bytes, bytes]:
    origins = {}
    for layer in layers:
        renames = {}
        for change in layer:
            if change.status == "R":
                source, target = change.old.path, change.new.path
                renames[target] = origins.pop(source, source)
            elif change.status == "D":
                origins.pop(change.old.path, None)
        origins.update(renames)
    return origins


def _effective_changes(
    git: _Git,
    original: tuple[Entry, ...],
    captured: _LocalCapture,
    origins: dict[bytes, bytes] | None = None,
) -> tuple[Change, ...]:
    old = {entry.path: entry for entry in original}
    new = {entry.path: entry for entry in captured.observation.effective_entries}
    removed = old.keys() - new.keys()
    added = new.keys() - old.keys()
    result = []
    for target, source in (origins or {}).items():
        if source in removed and target in added:
            result.append(Change("R", old[source], new[target]))
            removed.remove(source)
            added.remove(target)
    result.extend(Change("D", old[path], None) for path in removed)
    result.extend(Change("A", None, new[path]) for path in added)
    for path in old.keys() & new.keys():
        prior, current = old[path], new[path]
        if prior.mode != current.mode or prior.content_id != git.object_id(
            "blob", captured.contents[path].data
        ):
            result.append(Change(_modified(prior.mode, current.mode), prior, current))
    return _sorted_changes(result)


def _local(repo: Path, request: LocalRequest) -> tuple[Snapshot, Snapshot]:
    if not request.base_commit:
        raise SnapshotUncertain("local", "missing_baseline")
    if not request.repository:
        raise SnapshotUncertain("local", "missing_authority")
    if (
        not isinstance(request.repository, str)
        or not re.fullmatch(r"[^/\s]+/[^/\s]+", request.repository)
        or request.ref_role != "local-effective"
    ):
        raise SnapshotUncertain("local", "identity_mismatch")
    for path in request.relevant_ignored:
        _check_path(path, "local")
    if len(set(request.relevant_ignored)) != len(request.relevant_ignored):
        raise SnapshotUncertain("local", "unsafe_path")
    git = _Git(repo, "local")
    baseline, _ = git.commit(git.oid(request.base_commit, "identity_mismatch"))
    old_entries = git.tree_entries(baseline.tree)
    git.require_blobs(old_entries)
    try:
        root = os.open(git.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        with ExitStack() as stack:
            stack.callback(os.close, root)
            worktree = _CheckedTree(git.root, root)
            first = _observe_local(git, worktree, request)
            committed = git.tree_changes(
                baseline, first.observation.head, old_entries, first.head_entries
            )
            second = _observe_local(git, worktree, request)
            if first != second:
                git.refuse("observation_drift")
    except OSError:
        git.refuse("unreadable_input")

    observation = first.observation
    effective = WorktreeEndpoint(
        _sha256(_canonical({"version": 1, "observation": observation}))
    )
    unstaged = _effective_changes(git, observation.index_entries, first)
    changes = _effective_changes(
        git, old_entries, first, _rename_origins(committed, first.staged)
    )
    provenance = LocalProvenance(
        git.profile, observation, committed, first.staged, unstaged
    )

    def read_effective(entry: Entry) -> bytes:
        return first.contents[entry.path].data

    return (
        Snapshot(
            request.repository,
            "local",
            "baseline",
            baseline,
            baseline,
            old_entries,
            changes,
            provenance,
            git.read_blob,
        ),
        Snapshot(
            request.repository,
            "local",
            request.ref_role,
            effective,
            baseline,
            observation.effective_entries,
            changes,
            provenance,
            read_effective,
        ),
    )


def resolve(
    repo: Path, request: HostedRequest | LocalRequest
) -> tuple[Snapshot, Snapshot]:
    """Resolve the complete pair, before first, or raise typed uncertainty."""
    if isinstance(request, LocalRequest):
        return _local(repo, request)
    return _hosted(repo, request)
