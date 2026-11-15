"""Durable, cursor-free scheduling hints for the private monitor."""

import json
import os
import re
from bisect import bisect_right
from collections import defaultdict, deque
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, replace
from enum import StrEnum
from math import isfinite
from pathlib import Path
from time import monotonic
from typing import Protocol

from .ledger import LedgerError, _pin_directory, _PinnedPath
from .monitor_registry import Registry
from .monitor_types import MonitorProvider
from .scopes import _private_child, _publication, _publish, _read_private
from .sources.hooks import HookEvent, WakeKind
from .types import SourceRef, _decode, _encode

_WAKE_DIRECTORY = "wake"
_SLOT = re.compile(r"[a-f0-9]{64}\.json")
_FORMAT = "aitm.monitor-wake/v1"
_UNAVAILABLE = "Private wake schedule is unavailable"


class ScheduleState(StrEnum):
    ACTIVE = "active"
    SETTLING = "settling"
    PARKED = "parked"


class WakeResolutionKind(StrEnum):
    RESOLVED = "resolved"
    UNKNOWN_LOCATOR = "unknown-locator"
    WRONG_SOURCE_TYPE = "wrong-source-type"
    STOP_WITHOUT_CURRENT_TURN = "stop-without-verified-current-turn"


@dataclass(frozen=True, slots=True)
class ResolvedWake:
    provider: MonitorProvider
    stream: SourceRef
    session: SourceRef
    turn: SourceRef | None
    project: SourceRef | None
    fact: SourceRef
    current_stop: bool


@dataclass(frozen=True, slots=True)
class WakeResolution:
    kind: WakeResolutionKind
    facts: ResolvedWake | None = None


class WakeResolver(Protocol):
    def resolve(self, request: HookEvent, *, lease: _PinnedPath) -> WakeResolution: ...


@dataclass(frozen=True, slots=True)
class _ScheduledWake:
    facts: ResolvedWake
    generation: int
    state: ScheduleState
    pending: bool
    format: str = _FORMAT


@dataclass(frozen=True, slots=True)
class _SealedWake:
    wake: _ScheduledWake
    seal: SourceRef


@dataclass(frozen=True, slots=True, init=False)
class WakeHint:
    """An exact update issued by the current scheduler's resolution path."""

    _issuer: object
    _update: _ScheduledWake


@dataclass(frozen=True, slots=True)
class WorkItem:
    provider: MonitorProvider
    stream: SourceRef
    session: SourceRef
    turn: SourceRef | None
    project: SourceRef | None
    generation: int
    state: ScheduleState
    lease_until: float
    _slot: str


class Scheduler:
    """Retain authenticated wake hints across process-local scan leases."""

    def __init__(
        self,
        writer: Registry,
        *,
        clock: Callable[[], float] = monotonic,
        lease_ttl: float = 5.0,
    ) -> None:
        if (
            type(lease_ttl) not in (float, int)
            or not isfinite(lease_ttl)
            or lease_ttl <= 0
        ):
            raise ValueError("Expected a positive wake lease duration")
        writer.lease
        key_id = writer.view().source_key_id
        if key_id is None:
            raise LedgerError(_UNAVAILABLE)
        self._writer = writer
        self._evidence = writer.source_evidence()
        if self._evidence.key_id != key_id:
            raise LedgerError(_UNAVAILABLE)
        self._clock = clock
        self._ttl = lease_ttl
        self._issuer = object()
        self._records: dict[str, _ScheduledWake] = {}
        self._leased: dict[str, WorkItem] = {}
        self._retry: dict[str, float] = {}
        self._last_group = ""
        self._generation = 0
        with self._directory() as directory:
            for name in os.listdir(directory.fd):
                if name.startswith(".publishing-"):
                    continue
                if not _SLOT.fullmatch(name):
                    raise LedgerError(_UNAVAILABLE)
                raw = _read_private(directory, name)
                if raw is None:
                    raise LedgerError(_UNAVAILABLE)
                value = _decode(raw, _SealedWake).wake
                if (
                    value.format != _FORMAT
                    or type(value.generation) is not int
                    or value.generation <= 0
                    or (value.state is ScheduleState.PARKED and value.pending)
                    or not self._valid_facts(value.facts)
                    or self._slot(value.facts) != name
                    or self._encode(value) != raw
                ):
                    raise LedgerError(_UNAVAILABLE)
                self._records[name] = value
                self._generation = max(self._generation, value.generation)
            os.fsync(directory.fd)
            directory.check()
        now = self._clock()
        self._due = {
            name: now for name, value in self._records.items() if value.pending
        }

    @property
    def root(self) -> Path:
        return self._writer.root

    @property
    def lease(self) -> _PinnedPath:
        return self._writer.lease

    @contextmanager
    def _directory(self) -> Iterator[_PinnedPath]:
        lease = self.lease
        if self._writer.view().source_key_id != self._evidence.key_id:
            raise LedgerError(_UNAVAILABLE)
        try:
            with (
                _pin_directory(self.root) as root,
                _private_child(root, _WAKE_DIRECTORY, create=True) as directory,
            ):
                assert directory is not None
                with _publication(directory):
                    yield directory
                    lease.check()
                    root.check()
        except (OSError, ValueError):
            raise LedgerError(_UNAVAILABLE) from None

    def _valid_facts(self, facts: ResolvedWake) -> bool:
        if (
            type(facts) is not ResolvedWake
            or type(facts.provider) is not MonitorProvider
            or type(facts.current_stop) is not bool
        ):
            return False
        for item in (facts.stream, facts.session, facts.fact):
            self._evidence.validate_source_ref(item)
        for item in (facts.turn, facts.project):
            if item is not None:
                self._evidence.validate_source_ref(item)
        return True

    def _slot(self, facts: ResolvedWake) -> str:
        material = json.dumps(
            [
                facts.provider.value,
                facts.session.value,
                facts.turn.value if facts.turn else None,
            ],
            separators=(",", ":"),
        )
        reference = self._evidence.pseudonymize("monitor-wake-slot-v1", material)
        return reference.value.split(":")[1] + ".json"

    def _encode(self, wake: _ScheduledWake) -> bytes:
        seal = self._evidence.pseudonymize(
            "monitor-wake-state-v1", _encode(wake, _ScheduledWake)
        )
        return _encode(_SealedWake(wake, seal), _SealedWake).encode()

    def _persist(self, name: str, update: _ScheduledWake) -> None:
        data = self._encode(update)
        previous = self._records.get(name)
        expected = self._encode(previous) if previous is not None else None
        with self._directory() as directory:
            actual = _read_private(directory, name)
            if actual == data:
                os.fsync(directory.fd)
                directory.check()
            elif actual != expected or not _publish(
                directory, name, data, replace_pending=actual is not None
            ):
                raise LedgerError(_UNAVAILABLE)
        self._records[name] = update

    def _admit(self, request: HookEvent, resolver: WakeResolver) -> bool:
        lease = self.lease
        if request.kind is WakeKind.PARK:
            return self.park(request.session)
        result = resolver.resolve(request, lease=lease)
        if (
            type(result) is not WakeResolution
            or result.kind is not WakeResolutionKind.RESOLVED
            or not self._valid_facts(result.facts)
        ):
            return False
        facts = result.facts
        if request.provider is not facts.provider:
            return False
        lease.check()
        stop = request.kind is WakeKind.STOP
        if stop and (not facts.current_stop or facts.turn is None):
            return False
        name = self._slot(facts)
        previous = self._records.get(name)
        if previous is not None and previous.facts.stream != facts.stream:
            return False
        if stop and any(
            item.facts.session == facts.session
            and item.facts.provider is facts.provider
            and item.facts.turn != facts.turn
            and (previous is None or item.generation > previous.generation)
            for item in self._records.values()
        ):
            return False
        same_fact = previous is not None and previous.facts.fact == facts.fact
        if same_fact and (not stop or previous.state is not ScheduleState.ACTIVE):
            return True
        generation = previous.generation if same_fact else self._generation + 1
        state = ScheduleState.SETTLING if stop else ScheduleState.ACTIVE
        hint = object.__new__(WakeHint)
        object.__setattr__(hint, "_issuer", self._issuer)
        object.__setattr__(
            hint, "_update", _ScheduledWake(facts, generation, state, True)
        )
        self.notify(hint)
        return True

    def notify(self, hint: WakeHint) -> None:
        """Publish the exact authorized hint before making it due."""
        self.lease
        if (
            type(hint) is not WakeHint
            or getattr(hint, "_issuer", None) is not self._issuer
        ):
            raise LedgerError(_UNAVAILABLE)
        object.__setattr__(hint, "_issuer", None)
        update = hint._update
        name = self._slot(update.facts)
        previous = self._records.get(name)
        if previous is not None and update.generation < previous.generation:
            return
        self._persist(name, update)
        self._generation = max(self._generation, update.generation)
        self._make_due(name)

    def _make_due(self, name: str) -> None:
        self._leased.pop(name, None)
        self._retry.pop(name, None)
        self._due[name] = self._clock()

    def park(self, session: SourceRef) -> bool:
        self.lease
        self._evidence.validate_source_ref(session)
        found = False
        for name, item in tuple(self._records.items()):
            if item.facts.session != session:
                continue
            found = True
            if item.state is ScheduleState.ACTIVE:
                self._persist(
                    name, replace(item, state=ScheduleState.SETTLING, pending=True)
                )
                self._make_due(name)
        return found

    def take_due(self, now: float, limit: int) -> tuple[WorkItem, ...]:
        self.lease
        if type(limit) is not int or not 0 < limit <= 64 or not isfinite(now):
            raise ValueError("Expected a bounded wake work request")
        for name, item in tuple(self._leased.items()):
            if item.lease_until <= now:
                del self._leased[name]
        by_group: dict[str, deque[str]] = defaultdict(deque)
        for name, moment in sorted(
            self._due.items(), key=lambda item: (item[1], item[0])
        ):
            if moment <= now and name not in self._leased:
                facts = self._records[name].facts
                by_group[(facts.project or facts.stream).value].append(name)
        result = []
        while by_group and len(result) < limit:
            groups = sorted(by_group)
            group = groups[bisect_right(groups, self._last_group) % len(groups)]
            self._last_group = group
            name = by_group[group].popleft()
            if not by_group[group]:
                del by_group[group]
            item = self._records[name]
            facts = item.facts
            work = WorkItem(
                facts.provider,
                facts.stream,
                facts.session,
                facts.turn,
                facts.project,
                item.generation,
                item.state,
                now + self._ttl,
                name,
            )
            self._leased[name] = work
            result.append(work)
        return tuple(result)

    def finish(self, item: WorkItem, *, caught_up: bool) -> bool:
        """Retire only the exact current work lease after successful catch-up."""
        self.lease
        if (
            type(item) is not WorkItem
            or type(caught_up) is not bool
            or self._leased.get(item._slot) is not item
            or item.lease_until <= self._clock()
        ):
            return False
        name = item._slot
        if caught_up:
            current = self._records[name]
            state = (
                ScheduleState.PARKED
                if current.state is ScheduleState.SETTLING
                else current.state
            )
            self._persist(name, replace(current, state=state, pending=False))
            self._due.pop(name)
            self._retry.pop(name, None)
        else:
            delay = min(8.0, self._retry.get(name, 0.125) * 2)
            self._retry[name] = delay
            self._due[name] = self._clock() + delay
        del self._leased[name]
        return True
