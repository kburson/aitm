"""Build typed qualification inputs with an in-memory trust boundary."""

from contextlib import nullcontext
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID

from aitm_usage import monitor_registry
from aitm_usage._monitor_qualification import (
    _InstallationProof,
    _LiveProfile,
    _LiveSourceTuple,
)
from aitm_usage.monitor_registry import (
    ApprovedSource,
    CaptureFrontier,
    RegisteredProject,
    Registry,
    RegistryView,
    SourceApprovalRequest,
    _PhysicalDirectory,
    _ServiceEvidence,
)
from aitm_usage.monitor_types import NativeSurface
from aitm_usage.sources.adapter import ProviderAdapter, SourceLocator, SourceRoot
from aitm_usage.sources.scan import CandidateSource, _CapturePosition
from aitm_usage.types import (
    BoundaryKind,
    ClientVersion,
    Provider,
    ProviderCheckpoint,
    SourceBoundary,
    SourceCheckpoint,
    SourceCursor,
)


def qualification_policy(
    monkeypatch, source_id, cutoff, *, provider=Provider.CODEX, evidence_key=None
):
    lease = Mock()
    writer = Registry(Path("/fixture/monitor"), lease)
    foreign = Registry(Path("/fixture/other-monitor"), Mock())
    evidence = _ServiceEvidence(
        b"fixture-qualification" if evidence_key is None else evidence_key
    )
    other_evidence = _ServiceEvidence(b"foreign-fixture-qualification")
    root, foreign_root, directory = (
        _PhysicalDirectory(path, (1, index))
        for index, path in enumerate(
            (str(writer.root), str(foreign.root), "/fixture/transcripts"), start=1
        )
    )
    provider, surface, version = (
        (Provider.CLAUDE, NativeSurface.CLAUDE_CODE_MACOS, "2.1.318")
        if provider is Provider.CLAUDE
        else (Provider.CODEX, NativeSurface.CODEX_DESKTOP_MACOS, "0.167.0-alpha.3.2")
    )
    approved = ApprovedSource(
        SourceApprovalRequest(
            source_id,
            provider.value,
            surface.value,
            "Darwin",
            "arm64",
            version,
            1,
            directory.path,
        ),
        directory,
    )
    project = RegisteredProject(UUID(int=1), root, "Fixture", None, (), None)
    view = RegistryView(
        projects=(project,), sources=(approved,), source_key_id=evidence.key_id
    )
    directories = {item.path: item for item in (root, foreign_root, directory)}
    monkeypatch.setattr(
        monitor_registry, "_directory", lambda path, **_: directories[path]
    )
    monkeypatch.setattr(writer, "source_evidence", lambda: evidence)
    monkeypatch.setattr(foreign, "source_evidence", lambda: other_evidence)
    monkeypatch.setattr(writer, "view", lambda: view)
    monkeypatch.setattr(writer, "capture_read_limit", Mock(return_value=None))
    profile = _LiveProfile(
        root,
        lease,
        evidence.pseudonymize("generation", "local"),
        (
            _InstallationProof(
                directory,
                _LiveSourceTuple.from_approval(approved),
                evidence.pseudonymize("executable", "local"),
            ),
        ),
        lambda _: True,
    )
    writer._live_profile = profile
    monkeypatch.setattr(writer, "_save", Mock())
    path = Path(directory.path)
    locator = SourceLocator(
        CandidateSource(
            provider,
            evidence.pseudonymize("fixture", "session"),
            evidence.pseudonymize("fixture", "stream"),
            evidence.pseudonymize("fixture", "locator"),
            evidence.pseudonymize("fixture", "incarnation"),
            path / "capture.jsonl",
            (),
            SourceRoot(path, cutoff, (), evidence),
            evidence,
            _native_surface=surface,
        )
    )
    monkeypatch.setattr(
        writer, "_current_candidate", Mock(return_value=(approved, locator))
    )
    return SimpleNamespace(
        writer=writer,
        foreign=foreign,
        root=root,
        view=view,
        approved=approved,
        profile=profile,
        locator=locator,
    )


class CapturePolicy:
    """Drive real capture proof issuance with controlled scanner observations."""

    def __init__(self, monkeypatch, source_id, cutoff, projects):
        authority = qualification_policy(monkeypatch, source_id, cutoff)
        self.writer = authority.writer
        self.approved = authority.approved
        self.first = authority.locator
        self.evidence = self.writer.source_evidence()
        self.view = replace(
            authority.view,
            projects=tuple(
                replace(authority.view.projects[0], project_id=project)
                for project in projects
            ),
        )
        self._boundaries = {self.first.stream_ref: []}
        monkeypatch.setattr(self.writer, "view", lambda **_: self.view)
        monkeypatch.setattr(self.writer, "_save", self._save)
        monkeypatch.setattr(self.writer, "_native_delta", self._native_delta)
        monkeypatch.setattr(
            self.writer,
            "_current_candidate",
            lambda view, source_id, locator, **_: (self.approved, locator),
        )

        def check_root(directory):
            assert directory == authority.approved.directory

        monkeypatch.setattr(monitor_registry, "_check_capture_root", check_root)

    def _save(self, view):
        self.view = view

    def ref(self, label):
        return self.evidence.pseudonymize("fixture", label)

    def new_stream(self):
        second = SourceLocator(
            replace(
                self.first._source,
                session_ref=self.ref("session-2"),
                stream_ref=self.ref("stream-2"),
                locator_ref=self.ref("locator-2"),
                incarnation_ref=self.ref("incarnation-2"),
            )
        )
        self._boundaries[second.stream_ref] = []
        return second

    def append(self, locator, count=1):
        source = locator._source
        committed = self._boundaries[source.stream_ref]
        added = []
        for _ in range(count):
            ordinal = len(committed) + 1
            boundary = SourceBoundary(
                Provider.CODEX,
                source.stream_ref,
                source.session_ref,
                ordinal,
                BoundaryKind.REQUEST,
                self.ref(f"{source.stream_ref.value}:{ordinal}"),
            )
            committed.append(boundary)
            added.append(boundary)
        return tuple(added)

    def _native_delta(self, view, change, locator, prior, *, arm=False, inventory=None):
        source = locator._source
        boundaries = self._boundaries[source.stream_ref]
        ordinal = len(boundaries)
        if prior is not None:
            assert (
                prior.stream_ref == source.stream_ref and prior.last_ordinal <= ordinal
            )
        cursor = self._cursor(source, ordinal)
        checkpoint = SourceCheckpoint(
            cursor,
            ProviderCheckpoint(
                Provider.CODEX,
                ordinal=ordinal,
                client_version=ClientVersion.CODEX_0_167_0_ALPHA_3_2,
                format_version=1,
            ),
        )
        previous_ordinal = 0 if prior is None else prior.last_ordinal
        return CaptureFrontier(checkpoint, ordinal), tuple(
            boundaries[previous_ordinal:]
        )

    def _cursor(self, source, ordinal):
        return SourceCursor(
            source.stream_ref,
            source.locator_ref,
            source.incarnation_ref,
            ordinal * 32,
            self.ref(f"{source.stream_ref.value}:prefix:{ordinal}"),
        )

    def advance(self, change, locator):
        frontier = self.writer.capture_frontier(change, locator)
        self.append(locator)
        return self.writer.verify_boundary(change, locator, frontier)

    def stub_native_reads(self, monkeypatch):
        """Model a stable pinned installation while retaining queue and epoch logic."""
        monkeypatch.setattr(
            monitor_registry,
            "platform",
            SimpleNamespace(system=lambda: "Darwin", machine=lambda: "arm64"),
        )
        monkeypatch.setattr(ProviderAdapter, "_capture_gap_start", lambda *a, **k: None)
        monkeypatch.setattr(self.writer, "_locator_lost", lambda *args: None)
        monkeypatch.setattr(
            self.writer,
            "capture_read_limit",
            Registry.capture_read_limit.__get__(self.writer),
        )

        def physical(source, prior, *, fixed=None):
            ordinal = len(self._boundaries[source.stream_ref])
            if fixed is not None:
                ordinal = fixed.offset // 32
            cursor = self._cursor(source, ordinal)
            if fixed is not None:
                assert fixed == cursor
            if prior is not None:
                assert prior == self._cursor(source, prior.offset // 32)
                assert prior.offset <= cursor.offset
            return _CapturePosition(
                cursor,
                ordinal + 1,
                None,
                Provider.CODEX,
                source._native_surface,
                ClientVersion.CODEX_0_167_0_ALPHA_3_2,
                1,
            )

        monkeypatch.setattr(monitor_registry, "_capture_position", physical)


class CaptureInbox:
    """Sequence known queued commands without a filesystem publication."""

    def __init__(self, writer):
        self.root = writer.root
        self.pending = []
        self._lock = object()

    def publication(self):
        return nullcontext(self._lock)

    def iter_pending(self, locked):
        assert locked is self._lock
        return tuple(self.pending)

    def discard(self, locked, command):
        assert locked is self._lock
        self.pending.remove(command)
