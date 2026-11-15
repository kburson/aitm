"""Exercise committed claims and the two private destination commits."""

from dataclasses import replace

import pytest
from test_monitor_journal import COPY, LIVE, A, B, NativeJournalFixture
from test_monitor_journal import journal_claude as journal_claude

from aitm_usage.ledger import ConflictError, Ledger, LedgerError
from aitm_usage.monitor_journal import RoutingJournal
from aitm_usage.monitor_scope import ScopeState

pytestmark = pytest.mark.usefixtures("legacy_monitor_qualification")


@pytest.fixture
def native(tmp_path, monkeypatch):
    return NativeJournalFixture(tmp_path, monkeypatch)


@pytest.fixture
def independent(tmp_path, monkeypatch):
    return NativeJournalFixture(tmp_path, monkeypatch, independent_copy=True)


def _enable(native, journal):
    with journal._store.transaction(write=True) as conn:
        journal._store._enable_coverage(conn)
    journal.enable_delivery(journal.as_of().sequence)
    for project in (A, B):
        ledger = Ledger.open(native.ledgers[project].root, project)
        ledger.upgrade_monitor_schema(ledger.as_of().sequence)
        ledger = Ledger.open(ledger.root, project)
        ledger.upgrade_delivery_schema(ledger.as_of().sequence)


def _journal(registry, *, cap=64):
    # Reopen the same physical coordinator after each interruption.
    return RoutingJournal(registry, ScopeState(registry), pending_per_project=cap)


def _reserve(native, journal, source=LIVE):
    return journal.reserve_batch(journal.prepare(source, native.locator(source)))


def test_restart_at_reserve_commit_and_ack_yields_one_row(native):
    from aitm_usage.monitor_writer import ProjectDelivery

    root = native.ledgers[A].root
    with native.registry.writer() as registry:
        journal = _journal(registry)
        (reserved,) = _reserve(native, journal)
        _enable(native, journal)
        tip = journal.as_of().sequence
        ticket = journal.reserve_delivery(reserved.key, 1)
        assert journal.as_of().sequence == tip

    with native.registry.writer() as registry:
        journal = _journal(registry)
        assert journal.reserve_delivery(reserved.key, 1) == ticket
        with Ledger.open(root, A).writer() as writer:
            delivery = ProjectDelivery.attach(journal, writer)
            result = delivery.commit(ticket)
            assert delivery.commit(ticket) == result
            assert len(writer.monitor_as_of(result.sequence).revisions) == 1
            assert writer.as_of().sequence == result.sequence
        assert journal.as_of().sequence == tip

    with native.registry.writer() as registry:
        journal = _journal(registry)
        with Ledger.open(root, A).writer() as writer:
            delivery = ProjectDelivery.attach(journal, writer)
            assert delivery.commit(ticket) == result
            ack = journal.ack(delivery, ticket, result)
            assert journal.as_of().sequence == tip + 1

    with native.registry.writer() as registry:
        journal = _journal(registry)
        with Ledger.open(root, A).writer() as writer:
            delivery = ProjectDelivery.attach(journal, writer)
            assert journal.ack(delivery, ticket, result) == ack
            assert journal.as_of().sequence == tip + 1
            assert writer.as_of().sequence == result.sequence


def test_stale_ack_never_rewinds_publication(native):
    from aitm_usage.monitor_writer import ProjectDelivery

    with native.registry.writer() as registry:
        journal = _journal(registry)
        (early,) = _reserve(native, journal)
        native.append(LIVE, native.turn(3))
        late = _reserve(native, journal)[-1]
        _enable(native, journal)
        with Ledger.open(native.ledgers[A].root, A).writer() as writer:
            delivery = ProjectDelivery.attach(journal, writer)
            first, second = (journal.reserve_delivery(d.key, 1) for d in (early, late))
            journal.ack(delivery, second, delivery.commit(second))
            assert journal.delivery_tail(A, writer.identity.key_id) == late.sequence
            journal.ack(delivery, first, delivery.commit(first))
            assert journal.delivery_tail(A, writer.identity.key_id) == late.sequence


def test_full_destination_queue_preserves_independent_progress(independent):
    from aitm_usage.monitor_writer import ProjectDelivery

    native = independent
    assert native.locator(LIVE).stream_ref != native.locator(COPY).stream_ref
    with native.registry.writer() as registry:
        journal = _journal(registry, cap=1)
        (original,) = _reserve(native, journal)
        _enable(native, journal)
        prior = journal.cursor_for(LIVE, native.locator(LIVE))
        native.append(LIVE, native.turn(3))
        native.append(LIVE, native.turn(4, checkout=B))
        full, other = _reserve(native, journal)[-2:]
        assert (full.status, other.status) == ("held", "pending")
        assert journal.cursor_for(LIVE, native.locator(LIVE)) == prior
        with Ledger.open(native.ledgers[B].root, B).writer() as writer:
            delivery = ProjectDelivery.attach(journal, writer)
            ticket = journal.reserve_delivery(other.key, 1)
            journal.ack(delivery, ticket, delivery.commit(ticket))
        (separate,) = _reserve(native, journal, COPY)
        assert separate.status == "pending"
        assert separate.project_id == B
        assert journal.cursor_for(COPY, native.locator(COPY)) is not None
        with Ledger.open(native.ledgers[A].root, A).writer() as writer:
            delivery = ProjectDelivery.attach(journal, writer)
            ticket = journal.reserve_delivery(original.key, 1)
            journal.ack(delivery, ticket, delivery.commit(ticket))
            replay = _reserve(native, journal)[-2:]
            assert [o.status for o in replay] == ["pending", "replay"]
            assert journal.cursor_for(LIVE, native.locator(LIVE)) != prior
            next_ticket = journal.reserve_delivery(replay[0].key, 1)
            journal.ack(delivery, next_ticket, delivery.commit(next_ticket))
            assert len(writer.monitor_as_of(writer.as_of().sequence).revisions) == 2
        assert {row.project_id for row in journal.as_of().claims} == {A, B}


def test_late_conflict_after_ack_produces_dispute_without_new_write(native):
    from aitm_usage.monitor_journal import _DeliveryRefused
    from aitm_usage.monitor_writer import ProjectDelivery

    native.append(LIVE, native.turn(3))
    with native.registry.writer() as registry:
        journal = _journal(registry)
        _, original = _reserve(native, journal)
        _enable(native, journal)
        with Ledger.open(native.ledgers[A].root, A).writer() as writer:
            delivery = ProjectDelivery.attach(journal, writer)
            ticket = journal.reserve_delivery(original.key, 1)
            receipt = delivery.commit(ticket)
            ack = journal.ack(delivery, ticket, receipt)
            native.append(COPY, native.turn(3, checkout=B))
            _, disputed = _reserve(native, journal, COPY)
            assert disputed.status == "disputed"
            assert journal.ack(delivery, ticket, receipt) == ack
            with pytest.raises(_DeliveryRefused):
                journal.ack(delivery, ticket, replace(receipt, claim_digest="0" * 64))
            forged = writer.pseudonymize("test-destination", "not-a-service-claim")
            with pytest.raises(LedgerError):
                journal.reserve_delivery(forged, 1)
            with writer._write_transaction() as conn:
                conn.execute("UPDATE monitor_delivery_receipts SET seal='forged'")
            with pytest.raises(_DeliveryRefused):
                journal.ack(delivery, ticket, receipt)
            assert writer.as_of().sequence == receipt.sequence
            assert len(writer.monitor_as_of(receipt.sequence).revisions) == 1
            (change,) = journal.dispute_changes(0)
            assert journal.publication_candidate(change).basis == "ownership"


def test_delivery_upgrades_are_explicit_and_keep_existing_histories(native):
    from aitm_usage._monitor_journal_store import _DELIVERY_SCHEMA_VERSION
    from aitm_usage.ledger import DELIVERY_SCHEMA_VERSION
    from aitm_usage.monitor_registry import ProjectRegistrationRequest

    root = native.ledgers[A].root
    project = Ledger.open(root, A)
    previous = project.as_of()
    with native.registry.writer() as registry:
        journal = _journal(registry)
        (existing,) = _reserve(native, journal)
        old = journal.as_of()
        with pytest.raises(LedgerError, match="coverage schema"):
            journal.enable_delivery(old.sequence)
        with pytest.raises(LedgerError, match="monitor ledger schema"):
            project.upgrade_delivery_schema(previous.sequence)
        _enable(native, journal)
        assert journal.as_of() == old
        assert journal.reserve_delivery(existing.key, 1).claim == old.claims[0]
        assert project.identity.schema_version == 1

        project = Ledger.open(root, A)
        assert project.identity.schema_version == DELIVERY_SCHEMA_VERSION
        assert project.as_of() == previous
        assert project.monitor_as_of(previous.sequence).legacy == previous
        assert project.upgrade_monitor_schema(previous.sequence) == project.identity
        assert (
            registry.register_project(
                ProjectRegistrationRequest(
                    A, str(root), "Project 1", anchors=(str(native.anchors[A]),)
                )
            ).project_id
            == A
        )
        with pytest.raises(ConflictError):
            journal.enable_delivery(old.sequence + 1)
        with pytest.raises(ConflictError):
            project.upgrade_delivery_schema(previous.sequence + 1)
        with journal._store.transaction(write=True) as conn:
            journal._store._enable_coverage(conn)
            assert journal._store._current_version(conn) == _DELIVERY_SCHEMA_VERSION


@pytest.mark.parametrize("written_before_supersession", [False, True])
def test_superseded_revision_cannot_create_an_ack(
    journal_claude, written_before_supersession
):
    from test_claude import usage as claude_usage
    from test_monitor_journal import _claude_candidates

    from aitm_usage.monitor_journal import _DeliveryRefused
    from aitm_usage.monitor_writer import ProjectDelivery

    native = journal_claude
    with native.native.registry.writer() as registry:
        native.approve(registry)
        ordinal = native.append(native.request(3, stop=None))
        journal = _journal(registry)
        prepared = journal.prepare(native.source_id, native.locator())
        (original,) = _claude_candidates(prepared, ordinal)
        accepted = journal.reserve(original, prepared.progress)
        assert accepted.status == "pending"
        _enable(native.native, journal)
        old = journal.reserve_delivery(accepted.key, 1)

        with Ledger.open(native.native.ledgers[A].root, A).writer() as writer:
            delivery = ProjectDelivery.attach(journal, writer)
            early = delivery.commit(old) if written_before_supersession else None
            native.append(native.request(3, counts=claude_usage(output=6)))
            rewritten = journal.prepare(native.source_id, native.locator())
            _, successor = _claude_candidates(rewritten, ordinal)
            assert journal.reserve(successor, rewritten.progress).status == "pending"
            tip = journal.as_of().sequence
            with pytest.raises(_DeliveryRefused):
                delivery.commit(old)
            if early is not None:
                with pytest.raises(_DeliveryRefused):
                    journal.ack(delivery, old, early)
            assert journal.as_of().sequence == tip
            latest = journal.reserve_delivery(accepted.key, 2)
            receipt = delivery.commit(latest)
            assert receipt.revision == 2
            journal.ack(delivery, latest, receipt)
            committed = writer.monitor_as_of(receipt.sequence)
            expected = (1, 2) if written_before_supersession else (2,)
            assert tuple(row.revision for row in committed.revisions) == expected
