from dataclasses import replace
from pathlib import Path
from shutil import copytree

import pytest
from test_monitor_qualification import qualify
from test_monitor_scope import SOURCE, ClaudeScopeFixture, NativeScopeFixture

from aitm_usage.ledger import LedgerError
from aitm_usage.monitor_journal import RoutingJournal
from aitm_usage.monitor_registry import Registry, _directory
from aitm_usage.monitor_scope import ScopeState


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


@pytest.mark.parametrize(
    "case",
    (
        "omitted",
        "duplicates",
        "missing-verifier",
        "rejected-verifier",
        "verifier-error",
        "foreign-root",
        "foreign-generation",
        "foreign-lease",
    ),
)
def test_only_stable_profile_denials_become_coverage(admitted_sources, tmp_path, case):
    native, _ = admitted_sources

    def unavailable(_):
        raise OSError("verifier unavailable")

    other = Registry(tmp_path / "other-monitor")
    with native.registry.writer() as writer, other.writer() as foreign:
        qualify(writer)
        profile = writer._live_profile
        approved = next(s for s in writer.view().sources if s.source_id == SOURCE)
        item = next(
            i for i in profile.installations if i.directory == approved.directory
        )
        fields = {
            "omitted": {"installations": ()},
            "duplicates": {"installations": (item, item)},
            "missing-verifier": {"current": None},
            "rejected-verifier": {"current": lambda _: False},
            "verifier-error": {"current": unavailable},
            "foreign-root": {"root": _directory(str(foreign.root), private=True)},
            "foreign-generation": {
                "generation": foreign.source_evidence().pseudonymize(
                    "generation", "other"
                ),
            },
            "foreign-lease": {"lease": foreign.lease},
        }[case]
        writer._live_profile = replace(profile, **fields)
        locator = native.locator()
        journal = RoutingJournal(writer, ScopeState(writer))
        with pytest.raises(LedgerError, match="qualification"):
            journal.prepare(SOURCE, locator)
        changes = journal.coverage_changes(0)
        assert len(changes) == (1 if case == "omitted" else 0)
        assert store_version(journal) == (6 if changes else 4)
        assert journal.cursor_for(SOURCE, locator) is None


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
        {"extent": "known"},
        {"reason": "UNVERIFIED"},
        {"root": "broader-root"},
    ),
)
def test_coverage_rejects_reserved_variants_even_with_a_valid_row_seal(
    admitted_sources, override
):
    import json

    from aitm_usage.monitor_journal import _coverage_seal

    native, claude = admitted_sources
    with native.registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        with pytest.raises(LedgerError, match="qualification"):
            journal.prepare(claude.source_id, claude.locator())
        with journal._store.transaction(write=True) as connection:
            sequence, raw = connection.execute(
                "SELECT sequence,payload FROM source_coverage"
            ).fetchone()
            altered = json.dumps(
                json.loads(raw) | override, separators=(",", ":"), sort_keys=True
            ).encode()
            seal = _coverage_seal(sequence, altered, journal._store.evidence)
            connection.execute(
                "UPDATE source_coverage SET payload=?,seal=?", (altered, seal.value)
            )
        with pytest.raises(LedgerError, match="Invalid private journal coverage"):
            journal.coverage_changes(0)
        assert journal.as_of().sequence == sequence


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
def test_coverage_readback_rejects_corrupted_event_binding(admitted_sources, alter):
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
            if alter == "commit":
                connection.execute(
                    "DELETE FROM commits WHERE sequence=?", (event.sequence,)
                )
            else:
                column = {"identity": "identity", "seal": "seal"}[alter]
                connection.execute(
                    f"UPDATE source_coverage SET {column}=?", ("invalid",)
                )
        with pytest.raises(LedgerError, match="Invalid private journal coverage"):
            journal.coverage_changes(0)


def test_open_refuses_unknown_schema_version(admitted_sources):
    from test_monitor_journal_store import _sqlite

    from aitm_usage._monitor_journal_store import _DATABASE, _STORE

    native, _ = admitted_sources
    with native.registry.writer() as writer:
        RoutingJournal(writer, ScopeState(writer))
        with _sqlite(writer.root / _STORE / _DATABASE) as conn:
            conn.execute("PRAGMA user_version = 7")
        with pytest.raises(
            LedgerError, match="Unsupported routing journal schema version"
        ):
            RoutingJournal(writer, ScopeState(writer))


@pytest.mark.parametrize("consent", (False, True))
def test_grok_coverage_rechecks_exact_consent_before_payload(
    admitted_sources, monkeypatch, tmp_path, consent
):
    from datetime import UTC, datetime
    from uuid import UUID

    from test_grok import FIXTURES, GROK_BINARY, SESSION
    from test_monitor_scope import A

    from aitm_usage.monitor_registry import (
        ApprovedSource,
        CaptureChange,
        SourceApprovalRequest,
    )
    from aitm_usage.sources.adapter import SourceRoot
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
