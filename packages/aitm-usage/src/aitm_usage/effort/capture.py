"""Bounded capture around caller-authorized harness and evidence sources."""

import asyncio
import math
import os
import subprocess
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import BinaryIO, Protocol

from .receipts import Enrollment, NativeTurn, Outcome, UsageReceipt

_DEFAULT_ENV = frozenset(
    {
        "PATH",
        "HOME",
        "USERPROFILE",
        "SYSTEMROOT",
        "APPDATA",
        "LOCALAPPDATA",
        "XDG_CACHE_HOME",
        "XDG_CONFIG_HOME",
        "XDG_DATA_HOME",
        "XDG_STATE_HOME",
        "TMP",
        "TEMP",
        "TMPDIR",
        "LANG",
        "LC_ALL",
        "LC_CTYPE",
    }
)
_DEFAULT_EVIDENCE_BYTES = 1 << 20
_REAP_TIMEOUT_SECONDS = 1


class ProcessState(StrEnum):
    EXITED = "exited"
    LAUNCH_FAILED = "launch-failed"
    OUTPUT_LIMIT = "output-limit"
    TIMED_OUT = "timed-out"


class CaptureGap(StrEnum):
    MISSING = "missing"
    MALFORMED = "malformed"
    UNEXPECTED_HARNESS = "unexpected-harness"
    WRONG_TURN = "wrong-turn"
    WRONG_ATTEMPT = "wrong-attempt"
    EVIDENCE_LIMIT = "evidence-limit"


def _validate_byte_limit(value: int) -> None:
    if type(value) is not int or not 0 < value < 2**31:
        raise ValueError("Expected a positive byte limit below 2 GiB")


@dataclass(frozen=True, slots=True)
class CaptureLimits:
    timeout_seconds: float = 120
    stdout_bytes: int = _DEFAULT_EVIDENCE_BYTES
    stderr_bytes: int = 64 << 10

    def __post_init__(self) -> None:
        if (
            type(self.timeout_seconds) not in (int, float)
            or not math.isfinite(self.timeout_seconds)
            or self.timeout_seconds <= 0
        ):
            raise ValueError("Expected a positive finite timeout")
        _validate_byte_limit(self.stdout_bytes)
        _validate_byte_limit(self.stderr_bytes)


@dataclass(frozen=True, slots=True)
class HarnessCommand:
    """An argument vector and environment allowlist from trusted configuration."""

    argv: tuple[str, ...] = field(repr=False)
    cwd: Path = field(repr=False)
    inherit_env: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if not self.argv or not Path(self.argv[0]).is_absolute():
            raise ValueError("Expected an absolute path to a configured harness")
        if not self.cwd.is_absolute():
            raise ValueError("Expected an absolute harness working directory")


@dataclass(frozen=True, slots=True)
class CaptureEvent:
    """Private captured bytes for one enrollment, with truncated pipe descriptors."""

    enrollment: Enrollment
    stdout: bytes = field(repr=False)
    stderr: bytes = field(repr=False)
    truncated_streams: frozenset[int]


@dataclass(frozen=True, slots=True)
class ExactReference:
    """Caller-selected native boundary and bounded private evidence."""

    enrollment: Enrollment
    turn: NativeTurn
    evidence: bytes = field(repr=False)


@dataclass(frozen=True, slots=True)
class Observation:
    outcome: Outcome = Outcome.UNKNOWN
    receipt: UsageReceipt | None = None
    gap: CaptureGap | None = None


class CaptureAdapter(Protocol):
    """Translate provider evidence and verify native identity before issuing a receipt."""

    def observe(self, event: CaptureEvent) -> Observation: ...

    def recover(self, exact_ref: ExactReference) -> Observation: ...


@dataclass(frozen=True, slots=True)
class ProcessStatus:
    state: ProcessState
    returncode: int | None


@dataclass(frozen=True, slots=True)
class CaptureResult:
    process: ProcessStatus
    observation: Observation


class _BoundedPipes(asyncio.SubprocessProtocol):
    def __init__(self, limits: CaptureLimits) -> None:
        self.done = asyncio.Event()
        self.buffers = {1: bytearray(), 2: bytearray()}
        self.limits = {1: limits.stdout_bytes, 2: limits.stderr_bytes}
        self.truncated_streams: set[int] = set()

    def connection_made(self, transport: asyncio.SubprocessTransport) -> None:
        self.transport = transport

    def pipe_data_received(self, fd: int, data: bytes) -> None:
        buffer = self.buffers[fd]
        remaining = self.limits[fd] - len(buffer)
        buffer.extend(data[:remaining])
        if len(data) > remaining:
            first_overflow = not self.truncated_streams
            self.truncated_streams.add(fd)
            self.transport.get_pipe_transport(fd).close()
            if first_overflow and self.transport.get_returncode() is None:
                try:
                    self.transport.kill()
                except ProcessLookupError:
                    pass

    def connection_lost(self, exc: Exception | None) -> None:
        self.done.set()


def _checked_observation(
    observation: Observation,
    enrollment: Enrollment,
    expected_turn: NativeTurn | None = None,
) -> Observation:
    receipt = observation.receipt
    if receipt is None:
        return observation
    if (receipt.project_id, receipt.attempt_id) != (
        enrollment.project_id,
        enrollment.attempt_id,
    ):
        return Observation(gap=CaptureGap.WRONG_ATTEMPT)
    if expected_turn is not None and receipt.turn.identity != expected_turn.identity:
        return Observation(gap=CaptureGap.WRONG_TURN)
    if receipt.outcome != observation.outcome:
        return Observation(gap=CaptureGap.MALFORMED)
    return observation


async def capture(
    adapter: CaptureAdapter,
    *,
    enrollment: Enrollment,
    command: HarnessCommand,
    limits: CaptureLimits = CaptureLimits(),
) -> CaptureResult:
    """Run one configured harness in its normal sign-in and sandbox context.

    The adapter derives terminal outcome solely from provider evidence. Raw bytes
    stay in memory and are passed only to the adapter.
    """
    env = {
        key: os.environ[key]
        for key in _DEFAULT_ENV | command.inherit_env
        if key in os.environ
    }
    loop = asyncio.get_running_loop()
    pipes = _BoundedPipes(limits)
    try:
        transport, _ = await loop.subprocess_exec(
            lambda: pipes,
            *command.argv,
            stdin=subprocess.DEVNULL,
            cwd=command.cwd,
            env=env,
        )
    except OSError:
        return CaptureResult(
            ProcessStatus(ProcessState.LAUNCH_FAILED, None),
            Observation(gap=CaptureGap.MISSING),
        )

    state = ProcessState.EXITED
    try:
        async with asyncio.timeout(limits.timeout_seconds):
            await pipes.done.wait()
    except TimeoutError:
        state = ProcessState.TIMED_OUT
    finally:
        transport.close()

    if pipes.truncated_streams:
        state = ProcessState.OUTPUT_LIMIT
    if not pipes.done.is_set():
        # A descendant can retain the write handles after the owned process exits.
        # Closing the transport stops reading them and lets the owned child reap.
        try:
            await asyncio.wait_for(pipes.done.wait(), timeout=_REAP_TIMEOUT_SECONDS)
        except TimeoutError:
            pass

    event = CaptureEvent(
        enrollment,
        bytes(pipes.buffers[1]),
        bytes(pipes.buffers[2]),
        frozenset(pipes.truncated_streams),
    )
    return CaptureResult(
        ProcessStatus(state, transport.get_returncode()),
        _checked_observation(adapter.observe(event), enrollment),
    )


def recover(
    adapter: CaptureAdapter,
    *,
    enrollment: Enrollment,
    expected_turn: NativeTurn,
    evidence: BinaryIO,
    max_bytes: int = _DEFAULT_EVIDENCE_BYTES,
) -> Observation:
    """Read a caller-authorized evidence stream for one exact turn."""
    _validate_byte_limit(max_bytes)
    try:
        payload = evidence.read(max_bytes + 1)
    except OSError:
        return Observation(gap=CaptureGap.MISSING)
    if not payload:
        return Observation(gap=CaptureGap.MISSING)
    if len(payload) > max_bytes:
        return Observation(gap=CaptureGap.EVIDENCE_LIMIT)
    reference = ExactReference(enrollment, expected_turn, payload)
    return _checked_observation(adapter.recover(reference), enrollment, expected_turn)
