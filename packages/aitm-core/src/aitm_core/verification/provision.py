"""Provision and verify clone-local environments from an applicable capture."""

import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import sysconfig
import tomllib
from contextlib import contextmanager
from dataclasses import dataclass
from hashlib import file_digest, sha256
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory, mkdtemp
from typing import Annotated, Literal
from urllib.parse import urlsplit

import rfc8785
from pydantic import Field

from aitm_core.config import PolicySnapshot
from aitm_core.models.attempts import AttemptFact, SourceSnapshot, Text
from aitm_core.models.binding import Binding
from aitm_core.models.events import DIGEST
from aitm_core.models.operations import repository_path
from aitm_core.models.verification import CapturedInputs
from aitm_core.setup.journal import state_directory
from aitm_core.store.gate import _atomic_write
from aitm_core.store.installation import Installation
from aitm_core.store.objects import GitCommandError
from aitm_core.verification.capture import _discard, capture_applicable


class ProvisionUnavailable(ValueError):
    """The captured dependencies or environment could not be qualified."""


class ProvisionTools(AttemptFact):
    installer: Text
    installer_version: Text
    installer_digest: DIGEST
    python: Text
    python_version: Text
    python_digest: DIGEST
    platform: Text


class EnvironmentIdentity(AttemptFact):
    capture: DIGEST
    source: SourceSnapshot
    project_digest: DIGEST
    lock_digest: DIGEST
    policy: SourceSnapshot
    policy_digest: DIGEST
    tools: ProvisionTools

    @property
    def digest(self) -> str:
        return sha256(rfc8785.dumps(self.model_dump(mode="json"))).hexdigest()


class EnvironmentReceipt(AttemptFact):
    schema_version: Literal["aitm.prepared-environment/v1"] = Field(
        default="aitm.prepared-environment/v1", alias="schema"
    )
    identity: EnvironmentIdentity
    runtime: Annotated[str, Field(pattern=r"^environment-[a-z0-9_]{8,32}$")]
    inventory_digest: DIGEST


class InstallerCacheReceipt(AttemptFact):
    fingerprint: DIGEST
    environment: DIGEST
    runtime: Annotated[str, Field(pattern=r"^environment-[a-z0-9_]{8,32}$")]
    inventory_digest: DIGEST


@dataclass(frozen=True, slots=True)
class PreparedEnvironment:
    directory: Path
    receipt: EnvironmentReceipt


@dataclass(frozen=True, slots=True)
class EnvironmentResult:
    status: Literal["ready", "unavailable", "stale"]
    prepared: PreparedEnvironment | None = None
    reason: str | None = None


def _hash(path: Path) -> str:
    with path.open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def _tools() -> ProvisionTools:
    selected = shutil.which("uv")
    if selected is None:
        raise ProvisionUnavailable("The installed uv tool is unavailable.")
    installer = Path(selected).resolve(strict=True)
    python = Path(sys.executable).resolve(strict=True)
    version = subprocess.run(
        (str(installer), "--version"),
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return ProvisionTools(
        installer=str(installer),
        installer_version=version,
        installer_digest=_hash(installer),
        python=str(python),
        python_version=sys.version,
        python_digest=_hash(python),
        platform="|".join(
            (
                sysconfig.get_platform(),
                sysconfig.get_config_var("SOABI") or "",
                " ".join(platform.libc_ver()),
                platform.mac_ver()[0],
            )
        ),
    )


def _lock_inputs(inputs: CapturedInputs) -> tuple[str, str]:
    entries = {row.path: row.digest for row in inputs.manifest.entries}
    if "pyproject.toml" not in entries or "uv.lock" not in entries:
        raise ProvisionUnavailable("The capture requires pyproject.toml and uv.lock.")
    lock = tomllib.loads((inputs.source_directory / "uv.lock").read_text())
    packages = lock.get("package")
    if lock.get("version") != 1 or not isinstance(packages, list) or not packages:
        raise ProvisionUnavailable(
            "The captured uv.lock has no supported package inventory."
        )
    for package in packages:
        source = package.get("source") if isinstance(package, dict) else None
        if not isinstance(source, dict) or len(source) != 1:
            raise ProvisionUnavailable("A locked package has an unsupported source.")
        kind, value = next(iter(source.items()))
        if not isinstance(value, str):
            raise ProvisionUnavailable("A locked package has an invalid source.")
        wheels = package.get("wheels", [])
        if not isinstance(wheels, list):
            raise ProvisionUnavailable(
                "A locked package has an invalid wheel inventory."
            )
        if kind in {"registry", "url"}:
            address = urlsplit(value)
            if address.scheme not in {"http", "https"} or not address.hostname:
                raise ProvisionUnavailable(
                    "A locked registry or wheel URL is unsupported."
                )
            if not wheels or any(
                not isinstance(wheel, dict)
                or not isinstance(wheel.get("hash"), str)
                or not re.fullmatch(r"sha256:[0-9a-f]{64}", wheel["hash"])
                or not isinstance(wheel.get("url"), str)
                or urlsplit(wheel["url"]).scheme not in {"http", "https"}
                for wheel in wheels
            ):
                raise ProvisionUnavailable(
                    "A locked wheel lacks its exact artifact hash."
                )
        elif kind == "path":
            digest = entries.get(repository_path(value))
            if (
                digest is None
                or not value.endswith(".whl")
                or not any(
                    isinstance(wheel, dict)
                    and wheel.get("filename") == PurePosixPath(value).name
                    and wheel.get("hash") == f"sha256:{digest}"
                    for wheel in wheels
                )
            ):
                raise ProvisionUnavailable(
                    "A locked local wheel is absent or its captured hash disagrees."
                )
        elif (
            kind not in {"virtual", "editable"}
            or value != "."
            and (f"{repository_path(value)}/pyproject.toml" not in entries)
        ):
            raise ProvisionUnavailable(
                "A locked package is outside captured wheel or workspace sources."
            )
    return entries["pyproject.toml"], entries["uv.lock"]


def _identify(
    installation: Installation,
    binding: Binding,
    policy: PolicySnapshot,
    inputs: CapturedInputs,
) -> EnvironmentIdentity:
    if not capture_applicable(installation, binding, policy, inputs):
        raise ProvisionUnavailable("The captured source, inputs or policy are stale.")
    project, lock = _lock_inputs(inputs)
    return EnvironmentIdentity(
        capture=inputs.manifest.digest,
        source=inputs.manifest.source,
        project_digest=project,
        lock_digest=lock,
        policy=inputs.manifest.policy,
        policy_digest=policy.source.digest,
        tools=_tools(),
    )


def _cache(installation: Installation) -> Path:
    return state_directory(installation.repository) / "verification"


def _receipt_path(cache: Path, identity: EnvironmentIdentity) -> Path:
    return cache / "environments" / f"{identity.digest}.json"


def _directory(cache: Path, receipt: EnvironmentReceipt) -> Path:
    return cache / "runtime" / receipt.runtime / "environment"


@contextmanager
def _lock(marker: Path):
    import fcntl

    marker.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    descriptor = os.open(
        marker.with_suffix(".lock"), os.O_NOFOLLOW | os.O_RDWR | os.O_CREAT, 0o600
    )
    with os.fdopen(descriptor, "a+b") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        yield


def _walk(root: Path):
    def fail(error):
        raise error

    if not stat.S_ISDIR(root.lstat().st_mode):
        raise ProvisionUnavailable("The environment directory is not a real directory.")
    return os.walk(root, onerror=fail, followlinks=False)


def _inventory(root: Path, tools: ProvisionTools) -> str:
    rows = []
    for directory, directories, files in _walk(root):
        parent = Path(directory)
        for name in (*directories, *files):
            path = parent / name
            relative = path.relative_to(root).as_posix()
            state = path.lstat()
            mode = stat.S_IMODE(state.st_mode)
            if stat.S_ISLNK(state.st_mode):
                target = path.resolve(strict=True)
                link = os.readlink(path)
                interpreter = (
                    PurePosixPath(relative).parent == PurePosixPath("bin")
                    and name.startswith("python")
                    and target == Path(tools.python)
                )
                if not interpreter and (
                    Path(link).is_absolute() or not target.is_relative_to(root)
                ):
                    raise ProvisionUnavailable(
                        "The installed inventory has an unqualified link."
                    )
                rows.append((relative, "link", link))
            elif stat.S_ISDIR(state.st_mode) and not mode & 0o222:
                rows.append((relative, "directory", mode))
            elif (
                stat.S_ISREG(state.st_mode) and state.st_nlink == 1 and not mode & 0o222
            ):
                rows.append((relative, "file", mode, _hash(path)))
            else:
                raise ProvisionUnavailable(
                    "The installed inventory has mutable or unsupported entries."
                )
    if (
        root.stat().st_mode & 0o222
        or not (root / "pyvenv.cfg").is_file()
        or not (root / "bin/python").is_file()
    ):
        raise ProvisionUnavailable("The installed Python environment is incomplete.")
    return sha256(rfc8785.dumps(sorted(rows))).hexdigest()


def _seal(root: Path) -> None:
    for directory, directories, files in _walk(root):
        parent = Path(directory)
        for name in (*directories, *files):
            path = parent / name
            state = path.lstat()
            if stat.S_ISREG(state.st_mode):
                if state.st_nlink != 1:
                    raise ProvisionUnavailable(
                        "The installer produced a linked dependency file."
                    )
                path.chmod(0o555 if state.st_mode & 0o111 else 0o444)
        parent.chmod(0o555)


def _installer_marker(
    cache: Path, identity: EnvironmentIdentity, inputs: CapturedInputs
) -> Path:
    # Installer bytes can be reused under a different committed network policy.
    # The published environment still binds the full current policy and capture.
    fingerprint = sha256(
        rfc8785.dumps(
            (
                identity.source.model_dump(mode="json"),
                identity.tools.model_dump(mode="json"),
                identity.project_digest,
                identity.lock_digest,
                [entry.model_dump(mode="json") for entry in inputs.manifest.entries],
            )
        )
    ).hexdigest()
    return cache / "installer" / f"{fingerprint}.json"


def _installer_inventory(root: Path) -> str:
    rows = []
    for directory, directories, files in _walk(root):
        parent = Path(directory)
        for name in (*directories, *files):
            path = parent / name
            relative = path.relative_to(root).as_posix()
            state = path.lstat()
            if stat.S_ISDIR(state.st_mode):
                rows.append((relative, "directory", stat.S_IMODE(state.st_mode)))
            elif stat.S_ISREG(state.st_mode) and state.st_nlink == 1:
                rows.append(
                    (relative, "file", stat.S_IMODE(state.st_mode), _hash(path))
                )
            elif stat.S_ISLNK(state.st_mode):
                link = os.readlink(path)
                if Path(link).is_absolute() or not path.resolve(
                    strict=True
                ).is_relative_to(root):
                    raise ProvisionUnavailable(
                        "An installer cache link escapes its artifact."
                    )
                rows.append((relative, "link", link))
            else:
                raise ProvisionUnavailable(
                    "An installer cache entry cannot be copied safely."
                )
    return sha256(rfc8785.dumps(sorted(rows))).hexdigest()


def _relocate_installer(root: Path, destination: Path) -> None:
    """Keep uv's internal wheel links valid when its cache is moved or copied."""
    for directory, directories, files in _walk(root):
        parent = Path(directory)
        for name in (*directories, *files):
            path = parent / name
            if path.is_symlink():
                target = path.resolve(strict=True)
                if not target.is_relative_to(root):
                    raise ProvisionUnavailable(
                        "An installer cache link escapes its artifact."
                    )
                relative = os.path.relpath(target, parent)
                path.unlink()
                path.symlink_to(relative)
    root.rename(destination)


def _read_receipt(path: Path) -> bytes:
    status = path.lstat()
    if not stat.S_ISREG(status.st_mode) or status.st_nlink != 1:
        raise ProvisionUnavailable(
            "The verification receipt is not a private regular file."
        )
    return path.read_bytes()


def _copy_installer(cache: Path, marker: Path, destination: Path) -> bool:
    try:
        receipt = InstallerCacheReceipt.model_validate_json(_read_receipt(marker))
        admitted = EnvironmentReceipt.model_validate_json(
            _read_receipt(cache / "environments" / f"{receipt.environment}.json")
        )
        source = cache / "runtime" / receipt.runtime / "installer-cache"
        if (
            receipt.fingerprint != marker.stem
            or admitted.identity.digest != receipt.environment
            or admitted.runtime != receipt.runtime
            or source.resolve(strict=True) != source
            or _installer_inventory(source) != receipt.inventory_digest
        ):
            return False
        shutil.copytree(source, destination, symlinks=True)
        if _installer_inventory(destination) == receipt.inventory_digest:
            return True
    except (OSError, ValueError):
        pass
    if destination.exists():
        _discard(destination)
    return False


def _sync(
    tools: ProvisionTools,
    inputs: CapturedInputs,
    environment: Path,
    scratch: Path,
    *,
    offline: bool = False,
):
    env = {
        "PATH": os.defpath,
        "HOME": str(scratch),
        "XDG_CONFIG_HOME": str(scratch),
        "TMPDIR": str(scratch),
        "UV_PROJECT_ENVIRONMENT": str(environment),
        "UV_CACHE_DIR": str(scratch / "uv-cache"),
    }
    result = subprocess.run(
        (
            tools.installer,
            "--no-config",
            "sync",
            "--locked",
            "--no-build",
            "--no-install-workspace",
            "--no-editable",
            "--no-python-downloads",
            "--link-mode",
            "copy",
            "--python",
            tools.python,
            *(("--offline",) if offline else ()),
        ),
        cwd=inputs.source_directory,
        env=env,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise ProvisionUnavailable(
            "Locked uv provisioning failed for the captured dependencies."
        )


def _cached(cache: Path, identity: EnvironmentIdentity) -> PreparedEnvironment | None:
    path = _receipt_path(cache, identity)
    try:
        receipt = EnvironmentReceipt.model_validate_json(_read_receipt(path))
        directory = _directory(cache, receipt)
        if (
            receipt.identity == identity
            and directory.resolve(strict=True) == directory
            and receipt.inventory_digest == _inventory(directory, identity.tools)
        ):
            return PreparedEnvironment(directory, receipt)
    except (OSError, ValueError):
        pass
    return None


def validate_environment(
    installation: Installation,
    binding: Binding,
    policy: PolicySnapshot,
    inputs: CapturedInputs,
    prepared: PreparedEnvironment,
) -> EnvironmentResult:
    """Check the exact published receipt and current copied inventory."""
    try:
        identity = _identify(installation, binding, policy, inputs)
        if (
            _cached(_cache(installation), identity) == prepared
            and _identify(installation, binding, policy, inputs) == identity
        ):
            return EnvironmentResult("ready", prepared)
    except (OSError, ValueError, GitCommandError, subprocess.SubprocessError) as error:
        return EnvironmentResult("stale", reason=str(error))
    return EnvironmentResult(
        "stale", reason="The exact environment receipt or inventory changed."
    )


def provision(
    installation: Installation,
    binding: Binding,
    policy: PolicySnapshot,
    inputs: CapturedInputs,
    *,
    offline: bool = False,
) -> EnvironmentResult:
    """Reuse verified cache or run a permitted isolated locked installation."""
    staged = None
    try:
        identity = _identify(installation, binding, policy, inputs)
        cache = _cache(installation)
        marker = _receipt_path(cache, identity)
        with _lock(marker):
            cached = _cached(cache, identity)
            if _identify(installation, binding, policy, inputs) != identity:
                raise ProvisionUnavailable(
                    "The capture or tools changed during cache readback."
                )
            if cached is not None:
                return EnvironmentResult("ready", cached)
            offline_only = offline or policy.config.test.prepare_network == "deny"
            installer_marker = _installer_marker(cache, identity, inputs)
            if offline_only and not installer_marker.exists():
                raise ProvisionUnavailable(
                    "The exact locked environment and installer cache are unavailable offline."
                )
            runtimes = cache / "runtime"
            runtimes.mkdir(mode=0o700, parents=True, exist_ok=True)
            staged = Path(mkdtemp(prefix="environment-", dir=runtimes))
            environment = staged / "environment"
            with TemporaryDirectory(dir=staged) as temporary:
                scratch = Path(temporary)
                installer_cache = scratch / "uv-cache"
                if offline_only and not _copy_installer(
                    cache, installer_marker, installer_cache
                ):
                    raise ProvisionUnavailable(
                        "The exact locked installer cache failed readback."
                    )
                if _identify(installation, binding, policy, inputs) != identity:
                    raise ProvisionUnavailable(
                        "The capture or tools changed before installation."
                    )
                _sync(
                    identity.tools, inputs, environment, scratch, offline=offline_only
                )
                if not offline_only and installer_cache.is_dir():
                    try:
                        _relocate_installer(installer_cache, staged / "installer-cache")
                    except (OSError, ValueError):
                        pass
            _seal(environment)
            inventory = _inventory(environment, identity.tools)
            receipt = EnvironmentReceipt(
                identity=identity, runtime=staged.name, inventory_digest=inventory
            )
            artifact = staged / "installer-cache"
            installer_receipt = None
            if artifact.is_dir():
                try:
                    installer_receipt = InstallerCacheReceipt(
                        fingerprint=installer_marker.stem,
                        environment=identity.digest,
                        runtime=staged.name,
                        inventory_digest=_installer_inventory(artifact),
                    )
                except (OSError, ValueError):
                    # A verified environment may exist even when the tool cache cannot be retained.
                    installer_receipt = None
            if _identify(installation, binding, policy, inputs) != identity:
                raise ProvisionUnavailable(
                    "The capture or tools changed during provisioning."
                )
            _atomic_write(marker, receipt.model_dump(mode="json", by_alias=True))
            staged = None
            if installer_receipt is not None:
                try:
                    _atomic_write(
                        installer_marker, installer_receipt.model_dump(mode="json")
                    )
                except OSError:
                    # The environment receipt remains valid without an installer artifact.
                    pass
            return EnvironmentResult("ready", PreparedEnvironment(environment, receipt))
    except (OSError, ValueError, GitCommandError, subprocess.SubprocessError) as error:
        if staged is not None:
            _discard(staged)
        return EnvironmentResult("unavailable", reason=str(error))
