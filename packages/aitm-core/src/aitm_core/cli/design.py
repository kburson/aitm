"""Installed acceptance for a story's current design."""

from aitm_core.cli.review_import import accept
from aitm_core.models.common import CommandResult


def handle(_route: tuple[str, ...], arguments: tuple[str, ...]) -> CommandResult:
    return accept("design", arguments)
