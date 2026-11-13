"""Render the sanitized #267 report from the reconciled evidence."""

import hashlib
import json
import sys
from pathlib import Path


def summary(profiles):
    count = sum(len(entry["selected_ids"]) for entry in profiles.values())
    seconds = sum(entry["seconds"] for entry in profiles.values())
    return count, seconds


def row(seed, data):
    count, serial_seconds = summary(data["serial"])
    testmon_count, testmon_seconds = summary(data["testmon"])
    testmon = data["testmon_comparison"]
    tia = data["tia_comparison"]
    plan = data["tia_plan"]
    return (
        f"| {seed} | {count} / {serial_seconds:.2f}s | {len(data['expected_ids'])} | "
        f"{len(data['observed_pass_to_failure'])} | {plan['mode']} / {tia['selected']} / "
        f"{plan['command_seconds']:.2f}s | {len(tia['misses_vs_predeclared_expected'])} / "
        f"{len(tia['extra_vs_predeclared_expected'])} / "
        f"{len(tia['misses_vs_observed_pass_to_failure'])} | {testmon_count} / "
        f"{testmon_seconds:.2f}s | {len(testmon['misses_vs_predeclared_expected'])} / "
        f"{len(testmon['extra_vs_predeclared_expected'])} / "
        f"{len(testmon['misses_vs_observed_pass_to_failure'])} |"
    )


def render(evidence, digest):
    seeds = evidence["seeds"]
    baseline_count, baseline_seconds = summary(evidence["baseline"])
    train_count, train_seconds = summary(evidence["training"])
    host = evidence["host"]
    versions = evidence["versions"]
    baseline_outcomes = {
        node: phases
        for entry in evidence["baseline"].values()
        for node, phases in entry["phase_outcomes"].items()
        if "failed" in phases.values()
    }
    lines = [
        "# #267 local TIA and pytest-testmon advisory measurement",
        "",
        f"AITM `{evidence['source_revision']}` on {host['os']} {host['version']} "
        f"{host['arch']} with APFS and native ACL support. One worker per profile, "
        f"Python {versions['python']}, pytest {versions['pytest']}, uv {versions['uv']}, "
        f"coverage {versions['coverage']} and pytest-testmon {versions['pytest-testmon']}.",
        "",
        f"The unchanged serial reference observed {baseline_count:,} test IDs in "
        f"{baseline_seconds:.2f}s. The unchanged Testmon history run observed "
        f"{train_count:,} IDs in {train_seconds:.2f}s. Both profiles in the history run "
        "used a fresh database with selection disabled. Each warm case started from "
        "a copy of the corresponding unchanged history.",
        "",
        "## Baseline diagnostics",
        "",
        f"The unchanged serial reference retained {len(baseline_outcomes)} failure(s). "
        "The unchanged full Testmon history run completed cleanly on the same inventory. "
        f"The evidence includes {len(evidence['unchanged_targeted_rechecks'])} isolated "
        "unchanged rechecks and the original baseline failure phase.",
        "",
        *[
            f"- `{node}` failed during {', '.join(stage for stage, value in phases.items() if value == 'failed')}."
            for node, phases in baseline_outcomes.items()
        ],
        "",
        "## Seed measurements",
        "",
        "| Seed | Serial IDs / wall | Expected IDs | Serial pass-to-failure IDs | #143 plan / IDs / wall | #143 expected misses / expected extras / observed misses | Testmon IDs / wall | Testmon expected misses / expected extras / observed misses |",
        "| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |",
    ]
    for seed in ("cli", "non-code", "uncertain", "unavailable"):
        lines.append(row(seed, seeds[seed]))
    lines.extend(
        [
            "",
            "Expected misses are predeclared IDs omitted by the method. Expected extras "
            "are selected IDs outside that predeclared lower bound. Observed misses are "
            "IDs whose serial outcome changed from pass to failure and which the method "
            "omitted. A full fallback's extras include every full-run obligation outside "
            "the lower bound. The unavailable case reuses the full CLI-seed reference. "
            "Wall time sums the two profiles for direct serial and Testmon. The #143 plan "
            "wall includes dependency setup, snapshot verification and collection.",
            "",
            "## Method observations",
            "",
        ]
    )
    for seed in ("cli", "non-code", "uncertain", "unavailable"):
        info = seeds[seed]
        plan = info["tia_plan"]
        run = info["tia_run"]
        reasons = "; ".join(plan["reasons"])
        message = f"- **{seed}.** #143 plan exited {plan['exit_code']}."
        if reasons:
            message += f" It reported `{reasons}`."
        if run:
            message += (
                f" `--run` exited {run['exit_code']} with status `{run['result_status']}` "
                f"after {run['command_seconds']:.2f}s command wall and "
                f"{run['execution_seconds']:.2f}s execution stage. "
                f"It recorded {run['result_executed']:,} executed IDs."
            )
        per_profile = ", ".join(
            f"{profile} exit {entry['exit_code']} ({len(entry['selected_ids'])} selected)"
            for profile, entry in info["testmon"].items()
        )
        message += f" Testmon recorded {per_profile}."
        lines.append(message)
    lines.extend(
        [
            "",
            "## Evidence",
            "",
            f"The sanitized machine-readable evidence has SHA-256 `{digest}`. It binds "
            "the fixture patches and raw diagnostic files by digest and lists exact "
            "selected, omitted, extra and failed node IDs, plus phase outcomes. Raw "
            "tracebacks and full history databases are retained in private scratch. "
            "The [recipe](recipe.md) and [implementer notes](benchmark-notes.md) record "
            "fixture conditions and the baseline diagnostic.",
            "",
            "Use these results for advisory TIA evaluation. #103 remains the merge gate.",
            "",
            "Signed `codex-collaboration:/root/measure267`.",
            "",
        ]
    )
    return "\n".join(lines)


def main():
    source, output = map(Path, sys.argv[1:])
    data = source.read_bytes()
    output.write_text(render(json.loads(data), hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
