"""Project-bound delivery of exact private monitor journal changes."""

import json
from dataclasses import dataclass
from hashlib import sha256

from .ledger import Ledger, LedgerIdentity, _DeliveryReceipt
from .monitor_journal import RoutingJournal, _DeliveryClaim, _DeliveryRefused
from .monitor_registry import RegisteredProject, _directory, _project
from .monitor_types import (
    MonitorModel,
    MonitorObservation,
    MonitorProvider,
    MonitorRevision,
    ObservationTimeBasis,
)
from .types import _encode


@dataclass(frozen=True, slots=True)
class ProjectDelivery:
    """Attach one destination to its existing coordinator and writer custody."""

    _journal: RoutingJournal
    _writer: Ledger
    _identity: LedgerIdentity
    _registered: RegisteredProject

    @classmethod
    def attach(cls, journal: RoutingJournal, writer: Ledger) -> "ProjectDelivery":
        registry = journal._writer
        registry.lease
        selected = _project(registry.view(), writer.identity.project_id)
        result = cls(journal, writer, writer.identity, selected)
        result._require_current()
        journal._require_delivery_destination(
            writer.identity.project_id, writer.identity.key_id
        )
        return result

    def _require_current(self) -> None:
        registry = self._journal._writer
        registry.lease
        writer = self._writer
        writer._require_delivery_writer()
        if (
            writer.identity != self._identity
            or _project(registry.view(), self._identity.project_id) != self._registered
            or _directory(str(writer.root), private=True) != self._registered.state
            or self._registered.adopted_key_id not in (None, self._identity.key_id)
        ):
            raise _DeliveryRefused("Registered project delivery identity changed")

    def _monitor_revision(self, issued: _DeliveryClaim) -> MonitorRevision:
        claim = issued.claim
        if claim.project_id != self._identity.project_id:
            raise _DeliveryRefused("Destination claim belongs to another project")
        usage = claim.usage
        key = self._writer.pseudonymize(
            "monitor-delivery-row-v1",
            json.dumps(
                [issued.service_key, claim.key.value],
                ensure_ascii=True,
                separators=(",", ":"),
                allow_nan=False,
            ),
        )
        try:
            observation = MonitorObservation(
                MonitorProvider(usage.boundary.provider.value),
                claim.evidence.surface,
                None
                if claim.time_basis is ObservationTimeBasis.UNKNOWN
                else usage.observed_at,
                claim.time_basis,
                usage.tokens,
                usage.availability,
                MonitorModel(usage.model.value),
            )
        except ValueError:
            raise _DeliveryRefused("Destination usage shape is unsupported") from None
        return MonitorRevision(key, claim.revision, observation)

    def commit(self, issued: _DeliveryClaim) -> _DeliveryReceipt:
        """Commit one currently owed MonitorRevision with its durable receipt."""
        self._require_current()
        self._journal._require_delivery_destination(
            self._identity.project_id, self._identity.key_id
        )
        if type(issued) is not _DeliveryClaim or (
            self._journal.reserve_delivery(issued.claim.key, issued.claim.revision)
            != issued
        ):
            raise _DeliveryRefused("No current verified destination claim")
        row = self._monitor_revision(issued)
        self._require_current()
        return self._writer._commit_monitor_delivery(
            row, issued.claim.sequence, issued.digest
        )

    def _readback(
        self, issued: _DeliveryClaim, receipt: _DeliveryReceipt
    ) -> _DeliveryReceipt | None:
        self._require_current()
        row = self._monitor_revision(issued)
        payload = _encode(
            row, MonitorRevision, validate_ref=self._writer.validate_source_ref
        )
        if (
            (receipt.project_id, receipt.destination_key)
            != (self._identity.project_id, self._identity.key_id)
            or (receipt.key, receipt.revision) != (row.key, row.revision)
            or receipt.payload_digest != sha256(payload.encode()).hexdigest()
        ):
            raise _DeliveryRefused("Destination receipt was issued for another write")
        return self._writer._monitor_delivery_receipt(row.key, row.revision)
