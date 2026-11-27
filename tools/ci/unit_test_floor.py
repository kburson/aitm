"""Enforce each package's unit-test floor from an independent full collection."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.ci import category_sweep as sweep
from tools.ci.product_shards import partition

FLOOR = 92
CORE_TESTS = "packages/aitm-core/tests"
USAGE_TESTS = sweep.PROFILES["product"]
CLI_TEST = "tools/ci/tests/test_cli_evidence.py"
CLI_SMOKE = f"{CLI_TEST}::test_usage_console_help"


def count_categories(categories):
    unit = integration = 0
    for category in categories:
        if category in ("fast-unit", "slow-unit"):
            unit += 1
        elif category in ("local-integration", "systems-integration"):
            integration += 1
        else:
            raise sweep.Refusal(f"unknown category: {category}")
    return unit, integration


def meets_floor(unit, integration):
    total = unit + integration
    return bool(total and 100 * unit >= FLOOR * total)


def core_categories(nodes):
    # Core's unit/ lane enforces isolation with its autouse audit-hook fixture.
    lanes = {"unit": "fast-unit", "integration": "local-integration"}
    sweep.require(len(nodes) == len(set(nodes)), "duplicate Core node IDs")
    categories = []
    for node in nodes:
        relative = node.removeprefix(f"{CORE_TESTS}/")
        lane, _, test = relative.partition("/")
        sweep.require(
            relative != node and lane in lanes and "::" in test,
            f"unclassified Core node ID: {node}",
        )
        categories.append(lanes[lane])
    return categories


def usage_categories(nodes, catalog_path, host):
    catalog = sweep.read_catalog(catalog_path, host)
    expected = {
        node: category
        for node, category in catalog.items()
        if node.startswith(f"{USAGE_TESTS}/")
    }
    if host == "linux":
        sweep.require(
            catalog.get(CLI_SMOKE) == "systems-integration",
            f"missing or invalid installed CLI smoke classification: {CLI_SMOKE}",
        )
        expected[CLI_SMOKE] = catalog[CLI_SMOKE]
    return [
        lane
        for lane, classified_nodes in partition(nodes, expected).items()
        for _ in classified_nodes
    ]


def collect(root, package, targets):
    with TemporaryDirectory(prefix="aitm-unit-floor-") as temp:
        receipt = Path(temp) / "collection.json"
        env = dict(os.environ, AITM_CI_PYTEST_EVIDENCE=str(receipt))
        env.pop("PYTEST_ADDOPTS", None)
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-p",
                "tools.ci.pytest_evidence",
                "-p",
                "no:cacheprovider",
                "--rootdir",
                str(root),
                "-c",
                str(root / "packages" / package / "pyproject.toml"),
                "--collect-only",
                "-q",
                *targets,
            ],
            cwd=root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        if result.returncode:
            raise sweep.Refusal(f"pytest collection failed:\n{result.stdout}")
        observed = json.loads(receipt.read_bytes())
        sweep.require(
            observed["schema"] == sweep.PYTEST_SCHEMA
            and observed["exit_code"] == 0
            and not any(observed[k] for k in ("deselected", "reports", "children")),
            "incomplete full pytest collection",
        )
        return observed["collected"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", choices=("aitm-core", "aitm-usage"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    try:
        if args.package == "aitm-core":
            nodes = collect(root, args.package, [CORE_TESTS])
            categories = core_categories(nodes)
        else:
            targets = [USAGE_TESTS]
            if sys.platform == "linux":
                targets.append(CLI_TEST)
            nodes = collect(root, args.package, targets)
            categories = usage_categories(nodes, root / sweep.CATALOG, sys.platform)
            if sys.platform == "linux":
                print(
                    f"Installed CLI smoke counted as systems integration: `{CLI_SMOKE}`"
                )
        unit, integration = count_categories(categories)
        print(
            f"{args.package} ({sys.platform}) full collection: {unit} unit, "
            f"{integration} integration, {unit + integration} total. Unit floor: {FLOOR}%."
        )
        sweep.require(meets_floor(unit, integration), "unit-test floor not met")
    except sweep.Refusal as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
