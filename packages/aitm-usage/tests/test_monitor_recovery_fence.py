"""Exercise the private witness before any report or receiver effect."""

import hmac
import json
import os
from dataclasses import replace
from shutil import copytree

import pytest
from test_monitor_coverage import admitted_sources as admitted_sources
from test_monitor_journal import COPY, LIVE, B, NativeJournalFixture
from test_monitor_qualification import qualify
from test_monitor_scope import SOURCE

from aitm_usage.ledger import Ledger, LedgerError
from aitm_usage.monitor_journal import RoutingJournal
from aitm_usage.monitor_recovery import (
    ReceiverDelivery,
    ReceiverDisposition,
    RecoveryFence,
    VerifiedReceiverEvidence,
)
from aitm_usage.monitor_registry import _SOURCE_KEY_FILE, _STATE_FILE
from aitm_usage.monitor_scope import ScopeState


@pytest.fixture
def coverage_candidate(admitted_sources, tmp_path):
    # Use the same policy-backed Claude exclusion as the delivered M09a
    # test_unqualified_source_gap_publishes_without_project_write_or_ack.
    native, claude = admitted_sources
    root = tmp_path / "witness"
    root.mkdir(mode=0o700)
    with native.registry.writer() as writer:
        qualify(writer)
        journal = RoutingJournal(writer, ScopeState(writer))
        journal.reserve_batch(journal.prepare(SOURCE, native.locator()))
        with pytest.raises(LedgerError, match="qualification"):
            journal.prepare(claude.source_id, claude.locator())
        (change,) = journal.coverage_changes(0)
        yield journal, root, journal.publication_candidate(change)


@pytest.fixture
def dispute_candidates(tmp_path, monkeypatch, legacy_monitor_qualification, request):
    monkeypatch.setattr("aitm_usage.ledger._control_root", lambda: tmp_path / "control")
    native = NativeJournalFixture(tmp_path, monkeypatch)
    root = tmp_path / "witness"
    root.mkdir(mode=0o700)
    grouped = getattr(request, "param", True)
    for number in (3, 4):
        native.append(LIVE, native.turn(number))
    with native.registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        journal.reserve_batch(journal.prepare(LIVE, native.locator()))
        for number in (3, 4):
            native.append(COPY, native.turn(number, checkout=B))
            if grouped and number == 3:
                continue
            journal.reserve_batch(journal.prepare(COPY, native.locator(COPY)))
        first, second = journal.dispute_changes(0)
        assert (first.sequence == second.sequence) == grouped
        yield (
            journal,
            root,
            journal.publication_candidate(first),
            journal.publication_candidate(second),
        )


@pytest.mark.parametrize("after_link", [False, True], ids=["before-link", "after-link"])
def test_view_cannot_escape_before_recovery_fsync(
    coverage_candidate, monkeypatch, after_link
):
    from aitm_usage import monitor_recovery

    journal, root, candidate = coverage_candidate
    fence = RecoveryFence(journal, root)
    publish = monitor_recovery._publish

    def interrupted(*args, **kwargs):
        if after_link:
            publish(*args, **kwargs)
        raise OSError("interrupted witness publication")

    with monkeypatch.context() as failure:
        failure.setattr(monitor_recovery, "_publish", interrupted)
        with pytest.raises(LedgerError):
            fence.protect(candidate)
    assert len(list(root.iterdir())) == int(after_link)
    os_fsync = os.fsync
    directory_synced = []

    def observe_sync(fd):
        if os.fstat(fd).st_ino == root.stat().st_ino:
            directory_synced.append(root)
        return os_fsync(fd)

    monkeypatch.setattr(os, "fsync", observe_sync)
    recovered = fence.protect(candidate)
    assert directory_synced
    assert recovered.candidate == candidate
    assert recovered.anchor.ordinal == 1
    assert fence.protect(candidate) == recovered
    assert len(list(root.iterdir())) == 1


def test_restore_with_only_old_witness_holds_replay(dispute_candidates, tmp_path):
    journal, root, first, second = dispute_candidates
    fence = RecoveryFence(journal, root)
    one = fence.protect(first)
    older = tmp_path / "old-witness"
    copytree(root, older)
    two = fence.protect(second)
    assert one.candidate.sequence == two.candidate.sequence
    assert one.anchor != two.anchor
    current = fence.recover(two.anchor)
    assert current.common == two.anchor
    assert not current.held
    rolled_back = RecoveryFence(journal, older)
    result = rolled_back.recover(two.anchor)
    assert result.held
    assert result.common == one.anchor
    with pytest.raises(LedgerError):
        rolled_back.protect(second)
    assert len(list(older.iterdir())) == 1


@pytest.mark.parametrize("missing", [True, False], ids=["missing", "modified"])
def test_recovery_holds_at_the_authenticated_prefix(dispute_candidates, missing):
    journal, root, first, second = dispute_candidates
    fence = RecoveryFence(journal, root)
    one = fence.protect(first)
    two = fence.protect(second)
    tail = sorted(root.iterdir())[-1]
    if missing:
        tail.unlink()
    else:
        tail.write_bytes(tail.read_bytes().replace(b"monitor-recovery/v1", b"invalid"))
    assert fence.recover(two.anchor).common == one.anchor
    with pytest.raises(LedgerError):
        fence.protect(second)


def test_claude_coverage_gap_cannot_escape_before_recovery_fsync(
    coverage_candidate, monkeypatch
):
    journal, root, candidate = coverage_candidate
    assert candidate.basis.value == "coverage"
    before = journal.as_of()

    def destination_access(*_args, **_kwargs):
        pytest.fail("Coverage-only publication accessed a destination")

    monkeypatch.setattr(Ledger, "open", destination_access)
    monkeypatch.setattr(Ledger, "writer", destination_access)
    monkeypatch.setattr(journal, "ack", destination_access)
    os_fsync = os.fsync

    def fail_first_witness_directory_sync(fd):
        if os.fstat(fd).st_ino == root.stat().st_ino:
            raise OSError("witness parent not synchronized")
        return os_fsync(fd)

    fence = RecoveryFence(journal, root)
    with monkeypatch.context() as fault:
        fault.setattr(os, "fsync", fail_first_witness_directory_sync)
        with pytest.raises(LedgerError):
            fence.protect(candidate)
    assert journal.as_of() == before
    ready = fence.protect(candidate)
    assert ready.candidate == candidate
    assert ready.anchor.ordinal == 1
    assert journal.as_of() == before


def test_same_sequence_set_refuses_a_divergent_readback(
    dispute_candidates, monkeypatch
):
    journal, root, first, second = dispute_candidates
    fence = RecoveryFence(journal, root)
    one = fence.protect(first)
    two = fence.protect(second)
    assert one.anchor.ordinal == 1 and two.anchor.ordinal == 2
    changes = journal.dispute_changes(first.sequence - 1)
    assert len(changes) == 2
    # A restored listing can omit a member even when the other candidate
    # still reconstructs through the real journal.
    monkeypatch.setattr(journal, "dispute_changes", lambda _: changes[:1])
    assert journal.publication_candidate(changes[0]) == first
    with pytest.raises(LedgerError):
        fence.protect(first)
    assert len(list(root.iterdir())) == 2


@pytest.mark.parametrize("dispute_candidates", [False], indirect=True)
def test_fence_refuses_an_unwitnessed_older_candidate(dispute_candidates):
    journal, root, first, second = dispute_candidates
    assert first.sequence < second.sequence
    fence = RecoveryFence(journal, root)
    newest = fence.protect(second)
    with pytest.raises(LedgerError):
        fence.protect(first)
    assert fence.protect(second) == newest
    assert len(list(root.iterdir())) == 1


def test_forged_candidate_against_keyless_registry_creates_no_key(
    coverage_candidate,
):
    journal, root, candidate = coverage_candidate
    writer = journal._writer
    key_file = writer.root / _SOURCE_KEY_FILE
    key_file.unlink()
    (writer.root / _STATE_FILE).unlink()
    with pytest.raises(LedgerError):
        RecoveryFence(journal, root).protect(
            replace(candidate, sequence=candidate.sequence + 1)
        )
    assert not key_file.exists()
    assert not list(root.iterdir())


def test_fence_rejects_forged_types_and_a_root_inside_journal(coverage_candidate):
    journal, root, candidate = coverage_candidate
    fence = RecoveryFence(journal, root)
    for forged in (
        replace(candidate, sequence=True),
        replace(candidate, basis=candidate.basis.value),
        replace(candidate, sequence=candidate.sequence + 1),
        replace(
            candidate,
            identity=journal._store.evidence.pseudonymize("fixture", "unrelated"),
        ),
    ):
        with pytest.raises(LedgerError):
            fence.protect(forged)
    assert not list(root.iterdir())
    nested = journal._writer.root / "would-be-witness"
    nested.mkdir(mode=0o700)
    with pytest.raises(LedgerError):
        RecoveryFence(journal, nested).protect(candidate)
    assert not list(nested.iterdir())
    with pytest.raises(LedgerError):
        RecoveryFence(journal, root, project_stores=(root,)).protect(candidate)
    assert not list(root.iterdir())


def test_fence_refuses_lost_coordinator_custody(coverage_candidate, monkeypatch):
    journal, root, candidate = coverage_candidate
    fence = RecoveryFence(journal, root)
    ready = fence.protect(candidate)
    with monkeypatch.context() as fault:
        fault.setattr(journal._writer, "_writer", None)
        with pytest.raises(LedgerError):
            fence.protect(candidate)
        lost = fence.recover(ready.anchor)
        assert lost.held and lost.common is None
    assert len(list(root.iterdir())) == 1


_RECEIVER_KEY = b"fixture receiver has an independent signing key"


def _receiver_signature(evidence):
    material = json.dumps(
        [
            evidence.receiver.value,
            evidence.key.value,
            evidence.payload_digest,
            evidence.attempt,
            evidence.disposition.value,
        ],
        separators=(",", ":"),
    ).encode()
    return hmac.digest(_RECEIVER_KEY, material, "sha256")


def _verify_receiver(evidence):
    return hmac.compare_digest(_receiver_signature(evidence), evidence.proof)


def _receipt(intent, disposition):
    delivery = intent.delivery
    statement = VerifiedReceiverEvidence(
        delivery.receiver,
        delivery.key,
        delivery.payload_digest,
        intent.attempt,
        disposition,
        b"",
    )
    return replace(statement, proof=_receiver_signature(statement))


def _receiver_delivery(journal, publication):
    authority = journal._store.evidence
    return ReceiverDelivery(
        publication,
        authority.pseudonymize("fixture-receiver", "receiver-one"),
        authority.pseudonymize("fixture-operation", "operation-one"),
        "a" * 64,
    )


def test_interrupted_export_requires_receiver_reconciliation(coverage_candidate):
    journal, root, candidate = coverage_candidate
    fence = RecoveryFence(journal, root, verify_receiver=_verify_receiver)
    delivery = _receiver_delivery(journal, fence.protect(candidate))
    first = fence.record_export_intent(delivery)
    assert first.can_send and first.attempt == 1

    restarted = RecoveryFence(journal, root, verify_receiver=_verify_receiver)
    assert restarted.recover(first.anchor).common == first.anchor
    assert restarted.record_export_intent(delivery) == replace(first, can_send=False)
    absence = _receipt(first, ReceiverDisposition.RETRY_ELIGIBLE)
    assert restarted.record_receiver_evidence(first, absence) is (
        ReceiverDisposition.RETRY_ELIGIBLE
    )
    second = restarted.record_export_intent(delivery)
    assert second.can_send and second.attempt == 2 and second.delivery == first.delivery
    assert (
        restarted.record_receiver_evidence(first, absence) is ReceiverDisposition.HELD
    )
    assert not restarted.record_export_intent(delivery).can_send

    # Verified late acceptance of attempt 1 is terminal even after attempt 2
    # opened. Both attempts carry the same receiver operation identity.
    accepted = _receipt(first, ReceiverDisposition.ACCEPTED)
    assert restarted.record_receiver_evidence(second, accepted) is (
        ReceiverDisposition.ACCEPTED
    )
    files = {item.name: item.read_bytes() for item in root.iterdir()}
    assert restarted.record_receiver_evidence(first, accepted) is (
        ReceiverDisposition.ACCEPTED
    )
    assert (
        restarted.record_receiver_evidence(
            second, _receipt(second, ReceiverDisposition.RETRY_ELIGIBLE)
        )
        is ReceiverDisposition.HELD
    )
    assert not restarted.record_export_intent(delivery).can_send
    assert files == {item.name: item.read_bytes() for item in root.iterdir()}
    assert all(accepted.proof.hex().encode() not in data for data in files.values())


def test_receiver_refuses_a_fresh_key_or_changed_bytes_for_the_same_publication(
    coverage_candidate,
):
    journal, root, candidate = coverage_candidate
    fence = RecoveryFence(journal, root, verify_receiver=_verify_receiver)
    delivery = _receiver_delivery(journal, fence.protect(candidate))
    first = fence.record_export_intent(delivery)
    alternative = journal._store.evidence.pseudonymize("fixture-operation", "other")
    for changed in (
        replace(delivery, key=alternative),
        replace(delivery, payload_digest="b" * 64),
    ):
        with pytest.raises(LedgerError):
            fence.record_export_intent(changed)
    assert fence.record_export_intent(delivery) == replace(first, can_send=False)
    assert len(list(root.iterdir())) == 2


def test_receiver_holds_unknown_mismatched_and_unauthenticated_proof(
    coverage_candidate,
):
    journal, root, candidate = coverage_candidate
    fence = RecoveryFence(journal, root, verify_receiver=_verify_receiver)
    delivery = _receiver_delivery(journal, fence.protect(candidate))
    proof = fence.record_export_intent(delivery)
    accepted = _receipt(proof, ReceiverDisposition.ACCEPTED)
    other = journal._store.evidence.pseudonymize("fixture-receiver", "foreign")
    for invalid in (
        replace(accepted, receiver=other),
        replace(accepted, payload_digest="b" * 64),
        replace(accepted, attempt=2),
        replace(accepted, disposition=ReceiverDisposition.HELD),
    ):
        signed = replace(invalid, proof=_receiver_signature(invalid))
        assert fence.record_receiver_evidence(proof, signed) is ReceiverDisposition.HELD
    assert (
        fence.record_receiver_evidence(proof, replace(accepted, proof=b"unverified"))
        is ReceiverDisposition.HELD
    )
    assert (
        RecoveryFence(journal, root).record_receiver_evidence(proof, accepted)
        is ReceiverDisposition.HELD
    )
    assert not fence.record_export_intent(delivery).can_send
    assert len(list(root.iterdir())) == 2
