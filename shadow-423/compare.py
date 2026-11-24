"""Compare one exact #423 hosted advisory assignment with independent pytest."""

from collections import Counter, defaultdict
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from time import monotonic

from candidates import (
    ADDED, BASE, INVENTORY_TEST, MODES, ORIGINAL, PACKAGE, RENAMED, SIGNATURES,
    WATCH_TEST, WITNESS, clone_lane, git, make_case,
)

ROOT = Path(__file__).resolve().parent.parent
PRODUCT = "product-cli"
HELPERS = "ci-helpers"
CLI = "tools/ci/tests/test_cli_evidence.py::test_usage_console_help"
TARGETS = {
    PRODUCT: ("packages/aitm-usage/tests/", CLI),
    HELPERS: tuple(
        "tools/ci/tests/" + name
        for name in (
            "test_file_checks.py", "test_pytest_evidence.py", "test_python_gate.py",
            "test_verify_pr.py", "test_path_map.py", "test_tia_local.py",
        )
    ),
}
WORKERS = {PRODUCT: 3, HELPERS: 0}
INVENTORY_CASES = {"add", "rename", "delete"}


def read(path):
    return json.loads(path.read_bytes())


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def unique(items):
    result = set(items)
    if len(items) != len(result):
        raise ValueError("duplicate node IDs")
    return result


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Compare:
    def __init__(self, case, out, work):
        self.case = case
        self.out = out
        self.work = work
        self.tool = work / "tool"
        clone_lane(ROOT, self.tool, BASE)
        self.repo = work / "candidate"
        self.identity = make_case(self.tool, self.repo, case)
        self.suites = read(self.tool / "tools/ci/tia/suites.json")
        self.policy = read(self.tool / "tools/ci/policy.json")
        self.pytest_env = dict(
            PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PYTHONDONTWRITEBYTECODE="1",
            PYTHONPATH=str(self.tool / "tools/ci"),
        )
        self.timings = {}

    def run(self, label, argv, cwd, additions=None):
        argv = list(map(str, argv))
        stdout = self.out / f"{label}.stdout"
        stderr = self.out / f"{label}.stderr"
        command = {
            "argv": [
                arg.replace(str(self.work), "<scratch>").replace(str(self.out), "<evidence>")
                for arg in argv
            ],
            "cwd": str(cwd).replace(str(self.work), "<scratch>"),
        }
        started = monotonic()
        with stdout.open("w") as stream, stderr.open("w") as errors:
            result = subprocess.run(
                argv, cwd=cwd, env=os.environ | (additions or {}),
                timeout=1050, check=False, stdout=stream, stderr=errors,
            )
        seconds = round(monotonic() - started, 3)
        record = command | {"exit": result.returncode, "seconds": seconds}
        self.timings[label] = record
        write(self.out / "commands.json", self.timings)
        print(f"{label}: exit {result.returncode}, {seconds:.3f} s", flush=True)
        return result.returncode

    def install(self, lane, repo):
        status = self.run(lane + "-setup", (
            "uv", "sync", "--project", repo / PACKAGE, "--locked",
            "--python", sys.executable,
        ), repo)
        require(status == 0, f"uv sync failed for {lane}")

    def pytest(self, label, repo, profile, targets, *, collect=False):
        private = self.work / label
        private.mkdir()
        receipt = self.out / f"{label}.json"
        args = [
            repo / PACKAGE / ".venv/bin/python", "-m", "pytest", "-p", "pytest_evidence",
            "-q", "-p", "no:cacheprovider", "-c", repo / PACKAGE / "pyproject.toml",
            "-o", "addopts=", "--rootdir", repo, "--confcutdir", repo,
            "--basetemp", private / "fixtures", "--tb=short",
        ]
        workers = 0 if collect else WORKERS[profile]
        if workers:
            args += ["-p", "xdist.plugin", "-n", str(workers), "--dist", "worksteal"]
        if collect:
            args.append("--collect-only")
        env = self.pytest_env | {
            "AITM_CI_PYTEST_EVIDENCE": str(receipt),
            "TMPDIR": str(private),
            "TMP": str(private),
            "TEMP": str(private),
        }
        if not collect and profile == PRODUCT:
            env["AITM_CI_CHILD_EVIDENCE"] = "1"
        status = self.run(label, [*args, "--", *targets], repo, env)
        result = read(receipt)
        require(
            status in ({0} if collect else {0, 1}) and status == result["exit_code"]
            and result["schema"] == "aitm.pytest-evidence/v1"
            and not result["deselected"],
            f"invalid pytest receipt {label}",
        )
        if workers:
            result = reconcile(receipt, result, workers)
            write(self.out / f"{label}-reconciled.json", result)
        ids = unique(result["collected"])
        if collect:
            require(not result["reports"] and not result["children"] and ids,
                    f"invalid collection-only evidence {label}")
            return ids
        return outcomes(result, ids, status)

    def seal(self):
        self.install("collect", self.repo)
        collected = {
            profile: sorted(self.pytest(f"collect-{profile}", self.repo, profile, args, collect=True))
            for profile, args in TARGETS.items()
        }
        all_nodes = unique(collected[PRODUCT] + collected[HELPERS])
        mandatory = set(self.policy["required_tests"]) | {CLI}
        require(mandatory <= all_nodes, "mandatory IDs missing from independent collection")
        module = (
            WATCH_TEST if self.case in {"leaf", "dynamic"} else
            INVENTORY_TEST if self.case in INVENTORY_CASES else None
        )
        behavior = {node for node in all_nodes if node.partition("::")[0] == module}
        if self.case in {"shared", "transitive"}:
            behavior = all_nodes.copy()
        safety = all_nodes if self.case in {"shared", "transitive", "dynamic"} else behavior
        evidence = {
            "leaf": [f"{WATCH_TEST} imports host_watch; WatchSet startup reason asserted by {WITNESS}."],
            "transitive": [
                f"{WATCH_TEST} → host_watch.py → sources/scan.py::_directory",
                "tests/conftest.py → monitor_registry.py → sources/scan.py",
                "tests/conftest.py → host_fs.py also illustrates pytest fixture reach.",
            ],
            "shared": ["Pytest discovers tests/conftest.py for product test collection; the added non-autouse fixture has no consumer."],
            "docs": ["No root README runtime consumer found in the pinned product or helper test contract."],
            "dynamic": ["Nonliteral importlib loader in host_watch; leaf watcher test suite is the behavior bound and full is the safety bound."],
        }.get(self.case, [])
        if self.case in INVENTORY_CASES:
            expected = {
                "add": (True, True, False), "rename": (False, False, True),
                "delete": (False, False, False),
            }[self.case]
            observed = tuple(f"{INVENTORY_TEST}::{node}" in all_nodes
                             for node in (ORIGINAL, ADDED, RENAMED))
            require(observed == expected, "wrong independent inventory delta")
            evidence = [f"The existing {INVENTORY_TEST} module is the impact witness."]
        seal = {
            "case": self.case, "candidate": self.identity, "static_witness": evidence,
            "collected": collected, "mandatory": sorted(mandatory),
            "behavior": sorted(behavior), "safety": sorted(safety),
            "predicted_mode": MODES[self.case], "seed_witness": WITNESS if self.case in SIGNATURES else None,
        }
        path = self.out / "expectation.json"
        write(path, seal)
        return seal, sha256(path.read_bytes()).hexdigest()

    def probe(self, tree, label="probe"):
        status = self.run(label, (
            sys.executable, "-B", "-E", "-s", "-m", "tools.ci.tia.probe",
            "--repo", self.repo, "--parent", BASE, "--input", "pr",
            "--pr-head", self.identity["head"], "--tested-commit", self.identity["tested"],
            "--tested-tree", tree,
        ), self.tool)
        receipt = read(self.out / f"{label}.stdout")
        require(receipt["provenance"] == "local_advisory", "unexpected probe provenance")
        plan = receipt["plan"]
        require(status == (2 if plan["mode"] == "unavailable" else 0), "probe exit mismatch")
        return plan

    def lane(self, label, profiles, expected):
        repo = self.work / label
        clone_lane(self.repo, repo, self.identity["tested"])
        self.install(label, repo)
        results = {}
        for profile, targets in profiles.items():
            if targets:
                results[profile] = self.pytest(f"{label}-{profile}", repo, profile, targets)
            else:
                results[profile] = {}
            require(set(results[profile]) == set(expected[profile]),
                    f"{label} {profile} executed ID set differs from expectation")
        require(not git(repo, "status", "--porcelain", "--untracked-files=no"),
                f"tracked candidate tree drift in {label}")
        return results

    def labels(self, ids):
        overrides = {row["selector"]: row for row in self.suites["overrides"]}
        labels = set()
        for node in ids:
            source = node.partition("::")[0]
            selector = node.split("[", 1)[0]
            labels.add(overrides.get(selector, {}).get("suite", self.suites["modules"][source]["suite"]))
        return sorted(labels)

    def execute(self):
        identity = self.identity | {
            "case": self.case, "tool": BASE, "python": sys.version.split()[0],
            "workflow": git(ROOT, "rev-parse", "HEAD"),
            "workflow_blob": git(ROOT, "rev-parse", "HEAD:.github/workflows/shadow-423.yml"),
            "run": os.environ.get("GITHUB_RUN_ID"), "attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
            "image": os.environ.get("ImageOS", "") + ":" + os.environ.get("ImageVersion", ""),
            "arch": os.environ.get("RUNNER_ARCH"), "event": os.environ.get("GITHUB_EVENT_NAME"),
            "coverage": "disabled", "workers": WORKERS,
        }
        write(self.out / "identity.json", identity)
        (self.out / "tested-commit.txt").write_text(
            git(self.repo, "cat-file", "-p", self.identity["tested"]) + "\n"
        )
        (self.out / "patch.diff").write_text(
            git(self.repo, "diff", "--binary", BASE, self.identity["tested"]) + "\n"
        )
        seal, seal_sha = self.seal()
        plan = self.probe(self.identity["tree"])
        mode = plan["mode"]
        require(mode in {"full", "selected", "no-tests", "unavailable"}, "invalid plan mode")
        if mode != "unavailable":
            require(plan["snapshot"]["endpoint"] == {
                "commit": self.identity["tested"], "tree": self.identity["tree"],
            } and plan["snapshot"]["base"] == BASE, "probe attested wrong candidate")
        if self.case == "clean":
            wrong = make_case(self.tool, self.work / "wrong", "leaf")
            require(wrong["tree"] != self.identity["tree"], "wrong-tree control unchanged")
            refusal = self.probe(wrong["tree"], label="wrong-tree")
            require(refusal["mode"] == "unavailable" and not refusal["selected"],
                    "probe did not fail closed for wrong tree")
        status = self.run("path-map", (
            sys.executable, self.tool / "tools/ci/path_map.py",
            "--map", self.tool / "tools/ci/path_map.json", "--base", BASE,
            "--candidate", self.identity["tested"], "--pull-number", "423",
        ), self.repo)
        require(status == 0, "pinned path map refused experiment input")
        mapping = read(self.out / "path-map.stdout")
        planned = {profile: [] for profile in TARGETS}
        for row in plan["selected"]:
            planned[row["profile"]].append(row["nodeid"])
        require(all(unique(ids) <= set(seal["collected"][profile]) for profile, ids in planned.items()),
                "selector assigned IDs outside independent collection")
        if mode == "full":
            require(all(set(ids) == set(seal["collected"][profile]) for profile, ids in planned.items()),
                    "fallback plan does not cover exact candidate")
        if mode in {"no-tests", "unavailable"}:
            require(not any(planned.values()), f"{mode} returned runnable nodes")
        full = self.lane("full", TARGETS, seal["collected"])
        selected_args = TARGETS if mode == "full" else planned
        selected = (
            self.lane("selected", selected_args, planned)
            if mode in {"selected", "full"} else {profile: {} for profile in TARGETS}
        )
        all_full = flatten(full)
        all_selected = flatten(selected)
        mismatches = different(all_full, all_selected)
        failed = failures(all_full)
        seed_valid = self.signature("full", all_full) if self.case in SIGNATURES else None
        unexpected = (
            bool(failed) if self.case not in SIGNATURES else not seed_valid
        )
        repeat = None
        if mismatches or unexpected:
            repeat_full = self.lane("repeat-full", TARGETS, seal["collected"])
            repeat_selected = (
                self.lane("repeat-selected", selected_args, planned)
                if mode in {"selected", "full"} else selected
            )
            repeat = {
                "full_changes": different(all_full, flatten(repeat_full)),
                "selected_changes": different(all_selected, flatten(repeat_selected)),
                "mismatches": different(flatten(repeat_full), flatten(repeat_selected)),
                "seed_signature": self.signature("repeat-full", flatten(repeat_full))
                if self.case in SIGNATURES else None,
            }
        stats = {
            profile: self.stats(profile, full[profile], selected[profile], mode, seal)
            for profile in TARGETS
        }
        whole = self.stats(None, all_full, all_selected, mode, seal)
        write(self.out / "summary.json", {
            "identity": identity, "seal_sha256": seal_sha, "mode": mode,
            "reasons": plan["reasons"], "path_map_mode": mapping["mode"],
            "plan_seconds": self.timings["probe"]["seconds"],
            "map_seconds": self.timings["path-map"]["seconds"],
            "profiles": stats, "union": whole, "repeat": repeat,
            "seed_witness": seal["seed_witness"],
            "seed_full_signature": seed_valid,
            "seed_selected_signature": self.signature("selected", all_selected)
            if seed_valid else None,
        })

    def signature(self, lane, result):
        if WITNESS not in failures(result):
            return False
        diagnostic = (self.out / f"{lane}-{PRODUCT}.stdout").read_text()
        return WITNESS.split("::")[1] in diagnostic and SIGNATURES[self.case] in diagnostic

    def stats(self, profile, full, selected, mode, seal):
        full_ids, selected_ids = set(full), set(selected)
        behavior, safety = (full_ids & set(seal[key]) for key in ("behavior", "safety"))
        mandatory = full_ids & set(seal["mandatory"])
        profiles = [profile] if profile else TARGETS
        full_wall = sum(self.timings[f"full-{key}"]["seconds"] for key in profiles)
        selected_wall = sum(self.timings.get(f"selected-{key}", {}).get("seconds", 0)
                            for key in profiles)
        result = {
            "full": len(full), "full_seconds": round(full_wall, 3),
            "full_outcomes": dict(Counter(disposition(phases) for phases in full.values())),
            "oracle_failing": sorted(failures(full)),
            "behavior_suite_bound": self.labels(behavior),
        }
        if mode == "unavailable":
            return result | {"selected": None, "selected_seconds": None}
        excess = selected_ids - (behavior | mandatory)
        return result | {
            "selected": len(selected), "selected_seconds": round(selected_wall, 3),
            "fraction": len(selected) / len(full), "missed_failing": sorted(failures(full) - selected_ids),
            "mismatch": different(full, selected), "omitted_behavior": sorted(behavior - selected_ids),
            "omitted_mandatory": sorted(mandatory - selected_ids),
            "extra_behavior": sorted(excess), "extra_safety": sorted(selected_ids - (safety | mandatory)),
            "selected_suites": self.labels(selected_ids), "extra_suites": self.labels(excess),
            "extra_modules": sorted({node.partition("::")[0] for node in excess}),
            "net_seconds": round(full_wall - selected_wall - self.timings["probe"]["seconds"], 3)
            if not profile else None,
        }


def reconcile(path, controller, count):
    workers = [read(path.with_name(f"{path.stem}-gw{i}{path.suffix}")) for i in range(count)]
    require(len(list(path.parent.glob(f"{path.stem}-gw*{path.suffix}"))) == count,
            "unexpected worker receipts")
    require(not controller["collected"] and not controller["children"],
            "unexpected controller inventory or children")
    collected = workers[0]["collected"]
    require(all(worker["collected"] == collected and not worker["deselected"]
                and worker["exit_code"] in {0, 1} and worker["schema"] == controller["schema"]
                for worker in workers), "workers disagree about collection or exit status")
    worker_rows = Counter(json.dumps(row, sort_keys=True) for worker in workers for row in worker["reports"])
    require(worker_rows == Counter(json.dumps(row, sort_keys=True) for row in controller["reports"]),
            "worker/controller phase rows do not reconcile")
    return controller | {
        "collected": collected, "children": [child for worker in workers for child in worker["children"]],
    }


def outcomes(receipt, ids, status):
    phases = defaultdict(dict)
    for row in receipt["reports"]:
        node, when = row["nodeid"], row["when"]
        require(node in ids and when in {"setup", "call", "teardown"} and when not in phases[node],
                "unexpected or duplicate pytest phase")
        phases[node][when] = [row["outcome"], row["wasxfail"], row["skip_reason"]]
    require(set(phases) == ids, "an expected node has no outcome")
    for observed in phases.values():
        require("setup" in observed and "teardown" in observed
                and ("call" in observed) == (observed["setup"][0] == "passed"),
                "incomplete pytest phases")
    require(status == int(bool(failures(phases))), "pytest exit does not reconcile with outcomes")
    return dict(phases)


def disposition(phases):
    states = {outcome[0] for outcome in phases.values()}
    if "failed" in states:
        return "failed"
    return "skipped" if "skipped" in states else "passed"


def failures(result):
    return {node for node, phases in result.items() if disposition(phases) == "failed"}


def different(left, right):
    return sorted(node for node in left.keys() & right.keys() if left[node] != right[node])


def flatten(profiles):
    result = {}
    for lane in profiles.values():
        require(not result.keys() & lane.keys(), "profiles overlap")
        result.update(lane)
    return result


if __name__ == "__main__":
    case, evidence = sys.argv[1:]
    require(case in MODES and sys.version_info[:3] == (3, 13, 9), "wrong case or interpreter")
    destination = Path(evidence).resolve()
    destination.mkdir()
    with tempfile.TemporaryDirectory(prefix="comparison-") as work:
        Compare(case, destination, Path(work).resolve()).execute()
