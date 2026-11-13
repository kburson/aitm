"""Reconcile advisory suggestions with independent serial outcomes, without host paths."""

import hashlib
import json
import platform
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROFILES = ("ci-helpers", "product-cli")
EXPECTED = {
    "cli": {"tools/ci/tests/test_cli_evidence.py::test_usage_console_help"},
    "non-code": set(),
    "uncertain": {
        "packages/aitm-usage/tests/test_grok.py::test_headless_projection_is_only_corroboration"
    },
    "unavailable": {"tools/ci/tests/test_cli_evidence.py::test_usage_console_help"},
}


def read_json(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence_file_hashes(directory):
    names = (
        "exit",
        "stdout.log",
        "stderr.log",
        "pytest-evidence.json",
        "testmon-evidence.json",
        "diagnostics.jsonl",
        "report.json",
    )
    return {
        name: sha(directory / name) for name in names if (directory / name).is_file()
    }


def wall(directory):
    return float(
        next(
            line.split()[1]
            for line in reversed((directory / "stderr.log").read_text().splitlines())
            if line.startswith("real ")
        )
    )


def outcomes_for(receipt):
    phases = defaultdict(dict)
    for report in receipt["reports"]:
        phase = report["when"]
        node = report["nodeid"]
        if phase in phases[node]:
            raise ValueError(f"duplicate phase {node} {phase}")
        if report["wasxfail"]:
            outcome = "xfailed" if report["outcome"] == "skipped" else "xpassed"
        else:
            outcome = report["outcome"]
        phases[node][phase] = outcome
    return dict(sorted(phases.items()))


def outcome_for(phases):
    failures = [
        f"{stage}-failed" for stage, result in phases.items() if result == "failed"
    ]
    if failures:
        return "+".join(failures)
    return phases.get("call", phases.get("setup", "no-report"))


def load_profile(directory, mode):
    receipt = read_json(directory / "pytest-evidence.json")
    phases = outcomes_for(receipt)
    nodeids = sorted(receipt["collected"])
    assert nodeids == sorted(set(nodeids)) == sorted(phases), directory
    exit_code = int((directory / "exit").read_text())
    assert exit_code == receipt["exit_code"], directory
    entry = {
        "seconds": wall(directory),
        "exit_code": exit_code,
        "selected_ids": nodeids,
        "outcome_counts": dict(Counter(outcome_for(item) for item in phases.values())),
        "phase_outcomes": phases,
        "children": [
            {"label": child["label"], "returncode": child["returncode"]}
            for child in receipt["children"]
        ],
        "raw_sha256": evidence_file_hashes(directory),
    }
    if mode != "serial":
        testmon = read_json(directory / "testmon-evidence.json")
        assert sorted(testmon["selected"]) == nodeids
        assert testmon["exit"] == exit_code
        entry.update(
            {
                "history_was_new": testmon["history_was_new"],
                "collect_history": testmon["collect_history"],
                "selection_enabled": testmon["select"],
                "eligible_deselection_count": len(testmon["eligible_deselections"]),
                "eligible_deselections": testmon["eligible_deselections"],
                "ignored_file_candidates": testmon["ignored_file_candidates"],
                "unstable_file_count": len(testmon["unstable_files"]),
                "anonymous_deselection_reports": receipt["deselected"].count(None),
                "datafile_sha256": sha(directory / "testmon.sqlite"),
            }
        )
    return entry


def load_profiles(logs, seed, mode):
    return {
        profile: load_profile(logs / seed / profile / mode, mode)
        for profile in PROFILES
    }


def inventory(entries):
    per_profile = [entry["selected_ids"] for entry in entries.values()]
    all_ids = {node for nodes in per_profile for node in nodes}
    assert len(all_ids) == sum(map(len, per_profile))
    return all_ids


def outcomes(entries):
    return {
        node: outcome_for(phases)
        for entry in entries.values()
        for node, phases in entry["phase_outcomes"].items()
    }


def load_tia(directory, expected=()):
    report = read_json(directory / "report.json")
    plan = report["plan"]
    result = report["result"]
    row_ids = [row["nodeid"] for row in plan["selected"]]
    assert len(row_ids) == len(set(row_ids))
    entry = {
        "schema": report["schema"],
        "mode": plan["mode"],
        "provenance": plan["provenance"],
        "reasons": plan["reasons"],
        "selected_ids": sorted(row_ids),
        "command_seconds": wall(directory),
        "exit_code": int((directory / "exit").read_text()),
        "raw_sha256": evidence_file_hashes(directory),
        "inventory": plan.get("inventory"),
        "snapshot": plan.get("snapshot"),
        "changes": plan.get("changes", []),
        "expected_witnesses": [
            witness
            for witness in plan.get("selection", {}).get("witnesses", [])
            if witness["key"][-1] in expected
        ],
    }
    if result:
        entry.update(
            {
                "result_status": result["status"],
                "result_provenance": result["provenance"],
                "execution_seconds": result["seconds"],
                "result_executed": result["executed"],
                "result_errors": result["errors"],
                "plan_sha256": result["plan_sha256"],
                "profiles": [
                    {
                        k: item[k]
                        for k in (
                            "profile",
                            "returncode",
                            "seconds",
                            "executed",
                            "outcomes",
                            "errors",
                        )
                    }
                    | {
                        "children": [
                            {"label": child["label"], "returncode": child["returncode"]}
                            for child in item["children"]
                        ]
                    }
                    for item in result["profiles"]
                ],
            }
        )
        assert entry["exit_code"] == result["exit_code"]
    return entry


def compare(suggested, reference, expected, failures):
    return {
        "selected": len(suggested),
        "misses_vs_predeclared_expected": sorted(expected - suggested),
        "extra_vs_predeclared_expected": sorted(suggested - expected),
        "misses_vs_observed_pass_to_failure": sorted(failures - suggested),
        "extra_vs_observed_pass_to_failure": sorted(suggested - failures),
        "outside_serial_reference": sorted(suggested - reference),
        "omitted_serial_ids": sorted(reference - suggested),
    }


def history_rows(path):
    with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as connection:
        return dict(
            connection.execute(
                "SELECT test_name, failed FROM test_execution ORDER BY test_name"
            )
        )


def main():
    private, output = map(Path, sys.argv[1:])
    logs = private / "logs"
    baseline = load_profiles(logs, "baseline", "serial")
    train = load_profiles(logs, "train", "train")
    assert inventory(baseline) == inventory(train)
    base_outcomes = outcomes(baseline)
    history = {}
    for profile in PROFILES:
        datafile = private / "history" / f"{profile}.sqlite"
        records = history_rows(datafile)
        assert set(records) == set(train[profile]["selected_ids"]), profile
        assert (
            train[profile]["history_was_new"]
            and not train[profile]["selection_enabled"]
        )
        assert train[profile]["collect_history"]
        history[profile] = {"sha256": sha(datafile), "records": records}
    seed_evidence = {}
    for seed, expected in EXPECTED.items():
        serial_seed = "cli" if seed == "unavailable" else seed
        serial = load_profiles(logs, serial_seed, "serial")
        full = inventory(serial)
        after_outcomes = outcomes(serial)
        assert full == inventory(baseline), seed
        delta = {
            node: [base_outcomes[node], value]
            for node, value in after_outcomes.items()
            if value != base_outcomes[node]
        }
        failures = {
            node
            for node, (old, new) in delta.items()
            if old == "passed" and "failed" in new
        }
        testmon = load_profiles(logs, seed, "cold" if seed == "unavailable" else "warm")
        tia_plan = load_tia(logs / seed / "tia-plan", expected)
        tia_run_dir = logs / seed / "tia-run"
        tia_run = (
            load_tia(tia_run_dir, expected)
            if (tia_run_dir / "exit").is_file()
            else None
        )
        if tia_run:
            for field in (
                "mode",
                "snapshot",
                "inventory",
                "selected_ids",
                "provenance",
                "reasons",
            ):
                assert tia_run[field] == tia_plan[field], (seed, field)
        assert set(expected) <= full
        for profile, entry in testmon.items():
            cold = seed == "unavailable"
            assert entry["history_was_new"] == entry["collect_history"] == cold
            assert entry["selection_enabled"]
            if not cold:
                database = logs / seed / profile / "warm" / "testmon.sqlite"
                assert history_rows(database) == history[profile]["records"]
                entry["input_datafile_sha256"] = history[profile]["sha256"]
        testmon_selected = inventory(testmon)
        testmon_compare = compare(testmon_selected, full, expected, failures)
        testmon_outcomes = outcomes(testmon)
        testmon_compare["selected_outcome_deltas_vs_serial"] = {
            node: [after_outcomes[node], value]
            for node, value in testmon_outcomes.items()
            if node in after_outcomes and after_outcomes[node] != value
        }
        tia_compare = compare(set(tia_plan["selected_ids"]), full, expected, failures)
        if tia_run:
            run_outcomes = {
                row["nodeid"]: row["outcome"]
                for profile in tia_run["profiles"]
                for row in profile["outcomes"]
            }
            tia_run["selected_outcome_deltas_vs_serial"] = {
                node: [after_outcomes[node], value]
                for node, value in run_outcomes.items()
                if node in after_outcomes
                and value
                != (
                    "failed"
                    if "failed" in after_outcomes[node]
                    else after_outcomes[node]
                )
            }
        if seed == "unavailable":
            assert tia_plan["mode"] == "unavailable"
        seed_evidence[seed] = {
            "seed_patch_sha256": sha(logs / seed / "seed.patch"),
            "expected_ids": sorted(expected),
            "observed_pass_to_failure": sorted(failures),
            "observed_pass_to_call_failure": sorted(
                node for node in failures if "call-failed" in after_outcomes[node]
            ),
            "other_outcome_deltas": {
                key: value for key, value in delta.items() if key not in failures
            },
            "serial_reference_seed": serial_seed,
            "serial": serial,
            "testmon": testmon,
            "testmon_comparison": testmon_compare,
            "tia_plan": tia_plan,
            "tia_comparison": tia_compare,
            "tia_run": tia_run,
        }
    rechecks = [
        load_profile(directory, "serial")
        for directory in sorted((logs / "baseline").glob("recheck-*"))
    ]
    evidence = {
        "schema": "aitm.advisory-measurement-267/v1",
        "source_revision": "766504a02aaeb9dda339d588172dd7d5bdbd2b3f",
        "source_tree": "6f1ae4a5707f2344bbeb4c15efdb823480866feb",
        "host": {
            "os": platform.system(),
            "version": platform.mac_ver()[0],
            "arch": platform.machine(),
            "fixture_filesystem": "APFS",
            "workers_per_profile": 1,
        },
        "versions": {
            "python": "3.13.9",
            "pytest": "9.2.0",
            "uv": "0.10.6",
            "coverage": "7.17.2",
            "pytest-testmon": "2.3.0",
        },
        "baseline": baseline,
        "unchanged_targeted_rechecks": rechecks,
        "training": train,
        "unseeded_training_phase_deltas": {
            node: [base_outcomes[node], training_value]
            for node, training_value in outcomes(train).items()
            if training_value != base_outcomes[node]
        },
        "frozen_history": history,
        "seeds": seed_evidence,
    }
    sanitized = json.dumps(evidence, separators=(",", ":"), sort_keys=True) + "\n"
    for prefix in (str(private), str(Path.home()), "/private/var/folders/"):
        assert prefix not in sanitized, (
            f"personal or runner path leaked into evidence: {prefix}"
        )
    output.write_text(sanitized)
    print(
        f"{len(inventory(baseline))} serial obligations and {len(seed_evidence)} seeds reconciled"
    )


if __name__ == "__main__":
    main()
