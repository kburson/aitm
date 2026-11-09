import argparse
import json
import os
import sqlite3
import sys
from importlib.metadata import version
from pathlib import Path
from uuid import UUID, uuid4

from .export import export_as_of
from .ledger import (
    STORE_NAME,
    ConflictError,
    Ledger,
    LedgerError,
    _connection,
    _database_path,
    _pin_directory,
    _project_path,
    _state_files,
)
from .pricing import load_rate_card
from .scopes import MAX_COMMAND_BYTES, enqueue_command, session_reference
from .types import (
    DevelopmentBinding,
    DraftAlias,
    InboxCommand,
    ItemKey,
    ItemKind,
    ItemParent,
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


def open_project(root: Path) -> Ledger:
    """Discover an existing ledger's UUID and validate it without the writer lease."""
    root = _project_path(root)
    try:
        with (
            _pin_directory(root) as project,
            _pin_directory(root / STORE_NAME) as store,
        ):
            files = _state_files(root)
            with _connection(_database_path(root), write=False) as conn:
                row = conn.execute(
                    "SELECT project_id FROM identity WHERE singleton = 1"
                ).fetchone()
            if row is None or type(row[0]) is not str:
                raise LedgerError("Invalid private project identity")
            project_id = UUID(row[0])
            if str(project_id) != row[0]:
                raise LedgerError("Invalid private project identity")
            ledger = Ledger.open(root, project_id)
            project.check()
            store.check()
            if _state_files(root) != files:
                raise LedgerError("Private project files changed")
            return ledger
    except (OSError, ValueError, sqlite3.Error):
        raise LedgerError("Invalid private project identity") from None


def _item_key(text: str) -> ItemKey:
    if text.isascii() and text.isdecimal():
        return ItemKey(ItemKind.ISSUE, int(text))
    return ItemKey(ItemKind.DRAFT, UUID(text))


def _item_command(args: argparse.Namespace) -> InboxCommand:
    project_id = open_project(args.project).identity.project_id
    command_id = uuid4()
    if args.item_action == "alias":
        payload = DraftAlias(
            command_id,
            project_id,
            ItemKey(ItemKind.DRAFT, UUID(args.draft)),
            _item_key(args.issue),
        )
    else:
        payload = ItemParent(
            command_id, project_id, _item_key(args.child), _item_key(args.epic)
        )
    return InboxCommand(command_id, project_id, payload)


def _scope_command(args: argparse.Namespace) -> InboxCommand:
    with args.input.open("rb") as source:
        data = source.read(MAX_COMMAND_BYTES + 1)
    if len(data) > MAX_COMMAND_BYTES:
        raise ValueError("Command file is too large")
    payload = args.decode(data)
    if isinstance(payload, ScopeCorrection):
        command = InboxCommand(payload.correction_id, payload.project_id, payload)
    else:
        marker = payload.marker if isinstance(payload, DevelopmentBinding) else payload
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

    return command


def _queue_command(args: argparse.Namespace) -> int:
    try:
        command = args.command_factory(args)
        receipt = enqueue_command(args.project, command)
    except ConflictError:
        print("aitm-usage: inbox command conflict", file=sys.stderr)
        return 1
    except (LedgerError, OSError, ValueError, sqlite3.Error):
        print("aitm-usage: invalid private inbox command or project", file=sys.stderr)
        return 1
    status = "queued" if receipt is None else receipt.disposition.value
    if args.json:
        print(json.dumps({"command_id": str(command.command_id), "status": status}))
    else:
        print(f"{command.command_id} {status}")
    return 0


def _export_command(args: argparse.Namespace) -> int:
    try:
        rate_id = args.rate_card
        parts = rate_id.split(":")
        card = load_rate_card(parts[1] if len(parts) == 4 else rate_id)
        if rate_id not in (card.version, card.basis.identifier):
            raise ValueError("Invalid rate card identifier")
        view = open_project(args.project).as_of(args.as_of)
        receipt = export_as_of(view, card, args.output)
    except (LedgerError, OSError, ValueError, sqlite3.Error):
        print("aitm-usage: unable to export the requested snapshot", file=sys.stderr)
        return 1
    if args.json:
        print(
            json.dumps(
                {
                    "schema": receipt.schema,
                    "project_id": str(receipt.project_id),
                    "cutoff": receipt.cutoff,
                    "rate_basis": receipt.rate_basis,
                    "sha256": receipt.sha256,
                    "row_count": receipt.row_count,
                },
                sort_keys=True,
            )
        )
    else:
        print(f"{receipt.project_id} {receipt.cutoff} {receipt.sha256}")
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
        command.set_defaults(
            handler=_queue_command, command_factory=_scope_command, decode=decode
        )
    item = groups.add_parser("item").add_subparsers(required=True, dest="item_action")
    for name, options in (
        ("alias", ("--draft", "--issue")),
        ("parent", ("--child", "--epic")),
    ):
        command = item.add_parser(name)
        for option in options:
            command.add_argument(option, required=True)
        command.add_argument("--json", action="store_true")
        command.set_defaults(handler=_queue_command, command_factory=_item_command)
    export = groups.add_parser("export", help="Export one fixed ledger sequence")
    export.add_argument("--as-of", type=int, required=True, metavar="SEQUENCE")
    export.add_argument("--rate-card", required=True, metavar="ID")
    export.add_argument("--output", type=Path, required=True, metavar="DIRECTORY")
    export.add_argument("--json", action="store_true")
    export.set_defaults(handler=_export_command)
    args = parser.parse_args()
    if not hasattr(args, "handler"):
        parser.print_help()
        return 0
    if args.project is None:
        parser.error("--project is required")
    return args.handler(args)
