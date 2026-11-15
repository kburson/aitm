"""Verify and summarize completed #290 measurements."""
import json
from pathlib import Path
from statistics import mean
import sys


def load(path):
    return json.loads(path.read_bytes())


def coverage_points(path):
    report = load(path)
    return {
        name: (
            set(row["executed_lines"]),
            set(row["executed_lines"]) | set(row["missing_lines"]),
            {tuple(branch) for branch in row["executed_branches"]},
            {tuple(branch) for branch in row["executed_branches"] + row["missing_branches"]},
        )
        for name, row in report["files"].items()
    }


def coverage_diff(reference, candidate):
    assert set(reference) == set(candidate)
    changed = {}
    for name, (old_lines, denominator, old_branches, branch_denominator) in reference.items():
        lines, candidate_denominator, branches, candidate_branch_denominator = candidate[name]
        assert denominator == candidate_denominator and branch_denominator == candidate_branch_denominator
        if (lines, branches) != (old_lines, old_branches):
            changed[name] = {
                "additional_lines": sorted(lines - old_lines),
                "missing_lines": sorted(old_lines - lines),
                "additional_branches": sorted(branches - old_branches),
                "missing_branches": sorted(old_branches - branches),
            }
    return changed


def compare(work, manifest, hosted):
    names = ("workers-1-cold", "workers-1-warm", "workers-3-cold", "workers-3-warm")
    result = {name: load(work / name / "summary.json") for name in names}
    reference = result[names[0]]
    coverage_differences = {}
    for cohort, nodes in manifest["cohorts"].items():
        original = reference["cohorts"][cohort]
        coverage = coverage_points(work / names[0] / cohort / "coverage.json")
        coverage_differences[cohort] = {}
        for name, row in result.items():
            assert row["sha"] == manifest["source_sha"]
            assert row["assignments"] == manifest["assignment_count"] and row["queue_seconds"] == 0
            c = row["cohorts"][cohort]
            assert c["inventory_sha256"] == original["inventory_sha256"]
            assert c["node_outcomes_sha256"] == original["node_outcomes_sha256"]
            assert sum(c["outcome_counts"].values()) == len(nodes)
            assert [(w["label"], w["covered_product_lines"]) for w in c["children"]] == [
                (w["label"], w["covered_product_lines"]) for w in original["children"]
            ]
            coverage_differences[cohort][name] = coverage_diff(
                coverage, coverage_points(work / name / cohort / "coverage.json"),
            )
    return {
        "measurements": result,
        "coverage_differences_against_serial_cold": coverage_differences,
        "local_three_worker_speedup": round(
            mean(result[name]["elapsed_seconds"] for name in names[:2])
            / mean(result[name]["elapsed_seconds"] for name in names[2:]), 3,
        ),
        "observed_hosted_1817": hosted,
    }


if __name__ == "__main__":
    root, manifest, hosted = map(Path, sys.argv[1:])
    print(json.dumps(compare(root, load(manifest), load(hosted)), indent=2, sort_keys=True))
