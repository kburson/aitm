"""Private write-ahead evidence for report and export publication."""

import os
import re
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from pathlib import Path

from ._monitor_journal_store import _STORE as _JOURNAL_STORE
from .ledger import LedgerError, _physical_ancestry, _pin_directory, _PinnedPath
from .monitor_journal import PublicationCandidate, RoutingJournal, _CandidateBasis
from .monitor_registry import _ServiceEvidence
from .scopes import _publication, _publish, _read_private
from .types import SourceRef, _decode, _encode

_ENTRY = re.compile(r"[0-9]{20}\.json")
_FORMAT = "aitm.monitor-recovery/v1"
_HELD = "Verified publication recovery is held"
_DIGEST = re.compile(r"[a-f0-9]{64}")


@dataclass(frozen=True, slots=True)
class WitnessAnchor:
    ordinal: int
    seal: SourceRef


@dataclass(frozen=True, slots=True)
class FencedPublication:
    candidate: PublicationCandidate
    anchor: WitnessAnchor


@dataclass(frozen=True, slots=True)
class RecoveryReadback:
    common: WitnessAnchor | None
    held: bool


class ReceiverDisposition(StrEnum):
    HELD = "held"
    RETRY_ELIGIBLE = "retry-eligible"
    ACCEPTED = "accepted"


@dataclass(frozen=True, slots=True)
class ReceiverDelivery:
    publication: FencedPublication
    receiver: SourceRef
    key: SourceRef
    payload_digest: str


@dataclass(frozen=True, slots=True)
class ExportIntent:
    delivery: ReceiverDelivery
    attempt: int
    anchor: WitnessAnchor
    can_send: bool


@dataclass(frozen=True, slots=True)
class VerifiedReceiverEvidence:
    receiver: SourceRef
    key: SourceRef
    payload_digest: str
    attempt: int
    disposition: ReceiverDisposition
    proof: bytes


@dataclass(frozen=True, slots=True)
class _Publication:
    candidate: PublicationCandidate
    members: SourceRef


@dataclass(frozen=True, slots=True)
class _OpenedAttempt:
    delivery: ReceiverDelivery
    attempt: int


@dataclass(frozen=True, slots=True)
class _ReceiverOutcome:
    intent: WitnessAnchor
    disposition: ReceiverDisposition
    proof_digest: str


@dataclass(frozen=True, slots=True)
class _Record:
    ordinal: int
    previous: SourceRef | None
    key_id: str
    payload: _Publication | _OpenedAttempt | _ReceiverOutcome
    format: str = _FORMAT


@dataclass(frozen=True, slots=True)
class _Envelope:
    record: _Record
    seal: SourceRef

    @property
    def anchor(self) -> WitnessAnchor:
        return WitnessAnchor(self.record.ordinal, self.seal)


def _entry(ordinal: int) -> str:
    return f"{ordinal:020d}.json"


def _overlaps(first: Path, second: Path) -> bool:
    for first_id, first_tail in _physical_ancestry(first):
        for second_id, second_tail in _physical_ancestry(second):
            if first_id == second_id:
                length = min(len(first_tail), len(second_tail))
                if first_tail[:length] == second_tail[:length]:
                    return True
    return False


def _candidate_order(candidate: PublicationCandidate) -> tuple[str, str]:
    return candidate.basis.value, candidate.identity.value


def _check_candidate(candidate: PublicationCandidate) -> None:
    if (
        type(candidate) is not PublicationCandidate
        or type(candidate.sequence) is not int
        or not 0 < candidate.sequence < 2**63
        or type(candidate.basis) is not _CandidateBasis
        or type(candidate.identity) is not SourceRef
    ):
        raise LedgerError(_HELD)


def _intent_matches(
    records: tuple[_Envelope, ...], delivery: ReceiverDelivery
) -> tuple[list[_Envelope], tuple[_ReceiverOutcome, ...]]:
    intents = []
    for envelope in records:
        item = envelope.record.payload
        if (
            type(item) is not _OpenedAttempt
            or item.delivery.receiver != delivery.receiver
        ):
            continue
        if (
            item.delivery.publication != delivery.publication
            and item.delivery.key != delivery.key
        ):
            continue
        if item.delivery != delivery:
            raise LedgerError(_HELD)
        intents.append(envelope)
    anchors = {intent.anchor for intent in intents}
    outcomes = tuple(
        record.record.payload
        for record in records
        if type(record.record.payload) is _ReceiverOutcome
        and record.record.payload.intent in anchors
    )
    return intents, outcomes


def _confirm_readback(directory: _PinnedPath) -> None:
    os.fsync(directory.fd)
    directory.check()


def _seal(record: _Record, evidence: _ServiceEvidence) -> SourceRef:
    return evidence.pseudonymize(
        "monitor-recovery-envelope-v1", _encode(record, _Record)
    )


def _records(directory: _PinnedPath, evidence: _ServiceEvidence) -> Iterator[_Envelope]:
    names = [
        name for name in os.listdir(directory.fd) if not name.startswith(".publishing-")
    ]
    if not all(_ENTRY.fullmatch(name) for name in names):
        raise LedgerError(_HELD)
    previous = None
    for ordinal, name in enumerate(sorted(names), 1):
        if name != _entry(ordinal):
            raise LedgerError(_HELD)
        raw = _read_private(directory, name)
        if raw is None:
            raise LedgerError(_HELD)
        envelope = _decode(raw, _Envelope)
        record = envelope.record
        if (
            record.format != _FORMAT
            or record.ordinal != ordinal
            or record.previous != previous
            or record.key_id != evidence.key_id
            or envelope.seal != _seal(record, evidence)
            or _encode(envelope, _Envelope).encode() != raw
        ):
            raise LedgerError(_HELD)
        previous = envelope.seal
        yield envelope


class RecoveryFence:
    """Witness verified decisions outside the coordinator's rollback roots."""

    def __init__(
        self,
        journal: RoutingJournal,
        root: Path,
        *,
        project_stores: tuple[Path, ...] = (),
        verify_receiver: Callable[[VerifiedReceiverEvidence], bool] | None = None,
    ) -> None:
        self._journal = journal
        self._root = root
        self._project_stores = project_stores
        self._verify_receiver = verify_receiver
        self._held = False

    @contextmanager
    def _session(self) -> Iterator[tuple[_PinnedPath, _ServiceEvidence]]:
        writer = self._journal._writer
        try:
            lease = writer.lease
            key_id = writer.view().source_key_id
            if key_id is None:
                raise LedgerError(_HELD)
            evidence = self._journal._store.evidence
            if evidence.key_id != key_id:
                raise LedgerError(_HELD)
            with (
                _pin_directory(writer.root) as rollback,
                _pin_directory(rollback.path / _JOURNAL_STORE) as journal_store,
                _pin_directory(self._root) as directory,
                _publication(directory),
            ):
                if not _overlaps(rollback.path, journal_store.path):
                    raise LedgerError(_HELD)
                # This also proves the original lease and source key still
                # belong to the held registry root.
                self._journal._store._check_store(rollback, journal_store)
                if any(
                    _overlaps(directory.path, root)
                    for root in (rollback.path, *self._project_stores)
                ):
                    raise LedgerError(_HELD)
                yield directory, evidence
                self._journal._store._check_store(rollback, journal_store)
                lease.check()
        except (OSError, ValueError, LedgerError):
            raise LedgerError(_HELD) from None

    def _confirm(
        self, candidate: PublicationCandidate, evidence: _ServiceEvidence
    ) -> _Publication:
        _check_candidate(candidate)
        after = candidate.sequence - 1
        changes = (
            *self._journal.coverage_changes(after),
            *self._journal.dispute_changes(after),
        )
        members = sorted(
            (
                self._journal.publication_candidate(change)
                for change in changes
                if change.sequence == candidate.sequence
            ),
            key=_candidate_order,
        )
        if len(set(members)) != len(members):
            raise LedgerError(_HELD)
        selected = None
        material = bytearray(candidate.sequence.to_bytes(8) + len(members).to_bytes(8))
        for member in members:
            _check_candidate(member)
            evidence.validate_source_ref(member.identity)
            for field in _candidate_order(member):
                encoded = field.encode("ascii")
                material.extend(len(encoded).to_bytes(4))
                material.extend(encoded)
            if member == candidate:
                selected = member
        if selected is None:
            raise LedgerError(_HELD)
        digest = evidence.pseudonymize("monitor-recovery-candidates-v1", material.hex())
        return _Publication(selected, digest)

    def _append(
        self,
        directory: _PinnedPath,
        evidence: _ServiceEvidence,
        previous: _Envelope | None,
        payload: _Publication | _OpenedAttempt | _ReceiverOutcome,
    ) -> _Envelope:
        ordinal = 1 if previous is None else previous.record.ordinal + 1
        record = _Record(
            ordinal,
            None if previous is None else previous.seal,
            evidence.key_id,
            payload,
        )
        envelope = _Envelope(record, _seal(record, evidence))
        name = _entry(ordinal)
        raw = _encode(envelope, _Envelope).encode()
        if not _publish(directory, name, raw, replace_pending=False):
            if _read_private(directory, name) != raw:
                raise LedgerError(_HELD)
            _confirm_readback(directory)
        return envelope

    def protect(self, candidate: PublicationCandidate) -> FencedPublication:
        """Fence one authenticated member of an exact journal commit."""
        with self._session() as (directory, evidence):
            if self._held:
                raise LedgerError(_HELD)
            publication = self._confirm(candidate, evidence)
            records = tuple(_records(directory, evidence))
            sequence = publication.candidate.sequence
            latest_sequence = 0
            for envelope in records:
                previous = envelope.record.payload
                if type(previous) is not _Publication:
                    continue
                latest_sequence = previous.candidate.sequence
                if previous.candidate.sequence != sequence:
                    continue
                if previous.members != publication.members:
                    raise LedgerError(_HELD)
                if previous == publication:
                    _confirm_readback(directory)
                    return FencedPublication(publication.candidate, envelope.anchor)
            if latest_sequence > sequence:
                raise LedgerError(_HELD)
            envelope = self._append(
                directory, evidence, records[-1] if records else None, publication
            )
            return FencedPublication(publication.candidate, envelope.anchor)

    def recover(self, expected: WitnessAnchor | None) -> RecoveryReadback:
        """Read back the trusted common prefix without declaring an effect."""
        common = None
        matched = False
        self._held = True
        try:
            with self._session() as (directory, evidence):
                if expected is not None:
                    if (
                        type(expected) is not WitnessAnchor
                        or type(expected.ordinal) is not int
                        or expected.ordinal <= 0
                    ):
                        raise LedgerError(_HELD)
                    evidence.validate_source_ref(expected.seal)
                for envelope in _records(directory, evidence):
                    publication = envelope.record.payload
                    if (
                        type(publication) is _Publication
                        and self._confirm(publication.candidate, evidence)
                        != publication
                    ):
                        raise LedgerError(_HELD)
                    anchor = envelope.anchor
                    if expected is not None and anchor.ordinal == expected.ordinal:
                        if anchor != expected:
                            raise LedgerError(_HELD)
                        matched = True
                    common = anchor
                _confirm_readback(directory)
        except LedgerError:
            return RecoveryReadback(common, held=True)
        self._held = not matched
        return RecoveryReadback(common, self._held)

    def _require_publication(
        self,
        delivery: ReceiverDelivery,
        records: tuple[_Envelope, ...],
        evidence: _ServiceEvidence,
    ) -> None:
        if (
            type(delivery) is not ReceiverDelivery
            or type(delivery.publication) is not FencedPublication
            or type(delivery.publication.anchor) is not WitnessAnchor
            or type(delivery.publication.anchor.ordinal) is not int
            or not 0 < delivery.publication.anchor.ordinal <= len(records)
            or type(delivery.payload_digest) is not str
            or _DIGEST.fullmatch(delivery.payload_digest) is None
        ):
            raise LedgerError(_HELD)
        evidence.validate_source_ref(delivery.receiver)
        evidence.validate_source_ref(delivery.key)
        publication = delivery.publication
        saved = records[publication.anchor.ordinal - 1]
        if (
            saved.anchor != publication.anchor
            or type(saved.record.payload) is not _Publication
            or self._confirm(publication.candidate, evidence) != saved.record.payload
        ):
            raise LedgerError(_HELD)

    def record_export_intent(self, delivery: ReceiverDelivery) -> ExportIntent:
        """Durably open at most one attempt until current absence is proven."""
        with self._session() as (directory, evidence):
            if self._held or self._verify_receiver is None:
                raise LedgerError(_HELD)
            records = tuple(_records(directory, evidence))
            self._require_publication(delivery, records, evidence)
            intents, outcomes = _intent_matches(records, delivery)
            attempt = 1
            if intents:
                latest = intents[-1]
                attempt = latest.record.payload.attempt
                terminal = any(
                    outcome.disposition is ReceiverDisposition.ACCEPTED
                    for outcome in outcomes
                )
                absent = any(
                    outcome.intent == latest.anchor
                    and outcome.disposition is ReceiverDisposition.RETRY_ELIGIBLE
                    for outcome in outcomes
                )
                if terminal or not absent:
                    _confirm_readback(directory)
                    return ExportIntent(delivery, attempt, latest.anchor, False)
                attempt += 1
            opened = self._append(
                directory, evidence, records[-1], _OpenedAttempt(delivery, attempt)
            )
            return ExportIntent(delivery, attempt, opened.anchor, True)

    def record_receiver_evidence(
        self, intent: ExportIntent, evidence: VerifiedReceiverEvidence
    ) -> ReceiverDisposition:
        """Accept exact independently proved receiver evidence or keep the intent held."""
        held = ReceiverDisposition.HELD
        verifier = self._verify_receiver
        if (
            verifier is None
            or type(intent) is not ExportIntent
            or type(intent.attempt) is not int
            or type(evidence) is not VerifiedReceiverEvidence
            or type(evidence.attempt) is not int
            or type(evidence.disposition) is not ReceiverDisposition
            or evidence.disposition is held
            or type(evidence.proof) is not bytes
            or not 0 < len(evidence.proof) <= 8192
        ):
            return held
        try:
            with self._session() as (directory, authority):
                if self._held:
                    return held
                records = tuple(_records(directory, authority))
                delivery = intent.delivery
                self._require_publication(delivery, records, authority)
                intents, outcomes = _intent_matches(records, delivery)
                issued = {
                    entry.record.payload.attempt: entry.anchor for entry in intents
                }
                if (
                    issued.get(intent.attempt) != intent.anchor
                    or evidence.attempt not in issued
                    or (evidence.receiver, evidence.key, evidence.payload_digest)
                    != (delivery.receiver, delivery.key, delivery.payload_digest)
                    or verifier(evidence) is not True
                ):
                    return held
                decision = evidence.disposition
                accepted = ReceiverDisposition.ACCEPTED
                if any(outcome.disposition is accepted for outcome in outcomes):
                    if decision is not accepted:
                        return held
                    _confirm_readback(directory)
                    return accepted
                if decision is ReceiverDisposition.RETRY_ELIGIBLE and (
                    evidence.attempt != intent.attempt
                    or issued[evidence.attempt] != intents[-1].anchor
                ):
                    return held
                outcome = _ReceiverOutcome(
                    issued[evidence.attempt],
                    decision,
                    sha256(evidence.proof).hexdigest(),
                )
                prior = next(
                    (
                        item
                        for item in outcomes
                        if item.intent == outcome.intent
                        and item.disposition is decision
                    ),
                    None,
                )
                if prior is not None:
                    if prior != outcome:
                        return held
                    _confirm_readback(directory)
                    return decision
                self._append(directory, authority, records[-1], outcome)
                return decision
        except (LedgerError, OSError, TypeError, ValueError):
            return held
