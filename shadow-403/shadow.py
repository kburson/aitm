"""Run one exact advisory qualification case on an isolated GitHub runner."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from time import monotonic


TOOL = Path.cwd()
PRODUCT = Path("packages/aitm-usage")
CLI = "tools/ci/tests/test_cli_evidence.py::test_usage_console_help"
HELPERS = (
    "test_python_gate.py",
    "test_pytest_evidence.py",
    "test_verify_pr.py",
    "test_file_checks.py",
    "test_path_map.py",
    "test_tia_local.py",
)
SCOPE = "aitm-403-hosted-advisory/v1"
REPOSITORY = "kburson/aitm"
CONTROL_FILES = (
    ".github/workflows/ci.yml", "tools/ci/path_map.py", "tools/ci/path_map.json",
    "tools/ci/policy.json", "tools/ci/pytest_evidence.py", "tools/ci/tia/edges.json",
    "tools/ci/tia/suites.json", "tools/ci/tia/snapshot.py", "tools/ci/python_gate.py",
    "tools/ci/verify_pr.py", "tools/ci/tia/working_tree_run.py",
    "packages/aitm-usage/pyproject.toml", "packages/aitm-usage/uv.lock",
)


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def git(repo, *args):
    return subprocess.check_output(["git", *args], cwd=repo).strip()


def timed(label, command, cwd, out, env=None):
    start = monotonic()
    with (out / (label + ".stdout")).open("w") as stdout, (
        out / (label + ".stderr")
    ).open("w") as stderr:
        proc = subprocess.run(command, cwd=cwd, env=env, stdout=stdout, stderr=stderr, timeout=1000)
    seconds = round(monotonic() - start, 3)
    print(f"{label}: exit {proc.returncode}, {seconds}s", flush=True)
    return proc.returncode, seconds


def read_json(path):
    return json.loads(path.read_bytes())


def validate(receipt, expected, returncode):
    if receipt["schema"] != "aitm.pytest-evidence/v1" or receipt["exit_code"] != returncode:
        raise ValueError("exit code or schema mismatch")
    actual = receipt["collected"]
    if not actual or set(actual) != set(expected) or len(actual) != len(set(actual)) or receipt["deselected"]:
        raise ValueError("collection mismatch")
    phases = {node: {} for node in actual}
    for row in receipt["reports"]:
        node, phase = row["nodeid"], row["when"]
        if node not in phases or phase in phases[node] or phase not in {"setup", "call", "teardown"}:
            raise ValueError("unexpected or duplicated phase")
        phases[node][phase] = (row["outcome"], row["wasxfail"])
    outcomes = {}
    for node, observed in phases.items():
        if set(observed) != {"setup", "call", "teardown"}:
            raise ValueError(f"incomplete outcome for {node}")
        if observed["setup"] != ("passed", False) or observed["teardown"] != ("passed", False):
            raise ValueError(f"nonpassing custody phase for {node}")
        outcome, expected_failure = observed["call"]
        if outcome not in {"passed", "failed"} or expected_failure:
            raise ValueError(f"unsupported outcome for {node}")
        outcomes[node] = outcome
    if returncode != int("failed" in outcomes.values()):
        raise ValueError("exit disagrees with outcomes")
    return outcomes


def recorded_full(repo, out, env, prefix, group, targets, expected=None, workers=0):
    evidence = out / f"{prefix}-{group}.json"
    cwd = repo / PRODUCT if group == "product" else repo
    baseline = tempfile.mkdtemp(prefix=f"a403-{prefix}-{group}-", dir="/var/tmp")
    launch_env = dict(env)
    launch_env["AITM_CI_PYTEST_EVIDENCE"] = str(evidence)
    if group == "product":
        launch_env["AITM_CI_CHILD_EVIDENCE"] = "1"
    command = [
        str(repo / PRODUCT / ".venv/bin/python"), "-m", "pytest", "-p", "pytest_evidence",
        "--rootdir", str(repo), "-q", "-p", "no:cacheprovider", "--basetemp", baseline,
    ]
    if workers:
        command += ["-n", str(workers), "--dist", "worksteal"]
    status, seconds = timed(f"{prefix}-{group}", command + targets, cwd, out, launch_env)
    if workers:
        reconciled = reconcile_parallel(evidence, workers, status)
        evidence = out / f"{prefix}-{group}-reconciled.json"
        write(evidence, reconciled)
    receipt = read_json(evidence)
    if expected is None:
        expected = receipt["collected"]
    outcomes = validate(receipt, expected, status)
    return {"seconds": seconds, "exit": status, "receipt": evidence.name, "outcomes": outcomes}


def run_groups(repo, out, env, prefix, targets, expected=None, workers=0):
    results = {}
    for group, args in targets.items():
        if args:
            results[group] = recorded_full(
                repo, out, env, prefix, group, args,
                None if expected is None else expected[group],
                workers if group == "product" else 0,
            )
        else:
            results[group] = {"seconds": 0, "exit": 0, "receipt": None, "outcomes": {}}
    return results


def summarize(results):
    return {
        group: {
            key: value for key, value in result.items() if key != "outcomes"
        } | {
            "counts": dict(Counter(result["outcomes"].values())),
            "failures": sorted(node for node, status in result["outcomes"].items() if status != "passed"),
        }
        for group, result in results.items()
    }


def compare(full, subset):
    reference = {node: status for group in full.values() for node, status in group["outcomes"].items()}
    other = {node: status for group in subset.values() for node, status in group["outcomes"].items()}
    return {
        "missed_failures": sorted(node for node, status in reference.items() if status == "failed" and node not in other),
        "different_outcomes": sorted(node for node, status in other.items() if reference.get(node) != status),
    }


def control_digests(repo, oid):
    values = {}
    for path in CONTROL_FILES:
        proc = subprocess.run(["git", "show", f"{oid}:{path}"], cwd=repo, capture_output=True)
        values[path] = None if proc.returncode else sha256(proc.stdout).hexdigest()
    return values


def absolute_targets(repo, nodeids):
    return [str(repo / node) for node in nodeids]


def reconcile_parallel(destination, worker_count, status):
    controller = read_json(destination)
    if (
        controller["schema"] != "aitm.pytest-evidence/v1"
        or controller["exit_code"] != status
        or status not in {0, 1}
        or any(controller[field] for field in ("collected", "deselected", "children"))
    ):
        raise ValueError("inconsistent pytest controller evidence")
    expected = [
        destination.with_name(f"{destination.stem}-gw{i}{destination.suffix}")
        for i in range(worker_count)
    ]
    if set(destination.parent.glob(f"{destination.stem}-gw*{destination.suffix}")) != set(expected):
        raise ValueError("missing or unexpected worker receipts")
    workers = [read_json(file) for file in expected]
    collected = workers[0]["collected"]
    if not collected or any(
        worker["schema"] != controller["schema"] or worker["collected"] != collected
        or worker["deselected"] or worker["exit_code"] not in {0, 1}
        for worker in workers
    ):
        raise ValueError("inconsistent pytest worker inventories")
    reports = Counter(json.dumps(row, sort_keys=True) for worker in workers for row in worker["reports"])
    if reports != Counter(json.dumps(row, sort_keys=True) for row in controller["reports"]):
        raise ValueError("pytest controller and worker phase reports disagree")
    children = [child for worker in workers for child in worker["children"]]
    return dict(controller, collected=collected, children=children)


def probe(repo, case, out, env, label="probe"):
    command = [sys.executable, "-B", "-E", "-s", "-m", "tools.ci.tia.probe",
        "--repo", str(repo), "--parent", case["base"], "--input", "pr",
        "--pr-head", case["head"], "--tested-commit", case["tested"], "--tested-tree", case["tree"]]
    status, seconds = timed(label, command, TOOL, out, env)
    receipt = read_json(out / (label + ".stdout"))
    assert receipt["provenance"] == "local_advisory"
    plan = receipt["plan"]
    assert status == (2 if plan["mode"] == "unavailable" else 0)
    return plan, seconds


def run(case, out):
    temp = Path(os.environ["RUNNER_TEMP"])
    repo = temp / "candidate"
    env = os.environ.copy()
    env.update(
        GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_COUNT="0",
        PYTHONDONTWRITEBYTECODE="1", GIT_TERMINAL_PROMPT="0",
        PYTHONPATH=str(TOOL / "tools/ci"),
    )
    subprocess.run(["git", "init", "-q", str(repo)], check=True, env=env)
    subprocess.run(["git", "remote", "add", "origin", f"https://github.com/{REPOSITORY}.git"], check=True, cwd=repo, env=env)
    subprocess.run(["git", "fetch", "-q", "origin", f"refs/pull/{case['pr']}/merge"], check=True, cwd=repo, env=env)
    subprocess.run(["git", "checkout", "-q", "--detach", "FETCH_HEAD"], check=True, cwd=repo, env=env)
    assert git(repo, "rev-parse", "HEAD").decode() == case["tested"]
    assert git(repo, "rev-parse", "HEAD^{tree}").decode() == case["tree"]
    assert git(repo, "show", "-s", "--format=%P", "HEAD").decode().split() == [case["base"], case["head"]]
    assert git(TOOL, "rev-parse", "HEAD").decode() == case["tool"]
    assert sys.version_info[:3] == (3, 13, 9)
    identity = case | {
        "schema": SCOPE, "run": int(os.environ["GITHUB_RUN_ID"]),
        "attempt": int(os.environ["GITHUB_RUN_ATTEMPT"]),
        "workflow": os.environ["GITHUB_SHA"], "image": os.environ["ImageOS"] + ":" + os.environ["ImageVersion"],
        "runner_os": os.environ["RUNNER_OS"], "arch": os.environ["RUNNER_ARCH"],
        "controls": {name: control_digests(repo, case[name]) for name in ("base", "tested")},
        "tool_controls": control_digests(TOOL, case["tool"]),
    }
    write(out / "identity.json", identity)
    for name in ("path_map.py", "path_map.json"):
        with (out / name).open("wb") as stream:
            subprocess.run(["git", "show", f"{case['base']}:tools/ci/{name}"], cwd=repo, stdout=stream, check=True)
    code, map_time = timed(
        "path-map", [sys.executable, str(out / "path_map.py"), "--map", str(out / "path_map.json"),
                     "--base", case["base"], "--candidate", case["tested"], "--pull-number", str(case["pr"])],
        repo, out, env,
    )
    assert code == 0
    mapping = read_json(out / "path-map.stdout")
    planned, plan_time = probe(repo, case, out, env)
    mode = planned["mode"]
    assert mode == ("selected" if case["case"] == "narrow" else "full"), planned["reasons"]
    snapshot = planned["snapshot"]
    assert snapshot["base"] == case["base"]
    assert snapshot["endpoint"] == {"commit": case["tested"], "tree": case["tree"]}
    agreement = snapshot["source"]["path_agreement"]
    assert not agreement["divergence_only"] and not agreement["tested_only"]
    if case["case"] == "narrow":
        assert snapshot["source"]["merge_base"]["commit"] != case["base"]
    controls = {}
    if case["case"] == "narrow":
        for label, override in (
            ("wrong-tree", {"tree": git(repo, "rev-parse", f"{case['base']}^{{tree}}").decode()}),
            ("wrong-parent", {"head": case["base"]}),
        ):
            invalid, _ = probe(repo, case | override, out, env, label)
            assert invalid["mode"] == "unavailable" and not invalid["selected"]
            controls[label] = invalid["reasons"]
    code, setup = timed("setup", ["uv", "sync", "--project", str(repo / PRODUCT), "--locked", "--python", sys.executable], TOOL, out, env)
    assert code == 0
    interpreter = subprocess.check_output(
        [str(repo / PRODUCT / ".venv/bin/python"), "-c", "from pathlib import Path; import sys; print(Path(sys._base_executable).resolve())"],
        env=env, text=True,
    ).strip()
    assert Path(interpreter) == Path(sys.executable).resolve(), interpreter
    write(out / "interpreter.json", {"python": interpreter, "version": list(sys.version_info[:3])})
    product_args = ["tests", str(repo / CLI.split("::")[0])]
    helper_args = [str(repo / "tools/ci/tests" / name) for name in HELPERS]
    workers = 3
    groups = {"product-cli":"product", "ci-helpers":"helpers"}
    assignments = {group: [] for group in groups.values()}
    for row in planned["selected"]:
        assignments[groups[row["profile"]]].append(row["nodeid"])
    baseline = None
    selected = None
    watch = "packages/aitm-usage/tests/test_host_watch.py"
    if mode == "selected":
        assert len(set(assignments["product"])) == len(assignments["product"])
        assert set(assignments["product"]) - {CLI}
        assert all(item.startswith(watch+"::") or item == CLI for item in assignments["product"])
        old = temp / "baseline"
        subprocess.run(["git","worktree","add","--detach",str(old),case["base"]],cwd=repo,env=env,check=True)
        assert not git(repo, "diff", "--name-only", case["base"], case["tested"], "--", watch)
        baseline_status, _ = timed("baseline-setup", ["uv", "sync", "--project", str(old / PRODUCT),
                                        "--locked","--python",sys.executable], TOOL, out, env)
        assert baseline_status == 0
        baseline = run_groups(old, out, env, "baseline", {"product": [str(old / watch)]}, workers=workers)
        assert set(baseline["product"]["outcomes"].values()) == {"passed"}
        selected = run_groups(
            repo, out, env, "selected",
            {group: absolute_targets(repo, ids) for group, ids in assignments.items()},
            expected=assignments, workers=workers,
        )
    full = run_groups(repo, out, env, "full", {"product": product_args, "helpers": helper_args}, workers=workers)
    assert len(full["product"]["outcomes"]) == 1525 and len(full["helpers"]["outcomes"]) == 251
    if mode == "full":
        assert all(set(assignments[group]) == set(full[group]["outcomes"]) for group in assignments)
        assert any(item["code"] == "shared-conftest" for path in planned["selection"]["paths"]
                   for item in path["uncertainties"])
        selected = full
    map_mode = mapping["mode"]
    if map_mode == "full":
        mapped = full
    else:
        assert map_mode in {"mapped", "checks"}
        selected_product = run_groups(
            repo, out, env, "mapped", {"product": absolute_targets(repo, mapping["tests"])},
            workers=workers,
        )
        mapped = selected_product | {"helpers": full["helpers"]}
    if case["case"] == "narrow":
        full_receipt = read_json(out / full["product"]["receipt"])
        incomplete = deepcopy(full_receipt)
        incomplete["reports"].pop()
        try:
            validate(incomplete, full_receipt["collected"], full_receipt["exit_code"])
        except ValueError as error:
            controls["incomplete-full"] = str(error)
        else:
            raise AssertionError("accepted incomplete full outcome")
    reread, _ = probe(repo, case, out, env, "probe-reread")
    assert reread["mode"] == mode and reread["snapshot"] == snapshot and reread["selected"] == planned["selected"]
    assert git(repo, "rev-parse", "HEAD").decode() == case["tested"]
    assert not git(repo, "status", "--porcelain", "--untracked-files=no")
    comparison = compare(full, selected)
    assert not any(comparison.values())
    failures = sorted(node for group in full.values() for node, status in group["outcomes"].items() if status == "failed")
    if mode == "selected":
        assert failures and all(node.startswith(watch + "::") for node in failures)
        assert all(baseline["product"]["outcomes"][node] == "passed" for node in failures)
        witnessed = {entry["key"][-1] for entry in planned["selection"]["witnesses"] if entry["hops"]}
        assert set(failures) <= witnessed
    else:
        assert not failures
    write(out / "summary.json", identity | {
        "full": summarize(full),
        "baseline": summarize(baseline) if baseline else None,
        "suite": {
            "plan": planned, "seconds": plan_time, "outcomes": summarize(selected),
            "execution_source": "shared-full-run" if mode == "full" else "measured",
            "comparison": compare(full, selected),
        },
        "path_map": {
            "decision": mapping, "seconds": map_time, "outcomes": summarize(mapped),
            "execution_source": "shared-full-run" if map_mode == "full" else "measured-product-reused-helpers",
            "comparison": compare(full, mapped),
        },
        "setup_seconds": setup, "workers": workers, "negative_controls": controls,
    })


if __name__ == "__main__":
    name, matrix_path, output = sys.argv[1:]
    cases = read_json(Path(matrix_path))
    case = next(record for record in cases if record["case"] == name)
    output = Path(output)
    output.mkdir(parents=True)
    run(case, output)
