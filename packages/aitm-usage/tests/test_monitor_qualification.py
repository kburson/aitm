from contextlib import nullcontext
from dataclasses import replace
from pathlib import Path
from shutil import copytree
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest
from grok_capture_policy_cases import grok_capture_policy  # noqa: F401, F811
from qualification_policy_cases import CaptureInbox, CapturePolicy, qualification_policy
from test_codex import CUTOFF
from test_isolated_qualification import installed_policy as installed_policy

from aitm_usage import monitor_journal, monitor_registry, monitor_scope
from aitm_usage.ledger import LedgerError
from aitm_usage.monitor_registry import (
    ApprovedSource,
    CaptureChange,
    CaptureEpoch,
    CaptureFrontier,
    ControlCommand,
    ControlStatus,
    ProjectRegistrationRequest,
    Registry,
    SourceApprovalRequest,
    _directory,
    _PhysicalDirectory,
)
from aitm_usage.sources.adapter import AdapterBatch, ProviderAdapter, StreamCursor
from aitm_usage.sources.scan import _CapturePosition
from aitm_usage.types import (
    ClientVersion,
    Provider,
    ProviderCheckpoint,
    SourceCheckpoint,
    SourceCursor,
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


@pytest.fixture
def approval_policy(monkeypatch):
    project_id = UUID(int=2)
    capture = CapturePolicy(monkeypatch, UUID(int=1), CUTOFF, (project_id,))
    capture.stub_native_reads(monkeypatch)
    known_directory = monitor_registry._directory
    project = _PhysicalDirectory("/fixture/project", (1, 10))
    healthy = _PhysicalDirectory("/fixture/healthy-project", (1, 11))
    directories = {directory.path: directory for directory in (project, healthy)}

    def directory(path, **options):
        if path in directories:
            return directories[path]
        return known_directory(path, **options)

    monkeypatch.setattr(monitor_registry, "_directory", directory)
    monkeypatch.setattr(monitor_registry, "_path_exists", lambda path: False)
    existing = replace(capture.view.projects[0], state=project)
    capture.view = replace(capture.view, projects=(existing,))
    return capture


def _enable_capture(capture):
    locator = capture.first
    capture.append(locator)
    project_id = capture.view.projects[0].project_id
    change = CaptureChange(project_id, capture.approved.source_id, True)
    capture.writer.set_permission(change, capture.advance(change, locator))
    return change


def test_no_profile_rejects_new_and_retained_approval(approval_policy):
    capture = approval_policy
    writer = capture.writer
    retained = capture.approved
    writer._live_profile = None
    capture.view = replace(capture.view, sources=())
    with pytest.raises(LedgerError, match="qualification"):
        writer.approve_source(retained.approval)
    assert writer.view().sources == ()

    capture.view = replace(capture.view, sources=(retained,))
    with pytest.raises(LedgerError, match="qualification"):
        writer.approve_source(retained.approval)
    assert writer.view().sources == (retained,)


def test_rejected_approval_and_enable_leave_later_commands_runnable(approval_policy):
    capture = approval_policy
    writer = capture.writer
    project_id = capture.view.projects[0].project_id
    project = ProjectRegistrationRequest(project_id, "/fixture/project", "Project")
    writer.register_project(project)
    retained = capture.approved
    writer._live_profile = None

    # The later disable is allowed without a payload because there is no epoch.
    enable = CaptureChange(project_id, retained.source_id, True)
    disable = replace(enable, enabled=False)
    inbox = CaptureInbox(writer)
    inbox.pending.extend(
        ControlCommand(UUID(int=i), payload)
        for i, payload in enumerate(
            (retained.approval, enable, disable, project), start=3
        )
    )
    receipts = writer.apply_pending(inbox, writer.lease, None)

    assert [receipt.status for receipt in receipts] == [
        ControlStatus.REJECTED,
        ControlStatus.REJECTED,
        ControlStatus.APPLIED,
        ControlStatus.APPLIED,
    ]
    assert writer.view().sources == (retained,)
    assert writer.view().epochs == ()
    assert inbox.pending == []


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
        return NativeJournalFixture(tmp_path, monkeypatch)


def test_retained_codex_refuses_before_payload(approval_policy, monkeypatch):
    from aitm_usage._monitor_qualification import _LiveSourceUnavailable

    capture = approval_policy
    enable = _enable_capture(capture)
    writer = capture.writer
    writer._live_profile = None
    original = writer.view()
    read = Mock(side_effect=AssertionError("unqualified live payload read"))
    monkeypatch.setattr(ProviderAdapter, "read_delta", read)
    with pytest.raises(_LiveSourceUnavailable) as result:
        monitor_scope.ScopeState(writer).read_source(enable.source_id, capture.first)
    assert result.value.decision.source_id == enable.source_id
    assert writer.view() == original
    read.assert_not_called()


def test_retained_grok_refuses_before_payload(
    grok_capture_policy,  # noqa: F811
    monkeypatch,
):
    from aitm_usage._monitor_qualification import _LiveSourceUnavailable
    from aitm_usage.sources.grok import GrokAdapter

    capture = grok_capture_policy
    locator = capture.locator()
    capture.writer._live_profile = None
    original = capture.writer.view()
    read = Mock(side_effect=AssertionError("unqualified Grok payload read"))
    monkeypatch.setattr(GrokAdapter, "read_delta", read)
    with pytest.raises(_LiveSourceUnavailable, match="qualification") as result:
        capture.state.read_source(capture.source_id, locator)
    assert result.value.decision is None
    assert capture.writer.view() == original
    read.assert_not_called()


@pytest.mark.parametrize("change", ("supersede", "revoke", "verifier-unavailable"))
@pytest.mark.parametrize("existing_progress", (False, True))
def test_reserve_revalidates_the_exact_prepared_authority(
    request, monkeypatch, change, existing_progress
):
    from test_monitor_journal import LIVE
    from test_monitor_scope import SOURCE

    from aitm_usage.monitor_journal import RoutingJournal
    from aitm_usage.monitor_scope import ScopeState

    if (change, existing_progress) != ("revoke", True):
        _assert_prepared_authority_rechecked(
            monkeypatch, LIVE, change, existing_progress
        )
        return

    native, writer, _, activate, _, _ = request.getfixturevalue("installed_policy")
    activate()
    journal = RoutingJournal(writer, ScopeState(writer))
    locator = native.locator()
    prepared = journal.prepare(SOURCE, locator)
    assert prepared.candidates
    journal.reserve_batch(prepared)
    progress = journal.cursor_for(SOURCE, locator)
    assert progress == prepared.progress
    before = journal.as_of()
    assert before.claims
    writer._live_profile = None
    with pytest.raises(LedgerError, match="qualification"):
        journal.reserve_batch(prepared)
    assert journal.as_of() == before
    assert journal.cursor_for(SOURCE, locator) == progress


def _assert_prepared_authority_rechecked(
    monkeypatch, source_id, change, existing_progress
):
    from test_codex import CUTOFF

    case = qualification_policy(monkeypatch, source_id, CUTOFF)
    writer, locator = case.writer, case.locator
    source = locator._source
    evidence = writer.source_evidence()
    cursor = SourceCursor(
        source.stream_ref,
        source.locator_ref,
        source.incarnation_ref,
        123,
        evidence.pseudonymize("fixture", "prefix"),
    )
    client = ClientVersion.CODEX_0_167_0_ALPHA_3_2
    checkpoint = SourceCheckpoint(
        cursor,
        ProviderCheckpoint(Provider.CODEX, client_version=client, format_version=1),
    )
    frontier = CaptureFrontier(checkpoint, 1)
    epoch = CaptureEpoch(
        case.view.projects[0].project_id,
        source_id,
        source.stream_ref,
        0,
        evidence.pseudonymize("fixture", "boundary"),
        1,
        True,
        frontier,
        frontier,
        position=cursor,
    )
    view = replace(case.view, epochs=(epoch,))
    monkeypatch.setattr(writer, "view", lambda **_: view)
    position = _CapturePosition(
        cursor, 2, None, Provider.CODEX, source._native_surface, client, 1
    )

    def capture(native, prior, *, fixed=None):
        assert native is source and prior in (None, cursor)
        assert fixed == prior
        return position

    monkeypatch.setattr(monitor_scope, "_capture_position", capture)
    monkeypatch.setattr(monitor_scope, "_check_capture_root", Mock())
    read_delta = Mock(return_value=AdapterBatch(cursor=StreamCursor(checkpoint)))
    monkeypatch.setattr(ProviderAdapter, "read_delta", read_delta)
    state = monitor_scope.ScopeState(writer)
    monkeypatch.setattr(state, "_snapshot", lambda **_: monitor_scope._ScopeSnapshot())

    committed = {}

    def execute(sql, parameters=()):
        if sql.startswith("SELECT cursor FROM progress"):
            result = committed.get("cursor")
        elif sql.startswith("SELECT coalesce(max(sequence)"):
            result = (committed.get("sequence", 0),)
        elif sql.startswith("INSERT OR IGNORE INTO commits"):
            committed["sequence"] = parameters[0]
            result = None
        elif sql.startswith("INSERT INTO progress"):
            committed["cursor"] = (parameters[-1],)
            result = None
        else:
            pytest.fail(f"Unexpected journal statement {sql}")
        return SimpleNamespace(fetchone=lambda: result)

    connection = SimpleNamespace(execute=Mock(side_effect=execute))
    store = SimpleNamespace(
        transaction=lambda **_: nullcontext(connection),
        _current_version=lambda _: 4,
        evidence=evidence,
    )
    monkeypatch.setattr(monitor_journal, "JournalStore", Mock(return_value=store))
    journal = monitor_journal.RoutingJournal(writer, state)
    prepared = journal.prepare(source_id, locator)
    assert prepared.progress == StreamCursor(checkpoint)
    read_delta.assert_called_once()
    if existing_progress:
        journal.reserve_batch(prepared)
        assert journal.cursor_for(source_id, locator) == prepared.progress
    before = committed.copy()
    connection.execute.reset_mock()
    _change_prepared_authority(writer, change)
    with pytest.raises(LedgerError, match="qualification"):
        journal.reserve_batch(prepared)
    assert committed == before
    assert all(
        query.args[0].startswith("SELECT ")
        for query in connection.execute.call_args_list
    )
    read_delta.assert_called_once()


def _change_prepared_authority(writer, change):
    profile = writer._live_profile
    if change == "supersede":
        writer._live_profile = replace(
            profile,
            generation=writer.source_evidence().pseudonymize(
                "generation", "replacement"
            ),
        )
    elif change == "revoke":
        writer._live_profile = None
    else:
        writer._live_profile = replace(profile, current=None)


def test_claude_and_mismatched_build_refuse_under_an_active_profile(approval_policy):
    capture = approval_policy
    writer, retained = capture.writer, capture.approved
    approval = retained.approval
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
    with pytest.raises(LedgerError, match="qualification"):
        writer.approve_source(claude)


def test_revoked_capture_keeps_payload_dependent_disable_pending(approval_policy):
    capture = approval_policy
    writer, locator = capture.writer, capture.first
    enable = _enable_capture(capture)
    writer._live_profile = None
    before = writer.view()
    disable = replace(enable, enabled=False)
    inbox = CaptureInbox(writer)
    command = ControlCommand(UUID(int=987), disable)
    other_id = UUID(int=988)
    healthy = ControlCommand(
        other_id,
        ProjectRegistrationRequest(
            UUID(int=989), "/fixture/healthy-project", "Independent project"
        ),
    )
    inbox.pending.extend((command, healthy))

    def locate(change, known):
        assert change == disable
        return (locator,) if locator.stream_ref in known else ()

    (receipt,) = writer.apply_pending(inbox, writer.lease, locate)
    assert receipt.command_id == other_id
    assert receipt.status is ControlStatus.APPLIED
    assert writer.command_status(other_id) == receipt
    after = writer.view()
    assert after.epochs == before.epochs
    assert after.permissions == before.permissions
    assert writer.command_status(command.command_id) is None
    assert inbox.pending == [command]


def test_disposable_authority_cannot_follow_a_new_writer(approval_policy, monkeypatch):
    capture = approval_policy
    writer = capture.writer
    profile = writer._live_profile
    writer._writer = None
    with pytest.raises(LedgerError, match="lease"):
        writer.approve_source(capture.approved.approval)

    reopened = Registry(writer.root, Mock())
    monkeypatch.setattr(reopened, "view", writer.view)
    monkeypatch.setattr(reopened, "source_evidence", writer.source_evidence)
    reopened._live_profile = profile
    with pytest.raises(LedgerError, match="qualification"):
        reopened.approve_source(capture.approved.approval)


def test_substrate_shim_is_absent_from_the_installed_package():
    from importlib.util import find_spec
    from pathlib import Path

    import aitm_usage

    (root,) = aitm_usage.__path__
    assert find_spec("aitm_usage.legacy_monitor_qualification") is None
    assert not (Path(root) / "conftest.py").exists()


def test_old_capture_frontier_cannot_cross_a_profile_generation(approval_policy):
    capture = approval_policy
    writer, locator = capture.writer, capture.first
    project_id = capture.view.projects[0].project_id
    change = CaptureChange(project_id, capture.approved.source_id, True)
    frontier = writer.capture_frontier(change, locator)
    capture.append(locator)
    writer._live_profile = replace(
        writer._live_profile, generation=capture.ref("next-profile-generation")
    )
    before = writer.view()

    with pytest.raises(LedgerError, match="qualification"):
        writer.verify_boundary(change, locator, frontier)
    assert writer.view() == before


@pytest.mark.parametrize(
    "mismatch",
    (
        "replaced-profile-root",
        "foreign-profile-root",
        "foreign-installation-directory",
        "replaced-approved-directory",
        "missing-installation",
        "ambiguous-installation",
    ),
)
def test_unqualified_physical_custody_cannot_approve_or_read(
    request, monkeypatch, mismatch
):
    from test_monitor_journal import LIVE

    from aitm_usage.monitor_journal import RoutingJournal
    from aitm_usage.monitor_scope import ScopeState

    if mismatch != "replaced-approved-directory":
        _assert_profile_mismatch_refuses_approval_and_read(monkeypatch, LIVE, mismatch)
        return

    previously_admitted = request.getfixturevalue("previously_admitted")
    tmp_path = request.getfixturevalue("tmp_path")
    registry = previously_admitted.registry
    expired_root = _directory(str(registry.root), private=True)
    prior_location = tmp_path / "previous-monitor"
    registry.root.rename(prior_location)
    copytree(prior_location, registry.root)

    with registry.writer() as writer:
        qualify(writer)
        profile = writer._live_profile
        approved = next(s for s in writer.view().sources if s.source_id == LIVE)
        locator = previously_admitted.locator()
        state = ScopeState(writer)
        journal = RoutingJournal(writer, state)
        before = writer.view()
        progress = journal.cursor_for(LIVE, locator)

        def assert_refusal_preserves_state():
            with pytest.raises(LedgerError, match="qualification"):
                writer.approve_source(approved.approval)
            with pytest.raises(LedgerError):
                state.read_source(LIVE, locator)
            assert writer.view() == before
            assert journal.cursor_for(LIVE, locator) == progress

        writer._live_profile = replace(profile, root=expired_root)
        assert_refusal_preserves_state()

        writer._live_profile = profile
        retained = Path(approved.directory.path)
        prior_location = retained.with_name("previous-installation")
        retained.rename(prior_location)
        copytree(prior_location, retained)
        assert_refusal_preserves_state()


def _assert_profile_mismatch_refuses_approval_and_read(
    monkeypatch, source_id, mismatch
):
    from test_codex import CUTOFF

    case = qualification_policy(monkeypatch, source_id, CUTOFF)
    writer, approved, profile = case.writer, case.approved, case.profile
    (installation,) = profile.installations
    changes = {
        "foreign-profile-root": {
            "root": _PhysicalDirectory(str(case.foreign.root), (1, 2))
        },
        "foreign-installation-directory": {
            "installations": (replace(installation, directory=case.root),)
        },
        "missing-installation": {"installations": ()},
        "ambiguous-installation": {"installations": (installation, installation)},
    }
    payload_read = Mock()
    monkeypatch.setattr(ProviderAdapter, "read_delta", payload_read)
    expected = writer._require_live_source(approved)
    assert expected.installation == installation
    initial = writer.view()
    if mismatch == "replaced-profile-root":
        directory = monitor_registry._directory

        def observe_replacement(path, **kwargs):
            observed = directory(path, **kwargs)
            if path == profile.root.path:
                return replace(observed, identity=(1, 99))
            return observed

        monkeypatch.setattr(monitor_registry, "_directory", observe_replacement)
    else:
        writer._live_profile = replace(profile, **changes[mismatch])
    with pytest.raises(LedgerError, match="qualification"):
        writer.approve_source(approved.approval)
    with pytest.raises(LedgerError, match="qualification"):
        monitor_scope.ScopeState(writer).read_source(source_id, case.locator)
    assert writer.view() == initial
    writer._save.assert_not_called()
    payload_read.assert_not_called()


@pytest.mark.parametrize("with_cursor", (False, True))
def test_codex_exclusion_requires_consent_for_its_exact_source(
    approval_policy, monkeypatch, with_cursor
):
    from test_monitor_journal import COPY

    capture = approval_policy
    enable = _enable_capture(capture)
    writer = capture.writer
    (epoch,) = writer.view().epochs
    cursor = StreamCursor(epoch.frontier.checkpoint) if with_cursor else None
    writer._live_profile = None
    capture.view = replace(capture.view, permissions=(replace(enable, source_id=COPY),))
    before = writer.view()
    read = Mock(side_effect=AssertionError("unconsented payload read"))
    monkeypatch.setattr(ProviderAdapter, "read_delta", read)
    with pytest.raises(LedgerError, match="no admitted unbounded read") as refusal:
        monitor_scope.ScopeState(writer).read_source(
            enable.source_id, capture.first, cursor=cursor
        )
    assert getattr(refusal.value, "decision", None) is None
    assert writer.view() is before
    read.assert_not_called()
