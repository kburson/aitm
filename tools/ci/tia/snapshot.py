"""Exact Git endpoints for test impact analysis."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import selectors
import shutil
import subprocess
import sys
import tempfile
import time
from bisect import bisect_left
from collections.abc import Callable
from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path

_GIT_TIMEOUT = 30
_GIT_OUTPUT_LIMIT = 128 * 1024 * 1024
_ENTRY_LIMIT = 200_000
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
    flags: tuple[str, ...] = _GIT_FLAGS
    diff_flags: tuple[str, ...] = _DIFF_FLAGS


@dataclass(frozen=True)
class HostedProvenance:
    binding: HostedBinding
    git: GitProfile


@dataclass(frozen=True)
class Snapshot:
    repository: str
    mode: str
    ref_role: str
    endpoint_identity: GitEndpoint
    baseline_identity: GitEndpoint
    entries: tuple[Entry, ...]
    changes: tuple[Change, ...]
    provenance: HostedProvenance
    _reader: Callable[[Entry], bytes] = field(repr=False, compare=False)

    def read_content(self, path: bytes) -> bytes:
        """Read original bytes bound to an entry in this endpoint."""
        _check_path(path, self.mode)
        index = bisect_left(self.entries, path, key=lambda entry: entry.path)
        if index == len(self.entries) or self.entries[index].path != path:
            raise SnapshotUncertain(self.mode, "absent_path")
        return self._reader(self.entries[index])

    def canonical_bytes(self) -> bytes:
        record = {
            item.name: getattr(self, item.name) for item in fields(self) if item.init
        }
        del record["_reader"]
        return _canonical({"version": 1, **record})

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
        self.command = (executable, *_GIT_FLAGS)
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
        digest = hashlib.new(self.profile.object_format)
        digest.update(f"{kind} {len(payload)}\0".encode("ascii"))
        digest.update(payload)
        if digest.hexdigest() != oid:
            self.refuse("identity_mismatch")
        return payload

    def commit(self, oid: str) -> tuple[GitEndpoint, tuple[str, ...]]:
        data = self.object(oid, "commit")
        headers, separator, _ = data.partition(b"\n\n")
        lines = headers.split(b"\n")
        if not separator or not lines[0].startswith(b"tree "):
            self.refuse("malformed_data")
        tree = self.oid(self.text(lines[0][5:]))
        parents = []
        rest = iter(lines[1:])
        for line in rest:
            if not line.startswith(b"parent "):
                break
            parents.append(self.oid(self.text(line[7:])))
        if any(line.startswith((b"tree ", b"parent ")) for line in rest):
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
            path = next(records, b"")
            _check_path(path, self.mode)
            old_entry = new_entry = None
            if re.fullmatch(r"R(?:0[5-9][0-9]|100)", status):
                new_path = next(records, b"")
                _check_path(new_path, self.mode)
                status = "R"
                if path == new_path:
                    self.refuse("malformed_data")
            elif status in ("A", "D", "M", "T"):
                new_path = path
            else:
                self.refuse("malformed_data")
            if status == "A":
                if (old_mode, old_oid) != ("000000", zero):
                    self.refuse("malformed_data")
            else:
                old_entry = Entry(path, old_mode, old_oid)
                if path not in remaining_old or old_entry != old[path]:
                    self.refuse("malformed_data")
                remaining_old.remove(path)
            if status == "D":
                if (new_mode, new_oid) != ("000000", zero):
                    self.refuse("malformed_data")
            else:
                new_entry = Entry(new_path, new_mode, new_oid)
                if new_path not in remaining_new or new_entry != new[new_path]:
                    self.refuse("malformed_data")
                remaining_new.remove(new_path)
            if _GITLINK in (old_mode, new_mode):
                self.refuse("unsupported_object")
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
        or not isinstance(request.repository, str)
        or not re.fullmatch(r"[^/\s]+/[^/\s]+", request.repository)
        or not isinstance(request.ref, str)
        or (is_pr and not re.fullmatch(r"refs/pull/[1-9][0-9]*/merge", request.ref))
        or (
            not is_pr
            and (
                request.ref_role != "trunk-tested"
                or not request.ref.startswith("refs/heads/")
                or request.pr_head is not None
            )
        )
    ):
        raise SnapshotUncertain("hosted", "identity_mismatch")
    if is_pr and not request.pr_head:
        raise SnapshotUncertain("hosted", "missing_authority")
    git = _Git(repo, "hosted")
    if not is_pr:
        git.run("check-ref-format", request.ref, failure="identity_mismatch")
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


def resolve(repo: Path, request: HostedRequest) -> tuple[Snapshot, Snapshot]:
    """Resolve the complete pair, before first, or raise typed uncertainty."""
    return _hosted(repo, request)
