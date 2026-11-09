"""Run the installed console wrapper with an isolated guard and crash barriers."""

import json
import os
import runpy
import sys
from pathlib import Path

from aitm_usage import ledger, scopes, service
from aitm_usage.types import MarkerDisposition, UsageObservation


def _pause(fd, event, **details):
    os.write(fd, (json.dumps({"event": event, **details}) + "\n").encode())
    if os.read(fd, 1) != b"\n":
        raise SystemExit("test parent closed the barrier")


def _instrument(fd, stop, target):
    proven_boundaries = []
    drain = service.drain_inbox

    def record_boundaries(writer, evidence):
        proven_boundaries[:] = [
            [entry.boundary.boundary_ref.value, entry.boundary.ordinal]
            for entry in evidence
            if entry.boundary.receipt_ref is not None
        ]
        return drain(writer, evidence)

    def between_scans(interval):
        assert interval == 15
        _pause(fd, "between-scans", pid=os.getpid(), boundaries=proven_boundaries)

    service.drain_inbox = record_boundaries

    # Replace only the service module's clock binding.
    class Clock:
        sleep = staticmethod(between_scans)

    service.time = Clock()

    append = ledger._append_checkpoint
    acknowledge = scopes._acknowledge

    def before_commit(conn, sequence, batch, *, revisions_changed):
        result = append(conn, sequence, batch, revisions_changed=revisions_changed)
        if any(
            isinstance(revision.record, UsageObservation)
            and revision.record.boundary.provider.value == target
            for revision in batch.revisions
        ):
            assert conn.in_transaction and revisions_changed and result
            (revisions,) = conn.execute(
                "SELECT COUNT(*) FROM revisions WHERE sequence = ?", (sequence,)
            ).fetchone()
            (checkpoints,) = conn.execute(
                "SELECT COUNT(*) FROM checkpoints WHERE sequence = ?", (sequence,)
            ).fetchone()
            assert revisions > 0 and checkpoints == 1
            _pause(
                fd,
                "before-commit",
                pid=os.getpid(),
                sequence=sequence,
                revisions=revisions,
                checkpoints=checkpoints,
            )
        return result

    def before_ack(inbox, directory, receipt, captured):
        if (
            str(receipt.command.command_id) == target
            and receipt.disposition is MarkerDisposition.ACCEPTED
        ):
            _pause(fd, "before-ack", pid=os.getpid())
        acknowledge(inbox, directory, receipt, captured)

    if stop == "before-commit":
        ledger._append_checkpoint = before_commit
    elif stop == "before-ack":
        scopes._acknowledge = before_ack
    else:
        assert stop == "between-scans"


control, console, fd, stop, target, *args = sys.argv[1:]
ledger._control_root = lambda: Path(control)
if fd != "-":
    _instrument(int(fd), stop, target)
sys.argv = [console, *args]
runpy.run_path(console, run_name="__main__")
