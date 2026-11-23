"""Execute trusted test selections in separate category-specific pytest runs."""

import argparse
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path
from time import monotonic
from xml.etree import ElementTree

from tools.ci import category_sweep as sweep
from tools.ci.pytest_evidence import reconcile_workers


def partition(collected, catalog):
    if len(collected) != len(catalog) or set(collected) != set(catalog):
        missing = sorted(set(catalog) - set(collected))
        extra = sorted(set(collected) - set(catalog))
        raise sweep.Refusal(
            f"product collection differs from catalog; missing={missing[:8]} extra={extra[:8]}"
        )
    lanes = {lane: [] for lane in sweep.CATEGORIES}
    for node in collected:
        lanes[catalog[node]].append(node)
    return {lane: nodes for lane, nodes in lanes.items() if nodes}


def merge_receipts(collected, lanes, receipts):
    if set(lanes) != set(receipts):
        raise sweep.Refusal("missing or unexpected product shard receipts")
    result = {
        "schema": sweep.PYTEST_SCHEMA,
        "exit_code": 0,
        "collected": collected,
        "deselected": [],
        "reports": [],
        "children": [],
    }
    for lane, nodes in lanes.items():
        receipt = receipts[lane]
        try:
            sweep.validate(receipt, set(nodes), sys.platform)
        except sweep.Refusal as exc:
            raise sweep.Refusal(f"{lane}: {exc}") from exc
        for field in ("reports", "children"):
            result[field].extend(receipt[field])
    return result


def run(output, root, fixtures, targets, workers, *, coverage, label):
    started_run = monotonic()
    root = root.resolve()
    selectors = tuple(Path(target).resolve().relative_to(root) for target in targets)
    catalog = {
        node: category
        for node, category in sweep.read_catalog(
            root / sweep.CATALOG, sys.platform
        ).items()
        if any(Path(node.partition("::")[0]).is_relative_to(path) for path in selectors)
    }
    observer = output / "observer"
    evidence = output / "evidence"
    observer.mkdir(parents=True, exist_ok=True)
    evidence.mkdir(parents=True, exist_ok=True)
    fixtures.mkdir(parents=True, exist_ok=True)
    pytest = [
        "-m",
        "pytest",
        "-p",
        "pytest_evidence",
        "--rootdir",
        str(root),
        "-q",
        "-p",
        "no:cacheprovider",
    ]
    collection_path = observer / "collection.json"
    started = monotonic()
    subprocess.run(
        [sys.executable, *pytest, "--collect-only", *targets],
        env=dict(os.environ, AITM_CI_PYTEST_EVIDENCE=str(collection_path)),
        check=True,
        stdout=subprocess.DEVNULL,
    )
    collection_seconds = round(monotonic() - started, 3)
    collection = sweep.read(collection_path)
    if (
        collection["schema"] != sweep.PYTEST_SCHEMA
        or collection["exit_code"] != 0
        or any(collection[key] for key in ("deselected", "reports", "children"))
    ):
        raise sweep.Refusal("inconsistent product collection receipt")
    collected = collection["collected"]
    lanes = partition(collected, catalog)
    receipts = {}
    timings = []
    junit = ElementTree.Element("testsuites")
    invocation = (
        [sys.executable, "-m", "coverage", "run"] if coverage else [sys.executable]
    )
    for index, (lane, nodes) in enumerate(lanes.items()):
        folder = observer / lane
        folder.mkdir()
        receipt_path = folder / "pytest.json"
        junit_path = evidence / f"product-{lane}.xml"
        node_file = folder / "tests.txt"
        node_file.write_text(
            "".join(f"{root / node}\n" for node in nodes), encoding="utf-8"
        )
        print(f"Running product shard {lane} ({len(nodes)} tests)", flush=True)
        started = monotonic()
        subprocess.run(
            [
                *invocation,
                *pytest,
                "-n",
                str(workers),
                "--dist",
                "worksteal",
                "--basetemp",
                str(fixtures / str(index)),
                f"--junitxml={junit_path}",
                f"--junit-prefix={lane}",
                "--durations=15",
                f"@{node_file}",
            ],
            env=dict(os.environ, AITM_CI_PYTEST_EVIDENCE=str(receipt_path)),
            check=True,
        )
        seconds = round(monotonic() - started, 3)
        receipt = reconcile_workers(receipt_path, workers)
        receipts[lane] = receipt
        calls = Counter(
            report["outcome"]
            for report in receipt["reports"]
            if report["when"] == "call"
        )
        worker_tests = []
        for worker in range(workers):
            raw = sweep.read(folder / f"pytest-gw{worker}.json")
            worker_tests.append(
                sum(report["when"] == "setup" for report in raw["reports"])
            )
        timing = {
            "category": lane,
            "tests": len(nodes),
            "passed": calls["passed"],
            "skipped": len(nodes) - calls["passed"],
            "seconds": seconds,
            "worker_tests": worker_tests,
        }
        timings.append(timing)
        print(
            "product-shard-evidence",
            json.dumps({"selection": label, **timing}, sort_keys=True),
            flush=True,
        )
        junit.extend(ElementTree.parse(junit_path).getroot())
    (evidence / "pytest.json").write_bytes(
        sweep.encoded(merge_receipts(collected, lanes, receipts))
    )
    ElementTree.ElementTree(junit).write(
        evidence / "product-junit.xml", encoding="utf-8", xml_declaration=True
    )
    report = {
        "selection": label,
        "collection_seconds": collection_seconds,
        "total_seconds": round(monotonic() - started_run, 3),
    }
    (evidence / "product-shards.json").write_bytes(
        sweep.encoded({**report, "shards": timings})
    )
    print("product-shard-summary", json.dumps(report, sort_keys=True), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fixtures", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--coverage", action="store_true")
    parser.add_argument("--label", required=True)
    parser.add_argument("targets", nargs="+")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers must be positive")
    run(
        args.output,
        args.root,
        args.fixtures,
        args.targets,
        args.workers,
        coverage=args.coverage,
        label=args.label,
    )


if __name__ == "__main__":
    main()
