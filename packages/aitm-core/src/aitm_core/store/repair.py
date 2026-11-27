"""Build and independently verify forward-only planning history repairs."""

from dataclasses import dataclass
from functools import partial
from hashlib import sha256
from json import dumps

from aitm_core.models.common import (
    CommandResult,
    LocalOutcome,
    PublicationOutcome,
    StoreAnchor,
)
from aitm_core.services import backend, preflight_policy
from aitm_core.store.backend import OperationResult, Snapshot
from aitm_core.store.continuity import ContinuityStatus
from aitm_core.store.fetch import Freshness
from aitm_core.store.git_backend import ValidationRejected
from aitm_core.store.installation import Installation
from aitm_core.store.objects import GitCommandError, Repository
from aitm_core.store.publication import Publisher
from aitm_core.store.validation import (
    DiagnosedHistory,
    ForwardRepairVerifier,
    ValidationReport,
    _entries,
    validate_history,
)


class RepairConflict(ValueError):
    """The observed tip or authorized repair basis changed."""


@dataclass(frozen=True, slots=True)
class RepairPlan:
    anchor: StoreAnchor
    bad_tip: Snapshot
    valid_prefix: Snapshot
    first_invalid: str
    receipt_path: str
    receipt: bytes

    @property
    def operation_id(self) -> str:
        return self.receipt_path.removeprefix(".aitm/repairs/").removesuffix(".json")


def _receipt(
    repository: Repository, anchor: StoreAnchor, diagnosis: DiagnosedHistory
) -> tuple[str, bytes]:
    offending = repository.read_tree(diagnosis.first_invalid)
    parent = repository.parent(offending)
    changed = repository._git(
        "diff-tree",
        "-r",
        "--no-renames",
        "--no-commit-id",
        "--name-only",
        "-z",
        parent,
        offending.revision,
    )
    value = {
        "schema": "aitm.forward-repair/v1",
        "store": {
            "uuid": anchor.store_uuid,
            "root": anchor.root_commit,
            "ref": anchor.planning_ref,
        },
        "bad_tip": {
            "commit": diagnosis.bad_tip.revision,
            "tree": diagnosis.bad_tip.tree,
        },
        "valid_prefix": {
            "commit": diagnosis.valid_prefix.revision,
            "tree": diagnosis.valid_prefix.tree,
        },
        "first_invalid": diagnosis.first_invalid,
        "paths": sorted(
            raw.decode("utf-8", "surrogateescape")
            for raw in changed.split(b"\0")
            if raw
        ),
    }
    receipt = (dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    return f".aitm/repairs/{sha256(receipt).hexdigest()}.json", receipt


def _verify(
    repository: Repository,
    anchor: StoreAnchor,
    diagnosis: DiagnosedHistory,
    candidate: Snapshot,
) -> ValidationReport:
    path, receipt = _receipt(repository, anchor, diagnosis)
    actual = _entries(repository, candidate)
    restored = _entries(repository, diagnosis.valid_prefix)
    metadata = actual.pop(path, None)
    parent = repository.parent(candidate)
    if (
        parent != diagnosis.bad_tip.revision
        or path in restored
        or actual != restored
        or metadata is None
        or (metadata.kind, metadata.mode) != ("blob", "100644")
        or repository.read_blobs(candidate.tree, (path,))[path] != receipt
    ):
        return ValidationReport(
            LocalOutcome.INTEGRITY_ERROR,
            candidate.revision,
            "forward repair does not match the independently diagnosed restoration",
        )
    return ValidationReport(LocalOutcome.COMPLETED, candidate.revision)


def repair_verifier(repository: Repository) -> ForwardRepairVerifier:
    return partial(_verify, repository)


def plan_repair(
    anchor: StoreAnchor, bad_tip: str, *, repository: Repository
) -> RepairPlan:
    report = validate_history(anchor, bad_tip, repository=repository)
    if (
        report.outcome != LocalOutcome.INTEGRITY_ERROR
        or report.valid_prefix is None
        or report.first_invalid is None
        or report.reason == "planning-history-must-be-linear"
    ):
        raise ValidationRejected(
            report.reason or "the exact tip has no eligible repair"
        )
    bad = repository.read_tree(bad_tip)
    prefix = repository.read_tree(report.valid_prefix)
    diagnosis = DiagnosedHistory(prefix, report.first_invalid, bad, report.reason or "")
    path, receipt = _receipt(repository, anchor, diagnosis)
    return RepairPlan(anchor, bad, prefix, report.first_invalid, path, receipt)


def _basis(installation: Installation, expected_tip: str) -> tuple[StoreAnchor, str]:
    repo = installation.repository
    repo._oid(expected_tip)
    observed = preflight_policy(installation)
    code = observed.views.local
    code_ref = installation.policy_ref(code)
    if (
        observed.policy is None
        or observed.policy.writes_fenced
        or code_ref is None
        or code.observed_commit is None
        or observed.views.code_freshness not in {Freshness.FRESH, Freshness.LOCAL_ONLY}
    ):
        raise ValidationRejected(
            observed.reason or "trusted code policy is unavailable"
        )
    if installation.store.planning_remote is None:
        if repo.tip().revision != expected_tip:
            raise RepairConflict(
                "local planning tip differs from the expected repair tip"
            )
    else:
        shared = observed.views.shared
        if (
            shared is None
            or shared.status != ContinuityStatus.QUARANTINED
            or shared.observation is None
            or shared.observation.observed_commit != expected_tip
            or shared.checkpoint != expected_tip
        ):
            raise RepairConflict(
                "shared planning tip differs from the expected quarantined tip"
            )
    return installation.store.model_copy(
        update={"code_default_ref": code_ref}
    ), code.observed_commit


def apply_repair(
    plan: RepairPlan, expected_tip: str, *, installation: Installation
) -> OperationResult:
    repo = installation.repository
    before = repo.tip()
    try:
        anchor, code = _basis(installation, expected_tip)
        target = backend(repo, anchor, code_pin=(anchor.code_default_ref, code))
        publisher = Publisher(installation)
        recovery = None
        with target._gate(repo, repo.ref) as gate:
            current = repo.tip()
            if (
                current != before
                or plan_repair(anchor, expected_tip, repository=repo) != plan
            ):
                raise RepairConflict("planning or the repair proof changed")
            namespace = f"refs/aitm/recovery/c10-{plan.operation_id}"
            receipt = repo.read_blobs(current.tree, (plan.receipt_path,))[
                plan.receipt_path
            ]
            if receipt == plan.receipt and repo.parent(current) == expected_tip:
                gate(current, None)
                candidate = current
                retained = repo._git("for-each-ref", "--format=%(refname)", namespace)
                recovery = next(iter(retained.decode().splitlines()), None)
            else:
                if repo._run(
                    "merge-base", "--is-ancestor", current.revision, expected_tip
                ).returncode:
                    recovery = f"{namespace}/{current.revision}"
                    publisher._retain_ref(recovery, current.revision)
                restored = repo.create_commit(
                    plan.valid_prefix,
                    {plan.receipt_path: plan.receipt},
                    plan.operation_id,
                )
                revision = (
                    repo._git(
                        "commit-tree",
                        restored.tree,
                        "-p",
                        expected_tip,
                        "-m",
                        f"AITM forward repair {plan.operation_id}",
                    )
                    .strip()
                    .decode()
                )
                candidate = repo.read_tree(revision)
                gate(current, candidate)
                if not repo.compare_and_swap(candidate.revision, current.revision):
                    raise RepairConflict("local planning ref changed during repair")
            if publisher.remote is not None:
                gate.assert_excluded()
                try:
                    publisher._push(candidate.revision, expected_tip)
                except (GitCommandError, OSError, ValueError):
                    # The local repair is durable. A fresh observation below
                    # determines publication even after a missing acknowledgement.
                    pass
        publication = PublicationOutcome.NOT_APPLICABLE
        if publisher.remote is not None:
            publication = PublicationOutcome.PENDING
            try:
                shared = preflight_policy(installation).views.shared
                if (
                    shared is not None
                    and shared.status == ContinuityStatus.VERIFIED
                    and shared.valid_tip is not None
                    and not repo._run(
                        "merge-base",
                        "--is-ancestor",
                        candidate.revision,
                        shared.valid_tip,
                    ).returncode
                ):
                    publication = PublicationOutcome.VERIFIED
            except (GitCommandError, OSError, ValueError):
                pass
        return OperationResult(
            CommandResult(
                operation_id=plan.operation_id,
                local=LocalOutcome.COMPLETED,
                publication=publication,
                evidence=(
                    f"Restored validated planning prefix {plan.valid_prefix.revision}.",
                    f"Repair commit {candidate.revision} extends {expected_tip}.",
                ),
                recovery=recovery,
            ),
            candidate,
        )
    except RepairConflict as error:
        return OperationResult(
            CommandResult(
                operation_id=plan.operation_id,
                local=LocalOutcome.CONFLICT,
                evidence=(str(error),),
            ),
            before,
            str(error),
        )
    except (GitCommandError, OSError, ValueError) as error:
        return OperationResult(
            CommandResult(
                operation_id=plan.operation_id,
                local=LocalOutcome.INTEGRITY_ERROR,
                evidence=(str(error),),
            ),
            before,
            str(error),
        )


def repair(installation: Installation, expected_tip: str) -> OperationResult:
    anchor, _ = _basis(installation, expected_tip)
    plan = plan_repair(anchor, expected_tip, repository=installation.repository)
    return apply_repair(plan, expected_tip, installation=installation)
