"""Exercise the private witness before any report or receiver effect."""

import hmac
import json
import os
import stat
from contextlib import nullcontext
from dataclasses import replace
from io import BytesIO
from pathlib import Path
from shutil import copytree
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from test_monitor_coverage import admitted_sources as admitted_sources
from test_monitor_journal import COPY, LIVE, B, NativeJournalFixture
from test_monitor_journal_store import _journal_observations
from test_monitor_qualification import qualify
from test_monitor_scope import SOURCE

from aitm_usage import ledger as ledger_module
from aitm_usage import monitor_recovery, scopes
from aitm_usage._monitor_journal_store import _STORE as _JOURNAL_STORE
from aitm_usage._monitor_journal_store import JournalStore
from aitm_usage.ledger import Ledger, LedgerError, _pin_directory
from aitm_usage.monitor_journal import (
    JournalChange,
    PublicationCandidate,
    RoutingJournal,
    _CandidateBasis,
)
from aitm_usage.monitor_recovery import (
    ReceiverDelivery,
    ReceiverDisposition,
    RecoveryFence,
    VerifiedReceiverEvidence,
    _overlaps,
)
from aitm_usage.monitor_registry import (
    _SOURCE_KEY_FILE,
    Registry,
    RegistryView,
    _ServiceEvidence,
)
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
def dispute_candidates(request, monkeypatch):
    if not getattr(request, "param", True):
        policy = request.getfixturevalue("recovery_policy")
        yield policy.journal, policy.root, *policy.disputes(grouped=False)
        return

    tmp_path = request.getfixturevalue("tmp_path")
    request.getfixturevalue("legacy_monitor_qualification")
    monkeypatch.setattr("aitm_usage.ledger._control_root", lambda: tmp_path / "control")
    native = NativeJournalFixture(tmp_path, monkeypatch)
    root = tmp_path / "witness"
    root.mkdir(mode=0o700)
    for number in (3, 4):
        native.append(LIVE, native.turn(number))
    with native.registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        journal.reserve_batch(journal.prepare(LIVE, native.locator()))
        for number in (3, 4):
            native.append(COPY, native.turn(number, checkout=B))
            if number == 3:
                continue
            journal.reserve_batch(journal.prepare(COPY, native.locator(COPY)))
        first, second = journal.dispute_changes(0)
        assert first.sequence == second.sequence
        yield (
            journal,
            root,
            journal.publication_candidate(first),
            journal.publication_candidate(second),
        )


class _RecoveryPolicy:
    """Supply verified journal candidates and witness bytes to the real fence."""

    def __init__(self, monkeypatch, *, observe_custody=False):
        self.root = Path("/fixture/witness")
        self.files = {}
        self.evidence = _ServiceEvidence(b"fixture recovery witness authority")
        self.changes = []
        self.journal = SimpleNamespace(
            _store=SimpleNamespace(evidence=self.evidence),
            coverage_changes=lambda after: self._listed(after, coverage=True),
            dispute_changes=lambda after: self._listed(after, coverage=False),
            publication_candidate=self._candidate,
        )
        directory = SimpleNamespace(path=self.root, fd=17, check=Mock())
        self.witness_fd = directory.fd

        def session(fence):
            assert fence._journal is self.journal and fence._root == self.root
            return nullcontext((directory, self.evidence))

        def listdir(fd):
            assert fd == directory.fd
            return tuple(self.files)

        def read(source, name):
            assert source is directory
            return self.files.get(name)

        def publish(destination, name, data, *, replace_pending):
            assert destination is directory and not replace_pending
            if name in self.files:
                return False
            self.files[name] = data
            return True

        if observe_custody:
            self._observe_custody(monkeypatch, directory)
        else:
            monkeypatch.setattr(RecoveryFence, "_session", session)
        monkeypatch.setattr(monitor_recovery, "_read_private", read)
        monkeypatch.setattr(monitor_recovery, "_publish", publish)
        monkeypatch.setattr(
            monitor_recovery, "os", SimpleNamespace(listdir=listdir, fsync=Mock())
        )

    def _observe_custody(self, monkeypatch, directory):
        memory = _journal_observations(monkeypatch)
        writer = Registry(memory.writer.root, memory.writer.lease)
        monkeypatch.setattr(writer, "view", memory.writer.view)
        monkeypatch.setattr(writer, "source_evidence", memory.writer.source_evidence)
        self.journal._writer = writer
        self.journal._store = JournalStore(writer)
        self.evidence = self.journal._store.evidence
        self.pin = memory.pin
        self.key_path = writer.root / _SOURCE_KEY_FILE
        self.key_stats = memory.files
        self.nested = writer.root / "would-be-witness"
        paths = {writer.root, memory.store, self.root, self.nested}
        identities = {
            path: (1, index)
            for index, path in enumerate(
                sorted({parent for path in paths for parent in (*path.parents, path)}),
                start=1,
            )
        }

        def ancestry(path, *, directory, allow_missing):
            assert path in paths and directory and allow_missing
            return tuple(identities[item] for item in (*reversed(path.parents), path))

        def pin(path):
            if path == self.root:
                return nullcontext(directory)
            if path == self.nested:
                return nullcontext(SimpleNamespace(path=path))
            return memory.pin(path)

        monkeypatch.setattr(ledger_module, "_validated_path", ancestry)
        monkeypatch.setattr(monitor_recovery, "_pin_directory", pin)
        monkeypatch.setattr(monitor_recovery, "_publication", nullcontext)

    def _listed(self, after, *, coverage):
        return tuple(
            change
            for change, candidate in self.changes
            if change.sequence > after
            and (candidate.basis is _CandidateBasis.COVERAGE) == coverage
        )

    def _candidate(self, change):
        return next(candidate for listed, candidate in self.changes if listed is change)

    def _add(self, sequence, basis, label):
        identity = self.evidence.pseudonymize("fixture-candidate", label)
        candidate = PublicationCandidate(sequence, basis, identity)
        self.changes.append((JournalChange(sequence), candidate))
        return candidate

    def coverage(self):
        return self._add(1, _CandidateBasis.COVERAGE, "coverage")

    def disputes(self, *, grouped=True):
        return (
            self._add(2, _CandidateBasis.OWNERSHIP, "first-dispute"),
            self._add(2 if grouped else 3, _CandidateBasis.OWNERSHIP, "second-dispute"),
        )


@pytest.fixture
def recovery_policy(monkeypatch):
    return _RecoveryPolicy(monkeypatch)


@pytest.fixture
def recovery_custody_policy(monkeypatch):
    return _RecoveryPolicy(monkeypatch, observe_custody=True)


@pytest.mark.parametrize("after_link", [False, True], ids=["before-link", "after-link"])
def test_view_cannot_escape_before_recovery_fsync(request, monkeypatch, after_link):
    if not after_link:
        policy = request.getfixturevalue("recovery_custody_policy")
        _assert_retry_after_unpublished_witness(policy, monkeypatch)
        return

    coverage_candidate = request.getfixturevalue("coverage_candidate")
    journal, root, candidate = coverage_candidate
    fence = RecoveryFence(journal, root)
    publish = monitor_recovery._publish

    def interrupted(*args, **kwargs):
        publish(*args, **kwargs)
        raise OSError("interrupted witness publication")

    with monkeypatch.context() as failure:
        failure.setattr(monitor_recovery, "_publish", interrupted)
        with pytest.raises(LedgerError):
            fence.protect(candidate)
    assert len(list(root.iterdir())) == 1
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


def _assert_retry_after_unpublished_witness(policy, monkeypatch):
    fence = RecoveryFence(policy.journal, policy.root)
    candidate = policy.coverage()
    staged = {}
    sync = monitor_recovery.os.fsync
    witness_fd = policy.witness_fd
    staged_fd = 18
    mode = os.stat_result((stat.S_IFREG | 0o600, 18, 1, 1, os.geteuid(), 0, 0, 0, 0, 0))
    output = None

    def open_stage(name, flags, permissions, *, dir_fd):
        nonlocal output
        assert dir_fd == witness_fd and permissions == 0o600
        assert flags == os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
        assert name.startswith(".publishing-") and name not in staged
        output = staged[name] = BytesIO()
        return staged_fd

    def unlink_stage(name, *, dir_fd):
        assert dir_fd == witness_fd
        try:
            del staged[name]
        except KeyError:
            raise FileNotFoundError(name) from None

    def file_stream(fd, mode):
        assert (fd, mode) == (staged_fd, "wb") and output is not None
        return nullcontext(output)

    def publish(src_fd, source, dst_fd, destination):
        assert (src_fd, dst_fd) == (witness_fd, witness_fd)
        assert destination not in policy.files
        policy.files[destination] = staged.pop(source).getvalue()
        return True

    monkeypatch.setattr(monitor_recovery, "_publish", scopes._publish)
    monkeypatch.setattr(scopes, "_check_acl", Mock())
    monkeypatch.setattr(
        scopes,
        "os",
        SimpleNamespace(
            O_WRONLY=os.O_WRONLY,
            O_CREAT=os.O_CREAT,
            O_EXCL=os.O_EXCL,
            O_NOFOLLOW=os.O_NOFOLLOW,
            open=open_stage,
            fdopen=file_stream,
            fchmod=Mock(),
            fstat=lambda fd: mode,
            fsync=sync,
            unlink=unlink_stage,
        ),
    )
    rename = Mock(side_effect=(OSError("interrupted before witness link"), True))

    def publish_after_fault(*args):
        rename(*args)
        return publish(*args)

    monkeypatch.setattr(scopes, "publish_noreplace", publish_after_fault)
    with pytest.raises(LedgerError, match="Verified publication recovery is held"):
        fence.protect(candidate)
    assert not staged and not policy.files
    sync.assert_called_once_with(staged_fd)

    recovered = fence.protect(candidate)
    assert recovered.candidate == candidate and recovered.anchor.ordinal == 1
    assert [invocation.args for invocation in sync.call_args_list] == [
        (staged_fd,),
        (staged_fd,),
        (witness_fd,),
    ]
    assert not staged and len(policy.files) == 1
    assert fence.protect(candidate) == recovered
    assert rename.call_count == 2


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
def test_recovery_holds_at_the_authenticated_prefix(recovery_policy, missing):
    policy = recovery_policy
    journal, root = policy.journal, policy.root
    first, second = policy.disputes()
    fence = RecoveryFence(journal, root)
    one = fence.protect(first)
    two = fence.protect(second)
    tail = max(policy.files)
    if missing:
        del policy.files[tail]
    else:
        policy.files[tail] = policy.files[tail].replace(
            b"monitor-recovery/v1", b"invalid"
        )
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


def test_same_sequence_set_refuses_a_divergent_readback(recovery_policy, monkeypatch):
    journal, root = recovery_policy.journal, recovery_policy.root
    first, second = recovery_policy.disputes()
    fence = RecoveryFence(journal, root)
    one = fence.protect(first)
    two = fence.protect(second)
    assert one.anchor.ordinal == 1 and two.anchor.ordinal == 2
    changes = journal.dispute_changes(first.sequence - 1)
    assert len(changes) == 2
    # A restored listing can omit a member while the other candidate remains valid.
    monkeypatch.setattr(journal, "dispute_changes", lambda _: changes[:1])
    assert journal.publication_candidate(changes[0]) == first
    with pytest.raises(LedgerError):
        fence.protect(first)
    assert len(recovery_policy.files) == 2


@pytest.mark.parametrize("dispute_candidates", [False], indirect=True)
def test_fence_refuses_an_unwitnessed_older_candidate(
    dispute_candidates, recovery_policy
):
    journal, root, first, second = dispute_candidates
    assert first.sequence < second.sequence
    fence = RecoveryFence(journal, root)
    newest = fence.protect(second)
    with pytest.raises(LedgerError):
        fence.protect(first)
    assert fence.protect(second) == newest
    assert len(recovery_policy.files) == 1


def test_forged_candidate_against_keyless_registry_creates_no_key(
    recovery_custody_policy,
    monkeypatch,
):
    policy = recovery_custody_policy
    journal, root, candidate = policy.journal, policy.root, policy.coverage()
    writer = journal._writer
    del policy.key_stats[policy.key_path]
    monkeypatch.setattr(writer, "view", lambda: RegistryView())
    writer.source_evidence.reset_mock()
    policy.pin.reset_mock()
    with pytest.raises(LedgerError):
        RecoveryFence(journal, root).protect(
            replace(candidate, sequence=candidate.sequence + 1)
        )
    assert policy.key_path not in policy.key_stats
    assert not policy.files
    writer.source_evidence.assert_not_called()
    policy.pin.assert_not_called()


def test_fence_rejects_forged_types_and_a_root_inside_journal(recovery_custody_policy):
    policy = recovery_custody_policy
    journal, root, candidate = policy.journal, policy.root, policy.coverage()
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
    assert not policy.files
    with pytest.raises(LedgerError):
        RecoveryFence(journal, policy.nested).protect(candidate)
    with pytest.raises(LedgerError):
        RecoveryFence(journal, root, project_stores=(root,)).protect(candidate)
    assert not policy.files


def test_fence_refuses_lost_coordinator_custody(recovery_custody_policy, monkeypatch):
    policy = recovery_custody_policy
    journal, root, candidate = policy.journal, policy.root, policy.coverage()
    fence = RecoveryFence(journal, root)
    ready = fence.protect(candidate)
    with monkeypatch.context() as fault:
        fault.setattr(journal._writer, "_writer", None)
        with pytest.raises(LedgerError):
            fence.protect(candidate)
        lost = fence.recover(ready.anchor)
        assert lost.held and lost.common is None
    assert len(policy.files) == 1


def test_journal_store_key_and_lease_share_the_derived_rollback_root(
    coverage_candidate,
):
    journal, root, candidate = coverage_candidate
    writer = journal._writer
    lease = writer.lease
    key = writer.root / _SOURCE_KEY_FILE
    store = writer.root / _JOURNAL_STORE
    with _pin_directory(writer.root) as rollback, _pin_directory(store) as pinned:
        for contained in (pinned.path, key.parent, lease.path.parent):
            assert _overlaps(rollback.path, contained)
        for name, expected in (
            (_JOURNAL_STORE, os.fstat(pinned.fd)),
            (_SOURCE_KEY_FILE, key.lstat()),
            (lease.path.name, os.fstat(lease.fd)),
        ):
            actual = os.stat(name, dir_fd=rollback.fd, follow_symlinks=False)
            assert os.path.samestat(actual, expected)
    assert RecoveryFence(journal, root).protect(candidate).candidate == candidate
    moved = root.parent / "moved-store"
    store.rename(moved)
    store.symlink_to(moved, target_is_directory=True)
    with pytest.raises(LedgerError):
        RecoveryFence(journal, root).protect(candidate)
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
    recovery_policy,
):
    journal, root = recovery_policy.journal, recovery_policy.root
    candidate = recovery_policy.coverage()
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
    assert len(recovery_policy.files) == 2


def test_receiver_holds_unknown_mismatched_and_unauthenticated_proof(
    recovery_policy,
):
    journal, root = recovery_policy.journal, recovery_policy.root
    candidate = recovery_policy.coverage()
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
    assert len(recovery_policy.files) == 2
