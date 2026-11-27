"""Wiring slots for optional implementations of mandatory Core capabilities."""

from __future__ import annotations

from contextlib import AbstractContextManager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, cast

if TYPE_CHECKING:
    from aitm_core.models.common import StoreAnchor
    from aitm_core.store.backend import OperationCategories
    from aitm_core.store.gate import Gate
    from aitm_core.store.git_backend import GitBackend
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
) -> GitBackend:
    """Compose the Git backend with the mandatory anchored planning validator."""
    from aitm_core.store.gate import RefIdentity, RefMutationKind, ref_gate
    from aitm_core.store.git_backend import GitBackend
    from aitm_core.store.validation import validate_history

    services = ports if ports is not None else ServicePorts()

    def check(tip: str) -> ValidationReport:
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
