"""Build typed qualification inputs with an in-memory trust boundary."""

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
    RegisteredProject,
    Registry,
    RegistryView,
    SourceApprovalRequest,
    _PhysicalDirectory,
    _ServiceEvidence,
)
from aitm_usage.monitor_types import NativeSurface
from aitm_usage.sources.adapter import SourceLocator, SourceRoot
from aitm_usage.sources.scan import CandidateSource
from aitm_usage.types import Provider


def qualification_policy(monkeypatch, source_id, cutoff, *, provider=Provider.CODEX):
    lease = Mock()
    writer = Registry(Path("/fixture/monitor"), lease)
    foreign = Registry(Path("/fixture/other-monitor"), Mock())
    evidence = _ServiceEvidence(b"fixture-qualification")
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
