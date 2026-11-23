import json
from contextlib import contextmanager, nullcontext
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from shutil import copytree
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, call
from uuid import UUID

import pytest
from grok_capture_policy_cases import grok_capture_policy as grok_capture_policy
from qualification_policy_cases import qualification_policy
from test_monitor_qualification import qualify
from test_monitor_scope import (
    SOURCE,
    ClaudeScopeFixture,
    MemoryNativeScopeFixture,
    NativeScopeFixture,
)

from aitm_usage import monitor_journal, monitor_registry
from aitm_usage.ledger import LedgerError
from aitm_usage.monitor_journal import RoutingJournal
from aitm_usage.monitor_registry import (
    CaptureChange,
    CaptureEpoch,
    CaptureFrontier,
    Registry,
    _ServiceEvidence,
)
from aitm_usage.monitor_scope import ScopeState
from aitm_usage.monitor_types import NativeSurface
from aitm_usage.sources.adapter import SourceLocator, StreamCursor
from aitm_usage.types import (
    Provider,
    ProviderCheckpoint,
    SourceCheckpoint,
    SourceCursor,
    _encode,
)


@pytest.fixture
def admitted_sources(tmp_path, monkeypatch):
    monkeypatch.setattr("aitm_usage.ledger._control_root", lambda: tmp_path / "control")
    authority = object()
    with monkeypatch.context() as setup:
        setup.setattr(Registry, "_require_live_source", lambda *_, **__: authority)
        native = NativeScopeFixture(tmp_path, monkeypatch)
        claude = ClaudeScopeFixture(native)
        with native.registry.writer() as writer:
            claude.approve(writer)
    return native, claude


def store_version(journal):
    with journal._store.transaction() as connection:
        return journal._store._current_version(connection)


class _CoveragePolicyStore:
    """Observe staging and represent only committed coverage to later readers."""

    def __init__(self, evidence):
        self.evidence = evidence
        self.committed = SimpleNamespace(version=4, sequence=0, events={})
        self.attempt = None
        self.writes = []
        self.progress = {}

    @contextmanager
    def transaction(self, *, write=False):
        view = self.committed
        if write:
            view = SimpleNamespace(
                version=view.version, sequence=view.sequence, events=dict(view.events)
            )
            self.attempt = view

        def execute(sql, params=()):
            if sql.startswith("SELECT cursor FROM progress "):
                raw = self.progress.get(params)
                return SimpleNamespace(fetchone=lambda: (raw,) if raw else None)
            if sql == "SELECT coalesce(max(sequence), 0) FROM commits":
                return SimpleNamespace(fetchone=lambda: (view.sequence,))
            if sql == monitor_journal._COVERAGE_ROWS + " WHERE s.identity=?":
                return SimpleNamespace(fetchone=lambda: view.events.get(params[0]))
            if sql == monitor_journal._COVERAGE_ROWS + " WHERE s.sequence=?":
                return SimpleNamespace(
                    fetchall=lambda: [
                        row for row in view.events.values() if row[1] == params[0]
                    ]
                )
            if (
                sql
                == monitor_journal._COVERAGE_ROWS
                + " WHERE s.sequence>? ORDER BY s.sequence"
            ):
                return tuple(row for row in view.events.values() if row[1] > params[0])
            if sql.startswith(
                (
                    "SELECT key,project,payload,digest,sequence FROM claims",
                    "SELECT key, contender, evidence, sequence FROM disputes",
                    "SELECT d.key,c.project,c.payload,c.digest,d.sequence,d.payload"
                    " FROM content_disputes",
                    monitor_journal._DISPOSITION_ROWS,
                    "SELECT s.sequence,s.payload,c.sequence FROM paired_settlements",
                )
            ):
                return ()
            assert write, f"Read-only coverage issued {sql}"
            self.writes.append((sql, params))
            if sql == "INSERT OR IGNORE INTO commits VALUES (?)":
                (view.sequence,) = params
                return None
            assert sql == "INSERT INTO source_coverage VALUES (?,?,?,?)"
            key, sequence, payload, seal = params
            assert sequence == view.sequence
            view.events[key] = (key, sequence, view.sequence, payload, seal)
            return None

        yield SimpleNamespace(execute=execute, view=view, write=write)
        if write:
            self.committed = view

    def _enable_coverage(self, connection):
        assert connection.write
        connection.view.version = 6

    def _current_version(self, connection):
        return connection.view.version


def _consented_view(view, source_id, locator, evidence):
    project = view.projects[0].project_id
    candidate = locator._source
    cursor = SourceCursor(
        locator.stream_ref,
        candidate.locator_ref,
        candidate.incarnation_ref,
        0,
        evidence.pseudonymize("fixture", "anchor"),
    )
    frontier = CaptureFrontier(
        SourceCheckpoint(cursor, ProviderCheckpoint(candidate.provider)), 0
    )
    epoch = CaptureEpoch(
        project,
        source_id,
        locator.stream_ref,
        1,
        evidence.pseudonymize("fixture", "capture-boundary"),
        1,
        True,
        frontier,
        frontier,
    )
    return replace(
        view,
        permissions=(*view.permissions, CaptureChange(project, source_id, True)),
        epochs=(*view.epochs, epoch),
    )


def _coverage_policy(monkeypatch, source, *, provider=Provider.CLAUDE):
    from test_codex import CUTOFF

    authority = qualification_policy(monkeypatch, source, CUTOFF, provider=provider)
    writer, locator = authority.writer, authority.locator
    store = _CoveragePolicyStore(writer.source_evidence())
    authority.view = _consented_view(authority.view, source, locator, store.evidence)
    monkeypatch.setattr(writer, "view", lambda: authority.view)
    monkeypatch.setattr(
        writer, "capture_read_limit", Registry.capture_read_limit.__get__(writer)
    )
    monkeypatch.setattr(monitor_journal, "JournalStore", Mock(return_value=store))
    state = ScopeState(writer)
    return authority, state, RoutingJournal(writer, state), store


@pytest.mark.parametrize("version", (4, 5))
def test_reading_coverage_cannot_upgrade_an_empty_older_store(monkeypatch, version):
    authority, _, journal, store = _coverage_policy(monkeypatch, SOURCE)
    authority.writer._live_profile = None
    store.committed.version = version
    assert journal.coverage_changes(0) == ()
    assert store.attempt is None
    assert store.writes == []
    assert store_version(journal) == version
    with pytest.raises(LedgerError, match="qualification"):
        journal.prepare(SOURCE, authority.locator)
    assert store_version(journal) == 6
    (event,) = journal.coverage_changes(0)
    assert event.sequence == 1


def test_stable_exclusion_is_durable_and_independent_of_healthy_progress(
    monkeypatch,
):
    authority, scopes, journal, store = _coverage_policy(monkeypatch, SOURCE)
    locator = authority.locator
    healthy = UUID(int=22)
    started = authority.view.epochs[0].frontier.checkpoint
    expected = StreamCursor(replace(started, cursor=replace(started.cursor, offset=64)))
    healthy_stream = monitor_journal._stream(healthy, locator)
    store.progress[healthy_stream] = _encode(expected, StreamCursor).encode()
    store.committed.version = 5
    store.committed.sequence = 7
    before = journal.as_of()

    with pytest.raises(LedgerError, match="qualification"):
        journal.prepare(SOURCE, locator)
    (event,) = journal.coverage_changes(before.sequence)
    assert event.sequence == before.sequence + 1
    assert event.coverage.reason == "UNQUALIFIED_SOURCE"
    assert event.coverage.extent == "unknown"
    assert event.disposition is None and event.paired is None
    assert journal.cursor_for(SOURCE, locator) is None
    assert journal.cursor_for(healthy, locator) == expected
    reopened = RoutingJournal(authority.writer, scopes)
    assert reopened.as_of(before.sequence) == before
    assert reopened.coverage_changes(0) == (event,)
    assert reopened.coverage_changes(event.sequence) == ()
    assert store_version(reopened) == 6
    assert [sql for sql, _ in store.writes] == [
        "INSERT OR IGNORE INTO commits VALUES (?)",
        "INSERT INTO source_coverage VALUES (?,?,?,?)",
    ]


def test_restart_and_late_growth_do_not_duplicate_coverage_or_commit(monkeypatch):
    require_live = Registry._require_live_source
    native = MemoryNativeScopeFixture(monkeypatch, with_claude=True)
    claude = ClaudeScopeFixture(native)
    with native.registry.writer() as writer:
        claude.approve(writer)
    monkeypatch.setattr(Registry, "_require_live_source", require_live)
    store = _CoveragePolicyStore(native.evidence)

    def open_store(writer):
        assert writer.root == native.registry.root
        assert writer.source_evidence() == store.evidence
        return store

    monkeypatch.setattr(monitor_journal, "JournalStore", open_store)
    with native.registry.writer() as writer:
        writer._live_profile = None
        journal = RoutingJournal(writer, ScopeState(writer))
        with pytest.raises(LedgerError, match="qualification"):
            journal.prepare(claude.source_id, claude.locator())
        (event,) = journal.coverage_changes(0)
        writes = store.writes.copy()

    claude.append(claude.request(10))
    with native.registry.writer() as writer:
        writer._live_profile = None
        reopened = RoutingJournal(writer, ScopeState(writer))
        with pytest.raises(LedgerError, match="qualification"):
            reopened.prepare(claude.source_id, claude.locator())
        assert reopened.coverage_changes(0) == (event,)
        assert reopened.as_of().sequence == event.sequence
        assert store.writes == writes
        with pytest.raises(LedgerError, match="qualification"):
            reopened.prepare(SOURCE, native.locator())
        (new,) = reopened.coverage_changes(event.sequence)
        assert new.sequence == event.sequence + 1
        assert new.coverage.installation != event.coverage.installation


def _changed_live_profile(profile, case, approved, foreign, old_root):
    def unavailable(_):
        raise OSError("verifier unavailable")

    item = next(i for i in profile.installations if i.directory == approved.directory)
    fields = {
        "omitted": {"installations": ()},
        "valid-matrix-exclusion": {},
        "duplicates": {"installations": (item, item)},
        "missing-verifier": {"current": None},
        "rejected-verifier": {"current": lambda _: False},
        "verifier-error": {"current": unavailable},
        "foreign-root": {
            "root": monitor_registry._directory(str(foreign.root), private=True)
        },
        "replaced-root": {"root": old_root},
        "foreign-generation": {
            "generation": foreign.source_evidence().pseudonymize("generation", "other")
        },
        "foreign-lease": {"lease": foreign.lease},
        "wrong-profile-type": {},
    }[case]
    if case == "wrong-profile-type":

        class DifferentProfile(type(profile)):
            pass

        profile = DifferentProfile(
            profile.root,
            profile.lease,
            profile.generation,
            profile.installations,
            profile.current,
        )
    return replace(profile, **fields)


def _assert_unstable_profile_does_not_stage_coverage(monkeypatch, case, use_claude):
    from test_codex import CUTOFF

    authority = qualification_policy(
        monkeypatch,
        SOURCE,
        CUTOFF,
        provider=Provider.CLAUDE if use_claude else Provider.CODEX,
    )
    writer, locator = authority.writer, authority.locator
    writer._live_profile = _changed_live_profile(
        authority.profile, case, authority.approved, authority.foreign, authority.root
    )
    if case == "replaced-root":
        observed_directory = monitor_registry._directory

        def replacement(path, **kwargs):
            directory = observed_directory(path, **kwargs)
            if path == authority.root.path:
                return replace(directory, identity=(1, 99))
            return directory

        monkeypatch.setattr(monitor_registry, "_directory", replacement)

    reader, connection = Mock(), Mock()
    reader.execute.return_value.fetchone.return_value = None

    def transaction(*, write=False):
        return nullcontext(connection if write else reader)

    store = SimpleNamespace(
        transaction=Mock(side_effect=transaction), _enable_coverage=Mock()
    )
    monkeypatch.setattr(monitor_journal, "JournalStore", Mock(return_value=store))
    journal = RoutingJournal(writer, ScopeState(writer))
    with pytest.raises(LedgerError, match="qualification"):
        journal.prepare(SOURCE, locator)
    assert store.transaction.call_args_list == [call(), call(write=True)]
    store._enable_coverage.assert_not_called()
    connection.execute.assert_not_called()


@pytest.mark.parametrize(
    ("case", "use_claude", "records"),
    (
        ("omitted", False, True),
        ("valid-matrix-exclusion", True, True),
        ("duplicates", True, False),
        ("missing-verifier", True, False),
        ("foreign-root", True, False),
        ("replaced-root", True, False),
        ("foreign-generation", True, False),
        ("foreign-lease", True, False),
        ("wrong-profile-type", True, False),
        ("rejected-verifier", False, False),
        ("verifier-error", False, False),
    ),
)
def test_only_stable_profile_denials_become_coverage(
    monkeypatch, case, use_claude, records
):
    if not records:
        _assert_unstable_profile_does_not_stage_coverage(monkeypatch, case, use_claude)
        return
    authority, _, journal, store = _coverage_policy(
        monkeypatch,
        SOURCE,
        provider=Provider.CLAUDE if use_claude else Provider.CODEX,
    )
    authority.writer._live_profile = _changed_live_profile(
        authority.profile,
        case,
        authority.approved,
        authority.foreign,
        authority.root,
    )
    with pytest.raises(LedgerError, match="qualification"):
        journal.prepare(SOURCE, authority.locator)
    (change,) = journal.coverage_changes(0)
    assert change.coverage.generation == authority.profile.generation
    assert change.coverage.reason == "UNQUALIFIED_SOURCE"
    assert store.committed.sequence == change.sequence == 1
    assert store_version(journal) == 6
    assert journal.cursor_for(SOURCE, authority.locator) is None


@pytest.mark.parametrize("failure", ("policy", "consent", "location"))
@pytest.mark.parametrize("confirmation", (1, 2))
def test_changed_authority_rolls_back_any_migration_and_event(
    monkeypatch, failure, confirmation
):
    _assert_changed_authority_policy(monkeypatch, failure, confirmation)


def _assert_native_directory_change_rolls_back(journal, state, claude, monkeypatch):
    locator = claude.locator()
    verify = state._confirm_live_exclusion
    checks = 0
    old = Path(claude.root.path)
    prior = old.with_name("previous-claude")

    def changed(*args):
        nonlocal checks
        checks += 1
        if checks == 2:
            old.rename(prior)
            copytree(prior, old)
        return verify(*args)

    with monkeypatch.context() as fault:
        fault.setattr(state, "_confirm_live_exclusion", changed)
        with pytest.raises(LedgerError, match="qualification"):
            journal.prepare(claude.source_id, locator)
    assert checks == 2
    assert journal.coverage_changes(0) == ()
    assert journal.as_of().sequence == 0
    assert journal.cursor_for(claude.source_id, locator) is None
    assert store_version(journal) == 4
    # Restore the original inode before validating the independent successful path.
    old.rename(old.with_name("replacement-claude"))
    prior.rename(old)


def _assert_changed_authority_policy(monkeypatch, failure, confirmation):
    authority, state, journal, store = _coverage_policy(monkeypatch, SOURCE)
    writer, locator = authority.writer, authority.locator
    confirm = state._confirm_live_exclusion
    observed_directory = monitor_registry._directory
    checks = 0

    def changed_directory(path, **kwargs):
        directory = observed_directory(path, **kwargs)
        if path == authority.approved.directory.path:
            return replace(directory, identity=(1, 99))
        return directory

    def changed(*args):
        nonlocal checks
        checks += 1
        if checks == confirmation:
            if failure == "policy":
                writer._live_profile = replace(
                    authority.profile,
                    generation=store.evidence.pseudonymize(
                        "fixture", "next-generation"
                    ),
                )
            elif failure == "consent":
                authority.view = replace(authority.view, permissions=())
            else:
                monkeypatch.setattr(monitor_registry, "_directory", changed_directory)
        return confirm(*args)

    monkeypatch.setattr(state, "_confirm_live_exclusion", changed)
    with pytest.raises(LedgerError, match="qualification"):
        journal.prepare(SOURCE, locator)
    assert checks == confirmation
    if confirmation == 1:
        assert (
            store.attempt.version,
            store.attempt.sequence,
            store.attempt.events,
        ) == (4, 0, {})
    else:
        assert (store.attempt.version, store.attempt.sequence) == (6, 1)
        (row,) = store.attempt.events.values()
        change = monitor_journal._stored_coverage(row, store.evidence)
        assert change.sequence == 1
        assert change.coverage.generation == authority.profile.generation
    assert journal.coverage_changes(0) == ()
    assert store.committed.sequence == 0
    assert journal.cursor_for(SOURCE, locator) is None
    assert store_version(journal) == 4


@pytest.mark.parametrize(
    "override",
    (
        {},
        {"extent": "known"},
        {"reason": "UNVERIFIED"},
        {"root": "broader-root"},
    ),
)
def test_coverage_rejects_only_reserved_variants_with_matching_key_and_seal(override):
    from aitm_usage import monitor_journal

    evidence, event = _sample_coverage()
    payload = json.loads(_encode(event, monitor_journal.JournalCoverage)) | override
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    identity_fields = {
        field: value for field, value in payload.items() if field != "observed_at"
    }
    identity = evidence.pseudonymize(
        "journal-coverage-key-v1",
        json.dumps(identity_fields, separators=(",", ":"), sort_keys=True),
    )
    seal = monitor_journal._coverage_seal(1, raw, evidence)
    row = (identity.value, 1, 1, raw, seal.value)
    if override:
        with pytest.raises(LedgerError, match="Invalid private journal coverage"):
            monitor_journal._stored_coverage(row, evidence)
    else:
        assert monitor_journal._stored_coverage(
            row, evidence
        ) == monitor_journal.JournalChange(1, coverage=event)


def _sample_coverage(evidence=None):
    from aitm_usage import monitor_journal

    if evidence is None:
        evidence = _ServiceEvidence(b"journal-coverage-policy-fixture")
    value = monitor_journal.JournalCoverage(
        monitor_journal._CoverageReason.UNQUALIFIED_SOURCE,
        evidence.pseudonymize("fixture", "installation"),
        evidence.pseudonymize("fixture", "generation"),
        monitor_journal._CoverageExtent.UNKNOWN,
        datetime(2026, 1, 1, tzinfo=UTC),
    )
    return evidence, value


def test_copied_scope_and_missing_consent_cannot_publish_coverage(
    monkeypatch,
):
    from aitm_usage._monitor_qualification import _LiveSourceUnavailable

    authority, state, journal, store = _coverage_policy(
        monkeypatch, SOURCE, provider=Provider.CODEX
    )
    claude = UUID(int=6)
    approved = replace(
        authority.approved,
        approval=replace(
            authority.approved.approval,
            source_id=claude,
            provider="claude",
            surface="claude-code-macos",
            client_version="2.1.318",
        ),
    )
    locator = SourceLocator(
        replace(
            authority.locator._source,
            provider=Provider.CLAUDE,
            stream_ref=store.evidence.pseudonymize("fixture", "claude-stream"),
            _native_surface=NativeSurface.CLAUDE_CODE_MACOS,
        )
    )
    authority.view = _consented_view(
        replace(authority.view, sources=(*authority.view.sources, approved)),
        claude,
        locator,
        store.evidence,
    )
    discovered = {
        SOURCE: (authority.approved, authority.locator),
        claude: (approved, locator),
    }

    def current_candidate(view, source_id, candidate, **kwargs):
        source, current = discovered[source_id]
        assert source in view.sources and candidate is current
        return source, current

    monkeypatch.setattr(authority.writer, "_current_candidate", current_candidate)
    with pytest.raises(_LiveSourceUnavailable) as initial:
        state.read_source(claude, locator)

    def copy_denial(*_, **__):
        raise _LiveSourceUnavailable(replace(initial.value.decision, source_id=SOURCE))

    with monkeypatch.context() as patch:
        patch.setattr(state, "read_source", copy_denial)
        with pytest.raises(_LiveSourceUnavailable):
            journal.prepare(SOURCE, authority.locator)
    assert journal.coverage_changes(0) == ()

    authority.view = replace(
        authority.view,
        permissions=tuple(
            p for p in authority.view.permissions if p.source_id != claude
        ),
    )
    with pytest.raises(LedgerError, match="no admitted unbounded read"):
        journal.prepare(claude, locator)
    assert journal.coverage_changes(0) == ()
    assert store_version(journal) == 4


def test_unrelated_unavailable_source_key_cannot_mint_coverage(monkeypatch):
    from test_codex import CUTOFF
    from test_monitor_journal_store import _journal_observations

    memory = _journal_observations(monkeypatch)
    evidence = memory.writer.source_evidence()
    authority = qualification_policy(
        monkeypatch, SOURCE, CUTOFF, evidence_key=evidence.key
    )
    writer = authority.writer
    writer._writer = memory.writer.lease
    connection = MagicMock()

    def execute(sql):
        if sql == "BEGIN":
            return None
        assert sql == "SELECT coalesce(max(sequence), 0) FROM commits"
        return SimpleNamespace(fetchone=lambda: (0,))

    connection.execute.side_effect = execute
    memory.open_database.return_value = nullcontext(connection)
    journal = RoutingJournal(writer, ScopeState(writer))
    memory.open_database.reset_mock()
    with monkeypatch.context() as patch:
        patch.setattr(
            writer, "view", lambda: replace(authority.view, source_key_id=None)
        )
        with pytest.raises(
            LedgerError,
            match="Routing journal registry source key identity changed",
        ):
            journal.prepare(SOURCE, authority.locator)
    memory.open_database.assert_not_called()
    assert journal.coverage_changes(0) == ()
    assert store_version(journal) == 4


def test_lease_loss_is_not_reported_as_a_policy_refusal(monkeypatch):
    authority, _, journal, store = _coverage_policy(monkeypatch, SOURCE)
    writer = authority.writer
    lease = writer.lease
    stable = writer._stable_live_exclusion

    def lose_lease(approved):
        result = stable(approved)
        writer._writer = None
        return result

    monkeypatch.setattr(writer, "_stable_live_exclusion", lose_lease)
    try:
        with pytest.raises(LedgerError, match="coordinator lease is required"):
            journal.prepare(SOURCE, authority.locator)
    finally:
        writer._writer = lease

    assert store.committed.sequence == 0
    assert journal.coverage_changes(0) == ()
    assert store_version(journal) == 4


@pytest.mark.parametrize("alter", ("identity", "seal", "commit"))
def test_coverage_readback_rejects_corrupted_event_binding(alter):
    from aitm_usage import monitor_journal

    evidence, event = _sample_coverage()
    raw = _encode(event, monitor_journal.JournalCoverage).encode()
    key = monitor_journal._coverage_key(event, evidence).value
    seal = monitor_journal._coverage_seal(1, raw, evidence).value
    valid = (key, 1, 1, raw, seal)
    assert monitor_journal._stored_coverage(valid, evidence).coverage == event
    damaged = {
        "identity": ("invalid", 1, 1, raw, seal),
        "seal": (key, 1, 1, raw, "invalid"),
        "commit": (key, 1, None, raw, seal),
    }[alter]
    with pytest.raises(LedgerError, match="Invalid private journal coverage"):
        monitor_journal._stored_coverage(damaged, evidence)


def test_coverage_readback_rejects_deleted_commit_on_disk(
    admitted_sources, monkeypatch
):
    from test_monitor_journal_store import _sqlite

    from aitm_usage._monitor_journal_store import _DATABASE, _STORE

    native, claude = admitted_sources
    with native.registry.writer() as writer:
        qualify(writer)
        state = ScopeState(writer)
        journal = RoutingJournal(writer, state)
        _assert_native_directory_change_rolls_back(journal, state, claude, monkeypatch)
        locator = native.locator()
        native.append()
        journal.reserve_batch(journal.prepare(SOURCE, locator))
        with journal._store.transaction(write=True) as connection:
            journal._store._enable_paired(connection)
        before = journal.as_of()
        before_cursor = journal.cursor_for(SOURCE, locator)
        assert store_version(journal) == 5 and before.claims and before_cursor
        with pytest.raises(LedgerError, match="qualification"):
            journal.prepare(claude.source_id, claude.locator())
        (event,) = journal.coverage_changes(0)
        assert event.sequence == before.sequence + 1
        assert store_version(journal) == 6
        assert journal.as_of(before.sequence) == before
        assert journal.as_of().claims == before.claims
        assert journal.cursor_for(SOURCE, locator) == before_cursor
        candidate = journal.publication_candidate(event)
    with native.registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        assert journal.publication_candidate(event) == candidate
        path = writer.root / _STORE / _DATABASE
        _assert_native_coverage_publication_recovers_after_corruption(
            journal, event, candidate, writer.source_evidence(), path
        )
        with _sqlite(path) as connection:
            connection.execute(
                "DELETE FROM commits WHERE sequence=?", (event.sequence,)
            )
        with pytest.raises(LedgerError, match="Invalid private journal coverage"):
            journal.coverage_changes(0)


def test_open_refuses_unknown_schema_version(monkeypatch):
    from test_monitor_journal_store import _journal_metadata, _journal_observations

    from aitm_usage import _monitor_journal_store as store

    validate = store._validate_identity
    memory = _journal_observations(monkeypatch)
    monkeypatch.setattr(store, "_validate_identity", validate)
    for version, damage, message in (
        (
            store._DELIVERY_SCHEMA_VERSION,
            "ALTER TABLE claims ADD COLUMN unexpected TEXT",
            "Invalid routing journal table schema",
        ),
        (
            store._DELIVERY_SCHEMA_VERSION + 1,
            None,
            "Unsupported routing journal schema version",
        ),
    ):
        metadata = _journal_metadata(monkeypatch, version, damage)
        connection = MagicMock()

        def read(sql):
            if sql == "BEGIN":
                return None
            return metadata.execute(sql)

        connection.execute.side_effect = read
        memory.open_database.return_value = nullcontext(connection)
        memory.open_database.reset_mock()
        with pytest.raises(LedgerError, match=message):
            RoutingJournal(memory.writer, ScopeState(memory.writer))
        memory.open_database.assert_called_once_with(
            memory.store / store._DATABASE, write=False
        )


@pytest.mark.parametrize("consent", (False, True))
def test_grok_coverage_rechecks_exact_consent_before_payload(
    grok_capture_policy, monkeypatch, consent
):
    case = grok_capture_policy
    case.write(case.rows, 2)
    locator = case.locator()
    writer = case.writer
    if consent:
        initial = writer.view()
        permission = CaptureChange(case.project, case.source_id, True)
        writer._save(replace(initial, permissions=(*initial.permissions, permission)))
    store = _CoveragePolicyStore(writer.source_evidence())
    monkeypatch.setattr(monitor_journal, "JournalStore", lambda _: store)
    payload = Mock(side_effect=AssertionError("unqualified payload was read"))
    monkeypatch.setattr(case.reader, "read_delta", payload)
    journal = RoutingJournal(writer, case.state)
    installed = writer._live_profile
    writer._live_profile = None

    with pytest.raises(LedgerError, match="qualification"):
        journal.prepare(case.source_id, locator)
    if consent:
        (event,) = journal.coverage_changes(0)
        assert event.sequence == store.committed.sequence == 1
        assert event.coverage.reason == "UNQUALIFIED_SOURCE"
        assert store_version(journal) == 6
        assert [sql for sql, _ in store.writes] == [
            "INSERT OR IGNORE INTO commits VALUES (?)",
            "INSERT INTO source_coverage VALUES (?,?,?,?)",
        ]
    else:
        assert journal.coverage_changes(0) == ()
        assert store.committed.sequence == 0
        assert store_version(journal) == 4
        assert store.attempt is None
        assert store.writes == []

    before = journal.coverage_changes(0)
    writer._live_profile = installed
    with pytest.raises(LedgerError, match="no verified native session"):
        journal.prepare(case.source_id, locator)
    assert journal.coverage_changes(0) == before
    assert store.committed.sequence == len(before)
    payload.assert_not_called()


def test_coverage_readback_requires_the_original_live_writer(monkeypatch):
    from test_monitor_journal_store import _journal_observations

    from aitm_usage import _monitor_journal_store as journal_store

    observed = _journal_observations(monkeypatch)
    root = observed.writer.root
    evidence, coverage = _sample_coverage(observed.writer.source_evidence())
    raw = _encode(coverage, monitor_journal.JournalCoverage).encode()
    key = monitor_journal._coverage_key(coverage, evidence).value
    seal = monitor_journal._coverage_seal(1, raw, evidence).value
    row = (key, 1, 1, raw, seal)

    def execute(sql, parameters=()):
        if sql == "BEGIN":
            return None
        if sql == "SELECT coalesce(max(sequence), 0) FROM commits":
            return SimpleNamespace(fetchone=lambda: (1,))
        assert (
            sql
            == monitor_journal._COVERAGE_ROWS
            + " WHERE s.sequence>? ORDER BY s.sequence"
        )
        assert parameters == (0,)
        return (row,)

    def lease(path, *, create):
        assert path.parent == root and create
        return nullcontext(
            SimpleNamespace(identities=observed.writer.lease.identities, check=Mock())
        )

    prepared = observed.writer.view()
    monkeypatch.setattr(Registry, "view", lambda self: prepared)
    monkeypatch.setattr(Registry, "source_evidence", lambda self: evidence)
    monkeypatch.setattr(monitor_registry, "_ensure_private_directory", Mock())
    monkeypatch.setattr(monitor_registry, "_lease", lease)
    monkeypatch.setattr(journal_store, "_validate_identity", Mock(return_value=6))
    connection = MagicMock()
    connection.execute.side_effect = execute
    observed.open_database.return_value = nullcontext(connection)

    registry = Registry(root)
    with registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        (event,) = journal.coverage_changes(0)
        assert event == monitor_journal.JournalChange(1, coverage=coverage)

    calls = observed.open_database.call_count
    with pytest.raises(LedgerError, match="coordinator lease is required"):
        journal.coverage_changes(0)
    with registry.writer() as reopened:
        with pytest.raises(LedgerError, match="coordinator lease is required"):
            journal.coverage_changes(0)
        assert observed.open_database.call_count == calls
        assert RoutingJournal(reopened, ScopeState(reopened)).coverage_changes(0) == (
            event,
        )


def test_unqualified_source_gap_publishes_without_project_write_or_ack(monkeypatch):
    from aitm_usage.ledger import Ledger
    from aitm_usage.monitor_journal import JournalChange, JournalCoverage

    authority, state, journal, store = _coverage_policy(monkeypatch, SOURCE)
    writer, source = authority.writer, authority.locator
    writer._live_profile = None
    seed = store.evidence.pseudonymize("partial-test", "coverage")
    forged = JournalCoverage(
        monitor_journal._CoverageReason.UNQUALIFIED_SOURCE,
        seed,
        seed,
        monitor_journal._CoverageExtent.UNKNOWN,
        datetime.now(UTC),
    )
    store.committed.sequence = 1
    assert store_version(journal) == 4
    with pytest.raises(LedgerError, match="Verified journal-only publication"):
        journal.publication_candidate(JournalChange(1, coverage=forged))
    with pytest.raises(LedgerError, match="qualification"):
        journal.prepare(SOURCE, source)
    (change,) = journal.coverage_changes(0)
    assert change.sequence == 2 and store_version(journal) == 6
    before = journal.as_of()
    writes = store.writes.copy()
    prior = journal.cursor_for(SOURCE, source)

    def project_access(*_, **__):
        pytest.fail("A journal-only candidate touched a destination")

    monkeypatch.setattr(Ledger, "open", project_access)
    monkeypatch.setattr(Ledger, "writer", project_access)
    candidate = journal.publication_candidate(change)
    assert candidate.basis == "coverage" and candidate.sequence == change.sequence
    store.evidence.validate_source_ref(candidate.identity)
    assert journal.publication_candidate(change) == candidate
    assert journal.as_of() == before
    assert journal.cursor_for(SOURCE, source) is prior is None
    assert journal.coverage_changes(0) == (change,)
    for invalid in (
        replace(change, sequence=change.sequence + 1),
        JournalChange(change.sequence),
        replace(change, coverage=replace(change.coverage, reason="UNQUALIFIED_SOURCE")),
    ):
        with pytest.raises(LedgerError, match="Verified journal-only publication"):
            journal.publication_candidate(invalid)

    reopened = RoutingJournal(writer, state)
    assert reopened.publication_candidate(change) == candidate
    assert reopened.as_of() == before
    assert store.writes == writes

    (recorded,) = store.committed.events.values()
    key, sequence, commit, _, seal = recorded
    alternate = replace(change.coverage, installation=seed)
    alternate_key = monitor_journal._coverage_key(alternate, store.evidence).value
    alternate_payload = _encode(alternate, JournalCoverage).encode()
    store.committed.events = {
        alternate_key: (alternate_key, sequence, commit, alternate_payload, seal)
    }
    with pytest.raises(LedgerError, match="Verified journal-only publication"):
        reopened.publication_candidate(change)
    with pytest.raises(LedgerError, match="Invalid private journal coverage"):
        reopened.coverage_changes(0)
    store.committed.events = {key: recorded}
    assert reopened.publication_candidate(change) == candidate
    assert store.writes == writes


def _assert_native_coverage_publication_recovers_after_corruption(
    journal, change, candidate, evidence, database
):
    from aitm_usage._monitor_journal_store import _DELIVERY_SCHEMA_VERSION, _open
    from aitm_usage.monitor_journal import JournalCoverage, _coverage_key
    from aitm_usage.types import _decode

    seed = evidence.pseudonymize("partial-test", "coverage")
    alternate = replace(change.coverage, installation=seed)
    replacement = _encode(
        alternate, JournalCoverage, validate_ref=evidence.validate_source_ref
    ).encode()
    assert _decode(replacement, JournalCoverage) == alternate
    alternate_key = _coverage_key(alternate, evidence).value
    with journal._store.transaction(write=True) as connection:
        key, raw = connection.execute(
            "SELECT identity,payload FROM source_coverage"
        ).fetchone()
        # A complete, canonical substitute preserves the old seal.
        connection.execute(
            "UPDATE source_coverage SET identity=?,payload=?",
            (alternate_key, replacement),
        )
    with pytest.raises(LedgerError, match="Verified journal-only publication"):
        journal.publication_candidate(change)
    with pytest.raises(LedgerError, match="Invalid private journal coverage"):
        journal.coverage_changes(0)
    with journal._store.transaction(write=True) as connection:
        connection.execute(
            "UPDATE source_coverage SET identity=?,payload=?", (key, raw)
        )
    assert journal.publication_candidate(change) == candidate

    journal.enable_delivery(journal.as_of().sequence)
    assert journal.coverage_changes(0) == (change,)
    assert journal.publication_candidate(change) == candidate

    with _open(database, write=True) as connection:
        connection.execute(f"PRAGMA user_version = {_DELIVERY_SCHEMA_VERSION + 1}")
    with pytest.raises(LedgerError, match="Unsupported routing journal schema"):
        journal.publication_candidate(change)
    with _open(database, write=True) as connection:
        assert connection.execute("PRAGMA user_version").fetchone() == (
            _DELIVERY_SCHEMA_VERSION + 1,
        )
        connection.execute(f"PRAGMA user_version = {_DELIVERY_SCHEMA_VERSION}")
