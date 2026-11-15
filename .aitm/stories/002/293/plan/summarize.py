"""Compute the preregistered six-case qualification result."""

import json
import sys
from datetime import datetime
from hashlib import sha256
from math import ceil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ORDER = (
    "docs-add",
    "docs-edit",
    "fixture-equivalent",
    "fixture-regression",
    "source-regression",
    "test-inventory-add",
)


def evidence(path):
    return json.loads(path.read_bytes())


def percentile(rows, quantile):
    ordered = sorted(rows)
    return ordered[ceil(len(ordered) * quantile) - 1]


def elapsed(seconds):
    minutes, secs = divmod(round(seconds), 60)
    return f"{minutes}:{secs:02d}"


def analyze():
    catalog_path = ROOT / "lab/cases.json"
    workload_path = ROOT / "lab/workload.json"
    catalog, workload = evidence(catalog_path), evidence(workload_path)
    measurements = {}
    for name in ORDER:
        source = ROOT / "runs" / name / "verified.json"
        row = evidence(source)
        original = evidence(
            ROOT.parent / "delivery-293/runs" / name / "attempt-1/provider.json"
        )
        assert row["subject"]["case"] == name
        assert sum(v["full_assignments"] for v in row["comparison"].values()) >= 3020
        original_start = datetime.fromisoformat(original["registered_at"])
        revision_gap = (
            datetime.fromisoformat(row["provider"]["registered_at"]) - original_start
        ).total_seconds()
        measurements[name] = {
            "mode": row["mode"],
            "timing": row["timing"],
            "problems": row["problems"],
            "pr": row["subject"]["pull"],
            "run": row["provider"]["run"],
            "attempt": row["provider"]["attempt"],
            "verified_sha256": sha256(source.read_bytes()).hexdigest(),
            "assignment_counts": {
                key: {k: v[k] for k in ("full_assignments", "effective_assignments")}
                for key, v in row["comparison"].items()
            },
            "failures": {
                key: v["full_failures"] for key, v in row["comparison"].items()
            },
            "missed_failure_counts": {
                key: len(v["missed_failures"]) for key, v in row["comparison"].items()
            },
            "extra_failure_counts": {
                key: len(v["extra_failures"]) for key, v in row["comparison"].items()
            },
            "attempt_records": sorted(
                p.parent.name for p in source.parent.glob("attempt-*/provider.json")
            ),
            "original_producer_diagnostic": {
                "run": original["run"],
                "attempt": original["attempt"],
                "full_conclusion": original["jobs"]["full"]["conclusion"],
                "trigger_to_original_full_job_end": (
                    datetime.fromisoformat(original["jobs"]["full"]["completed_at"])
                    - original_start
                ).total_seconds(),
                "original_registration_to_corrected_effective_seconds": revision_gap
                + row["timing"]["registration_to_effective"],
            },
        }
    groups = {}
    for mode in ("selected", "full-required", "full-reference"):
        rows = [
            v["timing"]
            for v in measurements.values()
            if v["mode"] == mode or mode == "full-reference"
        ]
        trigger_key = (
            "first_trigger_to_full_reference"
            if mode == "full-reference"
            else "first_trigger_to_effective"
        )
        trigger = [r[trigger_key] for r in rows]
        from_commit = [
            r[trigger_key]
            + r["edit_commit_to_effective"]
            - r["first_trigger_to_effective"]
            for r in rows
        ]
        groups[mode] = {
            "count": len(rows),
            "trigger_to_verdict_p50_seconds": percentile(trigger, 0.50),
            "trigger_to_verdict_p95_seconds": percentile(trigger, 0.95),
            "edit_commit_to_verdict_p50_seconds": percentile(from_commit, 0.50),
            "edit_commit_to_verdict_p95_seconds": percentile(from_commit, 0.95),
            "samples_at_or_above_15_minutes": sum(value >= 900 for value in trigger),
        }
    all_valid = all(not v["problems"] for v in measurements.values())
    return {
        "production_source": catalog["source_sha"],
        "production_source_tree": catalog["source_tree"],
        "lab_baseline": (ROOT / "lab-default-commit").read_text().strip(),
        "catalog_sha256": sha256(catalog_path.read_bytes()).hexdigest(),
        "workload_sha256": sha256(workload_path.read_bytes()).hexdigest(),
        "workload": {
            "baseline_distinct_ids": len(workload["cohorts"]["full"]),
            "projected_repeat_assignments": len(workload["cohorts"]["projected"]),
        },
        "cases": measurements,
        "groups": groups,
        "all_paired_examples_reconciled": all_valid,
        "observed_selected_target_met": groups["selected"][
            "trigger_to_verdict_p95_seconds"
        ]
        < 600,
        "observed_effective_under_15_minutes": all(
            groups[mode]["samples_at_or_above_15_minutes"] == 0
            for mode in ("selected", "full-required")
        ),
        "fallback_rate": groups["full-required"]["count"] / len(measurements),
    }


def report(summary):
    print("""# #293 Hosted fast-story comparison

The disposable GitHub Actions project compared the exact same reviewed synthetic merge in both lanes on macOS ARM64/APFS. Each full reference executed all current product and helper IDs, plus an isolated repeat cohort stratified across the 47 current test families. The controlled-red witnesses were retained inside their original family quotas. The resulting 3,020 assignments model existing native and integration cost with 1,839 distinct IDs. The inventory case added one actual new test. Future Core coverage remains unmeasured.

| Exact lab PR | Story verdict | Effective assignments | Full assignments | First trigger to verdict | Commit to verdict | Full reference |
| --- | --- | ---: | ---: | ---: | ---: | ---: |""")
    for name, row in summary["cases"].items():
        full_count = sum(
            v["full_assignments"] for v in row["assignment_counts"].values()
        )
        effective_count = sum(
            v["effective_assignments"] for v in row["assignment_counts"].values()
        )
        t = row["timing"]
        url = f"https://github.com/kburson/aitm-fast-validation-293/actions/runs/{row['run']}/attempts/{row['attempt']}"
        print(
            f"| [{name}]({url}) | {row['mode']} | {effective_count} | {full_count} | "
            f"{elapsed(t['first_trigger_to_effective'])} | {elapsed(t['edit_commit_to_effective'])} | {elapsed(t['first_trigger_to_full_reference'])} |"
        )
    print(
        "\nSelected evidence was the actual fast lane on the reviewed Markdown cases and the disposable exact Grok fixture extension. Executable and inventory changes received the full fallback verdict. For fallback time, the later of the classification and full result is the effective verdict. Commit time supplies the observable edit-to-feedback proxy. Per-lane queue, job and pytest times are retained with every result."
    )
    print(
        "\nThe clock stops at hosted job completion after evidence upload. The job includes runner setup, "
        "locked package installation, and applicable test execution. Subsequent independent review and the "
        "separate production wheel smoke, coverage gate, and other #103 checks sit outside this timing."
    )
    if summary["all_paired_examples_reconciled"]:
        print(
            "\nEvery common assignment outcome agreed. The effective verdict missed no failures and added none. "
            "Both required subprocess witnesses were verified for every executed cohort."
        )
    else:
        print(
            "\nThe paired outcomes have unresolved differences. See the per-case comparison data."
        )
    print("\n| Controlled regression | Full-suite failing IDs |\n| --- | --- |")
    for label, row in summary["cases"].items():
        failures = sorted(set().union(*row["failures"].values()))
        if failures:
            print(
                f"| {label} | "
                + "<br>".join(f"\u0060{node}\u0060" for node in failures)
                + " |"
            )
    for key, group in summary["groups"].items():
        print(
            f"\n- **{key}** PR open p50 {elapsed(group['trigger_to_verdict_p50_seconds'])}, "
            f"p95 {elapsed(group['trigger_to_verdict_p95_seconds'])}. Candidate commit p50 "
            f"{elapsed(group['edit_commit_to_verdict_p50_seconds'])}, p95 "
            f"{elapsed(group['edit_commit_to_verdict_p95_seconds'])}. "
            f"{group['samples_at_or_above_15_minutes']} of {group['count']} reached 15 minutes from PR open."
        )
    print(
        f"- **Fallback rate** {summary['fallback_rate']:.1%} of these deliberately selected cases."
    )
    slowest_selected = max(
        (row for row in summary["cases"].values() if row["mode"] == "selected"),
        key=lambda row: row["timing"]["first_trigger_to_effective"],
    )["timing"]
    print(
        f"\nThe longest selected case spent {elapsed(slowest_selected['queues']['fast'])} "
        f"waiting after workflow registration and {elapsed(slowest_selected['job_seconds']['fast'])} "
        "in the job. The queue is included in the measured result."
    )
    print(
        "\nWith these sample counts, the nearest-rank p95 is the maximum in each group. The measurements do not estimate a production SLA. All admitted subjects had immutable, independently scrutinized scope. Production authorization and broader executable selection require separate qualification."
    )
    print(
        "\nThe timing table measures the corrected producer. All original attempts remain attached to the same case blobs. "
        "The original controller withheld full verdicts after a nested pytest cache violated the captured source boundary. "
        "The corrected producer ran a new matrix after the controller fix. Elapsed time across the two producer revisions "
        "includes diagnosis and redeployment and is retained below. Any repeated run of the corrected producer is measured "
        "from its first corrected trigger. [Original failure and fix](2026-11-15-293-cache-isolation.md)."
    )
    print(
        "\n| Case | Original producer | Original registration to failed full job end | Original registration to corrected effective verdict |\n| --- | --- | ---: | ---: |"
    )
    for label, row in summary["cases"].items():
        diagnostic = row["original_producer_diagnostic"]
        url = f"https://github.com/kburson/aitm-fast-validation-293/actions/runs/{diagnostic['run']}/attempts/{diagnostic['attempt']}"
        print(
            f"| {label} | [{diagnostic['full_conclusion']}]({url}) | {elapsed(diagnostic['trigger_to_original_full_job_end'])} | "
            f"{elapsed(diagnostic['original_registration_to_corrected_effective_seconds'])} |"
        )
    print(
        "\n[Comparison data](qualification-summary.json) · [Exact readback](read-hosted.py) · "
        "[Original and corrected receipts](benchmark-evidence.zip) · [Production gate readback](production-gate-readback.json)."
    )


if __name__ == "__main__":
    result = analyze()
    if "--report" in sys.argv:
        report(result)
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
