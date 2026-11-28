"""Apply a portable, single-document Git text patch in a private workspace."""

import os
import re
import subprocess
from collections.abc import Iterator
from pathlib import Path

_INDEX = re.compile(rb"index [0-9a-f]+\.\.[0-9a-f]+(?: 100644)?")
_HUNK = re.compile(rb"@@ -[0-9]+(?:,([0-9]+))? \+[0-9]+(?:,([0-9]+))? @@(?: .*)?")
_NO_NEWLINE = b"\\ No newline at end of file"


def _git_name(prefix: str, artifact: str) -> tuple[bytes, ...]:
    name = f"{prefix}/{artifact}".encode()
    escaped = b"".join(
        f"\\{value:03o}".encode() if value >= 128 else bytes((value,)) for value in name
    )
    if escaped != name:
        return (name, b'"' + escaped + b'"')
    return (name,)


def _validate_hunks(lines: Iterator[bytes]) -> None:
    line = next(lines, None)
    if line is None:
        raise ValueError("expected at least one text hunk")
    while line is not None:
        match = _HUNK.fullmatch(line)
        if match is None:
            raise ValueError("unexpected text outside a patch hunk")
        old_count, new_count = (int(value or b"1") for value in match.groups())
        line = next(lines, None)
        while old_count or new_count:
            if line is None or line[:1] not in (b" ", b"+", b"-"):
                raise ValueError("incomplete text hunk")
            old_count -= line[:1] != b"+"
            new_count -= line[:1] != b"-"
            if old_count < 0 or new_count < 0:
                raise ValueError("text hunk exceeds declared line counts")
            line = next(lines, None)
            if line == _NO_NEWLINE:
                line = next(lines, None)


def validate_patch(raw: bytes, artifact: str, *, create: bool) -> None:
    """Accept only creation or edits of the manifest's regular document."""
    if not raw and not create:
        return
    if not raw.endswith(b"\n") or b"\x00" in raw:
        raise ValueError("expected a Git text patch")
    lines = iter(raw[:-1].split(b"\n"))
    old_names, new_names = _git_name("a", artifact), _git_name("b", artifact)
    headers = {
        b"diff --git " + old + b" " + new for old, new in zip(old_names, new_names)
    }
    if next(lines, None) not in headers:
        raise ValueError("patch must target only the manifest artifact")
    line = next(lines, b"")
    if create:
        if line != b"new file mode 100644":
            raise ValueError("base patch must create a regular nonexecutable document")
        line = next(lines, b"")
    if _INDEX.fullmatch(line):
        line = next(lines, b"")
    before = (b"/dev/null",) if create else old_names
    after = next(lines, b"")
    if line.removeprefix(b"--- ").removesuffix(
        b"\t"
    ) not in before or not line.startswith(b"--- "):
        raise ValueError("unexpected old patch path or file mode")
    if after.removeprefix(b"+++ ").removesuffix(
        b"\t"
    ) not in new_names or not after.startswith(b"+++ "):
        raise ValueError("unexpected new patch path")
    _validate_hunks(lines)


def apply_patch(workspace: Path, artifact: str, raw: bytes) -> None:
    """Replay validated patch bytes without discovering a caller's repository or config."""
    result = subprocess.run(
        ["git", "apply", "--whitespace=nowarn", "--", "-"],
        cwd=workspace,
        input=raw,
        capture_output=True,
        check=False,
        env={
            "PATH": os.environ.get("PATH", os.defpath),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CEILING_DIRECTORIES": str(workspace.parent),
            "LC_ALL": "C",
        },
    )
    if result.returncode:
        raise ValueError(
            f"Git apply rejected {artifact}: {result.stderr.decode(errors='replace').strip()}"
        )
