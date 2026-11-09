import argparse
import json
import os
import sqlite3
import sys
from dataclasses import asdict
from importlib.metadata import version
from pathlib import Path
from uuid import UUID, uuid4

from .export import export_as_of
from .ledger import (
    STORE_NAME,
    ConflictError,
    Ledger,
    LedgerError,
    WriterActive,
    _connection,
    _database_path,
    _pin_directory,
    _project_path,
    _state_files,
)
from .pricing import load_rate_card
from .rollup import rollup
from .scopes import MAX_COMMAND_BYTES, enqueue_command, session_reference
from .service import (
    collect_once,
    load_registration,
    register_project,
    remember_claude_session,
    run_service,
    stage_source_anchor,
    status_report,
    verify_source_anchor_receipt,
)
from .types import (
    DevelopmentBinding,
    DraftAlias,
    InboxCommand,
    ItemKey,
    ItemKind,
    ItemParent,
    MarkerDisposition,
    Provider,
    ScopeCorrection,
    SourceAnchorCommand,
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
        if marker.provider is Provider.CLAUDE:
            ledger.validate_command(command)
            remember_claude_session(ledger, marker.session_ref)

    return command


def _queue_command(args: argparse.Namespace) -> int:
    try:
        command = args.command_factory(args)
        receipt = enqueue_command(args.project, command)
        if (
            receipt is not None
            and receipt.disposition is MarkerDisposition.ACCEPTED
            and isinstance(command.payload, SourceAnchorCommand)
        ):
            verify_source_anchor_receipt(
                Ledger.open(args.project, command.project_id), receipt
            )
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


def _print_result(payload: dict, *, as_json: bool) -> None:
    print(json.dumps(payload, sort_keys=True, indent=None if as_json else 2))


def _register_command(args: argparse.Namespace) -> int:
    try:
        registration = register_project(args.project, args.config)
    except WriterActive:
        return _collector_failure(args, "writer-active")
    except (LedgerError, OSError, ValueError, sqlite3.Error):
        return _collector_failure(args, "registration-failed")
    _print_result(
        {
            "project_id": str(registration.project_id),
            "cutoff": registration.cutoff.isoformat(),
        },
        as_json=args.json,
    )
    return 0


def _anchor_command(args: argparse.Namespace) -> InboxCommand:
    return stage_source_anchor(open_project(args.project), args.anchor)


def _collector_failure(args: argparse.Namespace, reason: str) -> int:
    if getattr(args, "json", False):
        _print_result({"status": reason}, as_json=True)
    else:
        print(f"aitm-usage: {reason}", file=sys.stderr)
    return 1


def _collect_command(args: argparse.Namespace) -> int:
    try:
        ledger = open_project(args.project)
        registration = load_registration(ledger)
        if args.continuous:
            return run_service(registration)
        report = collect_once(registration, ledger)
    except WriterActive:
        return _collector_failure(args, "writer-active")
    except (LedgerError, OSError, ValueError, sqlite3.Error):
        return _collector_failure(args, "collection-failed")
    _print_result(asdict(report), as_json=args.json)
    return 0


def _status_command(args: argparse.Namespace) -> int:
    try:
        ledger = open_project(args.project)
    except (LedgerError, OSError, ValueError, sqlite3.Error):
        ledger = None
    _print_result(status_report(args.project.absolute(), ledger), as_json=args.json)
    return 0


def _rollup_command(args: argparse.Namespace) -> int:
    try:
        ledger = open_project(args.project)
        view = ledger.as_of()
        item = (
            ItemKey(ItemKind.PROJECT)
            if args.item == "project"
            else _item_key(args.item)
        )
        totals = rollup(item, view)
    except (LedgerError, OSError, ValueError, sqlite3.Error):
        return _collector_failure(args, "rollup-failed")
    result = {
        "item": {
            "kind": totals.root.kind.value,
            "identifier": str(totals.root.identifier)
            if totals.root.identifier is not None
            else None,
        },
        "sequence": view.sequence,
    }
    for label in ("direct", "inclusive", "unattributed"):
        summary = asdict(getattr(totals, label))
        summary["known_usd"] = format(summary["known_usd"], "f")
        result[label] = summary
    _print_result(result, as_json=args.json)
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
    register = groups.add_parser(
        "register", help="Accept explicit private project configuration"
    )
    register.add_argument("--config", type=Path, required=True)
    register.add_argument("--json", action="store_true")
    register.set_defaults(handler=_register_command)
    source = groups.add_parser("source").add_subparsers(required=True)
    add_anchor = source.add_parser("add-anchor")
    add_anchor.add_argument("--anchor", type=Path, required=True)
    add_anchor.add_argument("--json", action="store_true")
    add_anchor.set_defaults(handler=_queue_command, command_factory=_anchor_command)
    collect = groups.add_parser("collect-once")
    collect.add_argument("--json", action="store_true")
    collect.set_defaults(handler=_collect_command, continuous=False)
    service = groups.add_parser("service").add_subparsers(required=True)
    service.add_parser("run").set_defaults(handler=_collect_command, continuous=True)
    status = groups.add_parser("status")
    status.add_argument("--json", action="store_true")
    status.set_defaults(handler=_status_command)
    rollup_parser = groups.add_parser("rollup")
    rollup_parser.add_argument("--item", required=True)
    rollup_parser.add_argument("--json", action="store_true")
    rollup_parser.set_defaults(handler=_rollup_command)
    args = parser.parse_args()
    if not hasattr(args, "handler"):
        parser.print_help()
        return 0
    if args.project is None:
        parser.error("--project is required")
    return args.handler(args)
