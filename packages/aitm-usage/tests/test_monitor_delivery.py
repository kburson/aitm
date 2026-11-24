"""Exercise committed claims and the two private destination commits."""

import json
import sqlite3
from contextlib import contextmanager, nullcontext
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID

import pytest
from delivery_policy_cases import (
    delivery_destination,
    delivery_destinations,
    delivery_journal_rows,
)
from test_ledger import _memory_ledger
from test_monitor_journal import (
    COPY,
    LIVE,
    A,
    B,
    NativeJournalFixture,
    _MemoryJournalTranscripts,
)
from test_monitor_journal import journal_claude_policy as journal_claude_policy
from test_monitor_journal import journal_transcript_policy as journal_transcript_policy

from aitm_usage import _monitor_journal_store as storage
from aitm_usage import ledger as ledger_module
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
        prior_journal = journal.as_of()
        original = Ledger.open(root, A)
        prior_project = original.as_of()
        _enable(native, journal)
        assert journal.as_of() == prior_journal
        assert original.identity.schema_version == 1
        upgraded = Ledger.open(root, A)
        assert upgraded.identity.schema_version == ledger_module.DELIVERY_SCHEMA_VERSION
        assert upgraded.as_of() == prior_project
        assert upgraded.monitor_as_of(prior_project.sequence).legacy == prior_project
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
            original_key = writer.key_path.read_bytes()
            changed_key = original_key[:-1] + bytes([original_key[-1] ^ 1])
            writer.key_path.write_bytes(changed_key)
            try:
                with pytest.raises(LedgerError, match="identity changed"):
                    delivery.commit(ticket)
                with pytest.raises(LedgerError, match="identity changed"):
                    delivery._readback(ticket, result)
                with pytest.raises(_DeliveryRefused):
                    journal.ack(delivery, ticket, result)
            finally:
                writer.key_path.write_bytes(original_key)
            ack = journal.ack(delivery, ticket, result)
            assert journal.as_of().sequence == tip + 1

    with native.registry.writer() as registry:
        journal = _journal(registry)
        with Ledger.open(root, A).writer() as writer:
            delivery = ProjectDelivery.attach(journal, writer)
            assert journal.ack(delivery, ticket, result) == ack
            assert journal.as_of().sequence == tip + 1
            assert writer.as_of().sequence == result.sequence


def test_stale_ack_never_rewinds_publication(journal_transcript_policy, monkeypatch):
    native = journal_transcript_policy
    store = delivery_journal_rows(monkeypatch, native.registry)
    with native.registry.writer() as registry:
        journal = _journal(registry)
        (early,) = _reserve(native, journal)
        native.append(LIVE, native.turn(3))
        late = _reserve(native, journal)[-1]
        store.delivery_enabled = True
        project = _project(registry.view(), A)
        ledger = Ledger.open(Path(project.state.path), A)
        writer, _ = delivery_destination(monkeypatch, journal, ledger)
        delivery = ProjectDelivery.attach(journal, writer)
        first, second = (journal.reserve_delivery(d.key, 1) for d in (early, late))
        journal.ack(delivery, second, delivery.commit(second))
        assert journal.delivery_tail(A, writer.identity.key_id) == late.sequence
        journal.ack(delivery, first, delivery.commit(first))
        assert journal.delivery_tail(A, writer.identity.key_id) == late.sequence


def test_full_destination_queue_preserves_independent_progress(monkeypatch):
    native = _MemoryJournalTranscripts(
        monkeypatch, competing=True, independent_copy=True
    )
    store = delivery_journal_rows(monkeypatch, native.registry)
    assert native.locator(LIVE).stream_ref != native.locator(COPY).stream_ref
    with native.registry.writer() as registry:
        journal = _journal(registry, cap=1)
        destination = delivery_destinations(monkeypatch, journal, A, B)

        (original,) = _reserve(native, journal)
        store.delivery_enabled = True
        prior = journal.cursor_for(LIVE, native.locator(LIVE))
        native.append(LIVE, native.turn(3))
        native.append(LIVE, native.turn(4, checkout=B))
        full, other = _reserve(native, journal)[-2:]
        assert (full.status, other.status) == ("held", "pending")
        assert journal.cursor_for(LIVE, native.locator(LIVE)) == prior
        with destination(B) as writer:
            delivery = ProjectDelivery.attach(journal, writer)
            ticket = journal.reserve_delivery(other.key, 1)
            journal.ack(delivery, ticket, delivery.commit(ticket))
            other_row = delivery._monitor_revision(ticket)
        (separate,) = _reserve(native, journal, COPY)
        assert separate.status == "pending"
        assert separate.project_id == B
        assert journal.cursor_for(COPY, native.locator(COPY)) is not None
        with destination(A) as writer:
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
        with destination(B) as writer:
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
    monkeypatch, ack_before_dispute
):
    native = _MemoryJournalTranscripts(monkeypatch, competing=True)
    store = delivery_journal_rows(monkeypatch, native.registry)
    _read_single_dispute(monkeypatch, store)

    native.append(LIVE, native.turn(3))
    with native.registry.writer() as registry:
        journal = _journal(registry)
        _, original = _reserve(native, journal)
        project = _project(registry.view(), A)
        ledger = Ledger.open(Path(project.state.path), A)
        store.delivery_enabled = True
        writer, destination = delivery_destination(monkeypatch, journal, ledger)

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


def test_foreign_writer_and_substituted_project_keys_cannot_deliver(monkeypatch):
    native = _MemoryJournalTranscripts(monkeypatch, competing=True)
    store = delivery_journal_rows(monkeypatch, native.registry)
    with native.registry.writer() as registry:
        journal = _journal(registry)
        (reserved,) = _reserve(native, journal)
        store.delivery_enabled = True
        ticket = journal.reserve_delivery(reserved.key, 1)
        open_destination = delivery_destinations(monkeypatch, journal, A, B)
        with open_destination(B) as writer:
            delivery = ProjectDelivery.attach(journal, writer)
            with pytest.raises(_DeliveryRefused, match="belongs to another project"):
                delivery.commit(ticket)
            assert writer.monitor_as_of(writer.as_of().sequence).revisions == ()
        with open_destination(A) as writer:
            delivery = ProjectDelivery.attach(journal, writer)
            receipt = delivery.commit(ticket)
            before = journal.as_of().sequence
            with monkeypatch.context() as fault:
                observed = Mock(return_value=b"replaced writer key")
                fault.setattr(ledger_module, "_read_key", observed)
                with pytest.raises(LedgerError, match="identity changed"):
                    delivery.commit(ticket)
                with pytest.raises(LedgerError, match="identity changed"):
                    delivery._readback(ticket, receipt)
                with pytest.raises(_DeliveryRefused):
                    journal.ack(delivery, ticket, receipt)
                assert observed.call_count == 3
                assert journal.as_of().sequence == before
            assert writer._monitor_delivery_receipt(receipt.key, 1) == receipt
            ack = journal.ack(delivery, ticket, receipt)
        substitute = replace(
            _memory_ledger(ledger_module, A, b"substitute project signing key"),
            root=writer.root,
        )
        with monkeypatch.context() as changed:
            writer, _ = delivery_destination(changed, journal, substitute)
            assert writer.identity.key_id != receipt.destination_key
            with pytest.raises(
                _DeliveryRefused, match="Destination ledger key changed"
            ):
                ProjectDelivery.attach(journal, writer)
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


def test_content_dispute_blocks_new_destination_ack(journal_claude_policy, monkeypatch):
    from test_claude import usage as claude_usage
    from test_monitor_journal import (
        _claude_archive,
        _claude_candidates,
        _common_claude_revision,
        _expose_claude_archive_directory,
    )

    native = journal_claude_policy
    store = delivery_journal_rows(monkeypatch, native.native.registry)
    with native.native.registry.writer() as registry:
        journal, ordinal, prefix = _common_claude_revision(native, registry)
        source = UUID(int=7)
        _expose_claude_archive_directory(native, source, monkeypatch)
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
        store.delivery_enabled = True
        ticket = journal.reserve_delivery(result.key, accepted.observation.revision)
        ledger = Ledger.open(native.native.ledgers[A].root, A)
        writer, _ = delivery_destination(monkeypatch, journal, ledger)
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
            writer._monitor_delivery_receipt(receipt.key, receipt.revision) == receipt
        )
        assert journal.as_of().sequence == dispute.sequence


def test_delivery_upgrades_are_explicit_and_keep_existing_histories(
    journal_transcript_policy, monkeypatch
):
    native = journal_transcript_policy
    store = delivery_journal_rows(monkeypatch, native.registry)
    with native.registry.writer() as registry:
        journal = _journal(registry)
        (existing,) = _reserve(native, journal)
        old = journal.as_of()
        native_version = storage._SCHEMA_VERSION
        observed_ddl = []
        rows = store.execute

        def statements(sql, params=()):
            nonlocal native_version
            if sql == "PRAGMA foreign_key_check":
                return SimpleNamespace(fetchone=lambda: None)
            if sql in storage._DELIVERY_SCHEMA:
                observed_ddl.append(sql)
                return None
            if sql == f"PRAGMA user_version = {storage._DELIVERY_SCHEMA_VERSION}":
                native_version = storage._DELIVERY_SCHEMA_VERSION
                return None
            return rows(sql, params)

        def journal_identity(connection, key, *, version):
            assert connection is store and key == store.evidence.key_id
            assert version == native_version

        monkeypatch.setattr(store, "execute", statements)
        monkeypatch.setattr(store, "_writer", registry, raising=False)
        monkeypatch.setattr(store, "_key_id", store.evidence.key_id, raising=False)
        monkeypatch.setattr(store, "in_transaction", True, raising=False)
        monkeypatch.setattr(store, "_current_version", lambda _: native_version)
        monkeypatch.setattr(
            store,
            "_enable_delivery",
            storage.JournalStore._enable_delivery.__get__(store),
            raising=False,
        )
        monkeypatch.setattr(storage, "_validate_identity", journal_identity)
        with pytest.raises(LedgerError, match="coverage schema"):
            journal.enable_delivery(old.sequence)
        assert observed_ddl == []

        project = replace(
            _memory_ledger(ledger_module, A, b"project delivery migration"),
            _writer=object(),
            _write_paths=SimpleNamespace(check=Mock()),
        )
        project_version = ledger_module.SCHEMA_VERSION
        project_ddl = []

        def destination_sql(sql):
            nonlocal project_version
            if sql == "SELECT COALESCE(MAX(sequence), 0) FROM commits":
                return SimpleNamespace(fetchone=lambda: (3,))
            if sql == "PRAGMA foreign_key_check":
                return SimpleNamespace(fetchone=lambda: None)
            prefix = "PRAGMA user_version = "
            if sql.startswith(prefix):
                project_version = int(sql.removeprefix(prefix))
            else:
                project_ddl.append(sql)

        connection = SimpleNamespace(execute=destination_sql)
        monkeypatch.setattr(
            Ledger, "_write_transaction", lambda _: nullcontext(connection)
        )

        def project_identity(actual, identity):
            assert actual is connection and identity.schema_version == project_version

        monkeypatch.setattr(ledger_module, "_validate_identity", project_identity)
        with pytest.raises(LedgerError, match="monitor ledger schema"):
            project.upgrade_delivery_schema(3)
        assert project_ddl == []

        native_version = storage._COVERAGE_SCHEMA_VERSION
        journal.enable_delivery(old.sequence)
        assert observed_ddl == list(storage._DELIVERY_SCHEMA)
        assert journal.as_of() == old
        assert journal.reserve_delivery(existing.key, 1).claim == old.claims[0]
        assert project.identity.schema_version == 1
        project = replace(project, identity=project.upgrade_monitor_schema(3))
        project = replace(project, identity=project.upgrade_delivery_schema(3))
        assert project.identity.schema_version == ledger_module.DELIVERY_SCHEMA_VERSION
        assert project.upgrade_monitor_schema(3) == project.identity
        assert project_ddl == [
            *ledger_module._MONITOR_SCHEMA,
            ledger_module._DELIVERY_SCHEMA,
        ]
        with pytest.raises(ConflictError, match="Journal changed"):
            journal.enable_delivery(old.sequence + 1)
        with pytest.raises(ConflictError, match="Ledger changed"):
            project.upgrade_delivery_schema(4)
        storage.JournalStore._enable_coverage(store, store)
        assert native_version == storage._DELIVERY_SCHEMA_VERSION
        assert observed_ddl == list(storage._DELIVERY_SCHEMA)


@pytest.mark.parametrize("written_before_supersession", [False, True])
def test_superseded_revision_cannot_create_an_ack(
    journal_claude_policy, monkeypatch, written_before_supersession
):
    from test_claude import usage as claude_usage
    from test_monitor_journal import _claude_candidates

    native = journal_claude_policy
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
        store.delivery_enabled = True
        writer, _ = delivery_destination(monkeypatch, journal, ledger)
        old = journal.reserve_delivery(accepted.key, 1)

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
        assert writer._monitor_delivery_receipt(receipt.key, 2) == receipt
        assert journal.ack(delivery, latest, receipt) == ack
        if early is not None:
            assert writer._monitor_delivery_receipt(early.key, 1) == early
