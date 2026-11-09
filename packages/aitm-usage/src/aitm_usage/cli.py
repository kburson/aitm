import argparse
import json
import os
import sys
from importlib.metadata import version
from pathlib import Path
from uuid import UUID

from .ledger import ConflictError, Ledger, LedgerError
from .scopes import MAX_COMMAND_BYTES, enqueue_command, session_reference
from .types import (
    DevelopmentBinding,
    InboxCommand,
    Provider,
    ScopeCorrection,
    decode_binding,
    decode_correction,
    decode_marker,
)


def default_project_root(project_id: UUID) -> Path:
    return (
        Path.home() / "Library" / "Application Support" / "aitm-usage" / str(project_id)
    )


def _queue_command(args: argparse.Namespace) -> int:
    try:
        with args.input.open("rb") as source:
            data = source.read(MAX_COMMAND_BYTES + 1)
        if len(data) > MAX_COMMAND_BYTES:
            raise ValueError("Command file is too large")
        payload = args.decode(data)
        if isinstance(payload, ScopeCorrection):
            command = InboxCommand(payload.correction_id, payload.project_id, payload)
        else:
            marker = (
                payload.marker if isinstance(payload, DevelopmentBinding) else payload
            )
            ledger = Ledger.open(args.project, marker.project_id)
            if marker.provider is Provider.CODEX:
                if args.session_id is not None:
                    raise ValueError("Codex scope requires the invoking thread")
                raw_session = os.environ.get("CODEX_THREAD_ID")
            else:
                raw_session = args.session_id
            if (
                session_reference(ledger, marker.provider, raw_session)
                != marker.session_ref
            ):
                raise ValueError("Invoking provider session does not match")
            command = InboxCommand(marker.marker_id, marker.project_id, payload)
        receipt = enqueue_command(args.project, command)
    except ConflictError:
        print("aitm-usage: inbox command conflict", file=sys.stderr)
        return 1
    except (LedgerError, OSError, ValueError):
        print("aitm-usage: invalid private inbox command or project", file=sys.stderr)
        return 1
    status = "queued" if receipt is None else receipt.disposition.value
    if args.json:
        print(json.dumps({"command_id": str(command.command_id), "status": status}))
    else:
        print(f"{command.command_id} {status}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="aitm-usage", description="Private local AITM usage"
    )
    parser.add_argument("--project", type=Path, metavar="STATE_DIR")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {version('aitm-usage')}"
    )
    groups = parser.add_subparsers()
    scope = groups.add_parser("scope").add_subparsers(required=True)
    development = groups.add_parser("development").add_subparsers(required=True)
    for group, name, option, decode in (
        (scope, "mark", "--marker", decode_marker),
        (scope, "correct", "--correction", decode_correction),
        (development, "bind", "--binding", decode_binding),
    ):
        command = group.add_parser(name)
        command.add_argument(option, type=Path, dest="input", required=True)
        command.add_argument("--json", action="store_true")
        if name != "correct":
            command.add_argument(
                "--session-id", help="Reserved or verified Claude session UUID"
            )
        command.set_defaults(handler=_queue_command, decode=decode)
    args = parser.parse_args()
    if not hasattr(args, "handler"):
        parser.print_help()
        return 0
    if args.project is None:
        parser.error("--project is required for private inbox commands")
    return args.handler(args)
