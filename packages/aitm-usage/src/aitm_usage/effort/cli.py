"""Portable effort reporting and caller-owned session capture."""

import argparse
import sqlite3
import sys
from collections.abc import Sequence
from pathlib import Path
from uuid import UUID

from .export import read_legacy, render_export
from .pinned_cli import add_pinned_commands, run_pinned_command
from .pinned_report import ReportUnavailable
from .report import build_report, render_text
from .rollup import RollupTarget
from .session_cli import add_session_commands, run_session_command
from .store import EffortStore


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aitm-effort", description=__doc__)
    parser.add_argument("--database", type=Path)
    parser.add_argument("--project", required=True, type=UUID)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("report", "export"):
        options = commands.add_parser(command)
        target = options.add_mutually_exclusive_group(required=True)
        target.add_argument("--story", type=int)
        target.add_argument("--epic", type=int)
        target.add_argument("--unattached", action="store_true")
        options.add_argument(
            "--legacy", type=Path, help="approved v1 usage export directory"
        )
        if command == "report":
            options.add_argument("--json", action="store_true")
    add_session_commands(commands)
    add_pinned_commands(commands)
    args = parser.parse_args(argv)
    if args.database is None and not args.command.startswith("story-report-"):
        parser.error("--database is required for this command")
    try:
        if args.command.startswith("story-report-"):
            return run_pinned_command(args)
        if args.command.startswith("session-"):
            return run_session_command(args)
        target = RollupTarget(args.project, epic=args.epic, story=args.story)
        snapshot = EffortStore(args.database, args.project, read_only=True).snapshot()
        legacy = None if args.legacy is None else read_legacy(args.legacy, args.project)
        report = build_report(snapshot, target, legacy=legacy)
    except ReportUnavailable as error:
        print(f"aitm-effort: unavailable: {error}", file=sys.stderr)
        return 3
    except (OSError, sqlite3.Error, ValueError) as error:
        print(f"aitm-effort: {error}", file=sys.stderr)
        return 2
    render = render_export if args.command == "export" or args.json else render_text
    sys.stdout.write(render(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
