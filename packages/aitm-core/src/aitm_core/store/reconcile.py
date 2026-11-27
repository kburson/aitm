"""Resolve a retained publication conflict through explicit, scoped recovery."""

from dataclasses import dataclass

from aitm_core.models.common import CommandResult, LocalOutcome, PublicationOutcome
from aitm_core.models.operations import Operation
from aitm_core.services import ServicePorts, backend, mutate, preflight_policy
from aitm_core.store.backend import OperationCategories, OperationResult, Snapshot
from aitm_core.store.continuity import ContinuityStatus
from aitm_core.store.fetch import Freshness
from aitm_core.store.git_backend import ValidationRejected
from aitm_core.store.installation import Installation
from aitm_core.store.objects import GitCommandError
from aitm_core.store.publication import Publisher, ReplayConflict


@dataclass(frozen=True, slots=True)
class Resolution:
    retained_revision: str
    expected_shared: str
    replacement: Operation | None = None


def _paths(operation: Operation) -> set[str]:
    return {
        entry.path for entry in (*operation.change.writes, *operation.change.events)
    }


def reconcile(
    installation: Installation,
    operation_id: str,
    resolution: Resolution,
    *,
    ports: ServicePorts | None = None,
    categories: OperationCategories | None = None,
) -> OperationResult:
    """Select the verified published prefix and optionally submit a resolution."""
    publisher = Publisher(installation, ports, categories)
    repo = installation.repository
    snapshot = repo.tip()
    try:
        original = publisher.request(operation_id)
        retained = repo._oid(resolution.retained_revision)
        recovery = publisher._recovery_ref(retained)
        if (
            repo._git("show-ref", "--verify", "--hash", recovery).strip().decode()
            != retained
        ):
            raise ReplayConflict("retained publication history could not be verified")
        if publisher.record(repo.read_tree(retained), original) is None:
            raise ReplayConflict(
                "the retained revision does not contain the requested operation"
            )

        replacement = resolution.replacement
        if replacement is not None:
            if replacement.operation_id == operation_id or _paths(
                replacement
            ) != _paths(original):
                raise ReplayConflict(
                    "replacement requires a new identity and the original write scope"
                )

        observed = preflight_policy(installation, ports=ports)
        shared = observed.views.shared
        code = observed.views.local
        policy_ref = installation.policy_ref(code)
        if (
            observed.outcome != LocalOutcome.COMPLETED
            or observed.policy is None
            or policy_ref is None
            or code.observed_commit is None
            or observed.views.code_freshness
            not in {Freshness.FRESH, Freshness.LOCAL_ONLY}
            or shared is None
            or shared.status != ContinuityStatus.VERIFIED
            or shared.valid_tip != resolution.expected_shared
        ):
            raise ReplayConflict(
                "reconciliation requires the exact verified shared tip and policy"
            )
        if (
            replacement is not None
            and replacement.policy_digest != observed.policy.source.digest
        ):
            raise ReplayConflict("resolution was prepared against a different policy")

        shared_snapshot = repo.read_tree(resolution.expected_shared)
        store = installation.store.model_copy(update={"code_default_ref": policy_ref})
        target = backend(
            repo,
            store,
            ports=ports,
            categories=categories,
            code_pin=(policy_ref, code.observed_commit),
        )
        with target._gate(repo, repo.ref) as gate:
            snapshot = target.snapshot()
            if snapshot.revision not in {retained, shared_snapshot.revision}:
                raise ReplayConflict("local planning moved during reconciliation")
            if replacement is not None:
                from hashlib import sha256

                reads = replacement.change.read_set
                blobs = target.read(shared_snapshot, tuple(item.path for item in reads))
                for item in reads:
                    blob = blobs[item.path]
                    digest = sha256(blob).hexdigest() if blob is not None else None
                    if digest != item.digest:
                        raise ReplayConflict(
                            "replacement read set disagrees with the shared tip"
                        )
            gate(snapshot, shared_snapshot)
            if replacement is not None:
                publisher.retain_supersession(original, replacement, retained)
            if snapshot != shared_snapshot and not repo.compare_and_swap(
                shared_snapshot.revision, snapshot.revision
            ):
                raise ReplayConflict("local planning moved during reconciliation")
        if replacement is not None:
            return mutate(
                installation,
                replacement,
                shared_snapshot,
                ports=ports,
                categories=categories,
            )
        return OperationResult(
            CommandResult(
                operation_id=operation_id,
                local=LocalOutcome.COMPLETED,
                publication=PublicationOutcome.NOT_APPLICABLE,
                evidence=(
                    "Selected the verified shared prefix. The original operation remains unpublished and retained for recovery.",
                ),
                recovery=recovery,
            ),
            shared_snapshot,
        )
    except ReplayConflict as error:
        return _failure(operation_id, snapshot, LocalOutcome.CONFLICT, error)
    except (GitCommandError, OSError, ValidationRejected, ValueError) as error:
        return _failure(operation_id, snapshot, LocalOutcome.UNAVAILABLE, error)


def _failure(
    operation_id: str, snapshot: Snapshot, outcome: LocalOutcome, error: Exception
) -> OperationResult:
    reason = str(error)
    return OperationResult(
        CommandResult(operation_id=operation_id, local=outcome, evidence=(reason,)),
        snapshot,
        reason,
    )
