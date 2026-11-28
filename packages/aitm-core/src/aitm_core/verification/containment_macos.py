"""Qualify and run macOS contained verification with the system sandbox helper."""

import os
import subprocess
import sys
from dataclasses import replace
from json import dumps
from pathlib import Path
from tempfile import TemporaryDirectory

from aitm_core.verification.lanes import (
    CapturedExport,
    ContainmentCapability,
    LaunchResources,
    ProcessLaunch,
)

SANDBOX = Path("/usr/bin/sandbox-exec")
SYSTEM_READS = tuple(
    Path(root)
    for root in (
        "/System/Library",
        "/System/Volumes/Preboot/Cryptexes/OS",
        "/usr/lib",
        "/usr/bin",
        "/bin",
    )
)
SYSTEM_FILES = tuple(
    Path(path) for path in ("/dev/null", "/dev/urandom", "/dev/random")
)
PROBE = """\
import errno
import socket
import subprocess
import sys
from pathlib import Path

output, external = map(Path, sys.argv[1:])
output.write_text("sandbox-active")
child = subprocess.run(
    (sys.executable, "-B", "-c", "import errno, sys; "
     "p = sys.argv[1]; "
     "from pathlib import Path; "
     "Path(p).stat()", str(external)),
    capture_output=True,
)
if not child.returncode or b"PermissionError" not in child.stderr:
    raise SystemExit(11)
try:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
except OSError as error:
    if error.errno not in (errno.EACCES, errno.EPERM):
        raise
else:
    raise SystemExit(12)
"""


def _path_rule(kind: str, path: Path) -> str:
    if (
        not path.is_absolute()
        or path == Path("/")
        or any(
            part == ".." or any(ord(character) < 32 for character in part)
            for part in path.parts
        )
    ):
        raise ValueError("macOS containment needs absolute, bounded profile paths.")
    return f"({kind} {dumps(str(path), ensure_ascii=False)})"


def macos_profile(
    read_roots: tuple[Path, ...], write_root: Path, individual_files: tuple[Path, ...]
) -> str:
    """Build a deny-default profile over explicitly named source and runtime roots."""
    if any(
        root.is_relative_to(write_root) or write_root.is_relative_to(root)
        for root in (*read_roots, *SYSTEM_READS, *individual_files, *SYSTEM_FILES)
    ):
        raise ValueError("macOS containment needs disjoint input and output paths.")
    output = _path_rule("subpath", write_root)
    reads = " ".join(
        (
            *(
                _path_rule("subpath", root)
                for root in (*SYSTEM_READS, *read_roots, write_root)
            ),
            *(
                _path_rule("literal", path)
                for path in (*SYSTEM_FILES, *individual_files)
            ),
        )
    )
    ancestors = sorted(
        {
            ancestor
            for root in (
                *read_roots,
                write_root,
                *individual_files,
                *SYSTEM_READS,
                *SYSTEM_FILES,
            )
            for ancestor in root.parents
            if ancestor != Path("/")
        }
    )
    metadata = " ".join(_path_rule("literal", path) for path in ancestors)
    return (
        "(version 1)\n"
        "(deny default)\n"
        "(deny network*)\n"
        # Recent macOS dyld opens the root directory while locating its shared cache.
        '(allow file-read-data (literal "/"))\n'
        "(allow process-exec process-fork sysctl-read)\n"
        f'(allow file-read-metadata (literal "/") {metadata} {reads})\n'
        f"(allow file-read-data file-map-executable {reads})\n"
        f"(allow file-write* {output})\n"
        '(allow file-write-data (literal "/dev/null"))\n'
    )


def probe_macos(helper: Path = SANDBOX) -> ContainmentCapability:
    label = "macOS sandbox-exec"
    if sys.platform != "darwin":
        return ContainmentCapability(None, f"{label} requires an actual macOS host.")
    if not os.access(helper, os.X_OK):
        return ContainmentCapability(None, f"{label} is missing or not executable.")
    try:
        with TemporaryDirectory(prefix="aitm-macos-probe-") as directory:
            base = Path(directory).resolve()
            output = base / "output"
            output.mkdir()
            external = base / "private.txt"
            external.write_text("outside the permitted roots")
            python = Path(sys.executable).resolve(strict=True)
            library = Path(sys.base_prefix).resolve(strict=True)
            proof = output / "proof"
            profile = macos_profile((library,), output, (python,))
            outcome = subprocess.run(
                (helper, "-p", profile, python, "-B", "-c", PROBE, proof, external),
                cwd=output,
                env={"PATH": os.defpath, "HOME": str(output), "TMPDIR": str(output)},
                capture_output=True,
                timeout=10,
                check=False,
            )
            if outcome.returncode == 0 and proof.read_text() == "sandbox-active":
                return ContainmentCapability("contained", f"{label} qualified.")
            return ContainmentCapability(
                None, f"{label} probe failed (exit {outcome.returncode})."
            )
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        return ContainmentCapability(
            None, f"{label} probe unavailable: {type(error).__name__}."
        )


class MacOSLane:
    def probe(self) -> ContainmentCapability:
        return probe_macos()

    def command(self, resources: LaunchResources) -> ProcessLaunch:
        scratch = resources.scratch.resolve(strict=True)
        launch = CapturedExport().command(replace(resources, scratch=scratch))
        runtime = resources.environment
        tools = runtime.receipt.identity.tools
        python = Path(tools.python).resolve(strict=True)
        installer = Path(tools.installer).resolve(strict=True)
        profile = macos_profile(
            (
                launch.cwd.resolve(strict=True),
                runtime.directory.resolve(strict=True),
                python.parent.parent,
            ),
            scratch,
            (python, installer),
        )
        return replace(launch, argv=(str(SANDBOX), "-p", profile, *launch.argv))


def adapter() -> MacOSLane:
    return MacOSLane()
