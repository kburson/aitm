"""Owned macOS LaunchAgent lifecycle and exact, offline wheel environments."""

import ctypes
import hashlib
import io
import json
import os
import plistlib
import pwd
import re
import shlex
import shutil
import sqlite3
import stat
import subprocess
import time
from collections.abc import Iterator
from contextlib import ExitStack, contextmanager
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime, timedelta
from email.parser import BytesParser
from functools import cache
from pathlib import Path
from secrets import token_hex
from uuid import UUID, uuid4
from xml.parsers.expat import ExpatError
from zipfile import BadZipFile, ZipFile

from .backup import (
    BackupReceipt,
    RestoreReceipt,
    _require_outside,
    _restore_stopped,
    backup,
    verify_backup,
)
from .ledger import (
    APPLICATION_ID,
    SCHEMA_VERSION,
    Ledger,
    LedgerError,
    WriterActive,
    _check_acl,
    _ensure_private_directory,
    _guard_path,
    _lease,
    _path_exists,
    _path_id,
    _pin_directory,
    _PinnedPath,
    _private,
    _supported_schema,
    _validated_path,
    project_guard,
)
from .scopes import _publish, _read_private
from .service import _read_status, load_registration, status_report
from .types import Registration

_VERSIONS = "versions"
_WHEELS = "wheels"
_BACKUPS = "service-backups"
_RUNTIME = "runtime.json"
_RUNTIME_FORMAT = "isolated-pure-wheel-v1"
_POLL_INTERVAL = 15
_VERSION = r"[0-9]{1,8}(?:\.[0-9]{1,8}){2}[a-z0-9.+-]{0,32}"
_DIGEST = r"[0-9a-f]{64}"
_VERSION_DIR = re.compile(rf"({_VERSION})-({_DIGEST})")
_WHEEL_NAME = re.compile(rf"aitm_usage-({_VERSION})-py3-none-any\.whl")
_RUNTIME_DIR = re.compile(r"venv-[0-9a-f]{32}")
_WHEEL_LIMIT = 64 * 1024 * 1024
_COMMAND_TIMEOUT = 120
_STOP_TIMEOUT = 10
_ENVIRONMENT = {
    "LC_ALL": "C",
    "PATH": "/usr/bin:/bin",
}
_FAILURES = (
    LedgerError,
    OSError,
    ValueError,
    sqlite3.Error,
    subprocess.SubprocessError,
)
_PROBE = """
import hashlib
import json
import platform
import sys
from importlib.metadata import distribution, distributions

site = sys.argv[1]
sys.path.insert(0, site)
from aitm_usage import service
from aitm_usage.ledger import APPLICATION_ID, SCHEMA_VERSION, _supported_schema

package = distribution('aitm-usage')
schema = json.dumps(_supported_schema(), separators=(',', ':')).encode()
print(json.dumps({
    'version': package.version,
    'interpreter_version': platform.python_version(),
    'interpreter': sys.executable,
    'schema': [APPLICATION_ID, SCHEMA_VERSION, hashlib.sha256(schema).hexdigest()],
    'packages': sorted(item.metadata['Name'] for item in distributions(path=[site])),
    'witness_capable': {'producer_mode', 'producer_pid'} <= service._Status.__dataclass_fields__.keys(),
    'entry_points': [[point.group, point.name, point.value] for point in package.entry_points],
}))
"""
_CREATE_VENV = """
import os
import sys
import venv
from pathlib import Path

class CollectorEnv(venv.EnvBuilder):
    def setup_python(self, context):
        os.symlink(sys.executable, Path(context.bin_path) / 'python')

    def setup_scripts(self, context):
        pass

    def create_configuration(self, context):
        (Path(context.env_dir) / 'pyvenv.cfg').write_text(sys.argv[2], encoding='utf-8')

CollectorEnv(symlinks=True).create(sys.argv[1])
"""
_RUN_CONSOLE = """
import sys
sys.path.insert(0, sys.argv.pop(1))
from aitm_usage.cli import main
raise SystemExit(main())
"""
_CONSOLE_ENTRY = b"[console_scripts]\naitm-usage = aitm_usage.cli:main\n"
_DIST_FILES = {"METADATA", "WHEEL", "entry_points.txt", "RECORD"}


class InstallError(LedgerError):
    """A sanitized lifecycle failure suitable for a CLI status."""

    def __init__(self, message: str, *, status: str | None = None):
        super().__init__(message)
        self.status = status


@dataclass(frozen=True, slots=True)
class LaunchJob:
    label: str
    plist: Path
    program: Path
    arguments: tuple[str, ...]
    pid: int | None


@dataclass(frozen=True, slots=True)
class _ProcessIdentity:
    pid: int
    started: datetime
    executable: Path


@dataclass(frozen=True, slots=True)
class _Health:
    heartbeat: str
    process: _ProcessIdentity


class _BSDProcessInfo(ctypes.Structure):
    # Darwin sys/proc_info.h, PROC_PIDTBSDINFO.
    _fields_ = [
        ("flags", ctypes.c_uint32),
        ("status", ctypes.c_uint32),
        ("xstatus", ctypes.c_uint32),
        ("pid", ctypes.c_uint32),
        ("parent_pid", ctypes.c_uint32),
        ("uid", ctypes.c_uint32),
        ("credentials", ctypes.c_uint32 * 6),
        ("command", ctypes.c_char * 16),
        ("name", ctypes.c_char * 32),
        ("terminal_and_priority", ctypes.c_uint32 * 6),
        ("start_seconds", ctypes.c_uint64),
        ("start_microseconds", ctypes.c_uint64),
    ]


@cache
def _libproc() -> ctypes.CDLL:
    library = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True)
    library.proc_pidinfo.argtypes = [
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_uint64,
        ctypes.c_void_p,
        ctypes.c_int,
    ]
    library.proc_pidinfo.restype = ctypes.c_int
    library.proc_pidpath.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32]
    library.proc_pidpath.restype = ctypes.c_int
    return library


def _process_identity(pid: int) -> _ProcessIdentity | None:
    if type(pid) is not int or not 0 < pid < 2**31:
        return None
    try:
        library = _libproc()

        def incarnation() -> tuple[int, int] | None:
            info = _BSDProcessInfo()
            size = ctypes.sizeof(info)
            if (
                library.proc_pidinfo(pid, 3, 0, ctypes.byref(info), size) != size
                or info.pid != pid
                or info.uid != os.geteuid()
                or info.status == 5  # SZOMB
                or not info.start_seconds
                or info.start_microseconds >= 1_000_000
            ):
                return None
            return info.start_seconds, info.start_microseconds

        before = incarnation()
        buffer = ctypes.create_string_buffer(4096)  # PROC_PIDPATHINFO_MAXSIZE
        if (
            before is None
            or library.proc_pidpath(pid, buffer, len(buffer)) <= 0
            or incarnation() != before
        ):
            return None
        start = datetime.fromtimestamp(before[0], UTC) + timedelta(
            microseconds=before[1]
        )
        executable = Path(os.fsdecode(buffer.value)).resolve(strict=True)
        return _ProcessIdentity(pid, start, executable)
    except (AttributeError, OSError, ValueError, OverflowError, RuntimeError):
        return None


class LaunchControl:
    """The GUI launchd boundary. Unknown inspection results fail closed."""

    activation_timeout = 120

    @property
    def plist_directory(self) -> Path:
        return Path(pwd.getpwuid(os.geteuid()).pw_dir) / "Library" / "LaunchAgents"

    @property
    def domain(self) -> str:
        return f"gui/{os.geteuid()}"

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(
                ["/bin/launchctl", *args],
                env=_ENVIRONMENT,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (OSError, subprocess.SubprocessError):
            raise InstallError("Unable to inspect or control launchd") from None

    def _required(self, *args: str) -> str:
        result = self._run(*args)
        if result.returncode:
            raise InstallError("Unable to control the owned LaunchAgent")
        return result.stdout

    def job(self, label: str) -> LaunchJob | None:
        target = f"{self.domain}/{label}"
        result = self._run("print", target)
        if result.returncode:
            # Distinguish an absent service from an unavailable GUI domain or
            # an authorization/inspection failure on the project host.
            absent = (
                f'Could not find service "{label}" in domain for user gui: '
                f"{os.geteuid()}"
            )
            if result.returncode == 113 and absent in result.stderr.splitlines():
                return None
            raise InstallError("Unable to inspect the owned LaunchAgent")
        return _parse_job(target, label, result.stdout)

    def process(self, pid: int) -> _ProcessIdentity | None:
        return _process_identity(pid)

    def is_disabled(self, label: str) -> bool:
        data = self._required("print-disabled", self.domain)
        if not (
            data.strip().startswith("disabled services = {")
            and data.strip().endswith("}")
        ):
            raise InstallError("Unable to verify LaunchAgent enablement")
        states = re.findall(rf'^\s*"{re.escape(label)}" => (\w+)\s*$', data, re.M)
        if len(states) > 1 or (states and states[0] not in {"enabled", "disabled"}):
            raise InstallError("Unable to verify LaunchAgent enablement")
        return states == ["disabled"]

    def disable(self, label: str) -> None:
        self._required("disable", f"{self.domain}/{label}")

    def enable(self, label: str) -> None:
        self._required("enable", f"{self.domain}/{label}")

    def bootout(self, label: str) -> None:
        self._required("bootout", f"{self.domain}/{label}")

    def bootstrap(self, path: Path) -> None:
        self._required("bootstrap", self.domain, str(path))


def _parse_job(target: str, label: str, output: str) -> LaunchJob:
    if not output.startswith(f"{target} = {{\n"):
        raise InstallError("Unexpected LaunchAgent inspection format")

    def field(name: str) -> str:
        values = re.findall(rf"^\t{re.escape(name)} = ([^\n]+)$", output, re.M)
        if len(values) != 1:
            raise InstallError("Incomplete LaunchAgent inspection")
        return values[0]

    blocks = re.findall(r"^\targuments = \{\n((?:\t\t[^\n]+\n)+)\t\}$", output, re.M)
    pids = re.findall(r"^\tpid = ([1-9][0-9]*)$", output, re.M)
    if field("type") != "LaunchAgent" or len(blocks) != 1 or len(pids) > 1:
        raise InstallError("Unable to verify the loaded LaunchAgent")
    return LaunchJob(
        label,
        Path(field("path")),
        Path(field("program")),
        tuple(line[2:] for line in blocks[0].splitlines()),
        int(pids[0]) if pids and field("state") == "running" else None,
    )


@dataclass(frozen=True, slots=True)
class InstallReceipt:
    project_id: str
    label: str
    status: str
    version: str | None = None
    wheel_sha256: str | None = None
    interpreter_version: str | None = None
    heartbeat: str | None = None
    poll_interval_seconds: int = _POLL_INTERVAL
    backup: BackupReceipt | None = None
    backup_id: str | None = None
    producer_mode: str | None = None
    producer_pid: int | None = None
    producer_started: str | None = None

    def as_dict(self) -> dict:
        data = asdict(self)
        if self.backup is not None:
            data["backup"] = self.backup.as_dict()
        return data


@dataclass(frozen=True, slots=True)
class _Wheel:
    version: str
    digest: str
    data: bytes
    files: dict[Path, bytes]


@dataclass(frozen=True, slots=True)
class _Runtime:
    executable: Path
    version: str
    wheel_sha256: str
    interpreter_version: str
    interpreter: Path
    witness_capable: bool


def _absolute(path: Path) -> None:
    if (
        not path.is_absolute()
        or ".." in path.parts
        or not path.name
        or any(ch in str(path) for ch in ("\n", "\r", "\0"))
    ):
        raise InstallError("Expected an absolute canonical runtime path")


@contextmanager
def _open_parent(path: Path) -> Iterator[int]:
    _absolute(path)
    ancestry = _validated_path(
        path.with_name(".usage-parent-validation"), directory=False, allow_missing=True
    )
    if len(ancestry) != len(path.parents):
        raise InstallError("LaunchAgent or runtime ancestry is unavailable")
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        if _path_id(os.fstat(fd)) != ancestry[-1]:
            raise InstallError("LaunchAgent or runtime ancestry changed")
        yield fd
        if ancestry != _validated_path(
            path.with_name(".usage-parent-validation"),
            directory=False,
            allow_missing=True,
        ):
            raise InstallError("LaunchAgent or runtime ancestry changed")
    finally:
        os.close(fd)


def _read_owned(path: Path, *, private: bool, limit: int) -> bytes | None:
    with _open_parent(path) as parent:
        try:
            fd = os.open(
                path.name, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW, dir_fd=parent
            )
        except FileNotFoundError:
            return None
        with os.fdopen(fd, "rb") as file:
            info = os.fstat(fd)
            if private:
                _private(info)
            elif (
                not stat.S_ISREG(info.st_mode)
                or info.st_uid not in {0, os.geteuid()}
                or info.st_mode & 0o022
            ):
                raise InstallError("Unsafe runtime input")
            _check_acl(fd)
            data = file.read(limit + 1)
            current = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
            if (
                len(data) > limit
                or not os.path.samestat(info, current)
                or info.st_mtime_ns != current.st_mtime_ns
                or info.st_ctime_ns != current.st_ctime_ns
            ):
                raise InstallError("Runtime input changed or exceeds its limit")
            return data


def _wheel_metadata(path: Path, data: bytes) -> tuple[str, dict[Path, bytes]]:
    match = _WHEEL_NAME.fullmatch(path.name)
    if match is None:
        raise InstallError("Expected a supported aitm-usage wheel")
    version = match[1]
    metadata_dir = Path(f"aitm_usage-{version}.dist-info")
    files = {}
    directories = set()
    try:
        with ZipFile(io.BytesIO(data)) as archive:
            entries = archive.infolist()
            names = [entry.filename.rstrip("/") for entry in entries]
            if (
                len(entries) > 4096
                or len(names) != len({name.casefold() for name in names})
                or sum(entry.file_size for entry in entries) > _WHEEL_LIMIT
            ):
                raise InstallError("Unsupported wheel size or duplicate path")
            for entry, name in zip(entries, names, strict=True):
                parts = name.split("/")
                kind = stat.S_IFMT(entry.external_attr >> 16)
                if any(
                    not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.+-]*", part)
                    for part in parts
                ) or kind not in {0, stat.S_IFDIR if entry.is_dir() else stat.S_IFREG}:
                    raise InstallError("Unsupported wheel path")
                relative = Path(*parts)
                if entry.is_dir():
                    directories.add(relative)
                    continue
                if not (
                    (
                        len(parts) > 1
                        and parts[0] == "aitm_usage"
                        and relative.suffix in {".py", ".json"}
                    )
                    or (
                        relative.parent == metadata_dir and relative.name in _DIST_FILES
                    )
                ):
                    raise InstallError("Unsupported pure-wheel file")
                files[relative] = archive.read(entry)
    except (BadZipFile, RuntimeError, NotImplementedError) as error:
        if isinstance(error, InstallError):
            raise
        raise InstallError("Invalid aitm-usage wheel") from None

    if (
        not {Path("aitm_usage/__init__.py"), Path("aitm_usage/cli.py")} <= files.keys()
        or not directories <= {parent for entry in files for parent in entry.parents}
        or not {metadata_dir / name for name in _DIST_FILES} <= files.keys()
        or files[metadata_dir / "entry_points.txt"]
        not in {_CONSOLE_ENTRY, _CONSOLE_ENTRY + b"\n"}
    ):
        raise InstallError("Incomplete pure-wheel contents")
    metadata = BytesParser().parsebytes(files[metadata_dir / "METADATA"])
    tags = BytesParser().parsebytes(files[metadata_dir / "WHEEL"])
    if (
        metadata.get_all("Name") != ["aitm-usage"]
        or metadata.get_all("Version") != [version]
        or metadata.get_all("Requires-Python") != [">=3.13"]
        or metadata.get_all("Requires-Dist")
        or tags.get_all("Wheel-Version") != ["1.0"]
        or tags.get_all("Tag") != ["py3-none-any"]
        or tags.get_all("Root-Is-Purelib") != ["true"]
    ):
        raise InstallError("Unsupported wheel metadata")
    return version, files


def _wheel(path: Path, expected: str | None, *, private: bool = False) -> _Wheel:
    data = _read_owned(path, private=private, limit=_WHEEL_LIMIT)
    if data is None:
        raise InstallError("Required wheel is unavailable")
    digest = hashlib.sha256(data).hexdigest()
    if expected is not None and digest != expected:
        raise InstallError("Wheel digest does not match the approved artifact")
    version, files = _wheel_metadata(path, data)
    return _Wheel(version, digest, data, files)


def _run_python(python: Path, *args: str) -> str:
    result = subprocess.run(
        [str(python), "-I", "-S", "-B", *args],
        env=_ENVIRONMENT,
        capture_output=True,
        text=True,
        timeout=_COMMAND_TIMEOUT,
    )
    if result.returncode:
        raise InstallError("Pinned Python environment verification failed")
    return result.stdout


def _interpreter(python: Path) -> str:
    data = _read_owned(python, private=False, limit=_WHEEL_LIMIT)
    if data is None or not os.access(python, os.X_OK):
        raise InstallError("Pinned Python interpreter is unavailable")
    version = _run_python(
        python,
        "-c",
        "import platform,sys\n"
        "assert sys.version_info >= (3,13) and sys.prefix == sys.base_prefix\n"
        "assert sys.flags.no_site and sys.flags.isolated\n"
        "print(platform.python_version())",
    ).strip()
    if not re.fullmatch(_VERSION, version):
        raise InstallError("Unsupported pinned Python version")
    return version


def _runtime_layout(ledger: Ledger, executable: Path) -> tuple[Path, str, str]:
    _absolute(executable)
    environment = executable.parent.parent
    directory = environment.parent
    version = _VERSION_DIR.fullmatch(directory.name)
    if (
        directory.parent != ledger.root / _VERSIONS
        or version is None
        or not _RUNTIME_DIR.fullmatch(environment.name)
        or executable != environment / "bin" / "aitm-usage"
    ):
        raise InstallError("Executable is outside the owned version environment")
    return directory, version[1], version[2]


def _wheel_path(ledger: Ledger, version: str, digest: str) -> Path:
    return ledger.root / _WHEELS / digest / f"aitm_usage-{version}-py3-none-any.whl"


def _venv_config(interpreter: Path, version: str) -> bytes:
    return (
        f"home = {interpreter.parent}\n"
        "include-system-site-packages = false\n"
        f"version = {version}\n"
        f"executable = {interpreter}\n"
    ).encode()


def _minor(version: str) -> str:
    return ".".join(version.split(".")[:2])


def _site(environment: Path, version: str) -> Path:
    return environment / "lib" / f"python{_minor(version)}" / "site-packages"


def _launcher(python: Path, site: Path) -> bytes:
    argv = [
        "/usr/bin/env",
        "-i",
        *(f"{key}={value}" for key, value in _ENVIRONMENT.items()),
        str(python),
        "-I",
        "-S",
        "-B",
        "-c",
        _RUN_CONSOLE,
        str(site),
    ]
    return f'#!/bin/sh\nexec {shlex.join(argv)} "$@"\n'.encode()


def _write_runtime_file(
    path: Path, contents: bytes, *, executable: bool = False
) -> None:
    mode = 0o700 if executable else 0o600
    with _open_parent(path) as parent:
        fd = os.open(
            path.name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            mode,
            dir_fd=parent,
        )
        with os.fdopen(fd, "wb") as file:
            os.fchmod(fd, mode)
            _check_acl(fd)
            file.write(contents)
            file.flush()
            os.fsync(fd)
        os.fsync(parent)


def _inspect_surface(
    executable: Path, interpreter: Path, python_version: str, wheel: _Wheel
) -> Path:
    environment = executable.parent.parent
    python = executable.with_name("python")
    site = _site(environment, python_version)
    config = environment / "pyvenv.cfg"
    contents = {
        config: _venv_config(interpreter, python_version),
        executable: _launcher(python, site),
        **{site / path: data for path, data in wheel.files.items()},
    }
    directories = {environment / "include" / f"python{_minor(python_version)}", site}
    for path in (*contents, python, *directories):
        directories.update(
            parent for parent in path.parents if parent.is_relative_to(environment)
        )
    children = {directory: set() for directory in directories}
    for entry in (*contents, python, *directories):
        if entry != environment:
            children[entry.parent].add(entry.name)
    with _pin_directory(environment) as pinned:
        for directory, names in children.items():
            with _open_parent(directory / ".surface") as fd:
                if set(os.listdir(fd)) != names:
                    raise InstallError("Unexpected installed runtime entry")
        with _open_parent(python) as parent:
            info = os.stat(python.name, dir_fd=parent, follow_symlinks=False)
            if (
                not stat.S_ISLNK(info.st_mode)
                or info.st_uid != os.geteuid()
                or os.readlink(python.name, dir_fd=parent) != str(interpreter)
            ):
                raise InstallError(
                    "Runtime Python link is not the pinned base interpreter"
                )
        for path, expected in contents.items():
            if (
                _read_owned(
                    path, private=path.is_relative_to(site), limit=len(expected)
                )
                != expected
            ):
                raise InstallError(
                    "Installed runtime bytes differ from the approved wheel or launcher"
                )
        if not os.access(executable, os.X_OK):
            raise InstallError("Verified launcher is not executable")
        pinned.check()
    return site


def _probe_runtime(
    executable: Path, interpreter: Path, python_version: str, wheel: _Wheel
) -> _Runtime:
    site = _inspect_surface(executable, interpreter, python_version, wheel)
    python = executable.with_name("python")
    observed = json.loads(_run_python(python, "-c", _PROBE, str(site)))
    if not isinstance(observed, dict):
        raise InstallError("Invalid isolated runtime probe")
    witness_capable = observed.pop("witness_capable", None)
    schema_bytes = json.dumps(_supported_schema(), separators=(",", ":")).encode()
    expected = {
        "version": wheel.version,
        "interpreter_version": python_version,
        "interpreter": str(python),
        "packages": ["aitm-usage"],
        "schema": [
            APPLICATION_ID,
            SCHEMA_VERSION,
            hashlib.sha256(schema_bytes).hexdigest(),
        ],
        "entry_points": [["console_scripts", "aitm-usage", "aitm_usage.cli:main"]],
    }
    if observed != expected or type(witness_capable) is not bool:
        raise InstallError("Installed environment identity or schema is incompatible")
    console = subprocess.run(
        [str(executable), "--version"],
        env=_ENVIRONMENT,
        capture_output=True,
        text=True,
        timeout=10,
    )
    if console.returncode or console.stdout.strip() != f"aitm-usage {wheel.version}":
        raise InstallError("Installed console reports an unexpected package version")
    return _Runtime(
        executable,
        wheel.version,
        wheel.digest,
        python_version,
        interpreter,
        witness_capable,
    )


def _read_runtime(
    ledger: Ledger, directory: Path, *, interpreter: Path | None = None
) -> _Runtime:
    with _pin_directory(directory) as parent:
        raw = _read_private(parent, _RUNTIME)
    if raw is None:
        raise InstallError("Exact installed runtime receipt is missing")
    record = json.loads(raw)
    if (
        not isinstance(record, dict)
        or set(record)
        != {
            "format",
            "environment",
            "interpreter",
            "console_sha256",
            "interpreter_sha256",
        }
        or any(type(value) is not str for value in record.values())
        or record["format"] != _RUNTIME_FORMAT
        or raw != json.dumps(record, sort_keys=True).encode()
    ):
        raise InstallError("Installed runtime requires explicit recovery")
    environment = record["environment"]
    if not _RUNTIME_DIR.fullmatch(environment):
        raise InstallError("Invalid installed runtime directory")
    base = Path(record["interpreter"])
    if interpreter is not None and base != interpreter:
        raise InstallError("This wheel is already pinned to a different interpreter")
    executable = directory / environment / "bin" / "aitm-usage"
    _, version, digest = _runtime_layout(ledger, executable)
    retained = _wheel(_wheel_path(ledger, version, digest), digest, private=True)
    for path, field, limit in (
        (executable, "console_sha256", 8192),
        (base, "interpreter_sha256", _WHEEL_LIMIT),
    ):
        data = _read_owned(path, private=False, limit=limit)
        if data is None or hashlib.sha256(data).hexdigest() != record[field]:
            raise InstallError("Verified runtime files changed")
    return _probe_runtime(executable, base, _interpreter(base), retained)


def _prepare(ledger: Ledger, wheel: _Wheel, interpreter: Path) -> _Runtime:
    python_version = _interpreter(interpreter)
    retained = _wheel_path(ledger, wheel.version, wheel.digest)
    _ensure_private_directory(retained.parent)
    with _pin_directory(retained.parent) as parent:
        if not _path_exists(retained):
            _publish(parent, retained.name, wheel.data)
    _wheel(retained, wheel.digest, private=True)

    directory = ledger.root / _VERSIONS / f"{wheel.version}-{wheel.digest}"
    _ensure_private_directory(directory)
    with _pin_directory(directory) as parent:
        if _read_private(parent, _RUNTIME) is not None:
            return _read_runtime(ledger, directory, interpreter=interpreter)
        environment = directory / f"venv-{token_hex(16)}"
        environment.mkdir(mode=0o700)
        executable = environment / "bin" / "aitm-usage"
        python = executable.with_name("python")
        site = _site(environment, python_version)
        with _pin_directory(environment) as env:
            _run_python(
                interpreter,
                "-c",
                _CREATE_VENV,
                str(environment),
                _venv_config(interpreter, python_version).decode(),
            )
            env.check()
            # The approved wheel is pure Python with no dependencies or .data.
            # Its files already have their final relative site-packages paths.
            for path, data in wheel.files.items():
                destination = site / path
                _ensure_private_directory(destination.parent)
                _write_runtime_file(destination, data)
            launcher = _launcher(python, site)
            _write_runtime_file(executable, launcher, executable=True)
            runtime = _probe_runtime(executable, interpreter, python_version, wheel)
            base_bytes = _read_owned(interpreter, private=False, limit=_WHEEL_LIMIT)
            if base_bytes is None:
                raise InstallError("Base interpreter disappeared during preparation")
            record = {
                "format": _RUNTIME_FORMAT,
                "environment": environment.name,
                "interpreter": str(interpreter),
                "console_sha256": hashlib.sha256(launcher).hexdigest(),
                "interpreter_sha256": hashlib.sha256(base_bytes).hexdigest(),
            }
            env.check()
            if not _publish(
                parent, _RUNTIME, json.dumps(record, sort_keys=True).encode()
            ):
                raise InstallError("Version runtime was already published")
        return runtime


@dataclass(frozen=True, slots=True)
class _Agent:
    ledger: Ledger
    launchctl: LaunchControl

    @property
    def label(self) -> str:
        return f"org.aitm.usage.{self.ledger.identity.project_id}"

    @property
    def plist(self) -> Path:
        return self.launchctl.plist_directory / f"{self.label}.plist"

    def payload(self, executable: Path) -> dict:
        _runtime_layout(self.ledger, executable)
        return {
            "Label": self.label,
            "ProgramArguments": [
                str(executable),
                "--project",
                str(self.ledger.root),
                "service",
                "run",
            ],
            "RunAtLoad": True,
            "KeepAlive": True,
        }

    def program(self, data: bytes) -> Path:
        try:
            payload = plistlib.loads(data)
            executable = Path(payload["ProgramArguments"][0])
            if payload == self.payload(executable) and data == plistlib.dumps(payload):
                return executable
        except (
            plistlib.InvalidFileException,
            ExpatError,
            KeyError,
            TypeError,
            IndexError,
            ValueError,
        ):
            pass
        raise InstallError("LaunchAgent plist is not an owned registration")

    def read(self) -> bytes:
        _validated_path(self.plist, directory=False, allow_missing=True)
        if not _path_exists(self.plist.parent):
            return b""
        data = _read_owned(self.plist, private=True, limit=65536)
        if data is not None:
            self.program(data)
        return data or b""

    def write(self, data: bytes, expected: bytes) -> None:
        if data:
            self.program(data)
        if not _path_exists(self.plist.parent):
            _ensure_private_directory(self.plist.parent)
        with _open_parent(self.plist) as parent:
            if self.read() != expected:
                raise InstallError("LaunchAgent plist changed during the operation")
            if data:
                stage = f".usage-plist-{token_hex(16)}"
                fd = os.open(
                    stage,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                    0o600,
                    dir_fd=parent,
                )
                try:
                    with os.fdopen(fd, "wb") as stream:
                        _private(os.fstat(fd))
                        _check_acl(fd)
                        stream.write(data)
                        stream.flush()
                        os.fsync(fd)
                    os.replace(
                        stage, self.plist.name, src_dir_fd=parent, dst_dir_fd=parent
                    )
                finally:
                    try:
                        os.unlink(stage, dir_fd=parent)
                    except FileNotFoundError:
                        pass
            elif expected:
                os.unlink(self.plist.name, dir_fd=parent)
            os.fsync(parent)

    def inspect(self, *owned: bytes) -> LaunchJob | None:
        job = self.launchctl.job(self.label)
        if job is None:
            return None
        for data in owned:
            if data:
                executable = self.program(data)
                if (
                    job.label == self.label
                    and job.plist == self.plist
                    and job.program == executable
                    and job.arguments
                    == tuple(self.payload(executable)["ProgramArguments"])
                ):
                    return job
        raise InstallError("Loaded LaunchAgent does not match an owned registration")

    def stop(self, *owned: bytes) -> None:
        self.inspect(*owned)
        if not self.launchctl.is_disabled(self.label):
            self.launchctl.disable(self.label)
        if self.inspect(*owned) is not None:
            try:
                self.launchctl.bootout(self.label)
            except InstallError:
                if self.inspect(*owned) is not None:
                    raise
        deadline = time.monotonic() + _STOP_TIMEOUT
        while self.inspect(*owned) is not None:
            if time.monotonic() >= deadline:
                raise InstallError("LaunchAgent did not unload")
            time.sleep(0.1)
        self.require_stopped(disabled=True)

    def require_stopped(self, *, disabled: bool) -> None:
        if self.launchctl.job(self.label) is not None or (
            disabled and not self.launchctl.is_disabled(self.label)
        ):
            raise InstallError("LaunchAgent is not confirmed stopped")

    def healthy(
        self, runtime: _Runtime, plist: bytes, after: datetime
    ) -> _Health | None:
        job = self.inspect(plist)
        if not runtime.witness_capable or job is None or job.pid is None:
            return None
        process = self.launchctl.process(job.pid)
        if (
            process is None
            or process.pid != job.pid
            or process.executable != runtime.interpreter
        ):
            return None
        status = status_report(self.ledger.root, self.ledger)
        if (
            status["read_gap"] is not False
            or status["registration_gap"] is not False
            or status["status_sequence"] is None
            or status["collector_version"] != runtime.version
            or status["collector_interpreter_version"] != runtime.interpreter_version
            or status["producer_mode"] != "service"
            or type(status["producer_pid"]) is not int
            or status["producer_pid"] != job.pid
        ):
            return None
        raw = status["heartbeat"]
        if raw is None or not (
            max(after, process.started)
            < datetime.fromisoformat(raw)
            <= datetime.now(UTC)
        ):
            return None
        if self.read() != plist or _runtime_for(self, runtime.executable) != runtime:
            raise InstallError(
                "Launch registration or runtime changed during health verification"
            )
        if self.inspect(plist) != job or self.launchctl.process(job.pid) != process:
            return None
        return _Health(raw, process)

    def start(self, runtime: _Runtime, plist: bytes) -> _Health:
        if not runtime.witness_capable:
            raise InstallError("Runtime cannot provide service process evidence")
        if self.read() != plist or self.inspect(plist) is not None:
            raise InstallError("Unexpected LaunchAgent state before bootstrap")
        if _runtime_for(self, runtime.executable) != runtime:
            raise InstallError("Installed runtime changed before bootstrap")
        if self.launchctl.is_disabled(self.label):
            self.launchctl.enable(self.label)
        previous = _read_status(self.ledger.root)
        started = datetime.now(UTC)
        if previous is not None:
            started = max(started, previous.heartbeat)
        self.launchctl.bootstrap(self.plist)
        deadline = time.monotonic() + self.launchctl.activation_timeout
        while True:
            health = self.healthy(runtime, plist, started)
            if health is not None:
                return health
            if time.monotonic() >= deadline:
                raise InstallError(
                    "LaunchAgent did not provide a fresh compatible heartbeat"
                )
            time.sleep(0.2)


@dataclass(frozen=True, slots=True)
class _Operation:
    prior: bytes
    candidate: bytes
    was_loaded: bool
    was_disabled: bool
    backup_id: str
    backup_manifest: str

    def encode(self) -> bytes:
        return plistlib.dumps(asdict(self), fmt=plistlib.FMT_BINARY)

    @classmethod
    def decode(cls, data: bytes) -> "_Operation":
        record = cls(**plistlib.loads(data))
        if (
            type(record.prior) is not bytes
            or type(record.candidate) is not bytes
            or not record.candidate
            or type(record.was_loaded) is not bool
            or type(record.was_disabled) is not bool
            or type(record.backup_id) is not str
            or type(record.backup_manifest) is not str
            or (record.backup_id and str(UUID(record.backup_id)) != record.backup_id)
            or (
                record.backup_manifest
                and not re.fullmatch(_DIGEST, record.backup_manifest)
            )
            or (record.was_loaded and not record.prior)
            or (record.backup_manifest and not record.backup_id)
            or record.encode() != data
        ):
            raise InstallError("Invalid private interrupted-upgrade record")
        return record


@contextmanager
def _lifecycle(agent: _Agent) -> Iterator[tuple[_PinnedPath, _PinnedPath]]:
    lock = _guard_path(agent.ledger.root, agent.ledger.identity.project_id)
    with (
        _pin_directory(lock.parent) as directory,
        _lease(lock.with_name(lock.stem + ".service.lock"), create=True) as guard,
    ):
        yield directory, guard


@contextmanager
def _stopped_writer(agent: _Agent, operation_guard: _PinnedPath) -> Iterator[None]:
    ledger = agent.ledger
    deadline = time.monotonic() + _STOP_TIMEOUT
    with ExitStack() as stack:
        while True:
            agent.require_stopped(disabled=True)
            try:
                guard = stack.enter_context(
                    project_guard(ledger.root, ledger.identity.project_id)
                )
                local = stack.enter_context(_lease(ledger.lock_path))
            except WriterActive:
                stack.close()
                if time.monotonic() >= deadline:
                    raise
                time.sleep(0.1)
            else:
                break
        project = stack.enter_context(_pin_directory(ledger.root))
        agent.require_stopped(disabled=True)
        for pin in (guard, local, project, operation_guard):
            pin.check()
        if (
            Ledger.open(ledger.root, ledger.identity.project_id).identity
            != ledger.identity
        ):
            raise InstallError("Project identity changed during lifecycle operation")
        yield
        for pin in (guard, local, project, operation_guard):
            pin.check()


def _record_name(agent: _Agent) -> str:
    return f"{agent.ledger.identity.project_id}.service-recovery.plist"


def _clear_record(agent: _Agent, directory: _PinnedPath) -> None:
    directory.check()
    os.unlink(_record_name(agent), dir_fd=directory.fd)
    os.fsync(directory.fd)


def _runtime_for(agent: _Agent, executable: Path) -> _Runtime:
    directory, _, _ = _runtime_layout(agent.ledger, executable)
    runtime = _read_runtime(agent.ledger, directory)
    if runtime.executable != executable:
        raise InstallError("Plist executable disagrees with the installed runtime")
    return runtime


def _recover(agent: _Agent, directory: _PinnedPath, guard: _PinnedPath) -> None:
    raw = _read_private(directory, _record_name(agent))
    if raw is None:
        return
    try:
        operation = _Operation.decode(raw)
        agent.program(operation.candidate)
        current = agent.read()
        if current not in {operation.prior, operation.candidate}:
            raise InstallError("Current plist differs from the interrupted operation")
        prior = (
            _runtime_for(agent, agent.program(operation.prior))
            if operation.prior
            else None
        )
        if operation.backup_manifest:
            saved = verify_backup(
                agent.ledger.root / _BACKUPS / operation.backup_id, agent.ledger
            )
            if saved.manifest_sha256 != operation.backup_manifest:
                raise InstallError(
                    "Interrupted upgrade backup does not match its receipt"
                )
        if (
            prior is not None
            and not prior.witness_capable
            and current == operation.prior
        ):
            raise InstallError("Retained prior runtime requires explicit recovery")
        guard.check()
        agent.stop(operation.prior, operation.candidate)
        with _stopped_writer(agent, guard):
            if current != operation.prior:
                agent.write(operation.prior, current)
        if prior is not None and not prior.witness_capable:
            raise InstallError("Retained prior runtime requires explicit recovery")
        if operation.was_loaded:
            assert prior is not None
            agent.start(prior, operation.prior)
        if operation.was_disabled != agent.launchctl.is_disabled(agent.label):
            action = (
                agent.launchctl.disable
                if operation.was_disabled
                else agent.launchctl.enable
            )
            action(agent.label)
        guard.check()
        _clear_record(agent, directory)
    except (*_FAILURES, TypeError, ExpatError, plistlib.InvalidFileException):
        raise InstallError(
            "Private interrupted upgrade requires recovery", status="recovery-required"
        ) from None


def _receipt(
    agent: _Agent,
    status: str,
    runtime: _Runtime | None = None,
    *,
    health: _Health | None = None,
    saved: BackupReceipt | None = None,
    backup_id: str | None = None,
) -> InstallReceipt:
    return InstallReceipt(
        str(agent.ledger.identity.project_id),
        agent.label,
        status,
        None if runtime is None else runtime.version,
        None if runtime is None else runtime.wheel_sha256,
        None if runtime is None else runtime.interpreter_version,
        None if health is None else health.heartbeat,
        backup=saved,
        backup_id=backup_id,
        producer_mode=None if health is None else "service",
        producer_pid=None if health is None else health.process.pid,
        producer_started=None if health is None else health.process.started.isoformat(),
    )


def _activate(
    agent: _Agent,
    runtime: _Runtime,
    action: str,
    directory: _PinnedPath,
    guard: _PinnedPath,
) -> InstallReceipt:
    if not runtime.witness_capable:
        raise InstallError(
            "Candidate runtime cannot provide service process evidence",
            status="witness-unavailable",
        )
    previous = agent.read()
    prior_job = agent.inspect(previous)
    previous_program = agent.program(previous) if previous else None
    candidate = plistlib.dumps(agent.payload(runtime.executable))
    if previous_program == runtime.executable and prior_job is not None:
        oldest = datetime.now(UTC) - timedelta(seconds=3 * _POLL_INTERVAL)
        health = agent.healthy(runtime, previous, oldest)
        if health is not None:
            return _receipt(agent, "already-active", runtime, health=health)
    if action == "install" and previous_program not in (None, runtime.executable):
        raise InstallError("Use upgrade to replace a different installed wheel")
    if action == "upgrade" and previous_program is None:
        raise InstallError("Install an owned service before upgrading it")
    if (
        previous_program is not None
        and not _runtime_for(agent, previous_program).witness_capable
    ):
        raise InstallError(
            "Installed runtime cannot provide service process evidence",
            status="witness-unavailable",
        )

    saved = None
    backup_id = str(uuid4()) if action == "upgrade" else ""
    operation = _Operation(
        previous,
        candidate,
        prior_job is not None,
        agent.launchctl.is_disabled(agent.label),
        backup_id,
        "",
    )
    if not _publish(directory, _record_name(agent), operation.encode()):
        raise InstallError("Another lifecycle recovery record already exists")
    try:
        guard.check()
        agent.stop(previous)
        with _stopped_writer(agent, guard):
            if backup_id:
                backup_dir = agent.ledger.root / _BACKUPS
                _ensure_private_directory(backup_dir)
                saved = backup(agent.ledger, backup_dir / backup_id)
                operation = replace(operation, backup_manifest=saved.manifest_sha256)
                _publish(
                    directory,
                    _record_name(agent),
                    operation.encode(),
                    replace_pending=True,
                )
            agent.write(candidate, previous)
        health = agent.start(runtime, candidate)
    except _FAILURES:
        _recover(agent, directory, guard)
        raise InstallError(
            "Activation failed and previous registration was restored",
            status="activation-rolled-back",
        ) from None
    guard.check()
    _clear_record(agent, directory)
    return _receipt(
        agent,
        "upgraded" if action == "upgrade" else "installed",
        runtime,
        health=health,
        saved=saved,
        backup_id=backup_id or None,
    )


def _check_install_plan(agent: _Agent, action: str, wheel: _Wheel) -> None:
    previous = agent.read()
    agent.inspect(previous)
    if action == "upgrade" and not previous:
        raise InstallError("Install an owned service before upgrading it")
    if action == "install" and previous:
        _, version, digest = _runtime_layout(agent.ledger, agent.program(previous))
        if (version, digest) != (wheel.version, wheel.digest):
            raise InstallError("Use upgrade to replace a different installed wheel")


def install_agent(
    project: Registration, executable: Path, launchctl: LaunchControl
) -> InstallReceipt:
    """Apply an install for an already prepared, exact owned executable."""
    ledger = Ledger.open(project.state_root, project.project_id)
    if load_registration(ledger) != project:
        raise InstallError("Expected the current accepted project registration")
    agent = _Agent(ledger, launchctl)
    with _lifecycle(agent) as (directory, guard):
        _recover(agent, directory, guard)
        return _activate(
            agent, _runtime_for(agent, executable), "install", directory, guard
        )


def install_wheel(
    ledger: Ledger,
    wheel_path: Path,
    interpreter: Path,
    launchctl: LaunchControl,
    *,
    action: str,
    expected_sha256: str | None = None,
    dry_run: bool = False,
) -> InstallReceipt:
    """Plan or apply an install or upgrade from one exact local wheel."""
    if action not in {"install", "upgrade"}:
        raise InstallError("Unknown LaunchAgent installation action")
    load_registration(ledger)
    wheel = _wheel(wheel_path, expected_sha256)
    agent = _Agent(ledger, launchctl)
    if dry_run:
        version = _interpreter(interpreter)
        _check_install_plan(agent, action, wheel)
        return InstallReceipt(
            str(ledger.identity.project_id),
            agent.label,
            "planned",
            wheel.version,
            wheel.digest,
            version,
        )
    with _lifecycle(agent) as (directory, guard):
        _recover(agent, directory, guard)
        _check_install_plan(agent, action, wheel)
        runtime = _prepare(ledger, wheel, interpreter)
        return _activate(agent, runtime, action, directory, guard)


def stop_agent(
    ledger: Ledger,
    launchctl: LaunchControl,
    *,
    uninstall: bool = False,
    dry_run: bool = False,
) -> InstallReceipt:
    """Disable respawn and optionally remove only the owned plist."""
    agent = _Agent(ledger, launchctl)
    if dry_run:
        agent.inspect(agent.read())
        return _receipt(agent, "planned")
    with _lifecycle(agent) as (directory, guard):
        _recover(agent, directory, guard)
        previous = agent.read()
        agent.inspect(previous)
        if previous:
            guard.check()
            agent.stop(previous)
            with _stopped_writer(agent, guard):
                if uninstall:
                    agent.write(b"", previous)
    return _receipt(agent, "uninstalled" if uninstall else "stopped")


def restore_for_agent(
    ledger: Ledger, source: Path, launchctl: LaunchControl
) -> RestoreReceipt:
    """Restore only after the managed LaunchAgent is absent and cannot respawn."""
    agent = _Agent(ledger, launchctl)
    with _lifecycle(agent) as (directory, guard):
        if _read_private(directory, _record_name(agent)) is not None:
            raise InstallError(
                "Resolve the interrupted lifecycle operation before restore"
            )
        plist = agent.read()

        def stopped() -> None:
            guard.check()
            if agent.read() != plist:
                raise InstallError("LaunchAgent registration changed before restore")
            agent.require_stopped(disabled=bool(plist))

        stopped()
        return _restore_stopped(source, ledger, stopped)


def prune_version(
    ledger: Ledger,
    version: str,
    digest: str,
    source: Path,
    launchctl: LaunchControl,
    *,
    dry_run: bool = False,
) -> InstallReceipt:
    """Remove an explicitly selected inactive environment with retained recovery data."""
    if not _VERSION_DIR.fullmatch(f"{version}-{digest}"):
        raise InstallError("Expected an exact version and SHA-256 for pruning")
    agent = _Agent(ledger, launchctl)
    with _lifecycle(agent) as (control, guard):
        if _read_private(control, _record_name(agent)) is not None:
            raise InstallError(
                "Resolve the interrupted lifecycle operation before pruning"
            )
        plist = agent.read()
        agent.inspect(plist)
        directory = ledger.root / _VERSIONS / f"{version}-{digest}"
        if plist and _runtime_layout(ledger, agent.program(plist))[0] == directory:
            raise InstallError("Cannot prune the currently registered runtime")
        wheel_path = _wheel_path(ledger, version, digest)
        with (
            _pin_directory(directory) as selected,
            _pin_directory(source) as bundle,
        ):
            _require_outside(selected, source)
            _require_outside(selected, wheel_path, file=True)
            saved = verify_backup(source, ledger)
            retained = _wheel(wheel_path, digest, private=True)
            guard.check()
            bundle.check()
            _require_outside(selected, source)
            _require_outside(selected, wheel_path, file=True)
            if not dry_run:
                shutil.rmtree(directory)
                with _pin_directory(directory.parent) as parent:
                    os.fsync(parent.fd)
        return InstallReceipt(
            str(ledger.identity.project_id),
            agent.label,
            "planned" if dry_run else "pruned",
            retained.version,
            retained.digest,
            backup=saved,
        )
