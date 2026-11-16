"""Dormant producer entry for an authenticated native Grok scope marker."""

# The scope hook binds the live prompt to its staged receipt.

import ctypes
import json
import os
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from .. import install
from ..monitor_registry import default_monitor_root
from ..scope_admission import _grok_image_ref, _grok_process_ref, bind_grok_prompt
from ..types import SourceRef, _unique_fields

_MAX_HOOK_BYTES = 65536


def _process_hop(pid: int) -> tuple[int, datetime] | None:
    info = install._BSDProcessInfo()
    size = ctypes.sizeof(info)
    if (
        install._libproc().proc_pidinfo(pid, 3, 0, ctypes.byref(info), size) != size
        or info.pid != pid
        or info.pid <= 1
        or info.uid != os.geteuid()
        or info.status == 5
        or not info.start_seconds
        or info.start_microseconds >= 1_000_000
    ):
        return None
    return info.parent_pid, datetime.fromtimestamp(info.start_seconds, UTC).replace(
        microsecond=info.start_microseconds
    )


def _has_process_ancestor(
    evidence,
    process: SourceRef,
    image: SourceRef,
    *,
    read_hop: Callable[[int], tuple[int, datetime] | None] = _process_hop,
) -> bool:
    def stable_hop(pid):
        before = read_hop(pid)
        return before if before is not None and read_hop(pid) == before else None

    caller = stable_hop(os.getpid())
    if caller is None or caller[0] != os.getppid():
        return False
    pid, child_started = caller
    for _ in range(8):
        if pid <= 1:
            return False
        hop = stable_hop(pid)
        if hop is None:
            return False
        parent, started = hop
        if started > child_started or parent == pid:
            return False
        if _grok_process_ref(evidence, pid, started) == process:
            observed = install._process_identity(pid)
            return (
                observed is not None
                and observed.started == started
                and _grok_image_ref(evidence, observed.executable) == image
                and stable_hop(pid) == hop
            )
        pid, child_started = parent, started
    return False


def main() -> int:
    """Use the exact staged marker, without sending hook stdout to the model."""
    try:
        if len(sys.argv) != 2:
            return 0
        selector = SourceRef(sys.argv[1])
        data = sys.stdin.buffer.read(_MAX_HOOK_BYTES + 1)
        if len(data) > _MAX_HOOK_BYTES:
            return 0
        row = json.loads(data, object_pairs_hook=_unique_fields)
        if type(row) is not dict:
            return 0
        event, session = row.get("hookEventName"), row.get("sessionId")
        prompt, checkout = row.get("promptId"), row.get("workspaceRoot")
        if (
            event != "user_prompt_submit"
            or os.environ.get("GROK_HOOK_EVENT") != event
            or type(session) is not str
            or os.environ.get("GROK_SESSION_ID") != session
            or type(prompt) is not str
            or type(checkout) is not str
        ):
            return 0
        bind_grok_prompt(
            default_monitor_root(), selector, session, prompt, Path(checkout)
        )
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
