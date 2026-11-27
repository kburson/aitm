"""Install cooperative Git hook backstops in the configured hooks directory."""

import os
import subprocess
import sys
from dataclasses import dataclass
from errno import ENOEXEC
from pathlib import Path
from shlex import quote, split
from stat import S_IMODE
from tempfile import NamedTemporaryFile

from aitm_core.models.common import LocalOutcome
from aitm_core.setup.journal import state_directory
from aitm_core.store.git_backend import ValidationRejected
from aitm_core.store.installation import Installation
from aitm_core.store.objects import GitCommandError, Repository
from aitm_core.store.validation import validate_history

NAMES = ("pre-commit", "pre-merge-commit", "pre-push")
MARKER = b"#!/bin/sh\n# AITM Core managed hook v1\n"
ROOT_IGNORE = b"/.aitm/"
IGNORE_COMMANDS = (
    "git add -- .gitignore",
    'git commit -m "Ignore root AITM workspace data" -- .gitignore',
)


@dataclass(frozen=True, slots=True)
class HookReport:
    path: Path
    installed: tuple[str, ...]
    chained: tuple[str, ...]


def _hooks_directory(repo: Repository) -> Path:
    return Path(
        os.fsdecode(
            repo._git(
                "rev-parse", "--path-format=absolute", "--git-path", "hooks"
            ).removesuffix(b"\n")
        )
    )


def _backup(path: Path) -> Path:
    return path.with_name(f".{path.name}.aitm-original")


def _wrapper(name: str) -> bytes:
    return (
        MARKER
        + (
            f'exec {quote(sys.executable)} -m aitm_core.setup.hooks {name} "$0" "$@"\n'
        ).encode()
    )


def _owned(path: Path, name: str) -> bool:
    if path.is_symlink() or not path.is_file() or not os.access(path, os.X_OK):
        return False
    payload = path.read_bytes()
    suffix = f' -m aitm_core.setup.hooks {name} "$0" "$@"\n'.encode()
    if not payload.startswith(MARKER) or not payload.endswith(suffix):
        return False
    try:
        prefix = payload[len(MARKER) : -len(suffix)].decode()
        command, interpreter = split(prefix)
    except (ValueError, UnicodeError):
        return False
    return (
        command == "exec"
        and Path(interpreter).is_absolute()
        and prefix == f"exec {quote(interpreter)}"
    )


def _atomic_replace(path: Path, data: bytes, mode: int) -> None:
    with NamedTemporaryFile(dir=path.parent, delete=False) as output:
        temp = Path(output.name)
        try:
            output.write(data)
            output.flush()
            os.fchmod(output.fileno(), mode)
            os.fsync(output.fileno())
            temp.replace(path)
        finally:
            temp.unlink(missing_ok=True)


def install_hooks(repo: Repository) -> HookReport:
    """Keep core.hooksPath and every original hook, then activate an exact wrapper."""
    import fcntl

    directory = _hooks_directory(repo)
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / ".aitm-install.lock").open("a+b") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        for name in NAMES:
            path = directory / name
            original = _backup(path)
            if _owned(path, name):
                if path.read_bytes() != _wrapper(name):
                    _atomic_replace(path, _wrapper(name), 0o755)
                continue
            if path.is_symlink() or (path.exists() and not path.is_file()):
                raise ValueError(f"Cannot safely chain the non-regular hook at {path}.")
            if path.exists() and path.read_bytes().startswith(MARKER):
                raise ValueError(
                    f"Repair or remove the changed AITM hook at {path} before reinstalling."
                )
            if original.exists() or original.is_symlink():
                if (
                    original.is_symlink()
                    or not path.exists()
                    or not path.samefile(original)
                ):
                    raise ValueError(f"Hook backup already exists at {original}.")
            elif path.exists():
                # A link preserves mode and contents, and the original remains active
                # if initialization stops before the atomic wrapper replacement.
                os.link(path, original)
            _atomic_replace(path, _wrapper(name), 0o755)
    return inspect_hooks(repo)


def inspect_hooks(repo: Repository) -> HookReport:
    directory = _hooks_directory(repo)
    installed = tuple(name for name in NAMES if _owned(directory / name, name))
    chained = tuple(
        name for name in installed if os.access(_backup(directory / name), os.X_OK)
    )
    return HookReport(directory, installed, chained)


def ignore_proposal(content: bytes) -> bytes:
    if ROOT_IGNORE in content.splitlines():
        return content
    newline = b"\r\n" if b"\r\n" in content else b"\n"
    boundary = newline if content and not content.endswith(newline) else b""
    return content + boundary + ROOT_IGNORE + newline


def prepare_ignore(repo: Repository) -> bool:
    path = repo.root / ".gitignore"
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValueError("Cannot safely update a non-regular root .gitignore.")
    original = path.read_bytes() if path.exists() else b""
    result = ignore_proposal(original)
    if result == original:
        return False
    mode = S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    _atomic_replace(path, result, mode)
    return True


def ignore_landing_commands(repo: Repository) -> tuple[str, ...]:
    path = ".gitignore"
    head = repo._git("rev-parse", "--verify", "HEAD").strip().decode()
    committed = repo.read_blobs(repo.read_tree(head).tree, (path,))[path]
    return IGNORE_COMMANDS if (repo.root / path).read_bytes() != committed else ()


def push_updates(
    data: bytes, planning_ref: str, oid_length: int
) -> tuple[tuple[str, str], ...]:
    """Parse Git's four-column pre-push protocol and select the literal target."""
    import re

    updates = []
    for row in data.splitlines():
        columns = row.split()
        if len(columns) != 4:
            raise ValueError("Malformed Git pre-push update.")
        _, local, target, remote = columns
        if target != planning_ref.encode():
            continue
        for oid in (local, remote):
            if not re.fullmatch(rb"[0-9a-f]{%d}" % oid_length, oid):
                raise ValueError("Malformed Git pre-push object identity.")
        updates.append((local.decode(), remote.decode()))
    return tuple(updates)


def _guard(installation: Installation, hook: str, data: bytes) -> None:
    repo = installation.repository
    target = installation.store.planning_ref
    if hook != "pre-push":
        head = repo._run("symbolic-ref", "-q", "HEAD")
        if head.returncode not in (0, 1):
            raise GitCommandError("symbolic-ref", head.stderr)
        if head.stdout.strip() == target.encode():
            raise ValidationRejected(
                f"Ordinary commits to the planning ref {target} are refused."
            )
        return
    zero = "0" * repo.oid_length
    for new, old in push_updates(data, target, repo.oid_length):
        if new == zero:
            raise ValidationRejected(
                f"Deletion of the planning ref {target} is refused."
            )
        if (
            old != zero
            and repo._run("merge-base", "--is-ancestor", old, new).returncode
        ):
            raise ValidationRejected(
                f"Planning ref {target} requires a proven fast-forward."
            )
        anchor = installation.store
        if installation.validated_code_ref is not None:
            anchor = anchor.model_copy(
                update={"code_default_ref": installation.validated_code_ref}
            )
        report = validate_history(anchor, new, repository=repo)
        if report.outcome != LocalOutcome.COMPLETED:
            raise ValidationRejected(
                f"Invalid planning ref update. {report.reason or report.outcome}"
            )


class GitHooks:
    def install(self, context: Installation) -> tuple[str, ...]:
        repo = context.repository
        report = install_hooks(repo)
        head = repo._run("symbolic-ref", "-q", "HEAD")
        commands = ()
        if head.stdout.strip() == context.store.code_default_ref.encode():
            prepare_ignore(repo)
            commands = ignore_landing_commands(repo)
        return (
            f"Installed AITM Git hooks in {report.path}.",
            *(f"Chained existing {name} hook." for name in report.chained),
            *commands,
        )


def _execute(hook: str, wrapper: Path, arguments: list[str]) -> int:
    from aitm_core.setup.init import _active_installation

    repo = Repository(Path.cwd(), "refs/heads/aitm-hook-probe")
    data = sys.stdin.buffer.read() if hook == "pre-push" else b""
    descriptor = state_directory(repo) / "installation.json"
    if descriptor.exists() or descriptor.is_symlink():
        installation, _ = _active_installation(repo)
        _guard(installation, hook, data)
    original = _backup(wrapper)
    if not os.access(original, os.X_OK) or not original.is_file():
        return 0
    # Keep real Git arguments, environment and stdin for foreign hooks.
    command = [str(original.absolute()), *arguments]
    supplied = data if hook == "pre-push" else None
    try:
        return subprocess.run(command, input=supplied, check=False).returncode
    except OSError as error:
        if error.errno != ENOEXEC:
            raise
        return subprocess.run(
            ["/bin/sh", *command], input=supplied, check=False
        ).returncode


def main() -> int:
    hook, wrapper, *arguments = sys.argv[1:]
    if hook not in NAMES:
        return 1
    try:
        return _execute(hook, Path(wrapper), arguments)
    except (ValueError, OSError, GitCommandError, ValidationRejected) as error:
        print(f"AITM hook refused. {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
