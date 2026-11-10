"""Canonical monitor scope command and receipt shared by native readers."""

import re
import shlex
from pathlib import PurePosixPath
from uuid import UUID

_QUEUED_RECEIPT = re.compile(
    r'\{"command_id": "([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-'
    r'[0-9a-f]{4}-[0-9a-f]{12})", "status": "queued"\}\n'
)


def is_monitor_scope(command: str, parts: list[str]) -> bool:
    if (
        len(parts) != 7
        or parts[:3] != ["aitm-usage", "monitor", "scope"]
        or parts[3] not in {"mark", "handoff", "dispose"}
        or parts[4] != "--request"
        or parts[6] != "--json"
        or command != shlex.join(parts)
    ):
        return False
    request = parts[5]
    path = PurePosixPath(request)
    return (
        path.anchor == "/"
        and bool(path.name)
        and ".." not in path.parts
        and "\0" not in request
        and str(path) == request
    )


def queued_monitor_scope_id(stdout: str) -> UUID | None:
    receipt = _QUEUED_RECEIPT.fullmatch(stdout)
    return UUID(receipt[1]) if receipt is not None else None
