"""Command boundary for immutable story reports."""

import sys
from pathlib import Path

from .pinned_report import (
    build_pinned_report,
    canonical,
    reopen_pinned_report,
)


def add_pinned_commands(commands):
    build = commands.add_parser(
        "story-report-build", help="freeze exact story evidence"
    )
    build.add_argument("story", type=int)
    build.add_argument("--repository", required=True, type=Path)
    build.add_argument("--planning-commit", required=True)
    build.add_argument("--window-start", required=True)
    build.add_argument("--window-end", required=True)
    build.add_argument("--cutoff", required=True)
    build.add_argument("--rate-card", required=True, type=Path)
    build.add_argument("--rate-sha256", required=True)
    reopen = commands.add_parser("story-report-open", help="read a frozen story report")
    reopen.add_argument("story", type=int)
    reopen.add_argument("report_id")
    reopen.add_argument("--repository", required=True, type=Path)
    reopen.add_argument("--artifact-commit", required=True)
    reopen.add_argument("--format", required=True, choices=("json", "text"))


def run_pinned_command(args):
    if args.command == "story-report-build":
        from .pinned_amounts import load_comparison_rates
        from .pinned_inputs import read_inputs

        inputs = read_inputs(
            args.repository,
            args.project,
            args.story,
            args.planning_commit,
            {
                "window_start_utc": args.window_start,
                "window_end_utc": args.window_end,
                "cutoff_utc": args.cutoff,
            },
        )
        rates = load_comparison_rates(args.rate_card, args.rate_sha256)
        result = build_pinned_report(inputs, rates)
    else:
        envelope = reopen_pinned_report(
            args.repository,
            args.artifact_commit,
            args.project,
            args.story,
            args.report_id,
        )
        result = (
            envelope["text"].encode("ascii")
            if args.format == "text"
            else canonical(envelope["report"])
        )
    sys.stdout.buffer.write(result)
    return 0
