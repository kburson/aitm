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
    from aitm_core.store.validation import (
        DiagnosedHistory,
        ForwardRepairVerifier,
        ValidationReport,
    )

ServicePortName = Literal[
    "policy_resolution",
    "policy_refresh",
    "validation_gate",
    "forward_repair_verifier",
    "write_authorization",
    "attempt_preflight",
    "init_hooks",
    "init_doctor",
    "init_provider",
    "init_git_host",
    "workflow_cutover",
    "action_retry",
    "entity_sync",
    "lane_selection",
    "kind_requirements",
    "planning_capacity",
    "implementation_binding",
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
    forward_repair_verifier: object | None = "default"
    write_authorization: object | None = None
    attempt_preflight: object | None = None
    init_hooks: object | None = None
    init_doctor: object | None = None
    init_provider: object | None = None
    init_git_host: object | None = None
    workflow_cutover: object | None = None
    action_retry: object | None = None
    lane_selection: object | None = None
    kind_requirements: object | None = None
    planning_capacity: object | None = None
    implementation_binding: object | None = None
    aggregate_evidence: object | None = None
    story_exit_guards: object | None = None
    extension_declarations: tuple[Extension, ...] = ()
    entity_sync: object | None = None

    def require(self, port: ServicePortName) -> object:
        implementation = getattr(self, port)
        if implementation is None:
            raise UnavailablePort(port)
        return implementation

    def workflow_guard_ports(self, source):
        """Compose the installed kind policy with any qualified provider ports."""
        from aitm_core.machine.kinds import KIND_EXIT_RULES, evaluate_kind_guard

        def kind(call):
            return evaluate_kind_guard(
                call,
                source=source,
                aggregate=self.aggregate_evidence
                if callable(self.aggregate_evidence)
                else None,
            )

        def exit_guard(call):
            if (
                call.story.kind in {"epic", "spike"}
                and call.identifier in KIND_EXIT_RULES
            ):
                return kind(call)
            if callable(self.story_exit_guards):
                return self.story_exit_guards(call)
            return kind(call)

        return self.kind_requirements if callable(
            self.kind_requirements
        ) else kind, exit_guard


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
                'ForwardRepairVerifier | Literal["default"] | None',
                services.forward_repair_verifier,
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
    from aitm_core.store.repair import repair_verifier

    verifier = ports.forward_repair_verifier if ports is not None else "default"
    if verifier == "default":

        def selected_verifier(
            store: StoreAnchor, diagnosis: DiagnosedHistory, candidate: Snapshot
        ) -> ValidationReport:
            return repair_verifier(anchor.repository)(store, diagnosis, candidate)

        verifier = selected_verifier
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
    from aitm_core.models.operations import Operation

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
    if isinstance(operation, Operation) and operation.intent.kind == "core.graduated":
        from aitm_core.graduation import GraduatedRecord

        record = GraduatedRecord.model_validate_json(operation.intent.payload)
        if record.workflow_digest != result.policy.workflow.digest:
            return replace(
                result,
                outcome=LocalOutcome.CONFLICT,
                reason="The committed graduation workflow changed. Rebuild from the current profile.",
            )
    if isinstance(operation, Operation) and operation.intent.kind in {
        "state.transition",
        "state.split",
        "state.design-rework",
        "state.non-delivery",
    }:
        from aitm_core.models.lifecycle import StateChange

        change = StateChange.model_validate_json(operation.intent.payload)
        if (
            change.to_state.revision != result.policy.workflow.digest
            or change.mode != result.policy.config.enforcement.mode
        ):
            return replace(
                result,
                outcome=LocalOutcome.CONFLICT,
                reason="The committed workflow or guard mode changed. Rebuild the transition.",
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
    return CommandService(anchor, target, ports, categories).execute(
        operation, expected, prepared
    )


@dataclass(frozen=True, slots=True)
class CommandService:
    installation: Installation
    target: GitBackend
    ports: ServicePorts | None = None
    categories: OperationCategories | None = None

    def execute(
        self, operation: Operation, expected: Snapshot, prepared: PolicyPreflight
    ) -> OperationResult:
        from aitm_core.models.operations import Operation
        from aitm_core.store.backend import OperationResult
        from aitm_core.store.objects import GitCommandError
        from aitm_core.store.publication import PublicationStatus, Publisher

        publisher = None
        if (
            isinstance(operation, Operation)
            and self.installation.store.planning_remote is not None
        ):
            publisher = Publisher(self.installation, self.ports, self.categories)
            try:
                publisher.retain_request(operation)
            except (GitCommandError, OSError, ValueError) as error:
                reason = f"Could not retain the publication request: {error}"
                return OperationResult(
                    CommandResult(
                        operation_id=operation.operation_id,
                        local=LocalOutcome.UNAVAILABLE,
                        publication=prepared.publication,
                        evidence=(*prepared.evidence, reason),
                    ),
                    expected,
                    reason,
                )

        result = self.target.transact(operation, expected)
        command = result.command
        publication = command.publication
        evidence = (*command.evidence, *prepared.evidence)
        recovery = command.recovery
        if command.local == LocalOutcome.COMPLETED and publisher is not None:
            published = publisher.publish(operation.operation_id)
            if published.status == PublicationStatus.PUBLISHED:
                publication = PublicationOutcome.VERIFIED
            elif published.status != PublicationStatus.NOT_APPLICABLE:
                publication = PublicationOutcome.PENDING
                evidence += (f"Publication {published.status}: {published.reason}",)
                recovery = published.recovery_ref or recovery
            elif publication == PublicationOutcome.NOT_APPLICABLE:
                publication = prepared.publication
        elif (
            command.local == LocalOutcome.COMPLETED
            and publication == PublicationOutcome.NOT_APPLICABLE
        ):
            publication = prepared.publication
        return replace(
            result,
            command=command.model_copy(
                update={
                    "publication": publication,
                    "evidence": evidence,
                    "recovery": recovery,
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
        or settings.keys()
        - required
        - optional
        - {"issuer", "legacy_root", "anchor", "accepted_revision"}
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
    from aitm_core.models.common import StoreAnchor

    retained_anchor = settings.pop("anchor", None)
    accepted_revision = settings.pop("accepted_revision", None)
    if (
        retained_anchor is not None
        and StoreAnchor.model_validate(retained_anchor) != store
    ):
        raise ValueError(
            "The supplied store anchor differs from the installed authority."
        )
    if accepted_revision is not None:
        repository._oid(accepted_revision)
    issuer = BacklogIssuer.model_validate(settings.pop("issuer", None))
    legacy = settings.pop("legacy_root", None)
    return Installation(
        repository=repository,
        store=store,
        issuer=issuer,
        legacy_root=LegacyRoot.model_validate(legacy) if legacy is not None else None,
        **settings,
    )


def stage_shared_graduation(
    anchor: Installation,
    operation: Operation,
    expected: Snapshot,
    *,
    ports: ServicePorts,
) -> OperationResult:
    """Validate a complete candidate and send it without advancing the local planning ref."""
    from aitm_core.ext.ownership import ExtensionWriteAuthorizer
    from aitm_core.ext.registry import load_extensions
    from aitm_core.store.backend import OperationResult, evaluate_operation
    from aitm_core.store.continuity import ContinuityStatus
    from aitm_core.store.fetch import Freshness
    from aitm_core.store.git_backend import ValidationRejected, _record_path
    from aitm_core.store.objects import GitCommandError
    from aitm_core.store.publication import Publisher

    prepared = prepare_mutation(anchor, operation, expected, ports=ports)
    repo = anchor.repository

    def result(
        local: LocalOutcome, message: str, recovery: str | None = None
    ) -> OperationResult:
        return OperationResult(
            CommandResult(
                operation_id=operation.operation_id,
                local=local,
                publication=PublicationOutcome.PENDING,
                evidence=(message,),
                recovery=recovery,
            ),
            expected,
            message,
        )

    shared = prepared.views.shared
    code = prepared.views.local
    code_ref = anchor.policy_ref(code)
    if (
        operation.intent.kind != "core.graduated"
        or anchor.store.planning_remote is None
        or prepared.outcome != LocalOutcome.COMPLETED
        or prepared.policy is None
        or shared is None
        or shared.status != ContinuityStatus.VERIFIED
        or shared.valid_tip != expected.revision
        or prepared.views.code_freshness not in {Freshness.FRESH, Freshness.LOCAL_ONLY}
        or code_ref is None
        or code.observed_commit is None
    ):
        return result(
            LocalOutcome.CONFLICT,
            prepared.reason or "The verified shared graduation frontier moved.",
        )

    recovery = None
    try:
        registry = load_extensions(prepared.policy, ports.extension_declarations)
        authorize = ports.write_authorization
        services = replace(
            ports,
            write_authorization=ExtensionWriteAuthorizer(
                registry,
                core=authorize if callable(authorize) else None,
            ),
        )
        store = anchor.store.model_copy(update={"code_default_ref": code_ref})
        target = backend(
            repo, store, ports=services, code_pin=(code_ref, code.observed_commit)
        )
        publisher = Publisher(anchor, services)
        with target._gate(repo, repo.ref) as validate:
            current = target.snapshot()
            if current != expected:
                return result(
                    LocalOutcome.CONFLICT,
                    "The local planning view moved before staging.",
                )
            validate(current, None)
            paths = tuple(item.path for item in operation.change.read_set)
            pinned = repo.read_blobs(current.tree, paths)
            evaluation = evaluate_operation(
                operation, current, pinned, ports=services, categories={}
            )
            if evaluation.outcome != LocalOutcome.COMPLETED:
                return result(
                    evaluation.outcome,
                    evaluation.reason or "Graduation candidate was refused.",
                )
            digest = operation.request_digest
            record = target._record(operation, digest, current, evaluation)
            staged = repo.create_commit(
                current,
                {
                    **evaluation.writes,
                    _record_path(
                        operation.operation_id
                    ): record.model_dump_json().encode(),
                },
                operation.operation_id,
            )
            validate(current, staged)
            publisher.retain_request(operation)
            reference = publisher._recovery_ref(staged.revision)
            publisher._retain_ref(reference, staged.revision)
            recovery = reference
            publisher._push(staged.revision, current.revision)
    except ValidationRejected as error:
        return result(LocalOutcome.CONFLICT, str(error), recovery)
    except (GitCommandError, OSError, ValueError) as error:
        return result(LocalOutcome.UNAVAILABLE, str(error), recovery)
    return result(
        LocalOutcome.COMPLETED,
        "The candidate remains provisional until shared readback.",
        recovery,
    )


def expansion_graduation(installation, owner, ports: ServicePorts | None = None):
    """Compose the production expansion finalizer with the selected Core ports."""
    from functools import partial

    from aitm_core.graduation import FinalizerRegistry, GraduationService
    from aitm_core.rules.expansion import EXPANSION_FINALIZER, build_expansion_related

    registry = FinalizerRegistry().register_candidate_finalizer(
        EXPANSION_FINALIZER,
        1,
        partial(build_expansion_related, installation.repository),
    )
    return GraduationService(
        installation,
        owner,
        registry=registry,
        ports=ports if ports is not None else ServicePorts(),
    )
