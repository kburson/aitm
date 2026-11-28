"""Select the committed assurance level and build the managed launch."""

import os
import shlex
import sys
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Literal, Protocol

from aitm_core.models.verification import CapturedInputs
from aitm_core.verification.provision import PreparedEnvironment

type Assurance = Literal["captured-export", "contained"]


@dataclass(frozen=True, slots=True)
class ContainmentCapability:
    assurance: Assurance | None
    reason: str


@dataclass(frozen=True, slots=True)
class LaunchResources:
    inputs: CapturedInputs
    environment: PreparedEnvironment
    scratch: Path
    command: str


@dataclass(frozen=True, slots=True)
class ProcessLaunch:
    argv: tuple[str, ...]
    cwd: Path
    environment: dict[str, str]


class LaneAdapter(Protocol):
    def probe(self) -> ContainmentCapability: ...

    def command(self, resources: LaunchResources) -> ProcessLaunch: ...


def capture_command(command: str, installer: Path) -> tuple[str, ...]:
    args = shlex.split(command)
    if len(args) < 3 or args[:2] != ["uv", "run"] or args[2].startswith("-"):
        raise ValueError(
            "Use one managed verification command in the form uv run COMMAND."
        )
    return (
        os.fspath(installer),
        "--no-config",
        "run",
        "--no-sync",
        "--offline",
        "--no-python-downloads",
        "--",
        *args[2:],
    )


class CapturedExport:
    def probe(self) -> ContainmentCapability:
        return ContainmentCapability(
            "captured-export", "captured-export is configured."
        )

    def command(self, resources: LaunchResources) -> ProcessLaunch:
        scratch = resources.scratch
        runtime = resources.environment
        tools = runtime.receipt.identity.tools
        return ProcessLaunch(
            capture_command(resources.command, Path(tools.installer)),
            resources.inputs.source_directory,
            {
                "PATH": os.pathsep.join((str(runtime.directory / "bin"), os.defpath)),
                "HOME": str(scratch),
                "TMPDIR": str(scratch),
                "XDG_CONFIG_HOME": str(scratch),
                "XDG_CACHE_HOME": str(scratch),
                "UV_CACHE_DIR": str(scratch / "uv-cache"),
                "UV_PROJECT_ENVIRONMENT": str(runtime.directory),
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTEST_ADDOPTS": f"-o cache_dir={shlex.quote(str(scratch / 'pytest-cache'))}",
            },
        )


@dataclass(frozen=True, slots=True)
class UnavailableLane:
    platform: str

    def probe(self) -> ContainmentCapability:
        return ContainmentCapability(
            None, f"Contained verification is unavailable on {self.platform}."
        )

    def command(self, resources: LaunchResources) -> ProcessLaunch:
        raise ValueError(self.probe().reason)


def select_lane(assurance: Assurance, platform: str = sys.platform) -> LaneAdapter:
    if assurance == "captured-export":
        return CapturedExport()
    modules = {"darwin": "containment_macos", "linux": "containment_linux"}
    suffix = modules.get(platform)
    if suffix is not None:
        module = f"{__package__}.{suffix}"
        try:
            return import_module(module).adapter()
        except ModuleNotFoundError as error:
            if error.name != module:
                raise
    return UnavailableLane(platform)
