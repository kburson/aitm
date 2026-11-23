import json
from contextlib import nullcontext
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from shutil import copytree
from types import SimpleNamespace
from unittest.mock import Mock, call
from uuid import UUID

import pytest
from qualification_policy_cases import qualification_policy
from test_monitor_qualification import qualify
from test_monitor_scope import SOURCE, ClaudeScopeFixture, NativeScopeFixture

from aitm_usage import monitor_journal, monitor_registry
from aitm_usage.ledger import LedgerError
from aitm_usage.monitor_journal import RoutingJournal
from aitm_usage.monitor_registry import (
    ApprovedSource,
    Registry,
    SourceApprovalRequest,
    _directory,
    _ServiceEvidence,
)
from aitm_usage.monitor_scope import ScopeState
from aitm_usage.sources.adapter import SourceRoot
from aitm_usage.types import Provider, _encode


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


@pytest.mark.parametrize("version", (4, 5))
def test_reading_coverage_cannot_upgrade_an_empty_older_store(
    admitted_sources, version
):
    native, claude = admitted_sources
    with native.registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        if version == 5:
            with journal._store.transaction(write=True) as connection:
                journal._store._enable_paired(connection)
        assert store_version(journal) == version
        assert journal.coverage_changes(0) == ()
        assert store_version(journal) == version
        with pytest.raises(LedgerError, match="qualification"):
            journal.prepare(claude.source_id, claude.locator())
        assert store_version(journal) == 6
        assert len(journal.coverage_changes(0)) == 1


def test_stable_exclusion_is_durable_and_independent_of_healthy_progress(
    admitted_sources,
):
    native, claude = admitted_sources
    with native.registry.writer() as writer:
        qualify(writer)
        journal = RoutingJournal(writer, ScopeState(writer))
        locator = native.locator()
        native.append()
        prepared = journal.prepare(SOURCE, locator)
        journal.reserve_batch(prepared)
        before = journal.as_of()
        before_cursor = journal.cursor_for(SOURCE, locator)
        assert before.claims and before_cursor is not None

        with pytest.raises(LedgerError, match="qualification"):
            journal.prepare(claude.source_id, claude.locator())
        (event,) = journal.coverage_changes(before.sequence)
        assert event.sequence == before.sequence + 1
        assert event.coverage.reason == "UNQUALIFIED_SOURCE"
        assert event.coverage.extent == "unknown"
        assert event.disposition is None and event.paired is None
        assert journal.cursor_for(claude.source_id, claude.locator()) is None
        assert journal.cursor_for(SOURCE, locator) == before_cursor
        assert journal.as_of(before.sequence) == before
        assert journal.as_of().claims == before.claims
        assert journal.as_of().settlements == before.settlements
        assert journal.as_of().dispositions == before.dispositions
        assert journal.coverage_changes(event.sequence) == ()
        assert store_version(journal) == 6


def test_restart_and_late_growth_do_not_duplicate_coverage_or_commit(admitted_sources):
    native, claude = admitted_sources
    with native.registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        with pytest.raises(LedgerError, match="qualification"):
            journal.prepare(claude.source_id, claude.locator())
        (event,) = journal.coverage_changes(0)

    claude.append(claude.request(10))
    with native.registry.writer() as writer:
        reopened = RoutingJournal(writer, ScopeState(writer))
        with pytest.raises(LedgerError, match="qualification"):
            reopened.prepare(claude.source_id, claude.locator())
        assert reopened.coverage_changes(0) == (event,)
        assert reopened.as_of().sequence == event.sequence
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
    request, monkeypatch, case, use_claude, records
):
    if not records and case != "replaced-root":
        _assert_unstable_profile_does_not_stage_coverage(monkeypatch, case, use_claude)
        return

    admitted_sources = request.getfixturevalue("admitted_sources")
    tmp_path = request.getfixturevalue("tmp_path")
    native, claude = admitted_sources
    source = claude.source_id if use_claude else SOURCE

    old_root = _directory(str(native.registry.root), private=True)
    if case == "replaced-root":
        previous = tmp_path / "previous-monitor"
        native.registry.root.rename(previous)
        copytree(previous, native.registry.root)

    other = Registry(tmp_path / "other-monitor")
    with native.registry.writer() as writer, other.writer() as foreign:
        qualify(writer)
        approved = next(s for s in writer.view().sources if s.source_id == source)
        writer._live_profile = _changed_live_profile(
            writer._live_profile, case, approved, foreign, old_root
        )
        locator = claude.locator() if use_claude else native.locator()
        journal = RoutingJournal(writer, ScopeState(writer))
        with pytest.raises(LedgerError, match="qualification"):
            journal.prepare(source, locator)
        changes = journal.coverage_changes(0)
        assert len(changes) == int(records)
        assert store_version(journal) == (6 if records else 4)
        assert journal.cursor_for(source, locator) is None


@pytest.mark.parametrize("failure", ("policy", "consent", "location"))
@pytest.mark.parametrize("confirmation", (1, 2))
def test_changed_authority_rolls_back_any_migration_and_event(
    admitted_sources, monkeypatch, failure, confirmation
):
    native, claude = admitted_sources
    with native.registry.writer() as writer:
        qualify(writer)
        state = ScopeState(writer)
        journal = RoutingJournal(writer, state)
        locator = claude.locator()
        verify = state._confirm_live_exclusion
        checks = 0

        def changed(*args):
            nonlocal checks
            checks += 1
            if checks == confirmation:
                if failure == "policy":
                    qualify(writer)
                elif failure == "consent":
                    before = writer.view()
                    writer._save(
                        replace(
                            before,
                            permissions=tuple(
                                p
                                for p in before.permissions
                                if p.source_id != claude.source_id
                            ),
                        )
                    )
                else:
                    old = Path(claude.root.path)
                    prior = old.with_name("previous-claude")
                    old.rename(prior)
                    copytree(prior, old)
            return verify(*args)

        monkeypatch.setattr(state, "_confirm_live_exclusion", changed)
        with pytest.raises(LedgerError, match="qualification"):
            journal.prepare(claude.source_id, locator)
        assert checks == confirmation
        assert journal.coverage_changes(0) == ()
        assert journal.as_of().sequence == 0
        assert journal.cursor_for(claude.source_id, locator) is None
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


def _sample_coverage():
    from aitm_usage import monitor_journal

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
    admitted_sources, monkeypatch
):
    from aitm_usage._monitor_qualification import _LiveSourceUnavailable

    native, claude = admitted_sources
    with native.registry.writer() as writer:
        state = ScopeState(writer)
        journal = RoutingJournal(writer, state)
        with pytest.raises(_LiveSourceUnavailable) as initial:
            state.read_source(claude.source_id, claude.locator())
        original = state.read_source

        def copy_denial(*_, **__):
            raise _LiveSourceUnavailable(
                replace(initial.value.decision, source_id=SOURCE)
            )

        monkeypatch.setattr(state, "read_source", copy_denial)
        with pytest.raises(_LiveSourceUnavailable):
            journal.prepare(SOURCE, native.locator())
        assert journal.coverage_changes(0) == ()

        monkeypatch.setattr(state, "read_source", original)
        before = writer.view()
        writer._save(
            replace(
                before,
                permissions=tuple(
                    p for p in before.permissions if p.source_id != claude.source_id
                ),
            )
        )
        with pytest.raises(LedgerError, match="no admitted unbounded read"):
            journal.prepare(claude.source_id, claude.locator())
        assert journal.coverage_changes(0) == ()


def test_unrelated_unavailable_source_key_cannot_mint_coverage(admitted_sources):
    native, _ = admitted_sources
    with native.registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        initial = writer.view()
        writer._save(replace(initial, source_key_id=None))
        try:
            with pytest.raises(
                LedgerError,
                match="Routing journal registry source key identity changed",
            ):
                journal.prepare(SOURCE, native.locator())
        finally:
            writer._save(initial)
        assert journal.coverage_changes(0) == ()
        assert store_version(journal) == 4


def test_lease_loss_is_not_reported_as_a_policy_refusal(admitted_sources, monkeypatch):
    native, claude = admitted_sources
    with native.registry.writer() as writer:
        state = ScopeState(writer)
        journal = RoutingJournal(writer, state)
        lease = writer.lease
        stable = writer._stable_live_exclusion

        def lose_lease(approved):
            result = stable(approved)
            writer._writer = None
            return result

        monkeypatch.setattr(writer, "_stable_live_exclusion", lose_lease)
        try:
            with pytest.raises(LedgerError, match="coordinator lease is required"):
                journal.prepare(claude.source_id, claude.locator())
        finally:
            writer._writer = lease

        assert journal.as_of().sequence == 0
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


def test_coverage_readback_rejects_deleted_commit_on_disk(admitted_sources):
    from test_monitor_journal_store import _sqlite

    from aitm_usage._monitor_journal_store import _DATABASE, _STORE

    native, claude = admitted_sources
    with native.registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        with pytest.raises(LedgerError, match="qualification"):
            journal.prepare(claude.source_id, claude.locator())
        (event,) = journal.coverage_changes(0)
        path = writer.root / _STORE / _DATABASE
        with _sqlite(path) as connection:
            connection.execute(
                "DELETE FROM commits WHERE sequence=?", (event.sequence,)
            )
        with pytest.raises(LedgerError, match="Invalid private journal coverage"):
            journal.coverage_changes(0)


def test_open_refuses_unknown_schema_version(admitted_sources):
    from test_monitor_journal_store import _sqlite

    from aitm_usage._monitor_journal_store import (
        _DATABASE,
        _DELIVERY_SCHEMA_VERSION,
        _STORE,
    )

    native, _ = admitted_sources
    with native.registry.writer() as writer:
        RoutingJournal(writer, ScopeState(writer))
        with _sqlite(writer.root / _STORE / _DATABASE) as conn:
            conn.execute(f"PRAGMA user_version = {_DELIVERY_SCHEMA_VERSION}")
        with pytest.raises(LedgerError, match="Invalid routing journal table schema"):
            RoutingJournal(writer, ScopeState(writer))
        with _sqlite(writer.root / _STORE / _DATABASE) as conn:
            conn.execute(f"PRAGMA user_version = {_DELIVERY_SCHEMA_VERSION + 1}")
        with pytest.raises(
            LedgerError, match="Unsupported routing journal schema version"
        ):
            RoutingJournal(writer, ScopeState(writer))


@pytest.mark.parametrize("consent", (False, True))
def test_grok_coverage_rechecks_exact_consent_before_payload(
    admitted_sources, monkeypatch, tmp_path, consent
):
    from datetime import UTC, datetime

    from test_grok import FIXTURES, GROK_BINARY, SESSION
    from test_monitor_scope import A

    from aitm_usage.monitor_registry import (
        CaptureChange,
    )
    from aitm_usage.sources.grok import GrokAdapter, GrokOrigin

    native, _ = admitted_sources
    root = tmp_path / "grok"
    session = root / SESSION
    session.mkdir(parents=True)
    for filename in ("updates.jsonl", "usage.json"):
        (session / filename).write_bytes((FIXTURES / filename).read_bytes())

    with native.registry.writer() as writer:
        source = UUID(int=99)
        req = SourceApprovalRequest(
            source,
            "grok",
            "grok-build-macos",
            "Darwin",
            "arm64",
            "1.0.77",
            1,
            str(root),
        )
        retained = ApprovedSource(req, _directory(str(root)))
        initial = writer.view()
        permissions = initial.permissions + (
            (CaptureChange(A, source, True),) if consent else ()
        )
        writer._save(
            replace(
                initial, sources=(*initial.sources, retained), permissions=permissions
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
        root_proof = SourceRoot(root, datetime(2026, 1, 1, tzinfo=UTC), (), evidence)
        (locator,) = reader.discover(root_proof)
        monkeypatch.setattr(
            GrokAdapter,
            "read_delta",
            lambda *a, **k: pytest.fail("unqualified payload"),
        )
        journal = RoutingJournal(writer, ScopeState(writer, grok_reader=reader))
        with pytest.raises(LedgerError, match="qualification"):
            journal.prepare(source, locator)
        assert len(journal.coverage_changes(0)) == int(consent)
        assert journal.as_of().claims == ()
        with journal._store.transaction() as connection:
            assert connection.execute("SELECT count(*) FROM progress").fetchone() == (
                0,
            )
        qualify(writer)
        with pytest.raises(LedgerError, match="no verified native session"):
            journal.prepare(source, locator)
        assert len(journal.coverage_changes(0)) == int(consent)


def test_coverage_readback_requires_the_original_live_writer(admitted_sources):
    native, claude = admitted_sources
    with native.registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        with pytest.raises(LedgerError, match="qualification"):
            journal.prepare(claude.source_id, claude.locator())
        (event,) = journal.coverage_changes(0)

    with pytest.raises(LedgerError, match="coordinator lease is required"):
        journal.coverage_changes(0)
    with native.registry.writer() as reopened:
        with pytest.raises(LedgerError, match="coordinator lease is required"):
            journal.coverage_changes(0)
        assert RoutingJournal(reopened, ScopeState(reopened)).coverage_changes(0) == (
            event,
        )


def test_unqualified_source_gap_publishes_without_project_write_or_ack(
    admitted_sources, monkeypatch
):
    from datetime import UTC, datetime

    from aitm_usage._monitor_journal_store import _DELIVERY_SCHEMA_VERSION, _open
    from aitm_usage.ledger import Ledger
    from aitm_usage.monitor_journal import (
        JournalChange,
        JournalCoverage,
        _coverage_key,
        _CoverageExtent,
        _CoverageReason,
    )
    from aitm_usage.types import _decode, _encode

    def project_access(*_, **__):
        pytest.fail("A journal-only candidate touched a destination")

    native, claude = admitted_sources
    source = claude.locator()
    with native.registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        qualify(writer)
        prepared = journal.prepare(SOURCE, native.locator())
        journal.reserve_batch(prepared)
        assert store_version(journal) == 4
        sequence = journal.as_of().sequence
        seed = writer.source_evidence().pseudonymize("partial-test", "coverage")
        forged = JournalCoverage(
            _CoverageReason.UNQUALIFIED_SOURCE,
            seed,
            seed,
            _CoverageExtent.UNKNOWN,
            datetime.now(UTC),
        )
        with pytest.raises(LedgerError):
            journal.publication_candidate(JournalChange(sequence, coverage=forged))
        with pytest.raises(LedgerError, match="qualification"):
            journal.prepare(claude.source_id, source)
        (change,) = journal.coverage_changes(0)
        before = journal.as_of()
        prior = journal.cursor_for(claude.source_id, source)

        with monkeypatch.context() as patch:
            patch.setattr(Ledger, "open", project_access)
            patch.setattr(Ledger, "writer", project_access)
            candidate = journal.publication_candidate(change)
            assert (
                candidate.basis == "coverage" and candidate.sequence == change.sequence
            )
            writer.source_evidence().validate_source_ref(candidate.identity)
            assert journal.publication_candidate(change) == candidate
            assert journal.as_of() == before
            assert journal.cursor_for(claude.source_id, source) is prior is None
            assert journal.coverage_changes(0) == (change,)
        with pytest.raises(LedgerError):
            journal.publication_candidate(replace(change, sequence=change.sequence + 1))
        with pytest.raises(LedgerError):
            journal.publication_candidate(JournalChange(change.sequence))
        with pytest.raises(LedgerError):
            journal.publication_candidate(
                replace(
                    change,
                    coverage=replace(change.coverage, reason="UNQUALIFIED_SOURCE"),
                )
            )
    with monkeypatch.context() as patch, native.registry.writer() as writer:
        patch.setattr(Ledger, "open", project_access)
        patch.setattr(Ledger, "writer", project_access)
        reopened = RoutingJournal(writer, ScopeState(writer))
        assert reopened.publication_candidate(change) == candidate
        assert reopened.as_of() == before
        (stored,) = reopened.coverage_changes(0)
        evidence = writer.source_evidence()
        alternate = replace(stored.coverage, installation=seed)
        replacement = _encode(
            alternate, JournalCoverage, validate_ref=evidence.validate_source_ref
        ).encode()
        assert _decode(replacement, JournalCoverage) == alternate
        alternate_key = _coverage_key(alternate, evidence).value
        with reopened._store.transaction(write=True) as connection:
            key, raw = connection.execute(
                "SELECT identity,payload FROM source_coverage"
            ).fetchone()
            # A complete, canonical substitute preserves the old seal.
            connection.execute(
                "UPDATE source_coverage SET identity=?,payload=?",
                (alternate_key, replacement),
            )
        with pytest.raises(LedgerError, match="Verified journal-only publication"):
            reopened.publication_candidate(stored)
        with pytest.raises(LedgerError, match="Invalid private journal coverage"):
            reopened.coverage_changes(0)
        with reopened._store.transaction(write=True) as connection:
            connection.execute(
                "UPDATE source_coverage SET identity=?,payload=?", (key, raw)
            )
        assert reopened.publication_candidate(stored) == candidate
        reopened.enable_delivery(reopened.as_of().sequence)
        assert reopened.coverage_changes(0) == (stored,)
        assert reopened.publication_candidate(stored) == candidate
        database = writer.root / "routing-journal-v1" / "journal.sqlite3"
        with _open(database, write=True) as connection:
            connection.execute(f"PRAGMA user_version = {_DELIVERY_SCHEMA_VERSION + 1}")
        with pytest.raises(LedgerError, match="Unsupported routing journal schema"):
            reopened.publication_candidate(stored)
        with _open(database, write=False) as connection:
            assert connection.execute("PRAGMA user_version").fetchone() == (
                _DELIVERY_SCHEMA_VERSION + 1,
            )
