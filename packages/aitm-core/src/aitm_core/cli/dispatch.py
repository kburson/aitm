"""Command adapters for retrying and resolving planning publication."""

from aitm_core.models.common import CommandResult, LocalOutcome, PublicationOutcome
from aitm_core.store.installation import Installation
from aitm_core.store.publication import PublicationStatus, Publisher
from aitm_core.store.reconcile import Resolution, reconcile


def publish(installation: Installation, operation_id: str) -> CommandResult:
    result = Publisher(installation).publish(operation_id)
    publication = {
        PublicationStatus.PUBLISHED: PublicationOutcome.VERIFIED,
        PublicationStatus.NOT_APPLICABLE: PublicationOutcome.NOT_APPLICABLE,
        PublicationStatus.PENDING: PublicationOutcome.PENDING,
        PublicationStatus.CONFLICT: PublicationOutcome.PENDING,
    }[result.status]
    return CommandResult(
        operation_id=operation_id,
        local=LocalOutcome.COMPLETED
        if result.local_completed
        else LocalOutcome.UNAVAILABLE,
        publication=publication,
        evidence=(f"Publication {result.status}: {result.reason}",)
        if result.reason
        else (),
        recovery=result.recovery_ref,
    )


def resolve(
    installation: Installation, operation_id: str, resolution: Resolution
) -> CommandResult:
    return reconcile(installation, operation_id, resolution).command
