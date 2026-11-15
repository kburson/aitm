from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from aitm_usage.ledger import LedgerError
from aitm_usage.monitor_control import ControlInbox
from aitm_usage.monitor_registry import (
    ApprovedSource,
    CaptureChange,
    ControlCommand,
    ControlStatus,
    ProjectRegistrationRequest,
    Registry,
    SourceApprovalRequest,
    _directory,
)


@pytest.fixture
def approval(tmp_path):
    source = tmp_path / "sources"
    source.mkdir(mode=0o700)
    return SourceApprovalRequest(
        UUID(int=1),
        "codex",
        "codex-desktop-macos",
        "Darwin",
        "arm64",
        "0.167.0-alpha.3.2",
        1,
        str(source),
    )


def retain_approval(writer, request):
    """Install a prior-version snapshot without exercising live approval."""
    directory = _directory(request.root)
    approval = ApprovedSource(replace(request, root=directory.path), directory)
    writer._save(replace(writer.view(), sources=(approval,)))
    return approval


def test_no_profile_rejects_new_and_retained_approval(tmp_path, approval):
    with Registry(tmp_path / "monitor").writer() as writer:
        with pytest.raises(LedgerError, match="qualification"):
            writer.approve_source(approval)
        assert writer.view().sources == ()

        retained = retain_approval(writer, approval)
        with pytest.raises(LedgerError, match="qualification"):
            writer.approve_source(approval)
        assert writer.view().sources == (retained,)


def test_rejected_approval_and_enable_leave_later_commands_runnable(tmp_path, approval):
    root = tmp_path / "monitor"
    writer_root = Registry(root)
    project_id = UUID(int=2)
    state = tmp_path / "project"
    state.mkdir(mode=0o700)
    project = ProjectRegistrationRequest(project_id, str(state), "Project")

    # The later disable is allowed without a payload because there is no epoch.
    enable = CaptureChange(project_id, approval.source_id, True)
    disable = replace(enable, enabled=False)
    commands = tuple(
        ControlCommand(UUID(int=i), payload)
        for i, payload in enumerate((approval, enable, disable, project), start=3)
    )
    inbox = ControlInbox(root)
    with writer_root.writer() as writer:
        writer.register_project(project)
        retained = retain_approval(writer, approval)
        for command in commands:
            inbox.enqueue(command)
        receipts = writer.apply_pending(inbox, writer.lease, None)

        assert [receipt.status for receipt in receipts] == [
            ControlStatus.REJECTED,
            ControlStatus.REJECTED,
            ControlStatus.APPLIED,
            ControlStatus.APPLIED,
        ]
        assert writer.view().sources == (retained,)
        assert writer.view().epochs == ()


def qualify(writer, *, current=lambda _: True):
    from aitm_usage._monitor_qualification import (
        _InstallationProof,
        _LiveProfile,
        _LiveSourceTuple,
    )

    evidence = writer.source_evidence()
    sources = writer.view().sources
    writer._live_profile = _LiveProfile(
        _directory(str(writer.root), private=True),
        writer.lease,
        evidence.pseudonymize("qualification-generation", str(uuid4())),
        tuple(
            _InstallationProof(
                source.directory,
                _LiveSourceTuple.from_approval(source),
                evidence.pseudonymize(
                    "qualification-executable", str(source.source_id)
                ),
            )
            for source in sources
        ),
        current,
    )


@pytest.fixture
def previously_admitted(tmp_path, monkeypatch):
    from test_monitor_journal import NativeJournalFixture

    monkeypatch.setattr("aitm_usage.ledger._control_root", lambda: tmp_path / "control")
    authority = object()
    with monkeypatch.context() as setup:
        setup.setattr(Registry, "_require_live_source", lambda *_, **__: authority)
        return NativeJournalFixture(tmp_path, setup)


def test_retained_codex_refuses_before_payload(previously_admitted, monkeypatch):
    from test_monitor_journal import LIVE

    from aitm_usage._monitor_qualification import _LiveSourceUnavailable
    from aitm_usage.monitor_scope import ScopeState
    from aitm_usage.sources.adapter import ProviderAdapter

    with previously_admitted.registry.writer() as writer:
        locator = previously_admitted.locator()
        original = writer.view()
        monkeypatch.setattr(
            ProviderAdapter,
            "read_delta",
            lambda *a, **k: pytest.fail("live payload read"),
        )
        with pytest.raises(_LiveSourceUnavailable) as result:
            ScopeState(writer).read_source(LIVE, locator)
        assert result.value.decision.source_id == LIVE
        assert writer.view() == original


def test_retained_grok_refuses_before_payload(previously_admitted, monkeypatch):
    from test_grok import FIXTURES, GROK_BINARY, SESSION

    from aitm_usage.monitor_scope import ScopeState
    from aitm_usage.sources.adapter import SourceRoot
    from aitm_usage.sources.grok import GrokAdapter, GrokOrigin

    root = previously_admitted.registry.root.parent / "grok"
    session = root / SESSION
    session.mkdir(parents=True)
    for filename in ("updates.jsonl", "usage.json"):
        (session / filename).write_bytes((FIXTURES / filename).read_bytes())

    with previously_admitted.registry.writer() as writer:
        source_id = UUID(int=99)
        approved = SourceApprovalRequest(
            source_id,
            "grok",
            "grok-build-macos",
            "Darwin",
            "arm64",
            "1.0.77",
            1,
            str(root),
        )
        directory = _directory(str(root))
        before = writer.view()
        writer._save(
            replace(
                before, sources=(*before.sources, ApprovedSource(approved, directory))
            )
        )
        evidence = writer.source_evidence()
        origin = GrokOrigin(
            session_id=SESSION,
            system="Darwin",
            architecture="arm64",
            version="1.0.77",
            build="50ca579fa996",
            executable_digest=GROK_BINARY,
            format_version=1,
            lineage_id=SESSION,
            incarnation=evidence.pseudonymize("grok-incarnation", "fixture"),
            checkout=None,
        )
        reader = GrokAdapter(
            lambda p: origin if p.parent == session else None, lambda *_: None
        )
        source_root = SourceRoot(root, datetime(2026, 1, 1, tzinfo=UTC), (), evidence)
        (locator,) = reader.discover(source_root)
        monkeypatch.setattr(
            GrokAdapter, "read_delta", lambda *a, **k: pytest.fail("Grok payload read")
        )
        with pytest.raises(LedgerError, match="qualification") as result:
            ScopeState(writer, grok_reader=reader).read_source(source_id, locator)
        assert result.value.decision is None


@pytest.mark.parametrize("change", ("supersede", "revoke", "verifier-unavailable"))
@pytest.mark.parametrize("existing_progress", (False, True))
def test_reserve_revalidates_the_exact_prepared_authority(
    previously_admitted, change, existing_progress
):
    from test_monitor_journal import LIVE

    from aitm_usage.monitor_journal import RoutingJournal
    from aitm_usage.monitor_scope import ScopeState

    with previously_admitted.registry.writer() as writer:
        qualify(writer)
        journal = RoutingJournal(writer, ScopeState(writer))
        locator = previously_admitted.locator()
        prepared = journal.prepare(LIVE, locator)
        if existing_progress:
            journal.reserve_batch(prepared)
            assert journal.cursor_for(LIVE, locator) == prepared.progress
        before = journal.as_of()
        progress = journal.cursor_for(LIVE, locator)

        if change == "supersede":
            qualify(writer)
        elif change == "revoke":
            writer._live_profile = None
        else:
            writer._live_profile = replace(writer._live_profile, current=None)
        with pytest.raises(LedgerError, match="qualification"):
            journal.reserve_batch(prepared)
        assert journal.as_of() == before
        assert journal.cursor_for(LIVE, locator) == progress


def test_claude_and_mismatched_build_refuse_under_an_active_profile(tmp_path, approval):
    with Registry(tmp_path / "monitor").writer() as writer:
        retained = retain_approval(writer, approval)
        qualify(writer)
        assert writer.approve_source(approval) == retained
        with pytest.raises(LedgerError, match="qualification"):
            writer.approve_source(replace(approval, client_version="different"))

        claude = replace(
            approval,
            source_id=UUID(int=12),
            provider="claude",
            surface="claude-code-macos",
        )
        before = writer.view()
        writer._save(
            replace(
                before,
                sources=(*before.sources, ApprovedSource(claude, retained.directory)),
            )
        )
        qualify(writer)
        with pytest.raises(LedgerError, match="qualification"):
            writer.approve_source(claude)


def test_revoked_capture_keeps_payload_dependent_disable_pending(previously_admitted):
    from test_monitor_journal import LIVE, A

    with previously_admitted.registry.writer() as writer:
        before = writer.view()
        disable = CaptureChange(A, LIVE, False)
        inbox = ControlInbox(writer.root)
        command = ControlCommand(UUID(int=987), disable)
        inbox.enqueue(command)

        def locate(change, known):
            assert change == disable
            locator = previously_admitted.locator()
            return (locator,) if locator.stream_ref in known else ()

        assert writer.apply_pending(inbox, writer.lease, locate) == ()
        after = writer.view()
        assert after.epochs == before.epochs
        assert after.permissions == before.permissions
        assert writer.command_status(command.command_id) is None
        with inbox.publication() as locked:
            assert list(inbox.iter_pending(locked)) == [command]


def test_disposable_authority_cannot_follow_a_new_writer(tmp_path, approval):
    registry = Registry(tmp_path / "monitor")
    with registry.writer() as writer:
        retain_approval(writer, approval)
        qualify(writer)
        profile = writer._live_profile

    with pytest.raises(LedgerError, match="lease"):
        writer.approve_source(approval)

    with registry.writer() as reopened:
        reopened._live_profile = profile
        with pytest.raises(LedgerError, match="qualification"):
            reopened.approve_source(approval)


def test_substrate_shim_is_absent_from_the_installed_package():
    from importlib.util import find_spec
    from pathlib import Path

    import aitm_usage

    (root,) = aitm_usage.__path__
    assert find_spec("aitm_usage.legacy_monitor_qualification") is None
    assert not (Path(root) / "conftest.py").exists()


def test_old_capture_frontier_cannot_cross_a_profile_generation(previously_admitted):
    from test_monitor_journal import LIVE, A

    with previously_admitted.registry.writer() as writer:
        qualify(writer)
        change = CaptureChange(A, LIVE, True)
        locator = previously_admitted.locator()
        frontier = writer.capture_frontier(change, locator)
        qualify(writer)
        before = writer.view()

        with pytest.raises(LedgerError, match="qualification"):
            writer.verify_boundary(change, locator, frontier)
        assert writer.view() == before
