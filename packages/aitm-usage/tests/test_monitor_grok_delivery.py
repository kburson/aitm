"""Exact guarded delivery for a currently verified Grok capture interval."""

import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from uuid import UUID

import pytest
from test_monitor_grok_capture import isolated_grok_capture as isolated_grok_capture

from aitm_usage import backup, install, service
from aitm_usage._monitor_journal_store import _DATABASE, _STORE
from aitm_usage.ledger import Ledger, LedgerError, _connection
from aitm_usage.monitor_control import ControlInbox
from aitm_usage.monitor_journal import (
    ClaimEvidence,
    ClaimStatus,
    PendingClaim,
    RoutingJournal,
    _ClaimPayload,
    _DeliveryRefused,
    _GrokProgress,
    _RevisionPayload,
    _source_checkpoint,
    _UsageMaterial,
)
from aitm_usage.monitor_registry import (
    CaptureChange,
    ControlCommand,
    ControlStatus,
    ProjectRegistrationRequest,
    Registry,
    _project,
)
from aitm_usage.monitor_scope import HandoffStatus, Mark, Scope, ScopeState
from aitm_usage.monitor_types import (
    GrokCheckpoint,
    GrokObservation,
    NativeSurface,
    ObservationTimeBasis,
)
from aitm_usage.monitor_writer import ProjectDelivery
from aitm_usage.sources.adapter import StreamCursor
from aitm_usage.sources.grok import GrokAdapter
from aitm_usage.sources.scan import checkout_anchor_reference
from aitm_usage.types import (
    Availability,
    BoundaryKind,
    ClientVersion,
    ItemKey,
    ItemKind,
    Provider,
    SourceBoundary,
    SourceRef,
    TokenCounts,
    UsageObservation,
    WorkPhase,
    _decode,
    _encode,
)


def _load_turns(fixture, *, mark=True, second=True):
    f = fixture
    f.submit(201, True)
    assert f.evaluate()
    selected = [*f.rows[:6], *f.rows[7:]] if second else f.rows[:5]
    f.write(selected, 2 if second else 1)
    if mark:
        command = Mark(
            UUID(int=202),
            Scope(f.project, ItemKey(ItemKind.ISSUE, 117), WorkPhase.PLANNING),
            f.receipt,
        )
        owner = f.state.operator(f.project)
        f.state.authorize(command, owner)
        batch = f.state.read_source(f.source_id, f.locator())
        (boundary,) = batch.boundaries
        verified = f.state.verify_boundary(command, owner, batch, boundary)
        assert f.state.apply_mark(command, verified).status is HandoffStatus.APPLIED
        return command.scope
    return None


def _ledger(f):
    registered = _project(f.writer.view(), f.project)
    return Ledger.open(Path(registered.state.path), f.project)


def _enable_delivery(f, journal):
    with journal._store.transaction(write=True) as conn:
        journal._store._enable_coverage(conn)
    journal.enable_delivery(journal.as_of().sequence)
    ledger = _ledger(f)
    ledger.upgrade_monitor_schema(ledger.as_of().sequence)
    ledger = _ledger(f)
    ledger.upgrade_delivery_schema(ledger.as_of().sequence)


def _stored_progress(journal, prepared):
    with journal._store.transaction() as conn:
        return journal._cursor(conn, prepared._read.stream)


def test_legacy_claim_and_revision_bytes_match_protected_trunk():
    def ref(n):
        return SourceRef(f"hmac-sha256:{'a' * 64}:{str(n) * 64}")

    usage = UsageObservation(
        SourceBoundary(
            Provider.CODEX,
            ref(1),
            ref(2),
            12,
            BoundaryKind.TURN,
            ref(3),
            receipt_ref=ref(4),
        ),
        datetime(2026, 11, 15, tzinfo=UTC),
        ClientVersion.UNKNOWN,
        1,
        TokenCounts(input_tokens=44, output_tokens=9),
        Availability.COMPLETE,
    )
    material = _UsageMaterial(
        usage, Scope(UUID(int=1)), ObservationTimeBasis.NATIVE_USAGE_EVENT
    )
    payload = _ClaimPayload(
        material,
        ClaimEvidence(
            UUID(int=2),
            NativeSurface.CODEX_DESKTOP_MACOS,
            ref(2),
            ref(1),
            12,
            13,
            1,
            ref(5),
        ),
    )
    revision = _RevisionPayload(usage, 2, ref(6), ref(7), ref(8))
    for value, golden in (
        (material, "d74678ebcb32b3fe621828ce4a41afc87614b10aeaa26636d835b354c02b623a"),
        (payload, "bd2c49dc8f2f3dcaa41c39dcc522a5dbb5f6829c2cc180e5edc6b2e8db84a2f6"),
        (revision, "2ae5685d86b1ffd362d3e13a918741f7b25621f08747d9f6db8d19cbb2dab9b9"),
    ):
        wire = _encode(value, type(value))
        assert sha256(wire.encode()).hexdigest() == golden
        assert _decode(wire, type(value)) == value


def test_verified_grok_marked_and_hookless_rows_write_once_through_real_ack(
    isolated_grok_capture,
):
    f = isolated_grok_capture
    marked_scope = _load_turns(f)
    journal = RoutingJournal(f.writer, f.state)
    current = journal.prepare(f.source_id, f.locator())
    assert type(current.progress.checkpoint) is GrokCheckpoint
    assert current._read.batch._grok_strict
    assert [candidate.route.scope for candidate in current.candidates] == [
        marked_scope,
        None,
    ]
    assert all(
        candidate.route.project_id == f.project for candidate in current.candidates
    )
    outcomes = journal.reserve_batch(current)
    assert [row.status for row in outcomes] == [
        ClaimStatus.PENDING,
        ClaimStatus.PENDING,
    ]
    assert _stored_progress(journal, current) == current.progress
    assert (
        _decode(_encode(current.progress, StreamCursor), StreamCursor)
        == current.progress
    )
    with pytest.raises(LedgerError, match="no verified native session"):
        journal.cursor_for(f.source_id, f.locator())

    _enable_delivery(f, journal)
    tickets = [journal.reserve_delivery(row.key, 1) for row in outcomes]
    assert [ticket.claim.scope for ticket in tickets] == [marked_scope, None]
    with _ledger(f).writer() as writer:
        deliver = ProjectDelivery.attach(journal, writer)
        receipts = [deliver.commit(ticket) for ticket in tickets]
        rows = writer.monitor_as_of(receipts[-1].sequence).revisions
        assert all(type(row.observation) is GrokObservation for row in rows)
        assert {row.observation for row in rows} == {
            ticket.claim.usage for ticket in tickets
        }
    # Reopen guarded destination after a lost ACK, without reopening live authority.
    reloaded = RoutingJournal(
        f.writer,
        ScopeState(f.writer, grok_reader=GrokAdapter(f.find_origin, f.verifier)),
    )
    for ticket, receipt in zip(tickets, receipts, strict=True):
        assert (
            reloaded.reserve_delivery(ticket.claim.key, ticket.claim.revision) == ticket
        )
        with _ledger(f).writer() as writer:
            deliver = ProjectDelivery.attach(reloaded, writer)
            assert deliver.commit(ticket) == receipt
            ack = reloaded.ack(deliver, ticket, receipt)
            assert reloaded.ack(deliver, ticket, receipt) == ack
    resumed = reloaded.prepare(f.source_id, f.locator())
    assert resumed._read.prior == current.progress
    assert resumed.candidates == ()
    assert reloaded.reserve_batch(resumed) == ()
    assert len(reloaded.as_of().claims) == 2


def test_grok_unsettled_mark_cannot_claim_or_advance(isolated_grok_capture):
    f = isolated_grok_capture
    _load_turns(f, mark=False, second=False)
    journal = RoutingJournal(f.writer, f.state)
    before = journal.as_of()
    prepared = journal.prepare(f.source_id, f.locator())
    assert prepared.candidates == ()
    assert journal.reserve_batch(prepared) == ()
    assert _stored_progress(journal, prepared) is None
    assert journal.as_of() == before


def test_grok_revocation_between_prepare_and_reserve_cannot_claim(
    isolated_grok_capture,
):
    from aitm_usage._monitor_qualification import _LiveSourceUnavailable

    f = isolated_grok_capture
    _load_turns(f)
    journal = RoutingJournal(f.writer, f.state)
    prepared = journal.prepare(f.source_id, f.locator())
    before = journal.as_of()
    f.revise("revoke", 2)
    with pytest.raises(_LiveSourceUnavailable):
        journal.reserve_batch(prepared)
    assert _stored_progress(journal, prepared) is None
    assert journal.as_of() == before


def test_grok_append_reuses_sealed_earlier_cursor_and_holds_on_prefix_change(
    isolated_grok_capture,
    monkeypatch,
):
    f = isolated_grok_capture
    _load_turns(f, second=False)
    journal = RoutingJournal(f.writer, f.state)
    first = journal.prepare(f.source_id, f.locator())
    (reserved,) = journal.reserve_batch(first)
    assert reserved.status is ClaimStatus.PENDING
    resume = RoutingJournal(
        f.writer,
        ScopeState(f.writer, grok_reader=GrokAdapter(f.find_origin, f.verifier)),
    )
    seen = []
    original = GrokAdapter.read_delta

    def record(adapter, locator, cursor, **kwargs):
        seen.append(cursor)
        return original(adapter, locator, cursor, **kwargs)

    monkeypatch.setattr(GrokAdapter, "read_delta", record)
    turns = [*f.rows[:6], *f.rows[7:]]
    f.write(turns, 2)
    later = resume.prepare(f.source_id, f.locator())
    assert first._read.stream == later._read.stream
    assert seen == [first.progress]
    assert later.progress.checkpoint.offset > first.progress.checkpoint.offset
    (new,) = resume.reserve_batch(later)
    assert new.status is ClaimStatus.PENDING and new.key != reserved.key
    before = resume.as_of()
    turns[0] = b" " + turns[0]
    f.write(turns, 2)
    with pytest.raises(LedgerError):
        resume.prepare(f.source_id, f.locator())
    assert _stored_progress(resume, later) == later.progress
    assert resume.as_of() == before


def test_grok_progress_seal_binds_the_current_locator(isolated_grok_capture):
    f = isolated_grok_capture
    _load_turns(f)
    journal = RoutingJournal(f.writer, f.state)
    prepared = journal.prepare(f.source_id, f.locator())
    journal.reserve_batch(prepared)
    stream = prepared._read.stream
    evidence = f.writer.source_evidence()
    with journal._store.transaction(write=True) as conn:
        (wire,) = conn.execute("SELECT cursor FROM progress").fetchone()
        saved = _decode(wire, _GrokProgress)
        other = evidence.pseudonymize("fixture-alternate-locator", "different")
        changed = _encode(replace(saved, locator=other), _GrokProgress).encode()
        conn.execute("UPDATE progress SET cursor = ?", (changed,))
    assert stream[3] == saved.locator.value
    with pytest.raises(LedgerError, match="progress seal changed"):
        journal.prepare(f.source_id, f.locator())


def test_unverified_grok_mark_does_not_advance_another_streams_cursor(
    isolated_grok_capture,
):
    f = isolated_grok_capture
    other, write_other = f.add_stream()
    f.submit(203, True)
    assert f.evaluate()
    f.refs.clear()
    f.write(f.rows[:5], 1)
    write_other(f.rows[1:5], 1)
    journal = RoutingJournal(f.writer, f.state)
    held = journal.prepare(f.source_id, f.locator())
    assert journal.reserve_batch(held) == ()
    assert _stored_progress(journal, held) is None
    independent = journal.prepare(f.source_id, other())
    (reserved,) = journal.reserve_batch(independent)
    assert reserved.status is ClaimStatus.PENDING
    assert _stored_progress(journal, independent) == independent.progress
    assert _stored_progress(journal, held) is None


def test_grok_original_claim_remains_after_revoke_and_refuses_other_destination(
    isolated_grok_capture,
    tmp_path,
):
    f = isolated_grok_capture
    scope = _load_turns(f, second=False)
    journal = RoutingJournal(f.writer, f.state)
    prepared = journal.prepare(f.source_id, f.locator())
    (reserved,) = journal.reserve_batch(prepared)
    assert reserved.status is ClaimStatus.PENDING
    _enable_delivery(f, journal)
    ticket = journal.reserve_delivery(reserved.key, 1)
    rival = UUID(int=19)
    root = tmp_path / "rival"
    Ledger.initialize(root, rival)
    f.writer.register_project(ProjectRegistrationRequest(rival, str(root), "Rival"))
    for upgrade in (Ledger.upgrade_monitor_schema, Ledger.upgrade_delivery_schema):
        ledger = Ledger.open(root, rival)
        upgrade(ledger, ledger.as_of().sequence)
    with Ledger.open(root, rival).writer() as writer:
        delivery = ProjectDelivery.attach(journal, writer)
        with pytest.raises(LedgerError):
            delivery.commit(ticket)
        assert writer.as_of().sequence == 0
    f.revise("revoke", 2)
    reopened = RoutingJournal(
        f.writer,
        ScopeState(f.writer, grok_reader=GrokAdapter(f.find_origin, f.verifier)),
    )
    assert reopened.reserve_delivery(reserved.key, 1) == ticket
    with pytest.raises(LedgerError):
        reopened.prepare(f.source_id, f.locator())
    (claim,) = reopened.as_of().claims
    assert claim.project_id == f.project and claim.scope == scope
    assert claim.usage == ticket.claim.usage


def test_pinned_grok_destination_restore_preserves_row_and_lost_ack(
    isolated_grok_capture,
    tmp_path,
    monkeypatch,
):
    class StoppedLaunchControl:
        def __init__(self, _ledger):
            pass

        plist_directory = tmp_path / "LaunchAgents"

        def job(self, label):
            return None

    monkeypatch.setattr(install, "ServiceSupervisor", StoppedLaunchControl)
    f = isolated_grok_capture
    config = tmp_path / "registration-input.json"
    config.write_text(
        json.dumps(
            {
                "project_id": str(f.project),
                "source_roots": [str(f.root.path)],
                "checkout_anchors": [str(tmp_path / "checkout")],
                "cutoff": "2026-01-01T00:00:00Z",
            }
        )
    )
    service.register_project(_ledger(f).root, config)
    _load_turns(f)
    journal = RoutingJournal(f.writer, f.state)
    first, later = journal.reserve_batch(journal.prepare(f.source_id, f.locator()))
    _enable_delivery(f, journal)
    first_ticket = journal.reserve_delivery(first.key, 1)
    later_ticket = journal.reserve_delivery(later.key, 1)
    ledger = _ledger(f)
    with ledger.writer() as writer:
        receipt = ProjectDelivery.attach(journal, writer).commit(first_ticket)
    saved = tmp_path / "saved"
    bundle = backup.backup(ledger, saved)
    with ledger.writer() as writer:
        ProjectDelivery.attach(journal, writer).commit(later_ticket)
    restored = backup.restore(saved, ledger.root, ledger.identity)
    assert restored.sequence == bundle.sequence == receipt.sequence
    with _ledger(f).writer() as writer:
        delivery = ProjectDelivery.attach(journal, writer)
        (row,) = writer.monitor_as_of(receipt.sequence).revisions
        assert row.observation == first_ticket.claim.usage
        assert delivery.commit(first_ticket) == receipt
        journal.ack(delivery, first_ticket, receipt)


@dataclass(frozen=True, slots=True)
class _LegacyUsageMaterial:
    usage: UsageObservation
    scope: Scope | None
    time_basis: ObservationTimeBasis


@dataclass(frozen=True, slots=True)
class _LegacyClaim:
    material: _LegacyUsageMaterial
    evidence: ClaimEvidence


@dataclass(frozen=True, slots=True)
class _LegacyPendingClaim:
    key: SourceRef
    project_id: UUID
    usage: UsageObservation
    scope: Scope | None
    time_basis: ObservationTimeBasis
    evidence: ClaimEvidence
    sequence: int
    revision: int = 1


def _save_test_journal_snapshot(journal, target):
    with journal._store.transaction() as live, closing(sqlite3.connect(target)) as copy:
        live.backup(copy)


def _restore_test_journal_snapshot(registry, source):
    database = registry.root / _STORE / _DATABASE
    with (
        closing(sqlite3.connect(source)) as source_copy,
        _connection(database, write=True) as live,
    ):
        source_copy.backup(live)


@pytest.mark.usefixtures("legacy_monitor_qualification")
def test_retained_legacy_journal_snapshot_restores_for_both_readers(
    tmp_path,
    monkeypatch,
):
    from test_monitor_journal import LIVE, NativeJournalFixture

    native = NativeJournalFixture(tmp_path, monkeypatch)
    native.append(LIVE, native.turn(3))
    backup_path = tmp_path / "prior-journal.sqlite3"
    with native.registry.writer() as registry:
        journal = RoutingJournal(registry, ScopeState(registry))
        locator = native.locator(LIVE)
        journal.reserve_batch(journal.prepare(LIVE, locator))
        earlier = journal.as_of()
        prior = journal.cursor_for(LIVE, locator)
        assert earlier.claims and prior is not None
        _save_test_journal_snapshot(journal, backup_path)
        assert (
            _decode(_encode(earlier.claims[0], PendingClaim), _LegacyPendingClaim).usage
            == earlier.claims[0].usage
        )

        with closing(sqlite3.connect(backup_path)) as snapshot:
            stored = {
                key: _decode(payload, _LegacyClaim).material.usage
                for key, payload in snapshot.execute("SELECT key,payload FROM claims")
            }
            (progress,) = snapshot.execute(
                "SELECT cursor FROM progress ORDER BY sequence DESC LIMIT 1"
            ).fetchone()
            assert stored == {claim.key.value: claim.usage for claim in earlier.claims}
            assert _decode(progress, StreamCursor) == prior

        native.append(LIVE, native.turn(4))
        journal.reserve_batch(journal.prepare(LIVE, native.locator(LIVE)))
        assert journal.as_of().sequence > earlier.sequence
        _restore_test_journal_snapshot(registry, backup_path)
        reopened = RoutingJournal(registry, ScopeState(registry))
        assert reopened.as_of() == earlier
        assert reopened.cursor_for(LIVE, native.locator(LIVE)) == prior


def test_grok_journal_snapshot_restores_private_rows_and_new_writer_holds(
    tmp_path,
    monkeypatch,
):
    # Exhausting the fixture releases the original physical coordinator lease.
    retained = isolated_grok_capture.__wrapped__(tmp_path, monkeypatch, request=None)
    f = next(retained)
    prompt_text = "synthetic private prompt"
    user = json.loads(f.rows[1])
    user["params"]["update"]["content"] = {"type": "text", "text": prompt_text}
    f.rows[1] = json.dumps(user).encode() + b"\n"
    _load_turns(f)
    assert prompt_text.encode() in f.locator()._source.path.read_bytes()
    journal = RoutingJournal(f.writer, f.state)
    prepared = journal.prepare(f.source_id, f.locator())
    outcomes = journal.reserve_batch(prepared)
    _enable_delivery(f, journal)
    ticket = journal.reserve_delivery(outcomes[0].key, 1)
    with _ledger(f).writer() as writer:
        delivery = ProjectDelivery.attach(journal, writer)
        receipt = delivery.commit(ticket)
        journal.ack(delivery, ticket, receipt)
    before = journal.as_of()
    snapshot = tmp_path / "grok-journal.sqlite3"
    _save_test_journal_snapshot(journal, snapshot)

    with closing(sqlite3.connect(snapshot)) as copy:
        rows = copy.execute("SELECT payload FROM claims").fetchall()
        (checkpoint,) = copy.execute("SELECT cursor FROM progress").fetchone()
        (ack,) = copy.execute("SELECT payload FROM delivery_acks").fetchone()
        for (claim,) in rows:
            with pytest.raises(ValueError):
                _decode(claim, _LegacyClaim)
        with pytest.raises(ValueError):
            _decode(_encode(before.claims[0], PendingClaim), _LegacyPendingClaim)
        with pytest.raises(ValueError):
            _decode(checkpoint, StreamCursor)
        persisted = b"".join(claim for (claim,) in rows) + checkpoint + ack.encode()
        native = f.locator()._source
        for sensitive in (
            str(native.path),
            native.origin.session_id,
            "synthetic-event-1",
        ):
            assert sensitive.encode() not in persisted
        assert prompt_text.encode() not in persisted

    # The staged copy predates a second durable ACK.
    second = journal.reserve_delivery(outcomes[1].key, 1)
    with _ledger(f).writer() as writer:
        delivery = ProjectDelivery.attach(journal, writer)
        journal.ack(delivery, second, delivery.commit(second))
    assert journal.as_of().sequence > before.sequence
    _restore_test_journal_snapshot(f.writer, snapshot)
    with pytest.raises(StopIteration):
        next(retained)

    with Registry(f.writer.root).writer() as writer:
        state = ScopeState(writer, grok_reader=GrokAdapter(f.find_origin, f.verifier))
        reopened = RoutingJournal(writer, state)
        with pytest.raises(LedgerError, match="authority"):
            reopened.prepare(f.source_id, f.locator())
        assert reopened.as_of() == before
        assert _stored_progress(reopened, prepared) == prepared.progress
        with _ledger(f).writer() as destination:
            delivery = ProjectDelivery.attach(reopened, destination)
            assert reopened.ack(delivery, ticket, receipt).sequence == before.sequence


def test_grok_existing_owner_survives_an_independently_eligible_rival_claim(
    isolated_grok_capture,
    tmp_path,
    monkeypatch,
):
    f = isolated_grok_capture
    f.submit(204, True)
    assert f.evaluate()[0].status is ControlStatus.APPLIED
    first_turn = f.rows[1:5]
    f.write(first_turn, 1)
    journal = RoutingJournal(f.writer, f.state)
    (original,) = journal.reserve_batch(journal.prepare(f.source_id, f.locator()))
    assert original.status is ClaimStatus.PENDING
    f.submit(205, False)
    assert f.evaluate()[0].status is ControlStatus.APPLIED
    _enable_delivery(f, journal)
    ticket = journal.reserve_delivery(original.key, 1)
    with _ledger(f).writer() as writer:
        delivered = ProjectDelivery.attach(journal, writer)
        journal.ack(delivered, ticket, delivered.commit(ticket))

    rival = UUID(int=39)
    root, checkout = (
        tmp_path / name for name in ("competing-project", "competing-checkout")
    )
    checkout.mkdir(mode=0o700)
    Ledger.initialize(root, rival)
    f.writer.register_project(
        ProjectRegistrationRequest(rival, str(root), "Rival", anchors=(str(checkout),))
    )
    evidence = f.writer.source_evidence()
    original_origin = f.find_origin(f.locator()._source.path)
    rival_origin = replace(
        original_origin,
        checkout=checkout_anchor_reference(evidence, checkout),
        incarnation=evidence.pseudonymize("grok-incarnation", "same-lineage-rival"),
    )
    monkeypatch.setattr(
        f.reader,
        "verify_origin",
        lambda path: rival_origin if f.find_origin(path) else None,
    )
    f.write([], 0)
    enabled = ControlCommand(UUID(int=206), CaptureChange(rival, f.source_id, True))
    ControlInbox(f.writer.root).enqueue(enabled)
    (applied,) = f.evaluate()
    assert (
        applied.command_id == enabled.command_id
        and applied.status is ControlStatus.APPLIED
    )
    f.write(first_turn, 1)
    candidate = journal.prepare(f.source_id, f.locator())
    (contender,) = candidate.candidates
    assert contender.route.project_id == rival
    assert contender.observation.key == original.key
    (disputed,) = journal.reserve_batch(candidate)
    assert disputed.status is ClaimStatus.DISPUTED and disputed.project_id == f.project
    assert _stored_progress(journal, candidate) is None
    view = journal.as_of()
    assert [(claim.key, claim.project_id) for claim in view.claims] == [
        (original.key, f.project)
    ]
    assert [row.contender for row in view.disputes] == [rival]
    assert Ledger.open(root, rival).as_of().sequence == 0


def test_preenrollment_and_stable_policy_exclusion_do_not_open_payload(
    tmp_path,
    monkeypatch,
):
    from aitm_usage._monitor_qualification import _LiveSourceUnavailable

    retained = isolated_grok_capture.__wrapped__(tmp_path, monkeypatch, request=None)
    f = next(retained)
    journal = RoutingJournal(f.writer, f.state)
    monkeypatch.setattr(
        GrokAdapter,
        "read_delta",
        lambda *a, **kw: pytest.fail("unauthenticated Grok read"),
    )
    with pytest.raises(LedgerError, match="no verified native session"):
        journal.prepare(f.source_id, f.locator())
    assert journal.coverage_changes(0) == ()
    # An old consent bit can persist without native enrollment and cannot
    # substitute for an admitted source or turn.
    view = f.writer.view()
    f.writer._save(
        replace(view, permissions=(CaptureChange(f.project, f.source_id, True),))
    )
    with pytest.raises(StopIteration):
        next(retained)
    with Registry(f.writer.root).writer() as writer:
        scopes = ScopeState(writer, grok_reader=GrokAdapter(f.find_origin, f.verifier))
        journal = RoutingJournal(writer, scopes)
        with pytest.raises(_LiveSourceUnavailable):
            journal.prepare(f.source_id, f.locator())
        (exclusion,) = journal.coverage_changes(0)
        assert exclusion.coverage.reason == "UNQUALIFIED_SOURCE"
        assert exclusion.coverage.extent == "unknown"
        assert journal.as_of().claims == ()
        with journal._store.transaction() as conn:
            assert conn.execute("SELECT count(*) FROM progress").fetchone() == (0,)


def test_observational_cursor_and_mismatched_guarded_grok_claim_fail_closed(
    isolated_grok_capture,
):
    f = isolated_grok_capture
    _load_turns(f, second=False)
    journal = RoutingJournal(f.writer, f.state)
    verified = journal.prepare(f.source_id, f.locator())
    observational = f.reader.read_delta(f.locator(), None).cursor
    assert type(observational.checkpoint) is GrokCheckpoint
    assert observational != verified.progress
    with pytest.raises(LedgerError, match="not issued together"):
        journal.reserve(verified.candidates[0], observational)
    with pytest.raises(LedgerError, match="requires a verified native cursor"):
        _source_checkpoint(verified.progress)
    assert _stored_progress(journal, verified) is None
    (reserved,) = journal.reserve_batch(verified)
    _enable_delivery(f, journal)
    ticket = journal.reserve_delivery(reserved.key, 1)
    mismatched = replace(ticket, claim=replace(ticket.claim, revision=2))
    with _ledger(f).writer() as writer:
        delivery = ProjectDelivery.attach(journal, writer)
        with pytest.raises(_DeliveryRefused, match="Grok usage proof changed"):
            delivery._monitor_revision(mismatched)
        with pytest.raises(_DeliveryRefused):
            delivery.commit(mismatched)
        assert writer.as_of().sequence == 0
