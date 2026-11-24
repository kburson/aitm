"""Verify #423 Actions artifact bytes and recompute results from pytest phases."""

from collections import Counter
from hashlib import sha1, sha256
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
import gzip
import json
import re
import subprocess
import sys

BASE = "45db935ac73911b95320a3e38d19f177cedd4fd2"
REPO = "kburson/aitm"
CASES = ("clean", "leaf", "transitive", "shared", "docs", "add", "rename", "delete", "dynamic")
PROFILES = ("product-cli", "ci-helpers")
ORDER = ("setup", "call", "teardown")
INVENTORY_FILE = "packages/aitm-usage/tests/test_monitor_policy_unit.py"
OLD_ID = INVENTORY_FILE + "::test_earlier_handoff_holds_later_handoff_with_stale_generation"
NEW_ID = INVENTORY_FILE + "::test_spike_423_added_inventory"
RENAMED_ID = INVENTORY_FILE + "::test_spike_423_renamed_inventory"
WATCH = "packages/aitm-usage/tests/test_host_watch.py::test_native_watch_reports_change_and_retires_resources"
SEEDS = {
    "leaf": 'item.reason == "startup"',
    "transitive": "WatchError: Authorized watch root is unavailable",
}


def gh(route):
    return subprocess.check_output(["gh", "api", f"repos/{REPO}/{route}"])


def verify(rule, message):
    if not rule:
        raise ValueError(message)


def load(archive, name):
    return json.loads(archive.read(name))


def pytest_nodes(archive, lane, profile):
    name = f"{lane}-{profile}"
    documents = set(archive.namelist())
    if name + ".json" not in documents:
        return {}
    controller = load(archive, name + ".json")
    workers = [load(archive, item) for item in sorted(documents)
               if re.fullmatch(re.escape(name) + r"-gw[0-9]+\.json", item)]
    actual = workers[0] if workers else controller

    def rows(config):
        return Counter((row["nodeid"], row["when"], row["outcome"], row["wasxfail"], row["skip_reason"])
                       for row in config["reports"])

    phase_rows = rows(controller)
    inventory = actual["collected"]
    if workers:
        verify(len(workers) == 3 and not controller["collected"]
               and all(worker["collected"] == inventory for worker in workers)
               and sum((rows(worker) for worker in workers), Counter()) == phase_rows,
               f"{name}: invalid xdist evidence")
    outcomes = {node: {} for node in inventory}
    verify(len(outcomes) == len(inventory), f"{name}: duplicate collected ID")
    for (node, stage, flag, xfail, reason), count in phase_rows.items():
        verify(count == 1 and stage not in outcomes[node], f"{name}: duplicate phase")
        outcomes[node][stage] = (flag, xfail, reason)
    for node, stages in outcomes.items():
        verify(set(stages) == (set(ORDER) if stages["setup"][0] == "passed" else {"setup", "teardown"}),
               f"{name}: incomplete phases for {node}")
    verify(controller["exit_code"] == int(bool(failed(outcomes))), f"{name}: exit disagree")
    return outcomes


def failed(lane):
    return {node for node, phases in lane.items()
            if any(flag == "failed" for flag, _, _ in phases.values())}


def mismatch(left, right):
    return sorted(key for key in left.keys() & right.keys() if left[key] != right[key])


def score(full, selected, seal):
    return {
        "missed_failing": sorted(failed(full) - selected.keys()),
        "mismatch": mismatch(full, selected),
        "extra_behavior": sorted(selected.keys() - (set(seal["behavior"]) | set(seal["mandatory"]))),
        "extra_safety": sorted(selected.keys() - (set(seal["safety"]) | set(seal["mandatory"]))),
        "omitted_behavior": sorted((full.keys() & set(seal["behavior"])) - selected.keys()),
        "omitted_mandatory": sorted((full.keys() & set(seal["mandatory"])) - selected.keys()),
    }


def combine(data):
    combined = data[PROFILES[0]] | data[PROFILES[1]]
    verify(len(combined) == sum(map(len, data.values())), "profile inventories overlap")
    return combined


def collect_case(path, run, attempt, githead, workflow_blob, digest, case, job, artifact):
    data = path.read_bytes()
    verify("sha256:" + sha256(data).hexdigest() == digest, f"{case}: artifact ZIP digest mismatch")
    with ZipFile(BytesIO(data)) as archive:
        verify(archive.testzip() is None, f"{case}: corrupted zip")
        ident = load(archive, "identity.json")
        summary = load(archive, "summary.json")
        verify(ident["run"] == run and ident["attempt"] == attempt and ident["workflow"] == githead
               and ident["workflow_blob"] == workflow_blob and ident["base"] == BASE
               and ident["case"] == case and ident == summary["identity"]
               and ident["arch"] == "X64" and ident["image"].startswith("ubuntu24:")
               and ident["python"] == "3.13.9" and ident["event"] == "push"
               and ident["coverage"] == "disabled", f"{case}: hosted identity drift")
        commit_bytes = archive.read("tested-commit.txt")
        commit_object = f"commit {len(commit_bytes)}\0".encode() + commit_bytes
        verify(sha1(commit_object).hexdigest() == ident["tested"], f"{case}: tested commit hash mismatch")
        commit_header = commit_bytes.decode().splitlines()
        verify(commit_header[:3] == [f"tree {ident['tree']}", f"parent {BASE}", f"parent {ident['head']}"],
               f"{case}: synthetic commit identity mismatch")
        expected = load(archive, "expectation.json")
        verify(sha256(archive.read("expectation.json")).hexdigest() == summary["seal_sha256"]
               and expected["case"] == case, f"{case}: seal mismatch")
        for name in ("base", "head", "tested", "tree", "path"):
            verify(expected["candidate"][name] == ident[name], f"{case}: seal source drift")
        probe = load(archive, "probe.stdout")
        decision = probe["plan"]
        path_map = load(archive, "path-map.stdout")
        mode = decision["mode"]
        verify(probe["provenance"] == "local_advisory" and mode == summary["mode"]
               and path_map["mode"] == summary["path_map_mode"], f"{case}: projection drift")
        if mode != "unavailable":
            verify(decision["snapshot"]["endpoint"] == {"commit": ident["tested"], "tree": ident["tree"]},
                   f"{case}: probe tested identity drift")
        if case == "clean":
            rejection = load(archive, "wrong-tree.stdout")["plan"]
            verify(rejection["mode"] == "unavailable" and not rejection["selected"],
                   "wrong-tree control did not reject")
        full = {profile: pytest_nodes(archive, "full", profile) for profile in PROFILES}
        selected = {profile: pytest_nodes(archive, "selected", profile) for profile in PROFILES}
        timers = load(archive, "commands.json")
        if mode == "unavailable":
            verify(not any(selected.values()), f"{case}: unavailable emitted execution")
        for profile in PROFILES:
            verified_ids = load(archive, f"collect-{profile}.json")["collected"]
            verify(set(verified_ids) == set(full[profile]) == set(expected["collected"][profile]),
                   f"{case}: independent collection mismatch")
            predicted = {row["nodeid"] for row in decision["selected"] if row["profile"] == profile}
            verify(predicted == set(selected[profile]), f"{case}: predicted execution mismatch")
            if mode != "unavailable":
                metrics = score(full[profile], selected[profile], expected)
                verify(all(summary["profiles"][profile][name] == value
                           for name, value in metrics.items()), f"{case}: {profile} score mismatch")
        full_nodes, selected_nodes = combine(full), combine(selected)
        metrics = None
        if mode != "unavailable":
            metrics = score(full_nodes, selected_nodes, expected)
            verify(all(summary["union"][name] == value for name, value in metrics.items()),
                   f"{case}: union score mismatch")
        full_s = sum(timers[f"full-{profile}"]["seconds"] for profile in PROFILES)
        selected_s = sum(timers.get(f"selected-{profile}", {}).get("seconds", 0) for profile in PROFILES)
        net_s = round(full_s - selected_s - timers["probe"]["seconds"], 3)
        verify(round(full_s, 3) == summary["union"]["full_seconds"] and
               (mode == "unavailable" or (round(selected_s, 3) == summary["union"]["selected_seconds"]
                and net_s == summary["union"]["net_seconds"])), f"{case}: wall time mismatch")
        seed_signature = None
        if case in SEEDS:
            def signature(lane, outcomes):
                raw = archive.read(f"{lane}-product-cli.stdout").decode()
                return WATCH in failed(outcomes) and SEEDS[case] in raw
            seed_signature = {
                "witness": WATCH,
                "signature": SEEDS[case],
                "full_reproduced": signature("full", full_nodes),
                "selected_reproduced": WATCH in failed(selected_nodes) and signature("selected", selected_nodes),
            }
            verify(seed_signature["full_reproduced"] == summary["seed_full_signature"]
                   and (not seed_signature["full_reproduced"] or
                        seed_signature["selected_reproduced"] == summary["seed_selected_signature"]),
                   f"{case}: seed summary mismatch")
        artifact["job"] = job
        result = {
            "identity": ident, "artifact": artifact, "expectation_sha256": summary["seal_sha256"],
            "mode": mode, "predicted_mode": expected["predicted_mode"],
            "reasons": decision["reasons"], "path_map_mode": path_map["mode"],
            "probe_seconds": timers["probe"]["seconds"], "map_seconds": timers["path-map"]["seconds"],
            "full_seconds": round(full_s, 3), "selected_seconds": round(selected_s, 3) if metrics is not None else None,
            "net_seconds": net_s if metrics is not None else None,
            "net_fraction": net_s / full_s if metrics is not None else None,
            "selected_fraction": len(selected_nodes) / len(full_nodes) if metrics is not None else None,
            "full_failures": sorted(failed(full_nodes)), "scores": metrics, "seed": seed_signature,
            "profiles": summary["profiles"], "union": summary["union"], "repeat": summary["repeat"],
        }
        structured = {
            name: load(archive, name)
            for name in archive.namelist()
            if name.endswith(".json") or name in {"probe.stdout", "path-map.stdout", "wrong-tree.stdout"}
        }
        for name in ("patch.diff", "tested-commit.txt"):
            structured[name] = archive.read(name).decode()
        if case in SEEDS:
            log = archive.read("full-product-cli.stdout")
            structured["seed_assertion"] = {
                "diagnostic_sha256": sha256(log).hexdigest(),
                "matching_lines": [line.strip() for line in log.decode().splitlines() if SEEDS[case] in line],
            }
        encoded = json.dumps(structured, sort_keys=True, separators=(",", ":")).encode()
        archive_path = path.with_name(f"{case}-structured.json.gz")
        archive_path.write_bytes(gzip.compress(encoded, mtime=0))
        result["lossless_structured_receipt"] = {
            "file": archive_path.name, "sha256": sha256(archive_path.read_bytes()).hexdigest(),
        }
    return result, full_nodes


def main():
    run, attempt, root_arg, workflow_blob = sys.argv[1:]
    root = Path(root_arg)
    metadata = json.loads(gh(f"actions/runs/{run}/attempts/{attempt}"))
    verify(metadata["status"] == "completed" and metadata["conclusion"] == "success"
           and metadata["event"] == "push" and metadata["head_branch"] == "codex/423-tia-validation"
           and metadata["path"] == ".github/workflows/shadow-423.yml",
           "unexpected Actions run")
    githead = metadata["head_sha"]
    jobs = json.loads(gh(f"actions/runs/{run}/attempts/{attempt}/jobs"))["jobs"]
    verify(len(jobs) == len(CASES) and all(job["conclusion"] == "success" for job in jobs), "incomplete jobs")
    artifact_rows = json.loads(gh(f"actions/runs/{run}/artifacts"))["artifacts"]
    selected = {row["name"]: row for row in artifact_rows if not row["expired"]}
    cases = {}
    all_full = {}
    for case in CASES:
        row = selected[f"shadow-423-{case}-a{attempt}"]
        zip_path = root / f"{case}.zip"
        if not zip_path.exists():
            zip_path.write_bytes(gh(f"actions/artifacts/{row['id']}/zip"))
        artifact = {key: row[key] for key in ("id", "name", "digest", "size_in_bytes")}
        job = next(job for job in jobs if job["name"] == f"shadow / {case}")
        cases[case], all_full[case] = collect_case(
            zip_path, run, attempt, githead, workflow_blob, row["digest"], case,
            {"id": job["id"], "url": job["html_url"], "conclusion": job["conclusion"]}, artifact,
        )
    clean = all_full["clean"]
    verify(WATCH in clean and WATCH not in failed(clean), "clean seed control did not pass")
    verify(not failed(clean), "clean oracle failed")
    for case, difference in {
        "add": ({NEW_ID}, set()), "rename": ({RENAMED_ID}, {OLD_ID}), "delete": (set(), {OLD_ID}),
    }.items():
        observed = (set(all_full[case]) - clean.keys(), clean.keys() - set(all_full[case]))
        verify(observed == difference, f"{case}: exact independent inventory delta mismatch")
        cases[case]["inventory_delta"] = {"added": sorted(observed[0]), "removed": sorted(observed[1])}
    for case in ("shared", "docs", "dynamic"):
        verify(clean.keys() == all_full[case].keys(), f"{case}: unexpected discovery changes")
        cases[case]["clean_outcome_disagreement"] = mismatch(clean, all_full[case])
    for case in SEEDS:
        cases[case]["seed"]["passes_clean"] = WATCH not in failed(clean)
    result = {
        "workflow": {"run": run, "attempt": attempt, "url": metadata["html_url"],
                     "head": githead, "blob": workflow_blob, "path": metadata["path"]},
        "clean_control": {"full_count": len(clean), "passed_seed_witness": WATCH, "wrong_tree_refused": True},
        "cases": cases,
    }
    (root / "comparison.json").write_text(json.dumps(result, indent=2) + "\n")
    for case, result in cases.items():
        print(case, result["mode"], result["union"]["full"], result["union"]["selected"],
              result["full_seconds"], result["selected_seconds"], result["probe_seconds"],
              result["net_seconds"], result["full_failures"], result["seed"], flush=True)


if __name__ == "__main__":
    main()
