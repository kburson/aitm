"""Exercise committed claims and the two private destination commits."""

import hashlib
import json
import sqlite3
from contextlib import closing, contextmanager, nullcontext
from dataclasses import replace
from pathlib import Path
from uuid import UUID

import pytest
from delivery_policy_cases import delivery_destination, delivery_journal_rows
from test_monitor_journal import (
    COPY,
    LIVE,
    A,
    B,
    NativeJournalFixture,
    _MemoryJournalTranscripts,
)
from test_monitor_journal import journal_claude as journal_claude
from test_monitor_journal import journal_claude_policy as journal_claude_policy
from test_monitor_journal import journal_transcript_policy as journal_transcript_policy

from aitm_usage.ledger import ConflictError, Ledger, LedgerError
from aitm_usage.monitor_journal import (
    _OWNERSHIP_DISPUTE_ROWS,
    PublicationCandidate,
    RoutingJournal,
    _CandidateBasis,
    _DeliveryRefused,
)
from aitm_usage.monitor_registry import _project
from aitm_usage.monitor_scope import ScopeState
from aitm_usage.monitor_writer import ProjectDelivery

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


def _read_single_dispute(monkeypatch, store):
    execute = store.execute
    ordered = " ORDER BY d.sequence,d.key,d.contender,d.digest,d.evidence"
    after = _OWNERSHIP_DISPUTE_ROWS + " WHERE d.sequence > ?" + ordered
    exact = _OWNERSHIP_DISPUTE_ROWS + " WHERE d.sequence=? AND d.key=?" + ordered

    def read(query, parameters=()):
        if query not in {after, exact}:
            return execute(query, parameters)
        (((key, contender, digest, evidence), sequence),) = store.disputes.items()
        assert (query, parameters) in {(after, (0,)), (exact, (sequence, key))}
        project, claim_digest, payload, _ = store.claims[key]
        return [
            (key, contender, project, digest, evidence, sequence, payload, claim_digest)
        ]

    monkeypatch.setattr(store, "execute", read)


def test_restart_at_reserve_commit_and_ack_yields_one_row(native):
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
            other_row = delivery._monitor_revision(ticket)
        (separate,) = _reserve(native, journal, COPY)
        assert separate.status == "pending"
        assert separate.project_id == B
        assert journal.cursor_for(COPY, native.locator(COPY)) is not None
        with Ledger.open(native.ledgers[A].root, A).writer() as writer:
            delivery = ProjectDelivery.attach(journal, writer)
            ticket = journal.reserve_delivery(original.key, 1)
            journal.ack(delivery, ticket, delivery.commit(ticket))
            original_row = delivery._monitor_revision(ticket)
            replay = _reserve(native, journal)[-2:]
            assert [o.status for o in replay] == ["pending", "replay"]
            assert journal.cursor_for(LIVE, native.locator(LIVE)) != prior
            next_ticket = journal.reserve_delivery(replay[0].key, 1)
            journal.ack(delivery, next_ticket, delivery.commit(next_ticket))
            settled_row = delivery._monitor_revision(next_ticket)
            assert set(writer.monitor_as_of(writer.as_of().sequence).revisions) == {
                original_row,
                settled_row,
            }
        with Ledger.open(native.ledgers[B].root, B).writer() as writer:
            delivery = ProjectDelivery.attach(journal, writer)
            ticket = journal.reserve_delivery(separate.key, 1)
            journal.ack(delivery, ticket, delivery.commit(ticket))
            assert set(writer.monitor_as_of(writer.as_of().sequence).revisions) == {
                other_row,
                delivery._monitor_revision(ticket),
            }
        assert {row.project_id for row in journal.as_of().claims} == {A, B}


@pytest.mark.parametrize("ack_before_dispute", [True, False])
def test_late_conflict_after_ack_produces_dispute_without_new_write(
    request, monkeypatch, ack_before_dispute
):
    store = None
    if ack_before_dispute:
        native = request.getfixturevalue("native")
    else:
        native = _MemoryJournalTranscripts(monkeypatch, competing=True)
        store = delivery_journal_rows(monkeypatch, native.registry)
        _read_single_dispute(monkeypatch, store)

    native.append(LIVE, native.turn(3))
    with native.registry.writer() as registry:
        journal = _journal(registry)
        _, original = _reserve(native, journal)
        project = _project(registry.view(), A)
        ledger = Ledger.open(Path(project.state.path), A)
        if store is None:
            _enable(native, journal)
            destination_writer = Ledger.open(ledger.root, A).writer()
        else:
            store.delivery_enabled = True
            writer, destination = delivery_destination(monkeypatch, journal, ledger)
            destination_writer = nullcontext(writer)

        with destination_writer as writer:
            delivery = ProjectDelivery.attach(journal, writer)
            ticket = journal.reserve_delivery(original.key, 1)
            receipt = delivery.commit(ticket)
            if ack_before_dispute:
                ack = journal.ack(delivery, ticket, receipt)
            native.append(COPY, native.turn(3, checkout=B))
            _, disputed = _reserve(native, journal, COPY)
            assert disputed.status == "disputed"
            if not ack_before_dispute:
                prior = journal.as_of().sequence
                ack = journal.ack(delivery, ticket, receipt)
                assert ack.sequence == prior + 1
            assert journal.ack(delivery, ticket, receipt) == ack
            with pytest.raises(_DeliveryRefused):
                journal.ack(delivery, ticket, replace(receipt, claim_digest="0" * 64))
            forged = writer.pseudonymize("test-destination", "not-a-service-claim")
            with pytest.raises(LedgerError):
                journal.reserve_delivery(forged, 1)
            if store is None:
                with writer._write_transaction() as conn:
                    conn.execute("UPDATE monitor_delivery_receipts SET seal='forged'")
            else:
                key = receipt.key.value, receipt.revision
                sequence, payload, _ = destination.receipts[key]
                destination.receipts[key] = sequence, payload, "forged"
            with pytest.raises(_DeliveryRefused):
                journal.ack(delivery, ticket, receipt)
            assert writer.as_of().sequence == receipt.sequence
            assert len(writer.monitor_as_of(receipt.sequence).revisions) == 1
            (change,) = journal.dispute_changes(0)
            assert change.sequence == disputed.sequence
            material = json.dumps(
                ["ownership", change.sequence, change.dispute.identity.value],
                separators=(",", ":"),
            )
            expected = registry.source_evidence().pseudonymize(
                "monitor-journal-publication-v1", material
            )
            assert journal.publication_candidate(change) == PublicationCandidate(
                disputed.sequence, _CandidateBasis.OWNERSHIP, expected
            )


def test_destination_transaction_rolls_back_when_receipt_insert_fails(
    native, monkeypatch
):
    with native.registry.writer() as registry:
        journal = _journal(registry)
        (reserved,) = _reserve(native, journal)
        _enable(native, journal)
        ticket = journal.reserve_delivery(reserved.key, 1)
        with Ledger.open(native.ledgers[A].root, A).writer() as writer:
            delivery = ProjectDelivery.attach(journal, writer)
            head = writer.as_of().sequence
            tables = []
            transaction = Ledger._write_transaction

            def deny_receipt(action, table, *_):
                if action == sqlite3.SQLITE_INSERT:
                    tables.append(table)
                    if table == "monitor_delivery_receipts":
                        return sqlite3.SQLITE_DENY
                return sqlite3.SQLITE_OK

            @contextmanager
            def interrupted(self):
                with transaction(self) as conn:
                    conn.set_authorizer(deny_receipt)
                    try:
                        yield conn
                    finally:
                        conn.set_authorizer(None)

            with monkeypatch.context() as fault:
                fault.setattr(Ledger, "_write_transaction", interrupted)
                with pytest.raises(sqlite3.DatabaseError, match="not authorized"):
                    delivery.commit(ticket)
            assert tables == [
                "commits",
                "monitor_revisions",
                "monitor_delivery_receipts",
            ]
            assert writer.as_of().sequence == head
            assert writer.monitor_as_of(head).revisions == ()
            row = delivery._monitor_revision(ticket)
            assert writer._monitor_delivery_receipt(row.key, row.revision) is None
            assert delivery.commit(ticket).sequence == head + 1


def test_foreign_writer_and_substituted_project_keys_cannot_deliver(native):
    with native.registry.writer() as registry:
        journal = _journal(registry)
        (reserved,) = _reserve(native, journal)
        _enable(native, journal)
        ticket = journal.reserve_delivery(reserved.key, 1)
        root = native.ledgers[A].root
        with Ledger.open(native.ledgers[B].root, B).writer() as writer:
            delivery = ProjectDelivery.attach(journal, writer)
            with pytest.raises(_DeliveryRefused, match="belongs to another project"):
                delivery.commit(ticket)
            assert writer.monitor_as_of(writer.as_of().sequence).revisions == ()
        with Ledger.open(root, A).writer() as writer:
            delivery = ProjectDelivery.attach(journal, writer)
            receipt = delivery.commit(ticket)
            original_key = writer.key_path.read_bytes()
            changed_key = original_key[:-1] + bytes([original_key[-1] ^ 1])
            writer.key_path.write_bytes(changed_key)
            try:
                with pytest.raises(LedgerError, match="identity changed"):
                    delivery.commit(ticket)
                with pytest.raises(LedgerError, match="identity changed"):
                    delivery._readback(ticket, receipt)
                with pytest.raises(_DeliveryRefused):
                    journal.ack(delivery, ticket, receipt)
            finally:
                writer.key_path.write_bytes(original_key)
            assert writer._monitor_delivery_receipt(receipt.key, 1) == receipt
            ack = journal.ack(delivery, ticket, receipt)
        writer.key_path.write_bytes(changed_key)
        key_id = "sha256:" + hashlib.sha256(changed_key[16:]).hexdigest()
        with closing(sqlite3.connect(writer.database_path)) as conn:
            with conn:
                conn.execute("UPDATE identity SET key_id=?", (key_id,))
            with Ledger.open(root, A).writer() as substitute:
                assert substitute.identity.key_id == key_id
                with pytest.raises(
                    _DeliveryRefused, match="Destination ledger key changed"
                ):
                    ProjectDelivery.attach(journal, substitute)
        assert (
            journal.delivery_tail(A, receipt.destination_key) == receipt.claim_sequence
        )
        assert journal.as_of().sequence == ack.sequence


def test_ack_refuses_changed_destination_row_payload(
    journal_transcript_policy, monkeypatch
):
    native = journal_transcript_policy
    store = delivery_journal_rows(monkeypatch, native.registry)
    with native.registry.writer() as registry:
        journal = _journal(registry)
        (reserved,) = _reserve(native, journal)
        store.delivery_enabled = True
        ticket = journal.reserve_delivery(reserved.key, 1)
        project = _project(registry.view(), A)
        ledger = Ledger.open(Path(project.state.path), A)
        writer, destination = delivery_destination(monkeypatch, journal, ledger)
        delivery = ProjectDelivery.attach(journal, writer)
        receipt = delivery.commit(ticket)
        assert (
            writer._monitor_delivery_receipt(receipt.key, receipt.revision) == receipt
        )
        key = receipt.key.value, receipt.revision
        sequence, original = destination.revisions[key]
        payload = json.loads(original)
        payload["observation"]["tokens"]["total_tokens"] += 1
        destination.revisions[key] = (
            sequence,
            json.dumps(payload, sort_keys=True, separators=(",", ":")),
        )
        with pytest.raises(
            LedgerError, match="Invalid committed project delivery receipt"
        ):
            writer._monitor_delivery_receipt(receipt.key, receipt.revision)
        tip = journal.as_of().sequence
        with pytest.raises(_DeliveryRefused):
            journal.ack(delivery, ticket, receipt)
        assert journal.as_of().sequence == tip
        assert not store.acks


def test_content_dispute_blocks_new_destination_ack(journal_claude):
    from test_claude import usage as claude_usage
    from test_monitor_journal import (
        _claude_archive,
        _claude_candidates,
        _common_claude_revision,
    )

    native = journal_claude
    with native.native.registry.writer() as registry:
        journal, ordinal, prefix = _common_claude_revision(native, registry)
        source = UUID(int=7)
        _, locate = _claude_archive(
            native,
            registry,
            [*prefix, native.request(3, counts=claude_usage(output=8))],
            source,
        )
        native.append(native.request(3, counts=claude_usage(output=7)))
        live = journal.prepare(native.source_id, native.locator())
        *_, accepted = _claude_candidates(live, ordinal)
        result = journal.reserve(accepted, live.progress)
        assert result.status == "pending"
        _enable(native.native, journal)
        ticket = journal.reserve_delivery(result.key, accepted.observation.revision)
        with Ledger.open(native.native.ledgers[A].root, A).writer() as writer:
            delivery = ProjectDelivery.attach(journal, writer)
            receipt = delivery.commit(ticket)
            rival = journal.prepare(source, locate())
            *_, contender = _claude_candidates(rival, ordinal)
            dispute = journal.reserve(contender, rival.progress)
            assert dispute.status == "disputed"
            assert journal.as_of().content_disputes[0].key == result.key
            with pytest.raises(_DeliveryRefused):
                journal.reserve_delivery(result.key, ticket.claim.revision)
            with pytest.raises(_DeliveryRefused):
                delivery.commit(ticket)
            with pytest.raises(_DeliveryRefused):
                journal.ack(delivery, ticket, receipt)
            assert (
                writer._monitor_delivery_receipt(receipt.key, receipt.revision)
                == receipt
            )
            assert journal.as_of().sequence == dispute.sequence


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
    request, monkeypatch, written_before_supersession
):
    from test_claude import usage as claude_usage
    from test_monitor_journal import _claude_candidates

    store = None
    if written_before_supersession:
        native = request.getfixturevalue("journal_claude")
    else:
        native = request.getfixturevalue("journal_claude_policy")
        store = delivery_journal_rows(monkeypatch, native.native.registry)
    with native.native.registry.writer() as registry:
        native.approve(registry)
        ordinal = native.append(native.request(3, stop=None))
        journal = _journal(registry)
        prepared = journal.prepare(native.source_id, native.locator())
        (original,) = _claude_candidates(prepared, ordinal)
        accepted = journal.reserve(original, prepared.progress)
        assert accepted.status == "pending"
        ledger = Ledger.open(native.native.ledgers[A].root, A)
        if store is None:
            _enable(native.native, journal)
            destination_writer = Ledger.open(ledger.root, A).writer()
        else:
            store.delivery_enabled = True
            writer, destination = delivery_destination(monkeypatch, journal, ledger)
            destination_writer = nullcontext(writer)
        old = journal.reserve_delivery(accepted.key, 1)

        with destination_writer as writer:
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
            ack = journal.ack(delivery, latest, receipt)
            committed = writer.monitor_as_of(receipt.sequence)
            expected = (1, 2) if written_before_supersession else (2,)
            assert tuple(row.revision for row in committed.revisions) == expected
            if store is not None:
                assert writer._monitor_delivery_receipt(receipt.key, 2) == receipt
                assert journal.ack(delivery, latest, receipt) == ack
