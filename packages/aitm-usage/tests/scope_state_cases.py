"""Typed inputs and in-memory publication for scope state policy tests."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from aitm_usage.monitor_registry import _ServiceEvidence
from aitm_usage.monitor_scope import (
    AffectedScope,
    ScopeAuthority,
    ScopePosition,
    ScopeState,
    VerifiedBoundary,
    _ScopeSnapshot,
)
from aitm_usage.monitor_types import NativeSurface
from aitm_usage.types import BoundaryKind, Provider, SourceBoundary, SourceCursor

_EVIDENCE = _ServiceEvidence(b"scope-state-test-fixture")


class MemoryScope:
    def __init__(self, monkeypatch, clock):
        self.state = ScopeState(
            SimpleNamespace(root=Path("/fixture/scope"), lease=object()), clock=clock
        )
        self.snapshot = _ScopeSnapshot()
        self.require_boundary = Mock()
        monkeypatch.setattr(self.state, "_require_boundary", self.require_boundary)
        monkeypatch.setattr(
            self.state, "_snapshot", lambda *, confirm=False: self.snapshot
        )
        monkeypatch.setattr(self.state, "_save", self._publish)

    def _publish(self, snapshot):
        self.snapshot = snapshot

    @staticmethod
    def reference(label):
        return _EVIDENCE.pseudonymize("fixture", label)

    def boundary(self, command, ordinal, *, owner, anchor, checkout):
        session = self.reference("session")
        stream = self.reference("stream")
        position = ScopePosition(
            owner, NativeSurface.CODEX_DESKTOP_MACOS, session, stream, ordinal
        )
        boundary = SourceBoundary(
            Provider.CODEX,
            stream,
            session,
            ordinal,
            BoundaryKind.REQUEST,
            self.reference(f"boundary-{ordinal}"),
            receipt_ref=command.receipt_ref,
        )
        cursor = SourceCursor(
            stream,
            self.reference("locator"),
            self.reference("incarnation"),
            ordinal + 1,
            self.reference(f"prefix-{ordinal}"),
        )
        return VerifiedBoundary(
            command.command_id,
            self.reference(str(command.command_id)).value.split(":")[1],
            position,
            checkout,
            anchor,
            True,
            AffectedScope(ordinal, ordinal + 1, (self.reference(f"usage-{ordinal}"),)),
            boundary,
            SimpleNamespace(
                _grok_strict=False, _admitted={owner}, _native_cursor=cursor
            ),
            ScopeAuthority(owner, "fixture"),
        )
