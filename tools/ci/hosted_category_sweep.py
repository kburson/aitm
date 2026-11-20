"""Assign hosted category jobs and reconcile receipts for one workflow attempt."""

import argparse
import json
import os
import signal
import subprocess
import sys
from collections import Counter
from pathlib import Path
from time import monotonic

from tools.ci import category_sweep as sweep

RUNNERS = {"linux": "ubuntu-24.04", "darwin": "macos-26"}


def allocate(linux, darwin):
    assignments = {}
    for node in sorted(linux.keys() | darwin.keys()):
        matches = [
            name for name, root in sweep.PROFILES.items() if node.startswith(root + "/")
        ]
        sweep.require(len(matches) == 1, f"unknown pytest profile for {node}")
        profile = matches[0]
        if node in linux and node in darwin:
            sweep.require(
                linux[node] == darwin[node], f"host categories disagree: {node}"
            )
        if profile == "native":
            sweep.require(node in darwin, f"native obligation needs Darwin: {node}")
        host = "darwin" if profile == "native" or node not in linux else "linux"
        category = (linux if host == "linux" else darwin)[node]
        assignments.setdefault((host, category), {}).setdefault(profile, []).append(
            node
        )
    return assignments


def slot_name(slot):
    return "-".join(slot)


def artifact_name(slot, context):
    return f"category-a{context['attempt']}-{slot_name(slot)}"


def slot_plan(source, slot, profiles, context):
    host, category = slot
    return {
        "schema": sweep.PLAN_SCHEMA,
        "source": source,
        "run": context,
        "host": host,
        "lanes": {category: profiles},
    }


def aggregate(assignments, source, context, artifacts):
    expected = {artifact_name(slot, context) for slot in assignments}
    actual = {path.name for path in artifacts.iterdir()}
    sweep.require(
        actual == expected,
        f"missing or unexpected artifacts: {sorted(expected ^ actual)}",
    )
    tested = 0
    children = Counter()
    receipts = {}
    for slot, profiles in assignments.items():
        artifact = artifacts / artifact_name(slot, context)
        plan = slot_plan(source, slot, profiles, context)
        receipt = sweep.verify(plan, artifact, require_children=False)
        timing = sweep.read(artifact / "timing.json")
        sweep.require(
            timing["plan_sha256"] == receipt["plan_sha256"],
            f"stale timing: {slot_name(slot)}",
        )
        receipts[slot_name(slot)] = receipt | {"timing": timing}
        tested += receipt["tested"]
        children.update(receipt["children"])
    sweep.require(
        children == sweep.REQUIRED_CHILDREN,
        "required child results are missing or duplicated",
    )
    return {
        "status": "pass",
        "source": source,
        "run": context,
        "tested": tested,
        "children": dict(children),
        "slots": receipts,
        "empty_categories": [
            category
            for category in sweep.CATEGORIES
            if not any(lane == category for _, lane in assignments)
        ],
    }


def github_context(source):
    environment = os.environ
    sweep.require(
        environment["GITHUB_REF"] == "refs/heads/trunk",
        "the hosted sweep requires trunk",
    )
    sweep.require(
        environment["GITHUB_SHA"] == source["commit"],
        "checkout differs from workflow SHA",
    )
    return {
        "repository": environment["GITHUB_REPOSITORY"],
        "workflow": environment["GITHUB_WORKFLOW_REF"],
        "run_id": environment["GITHUB_RUN_ID"],
        "attempt": environment["GITHUB_RUN_ATTEMPT"],
        "event": environment["GITHUB_EVENT_NAME"],
    }


def execute(repository, source, context, catalog, slot, profiles, output):
    host, category = slot
    sweep.require(
        sys.platform == host, f"required host: {host}, observed: {sys.platform}"
    )
    signal.signal(signal.SIGINT, signal.default_int_handler)
    setup_start = monotonic()
    plan = slot_plan(source, slot, profiles, context)
    output.mkdir(mode=0o700)
    with sweep.isolated_roots() as (scratch, short_scratch):
        collections = sweep.collect_profiles(repository, source, scratch, short_scratch)
        sweep.assign(collections, catalog)
        execution_start = monotonic()
        sweep.run_worker(
            repository, scratch, short_scratch, output / category, plan, category
        )
        finished = monotonic()
    timing = {
        "plan_sha256": sweep.digest(sweep.encoded(plan)),
        "collection_setup_seconds": round(execution_start - setup_start, 3),
        "worker_setup_and_execution_seconds": round(finished - execution_start, 3),
    }
    (output / "timing.json").write_bytes(sweep.encoded(timing))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("matrix")
    worker = commands.add_parser("execute")
    worker.add_argument("host", choices=RUNNERS)
    worker.add_argument("category", choices=sweep.CATEGORIES)
    worker.add_argument("output", type=Path)
    collect = commands.add_parser("aggregate")
    collect.add_argument("artifacts", type=Path)
    collect.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        repository = Path(sweep.git(Path.cwd(), "rev-parse", "--show-toplevel"))
        source = sweep.identity(repository)
        context = github_context(source)
        catalog = {
            host: sweep.read_catalog(repository / sweep.CATALOG, host)
            for host in RUNNERS
        }
        assignments = allocate(catalog["linux"], catalog["darwin"])
        if args.command == "matrix":
            print(
                json.dumps(
                    {
                        "include": [
                            {
                                "host": host,
                                "category": category,
                                "runner": RUNNERS[host],
                            }
                            for host, category in assignments
                        ]
                    },
                    separators=(",", ":"),
                )
            )
        elif args.command == "execute":
            slot = (args.host, args.category)
            output = args.output.resolve()
            sweep.require(
                not output.is_relative_to(repository),
                "output must be outside the source checkout",
            )
            execute(
                repository,
                source,
                context,
                catalog[args.host],
                slot,
                assignments[slot],
                output,
            )
        else:
            result = aggregate(assignments, source, context, args.artifacts)
            args.output.write_bytes(sweep.encoded(result))
            print(
                f"Verified {result['tested']} exact test IDs in {len(result['slots'])} hosted jobs."
            )
    except (
        ValueError,
        KeyError,
        TypeError,
        OSError,
        subprocess.CalledProcessError,
    ) as exc:
        print(f"Hosted category sweep failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
