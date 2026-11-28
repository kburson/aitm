"""Capture exact tracked and extra bytes in a private, read-only export."""

import os
import shutil
import stat
from collections.abc import Iterator
from hashlib import sha256
from pathlib import Path, PurePosixPath
from tempfile import gettempdir, mkdtemp
from typing import Literal

from aitm_core.config import PolicySnapshot, resolve_policy
from aitm_core.models.attempts import BindingPurpose, SourceSnapshot
from aitm_core.models.binding import Binding, StoryRef
from aitm_core.models.common import RefObservation, RefreshResult
from aitm_core.models.operations import repository_path
from aitm_core.models.verification import CapturedInput, CapturedInputs, CaptureManifest
from aitm_core.store.fetch import _direct_ref, _is_ancestor
from aitm_core.store.installation import Installation
from aitm_core.store.objects import GitCommandError
from aitm_core.store.workspace import Workspace, _parent, read_workspace


class CaptureUnavailable(ValueError):
    """An exact private export could not be qualified."""


def _relative(value: str) -> str:
    try:
        path = repository_path(value)
    except ValueError as error:
        raise CaptureUnavailable(f"Unsafe capture path: {value!r}.") from error
    if any(part.casefold() == ".git" for part in path.split("/")):
        raise CaptureUnavailable(f"Unsafe capture path: {value!r}.")
    return path


def _check_outputs(path: str, roots: tuple[str, ...]) -> None:
    if any(
        path == root or path.startswith(root + "/") or root.startswith(path + "/")
        for root in roots
    ):
        raise CaptureUnavailable(
            f"Declared output roots overlap captured input {path}."
        )


def _outside_worktrees(installation: Installation, path: Path) -> None:
    repo = installation.repository
    worktrees = (
        Path(os.fsdecode(row.removeprefix(b"worktree "))).resolve()
        for row in repo._git("worktree", "list", "--porcelain", "-z").split(b"\0")
        if row.startswith(b"worktree ")
    )
    if any(path.is_relative_to(worktree) for worktree in worktrees):
        raise CaptureUnavailable(
            "The export parent must be outside registered worktrees."
        )


def _source(
    installation: Installation, binding: Binding, policy: PolicySnapshot
) -> SourceSnapshot:
    repo = installation.repository
    if (
        binding.purpose != BindingPurpose.IMPLEMENTATION
        or not isinstance(binding.scope, StoryRef)
        or binding.source is None
        or binding.branch is None
        or binding.attempt is None
        or Workspace(installation).require(
            binding.scope, binding.identity, binding.generation, binding.session
        )
        != binding
    ):
        raise CaptureUnavailable(
            "Capture requires the exact current implementation binding."
        )
    code_ref = installation.validated_code_ref or installation.store.code_default_ref
    if _direct_ref(repo, code_ref) != policy.revision:
        raise CaptureUnavailable("The committed capture policy is stale.")
    admitted = RefObservation(
        ref=installation.code_remote_ref or installation.store.code_default_ref,
        remote=installation.code_remote,
        observed_commit=policy.revision,
    )
    if (
        resolve_policy(installation, RefreshResult(local=admitted)) != policy
        or policy.writes_fenced
    ):
        raise CaptureUnavailable(
            "The capture policy disagrees with the committed policy."
        )
    commit = _direct_ref(repo, binding.branch)
    head = repo._run("symbolic-ref", "-q", "HEAD")
    if (
        commit is None
        or head.returncode
        or head.stdout.strip().decode() != binding.branch
        or _is_ancestor(repo, binding.source.commit, commit) is not True
    ):
        raise CaptureUnavailable(
            "Capture requires the exact bound branch and source lineage."
        )
    tracked = repo._git("ls-files", "-v", "-z").split(b"\0")
    if (
        any(row[:1] == b"S" or row[:1].islower() for row in tracked)
        or repo._run(
            "--no-optional-locks",
            "diff",
            "--quiet",
            "--no-ext-diff",
            "--ignore-submodules=none",
            commit,
            "--",
        ).returncode
    ):
        raise CaptureUnavailable(
            "The bound source has dirty or unqualified tracked paths."
        )
    return SourceSnapshot(commit=commit, tree=repo.read_tree(commit).tree)


def _tracked(installation: Installation, source: SourceSnapshot) -> dict[str, bool]:
    tree = installation.repository._git("ls-tree", "-r", "-z", source.tree)
    paths = {}
    for raw in tree.split(b"\0"):
        if not raw:
            continue
        header, name = raw.split(b"\t", 1)
        mode, kind, _ = header.split()
        path = _relative(name.decode())
        if kind != b"blob" or mode not in {b"100644", b"100755"}:
            raise CaptureUnavailable(f"Expected a regular tracked file at {path}.")
        paths[path] = mode == b"100755"
    return paths


def _tracked_files(
    installation: Installation, source: SourceSnapshot, tracked: dict[str, bool]
) -> Iterator[tuple[CapturedInput, bytes]]:
    paths = tuple(tracked)
    for offset in range(0, len(paths), 128):
        blobs = installation.repository.read_blobs(
            source.tree, paths[offset : offset + 128]
        )
        for path, data in blobs.items():
            if data is None:
                raise CaptureUnavailable(f"Pinned tracked bytes are missing at {path}.")
            yield _entry(path, "tracked", data, tracked[path]), data


def _extra_paths(installation: Installation, declarations: tuple[str, ...]) -> set[str]:
    if not declarations:
        return set()
    patterns = tuple(_relative(pattern) for pattern in declarations)
    paths = tuple(
        PurePosixPath(row.decode())
        for row in installation.repository._git(
            "ls-files", "--cached", "--others", "-z"
        ).split(b"\0")
        if row
    )
    selected = set()
    for pattern in patterns:
        matches = {
            path.as_posix()
            for path in paths
            if path.full_match(pattern, case_sensitive=True)
        }
        if not matches:
            raise CaptureUnavailable(f"Declared input {pattern!r} matched no files.")
        selected.update(_relative(match) for match in matches)
    return selected


def _fingerprint(row: os.stat_result) -> tuple:
    return (
        row.st_dev,
        row.st_ino,
        row.st_mode,
        row.st_size,
        row.st_mtime_ns,
        row.st_ctime_ns,
    )


def _read_extra(root: Path, path: str) -> tuple[bytes, bool]:
    try:
        with _parent(root, path) as (parent, name):
            flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
            fd = os.open(name, flags, dir_fd=parent)
            with os.fdopen(fd, "rb") as stream:
                before = os.fstat(stream.fileno())
                if not stat.S_ISREG(before.st_mode):
                    raise CaptureUnavailable(
                        f"Expected a regular extra file at {path}."
                    )
                data = stream.read()
                after = os.fstat(stream.fileno())
                current = os.stat(name, dir_fd=parent, follow_symlinks=False)
                if _fingerprint(before) != _fingerprint(after) or _fingerprint(
                    after
                ) != _fingerprint(current):
                    raise CaptureUnavailable(f"Declared extra input changed at {path}.")
                return data, bool(before.st_mode & stat.S_IXUSR)
    except OSError as error:
        raise CaptureUnavailable(
            f"Cannot read a contained regular extra file at {path}."
        ) from error


def _write(root: Path, path: str, data: bytes, executable: bool) -> None:
    target = root.joinpath(*PurePosixPath(path).parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as stream:
        stream.write(data)
    target.chmod(0o555 if executable else 0o444)


def _entry(
    path: str, origin: Literal["tracked", "extra"], data: bytes, executable: bool
) -> CapturedInput:
    return CapturedInput(
        path=path, origin=origin, digest=sha256(data).hexdigest(), executable=executable
    )


def _stable_extras(installation, binding, declarations, tracked, expected):
    paths = _extra_paths(installation, declarations) - tracked
    if paths != expected.keys():
        raise CaptureUnavailable("Declared extra input membership changed.")
    for path in paths:
        data, executable = _read_extra(Path(binding.worktree), path)
        if _entry(path, "extra", data, executable) != expected[path]:
            raise CaptureUnavailable(f"Declared extra input changed at {path}.")


def _seal(root: Path) -> None:
    for directory, _, _ in os.walk(root, topdown=False):
        Path(directory).chmod(0o555)


def _discard(directory: Path) -> None:
    for path, _, _ in os.walk(directory):
        Path(path).chmod(0o700)
    shutil.rmtree(directory)


def _manifest(
    installation: Installation,
    binding: Binding,
    policy: PolicySnapshot,
    source: SourceSnapshot,
    output_roots: tuple[str, ...],
    entries: tuple[CapturedInput, ...],
) -> CaptureManifest:
    assert isinstance(binding.scope, StoryRef)
    return CaptureManifest(
        authority_store=installation.store.store_uuid,
        story=binding.scope.story,
        attempt=binding.attempt,
        binding=binding.identity,
        generation=binding.generation,
        branch=binding.branch,
        source=source,
        policy=SourceSnapshot(commit=policy.revision, tree=policy.tree),
        policy_digest=policy.source.digest,
        declarations=tuple(policy.config.test.inputs),
        output_roots=output_roots,
        entries=entries,
    )


def capture_inputs(
    installation: Installation,
    binding: Binding,
    policy: PolicySnapshot,
    *,
    parent: Path | None = None,
    output_roots: tuple[str, ...] = (),
) -> CapturedInputs:
    """Copy and seal inputs from the exact bound worktree without admitting execution."""
    directory = None
    try:
        parent = (parent if parent is not None else Path(gettempdir())).resolve(
            strict=True
        )
        _outside_worktrees(installation, parent)
        roots = tuple(sorted({_relative(root) for root in output_roots}))
        declarations = tuple(policy.config.test.inputs)
        with Workspace(installation).lock():
            source = _source(installation, binding, policy)
            tracked = _tracked(installation, source)
            extras = _extra_paths(installation, declarations) - tracked.keys()
            for path in {*tracked, *extras}:
                _check_outputs(path, roots)
            directory = Path(mkdtemp(prefix="aitm-capture-", dir=parent))
            exported = directory / "source"
            exported.mkdir()
            entries = {}
            for entry, data in _tracked_files(installation, source, tracked):
                _write(exported, entry.path, data, entry.executable)
                entries[entry.path] = entry
            for path in sorted(extras):
                data, executable = _read_extra(Path(binding.worktree), path)
                _write(exported, path, data, executable)
                entries[path] = _entry(path, "extra", data, executable)
            _stable_extras(
                installation,
                binding,
                declarations,
                tracked.keys(),
                {path: entries[path] for path in extras},
            )
            if _source(installation, binding, policy) != source:
                raise CaptureUnavailable("The exact source changed during capture.")
            manifest = _manifest(
                installation,
                binding,
                policy,
                source,
                roots,
                tuple(entries[path] for path in sorted(entries)),
            )
            _write(directory, "manifest.json", manifest.content, False)
            _seal(exported)
            return CapturedInputs(directory, manifest)
    except (OSError, GitCommandError, ValueError) as error:
        if directory is not None:
            _discard(directory)
        raise CaptureUnavailable(str(error)) from error


def _check_export(capture: CapturedInputs) -> bool:
    root = capture.source_directory
    if not stat.S_ISDIR(root.lstat().st_mode):
        return False
    files = set()
    expected_directories = {
        part.as_posix()
        for entry in capture.manifest.entries
        for part in PurePosixPath(entry.path).parents
        if part.parts
    }
    found_directories = set()

    def fail(error):
        raise error

    for parent, directories, names in os.walk(root, onerror=fail):
        base = Path(parent)
        for name in directories:
            child = base / name
            mode = child.lstat().st_mode
            if not stat.S_ISDIR(mode) or mode & 0o222:
                return False
            found_directories.add(child.relative_to(root).as_posix())
        files.update((base / name).relative_to(root).as_posix() for name in names)
    if (
        files != {entry.path for entry in capture.manifest.entries}
        or found_directories != expected_directories
        or root.stat().st_mode & 0o222
    ):
        return False
    for entry in capture.manifest.entries:
        state = (root / entry.path).lstat()
        data = read_workspace(root, entry.path)
        if (
            not stat.S_ISREG(state.st_mode)
            or state.st_nlink != 1
            or stat.S_IMODE(state.st_mode) != (0o555 if entry.executable else 0o444)
            or data is None
            or sha256(data).hexdigest() != entry.digest
        ):
            return False
    return True


def capture_applicable(
    installation: Installation,
    binding: Binding,
    policy: PolicySnapshot,
    capture: CapturedInputs,
    *,
    output_roots: tuple[str, ...] | None = None,
) -> bool:
    """Recheck exact current inputs and the sealed export for downstream admission."""
    try:
        source = _source(installation, binding, policy)
        manifest = capture.manifest
        roots = manifest.output_roots if output_roots is None else output_roots
        roots = tuple(sorted({_relative(root) for root in roots}))
        receipt = (capture.directory / "manifest.json").lstat()
        if (
            capture.directory.resolve(strict=True) != capture.directory
            or not stat.S_ISDIR(capture.directory.lstat().st_mode)
            or capture.directory.stat().st_mode & 0o077
            or not stat.S_ISREG(receipt.st_mode)
            or receipt.st_nlink != 1
            or stat.S_IMODE(receipt.st_mode) != 0o444
            or manifest
            != _manifest(installation, binding, policy, source, roots, manifest.entries)
            or read_workspace(capture.directory, "manifest.json") != manifest.content
            or not _check_export(capture)
        ):
            return False
        _outside_worktrees(installation, capture.directory)
        tracked = _tracked(installation, source)
        original = {
            entry.path: entry for entry in manifest.entries if entry.origin == "tracked"
        }
        if original.keys() != tracked.keys() or any(
            pinned != original[pinned.path]
            for pinned, _ in _tracked_files(installation, source, tracked)
        ):
            return False
        for entry in manifest.entries:
            _check_outputs(entry.path, roots)
        extras = {
            entry.path: entry for entry in manifest.entries if entry.origin == "extra"
        }
        _stable_extras(
            installation, binding, manifest.declarations, tracked.keys(), extras
        )
        return _source(installation, binding, policy) == source
    except (OSError, GitCommandError, ValueError):
        return False
