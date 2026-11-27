"""Wiring slots for optional implementations of mandatory Core capabilities."""

from __future__ import annotations

from contextlib import AbstractContextManager
from dataclasses import dataclass, replace
from json import loads
from os import fsdecode
from pathlib import Path
from typing import TYPE_CHECKING, Literal, cast

from aitm_core.models.common import CommandResult, LocalOutcome, PublicationOutcome

if TYPE_CHECKING:
    from aitm_core.config import PolicySnapshot
    from aitm_core.ext.api import Extension
    from aitm_core.models.common import RefreshResult, StoreAnchor
    from aitm_core.models.operations import Operation, ReadExpectation
    from aitm_core.store.backend import OperationCategories, OperationResult, Snapshot
    from aitm_core.store.fetch import RefreshedViews
    from aitm_core.store.gate import Gate
    from aitm_core.store.git_backend import GitBackend
    from aitm_core.store.installation import Installation
    from aitm_core.store.objects import Repository
    from aitm_core.store.validation import ForwardRepairVerifier, ValidationReport

ServicePortName = Literal[
    "policy_resolution",
    "policy_refresh",
    "validation_gate",
    "forward_repair_verifier",
    "write_authorization",
    "attempt_preflight",
    "init_hooks",
    "action_retry",
    "lane_selection",
    "kind_requirements",
    "aggregate_evidence",
    "story_exit_guards",
]


class UnavailablePort(RuntimeError):
    def __init__(self, port: ServicePortName):
        self.port = port
        super().__init__(f"Core service is unavailable: {port}")


@dataclass(frozen=True, slots=True)
class ServicePorts:
    policy_resolution: object | None = None
    policy_refresh: object | None = None
    validation_gate: object | None = None
    forward_repair_verifier: object | None = None
    write_authorization: object | None = None
    attempt_preflight: object | None = None
    init_hooks: object | None = None
    action_retry: object | None = None
    lane_selection: object | None = None
    kind_requirements: object | None = None
    aggregate_evidence: object | None = None
    story_exit_guards: object | None = None
    extension_declarations: tuple[Extension, ...] = ()

    def require(self, port: ServicePortName) -> object:
        implementation = getattr(self, port)
        if implementation is None:
            raise UnavailablePort(port)
        return implementation


def backend(
    repository: Repository,
    anchor: StoreAnchor,
    *,
    ports: ServicePorts | None = None,
    categories: OperationCategories | None = None,
    code_pin: tuple[str, str] | None = None,
) -> GitBackend:
    """Compose the Git backend with the mandatory anchored planning validator."""
    from aitm_core.store.gate import RefIdentity, RefMutationKind, ref_gate
    from aitm_core.store.git_backend import GitBackend
    from aitm_core.store.validation import ValidationReport, validate_history

    services = ports if ports is not None else ServicePorts()

    def check(tip: str) -> ValidationReport:
        if code_pin is not None:
            ref, revision = code_pin
            symbolic = repository._run("symbolic-ref", "-q", ref)
            current = repository._run("show-ref", "--verify", "--hash", ref)
            if (
                symbolic.returncode != 1
                or current.returncode != 0
                or current.stdout.strip() != revision.encode("ascii")
            ):
                return ValidationReport(
                    LocalOutcome.CONFLICT,
                    tip,
                    "code-policy pin changed before mutation",
                )
        return validate_history(
            anchor,
            tip,
            repository=repository,
            forward_repair_verifier=cast(
                "ForwardRepairVerifier | None", services.forward_repair_verifier
            ),
        )

    def gate(repo: Repository, target: str) -> AbstractContextManager[Gate]:
        return ref_gate(
            repo,
            RefIdentity(target),
            RefMutationKind.PLANNING,
            planning_validation=check,
        )

    return GitBackend(repository, gate, ports=services, categories=categories)


def policy(anchor: Installation, refresh: RefreshResult) -> PolicySnapshot:
    """Resolve effective policy through the committed Core authority."""
    from aitm_core.config import resolve_policy

    return resolve_policy(anchor, refresh)


@dataclass(frozen=True, slots=True)
class PolicyPreflight:
    """Policy and read inputs selected before taking an operation guard."""

    views: RefreshedViews
    policy: PolicySnapshot | None
    outcome: LocalOutcome
    publication: PublicationOutcome
    reason: str | None = None
    expected: Snapshot | None = None
    read_set: tuple[ReadExpectation, ...] = ()

    @property
    def evidence(self) -> tuple[str, ...]:
        lines = [f"Code policy freshness: {self.views.code_freshness}."]
        if self.policy is not None:
            lines.append(
                f"Committed policy {self.policy.revision} "
                f"(configuration {self.policy.source.digest})."
            )
        if self.views.shared is not None:
            lines.append(f"Shared planning status: {self.views.shared.status}.")
        if self.reason:
            lines.append(self.reason)
        return tuple(lines)


def refresh(
    anchor: Installation,
    *,
    cached: bool = False,
    ports: ServicePorts | None = None,
    trusted_checkpoint: str | None = None,
) -> RefreshedViews:
    """Select cached observations or run the common, anchored refresh adapter."""
    from aitm_core.store.fetch import (
        RefreshedViews,
        RefreshPolicy,
        cached_refs,
        refresh_refs,
    )

    verifier = ports.forward_repair_verifier if ports is not None else None
    request = RefreshPolicy(
        installation=anchor,
        trusted_checkpoint=trusted_checkpoint,
        forward_repair_verifier=cast("ForwardRepairVerifier | None", verifier),
    )
    if cached:
        return cached_refs(request)
    selected = ports.policy_refresh if ports is not None else None
    if selected is None:
        return refresh_refs(request)
    if not callable(selected):
        raise UnavailablePort("policy_refresh")
    result = selected(request)
    if not isinstance(result, RefreshedViews):
        raise UnavailablePort("policy_refresh")
    return result


def preflight_policy(
    anchor: Installation,
    *,
    cached: bool = False,
    ports: ServicePorts | None = None,
    trusted_checkpoint: str | None = None,
) -> PolicyPreflight:
    """Resolve only the admitted policy and distinguish permission from freshness."""
    from aitm_core.config import PolicyUnavailable
    from aitm_core.store.continuity import ContinuityStatus
    from aitm_core.store.fetch import Freshness

    views = refresh(
        anchor, cached=cached, ports=ports, trusted_checkpoint=trusted_checkpoint
    )
    shared = views.shared
    pending = views.code_freshness == Freshness.STALE or (
        shared is not None and shared.status != ContinuityStatus.LOCAL_ONLY
    )
    publication = (
        PublicationOutcome.PENDING if pending else PublicationOutcome.NOT_APPLICABLE
    )
    if views.code_freshness in (Freshness.UNKNOWN, Freshness.FENCED):
        return PolicyPreflight(
            views,
            None,
            LocalOutcome.INTEGRITY_ERROR,
            publication,
            views.code_reason or "No independently admitted committed policy.",
        )
    try:
        pinned = policy(anchor, views)
    except PolicyUnavailable as error:
        return PolicyPreflight(
            views, None, LocalOutcome.INTEGRITY_ERROR, publication, str(error)
        )
    refusal = None
    if pinned.writes_fenced:
        refusal = "Committed policy routing differs from the installation anchor."
    elif shared is not None and shared.status not in (
        ContinuityStatus.LOCAL_ONLY,
        ContinuityStatus.VERIFIED,
        ContinuityStatus.STALE,
        ContinuityStatus.UNKNOWN,
    ):
        refusal = (
            shared.reason or "Shared planning continuity could not be established."
        )
    return PolicyPreflight(
        views,
        pinned,
        LocalOutcome.INTEGRITY_ERROR if refusal else LocalOutcome.COMPLETED,
        publication,
        refusal,
    )


def prepare_mutation(
    anchor: Installation,
    operation: Operation,
    expected: Snapshot,
    *,
    ports: ServicePorts | None = None,
) -> PolicyPreflight:
    """Refresh and pin before dispatching into the clone's operation guard."""
    result = preflight_policy(anchor, ports=ports)
    result = replace(result, expected=expected, read_set=operation.change.read_set)
    if result.outcome != LocalOutcome.COMPLETED:
        return result
    if result.views.planning.observed_commit != expected.revision:
        return replace(
            result,
            outcome=LocalOutcome.CONFLICT,
            reason="The planning view moved. Rebuild the operation from a new snapshot.",
        )
    if result.policy is None or result.policy.source.digest != operation.policy_digest:
        return replace(
            result,
            outcome=LocalOutcome.CONFLICT,
            reason="The committed policy changed. Rebuild the operation and its guards.",
        )
    return result


def mutate(
    anchor: Installation,
    operation: Operation,
    expected: Snapshot,
    *,
    ports: ServicePorts | None = None,
    categories: OperationCategories | None = None,
) -> OperationResult:
    """Apply a normal local mutation using the same preflight as explicit refresh."""
    from aitm_core.models.operations import Operation
    from aitm_core.store.backend import OperationResult

    prepared = prepare_mutation(anchor, operation, expected, ports=ports)
    if prepared.outcome != LocalOutcome.COMPLETED:
        return OperationResult(
            CommandResult(
                operation_id=operation.operation_id,
                local=prepared.outcome,
                publication=prepared.publication,
                evidence=prepared.evidence,
            ),
            expected,
            prepared.reason,
        )
    if isinstance(operation, Operation):
        from aitm_core.ext.ownership import ExtensionWriteAuthorizer
        from aitm_core.ext.registry import load_extensions

        services = ports if ports is not None else ServicePorts()
        assert prepared.policy is not None
        try:
            registry = load_extensions(prepared.policy, services.extension_declarations)
            core = services.write_authorization
            authorizer = ExtensionWriteAuthorizer(
                registry, core=core if callable(core) else None
            )
        except ValueError as error:
            reason = str(error)
            return OperationResult(
                CommandResult(
                    operation_id=operation.operation_id,
                    local=LocalOutcome.REFUSED,
                    publication=prepared.publication,
                    evidence=(*prepared.evidence, reason),
                ),
                expected,
                reason,
            )
        ports = replace(services, write_authorization=authorizer)

    admitted = prepared.views.local
    ref = anchor.policy_ref(admitted)
    if ref is None or admitted.observed_commit is None:
        raise UnavailablePort("policy_refresh")
    store = anchor.store.model_copy(update={"code_default_ref": ref})
    target = backend(
        anchor.repository,
        store,
        ports=ports,
        categories=categories,
        code_pin=(ref, admitted.observed_commit),
    )
    result = target.transact(operation, expected)
    command = result.command
    publication = (
        prepared.publication
        if command.local == LocalOutcome.COMPLETED
        and command.publication == PublicationOutcome.NOT_APPLICABLE
        else command.publication
    )
    return replace(
        result,
        command=command.model_copy(
            update={
                "publication": publication,
                "evidence": (*command.evidence, *prepared.evidence),
            }
        ),
    )


def _unique_coordinates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    values = dict(pairs)
    if len(values) != len(pairs):
        raise ValueError("Installation coordinates contain a duplicate field.")
    return values


def load_installation(
    repository: Repository, store: StoreAnchor, descriptor: Path | None = None
) -> Installation:
    """Load C07 coordinates independently of the current story worktree."""
    from aitm_core.models.config import BacklogIssuer, LegacyRoot
    from aitm_core.store.installation import Installation

    if descriptor is None:
        common = repository._git(
            "rev-parse", "--path-format=absolute", "--git-common-dir"
        ).removesuffix(b"\n")
        descriptor = Path(fsdecode(common)) / "aitm" / "installation.json"
    settings = loads(descriptor.read_bytes(), object_pairs_hook=_unique_coordinates)
    if not isinstance(settings, dict):
        raise ValueError("Installation coordinates require a JSON object.")
    required = {"code_repository", "planning_repository", "bootstrap_source"}
    optional = {"code_remote", "code_remote_ref"}
    if (
        not required.issubset(settings)
        or settings.keys() - required - optional - {"issuer", "legacy_root"}
        or any(
            not isinstance(settings[key], str) or not settings[key].strip()
            for key in required
        )
        or any(
            settings.get(key) is not None
            and (not isinstance(settings[key], str) or not settings[key].strip())
            for key in optional
        )
    ):
        raise ValueError("Invalid anchored installation coordinates.")
    issuer = BacklogIssuer.model_validate(settings.pop("issuer", None))
    legacy = settings.pop("legacy_root", None)
    return Installation(
        repository=repository,
        store=store,
        issuer=issuer,
        legacy_root=LegacyRoot.model_validate(legacy) if legacy is not None else None,
        **settings,
    )
