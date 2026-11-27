"""Wiring slots for optional implementations of mandatory Core capabilities."""

from dataclasses import dataclass
from typing import Literal

ServicePortName = Literal[
    "policy_resolution",
    "policy_refresh",
    "validation_gate",
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
