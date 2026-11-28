"""Installed acceptance for a story's current plan."""

from uuid import uuid4

from aitm_core.cli.review_import import accept
from aitm_core.models.common import CommandResult, LocalOutcome


def handle(route: tuple[str, ...], arguments: tuple[str, ...]) -> CommandResult:
    if route == ("plan", "accept"):
        return accept("plan", arguments)
    return CommandResult(
        operation_id=uuid4().hex,
        local=LocalOutcome.UNAVAILABLE,
        evidence=(f"Core route is unavailable: {' '.join(route)}",),
    )
