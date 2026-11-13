"""Run exact live #103 readback and repeat the local controller catalog."""

import argparse
from copy import deepcopy
from dataclasses import replace
from io import BytesIO
import json
import os
from pathlib import Path
import platform
import plistlib
import subprocess
import sys
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from catalog import (
    CHILDREN, CLI_TEST, SERVICE_TEST, admit_local, evaluate_help, evaluate_service,
    run_behaviors, sanitized, sha,
)

REPO = "kburson/aitm"
REPO_ID = 1450406435
RUN_ID = 43257314192
WORKFLOW_ID = 412848571
ARTIFACT_ID = 13962226641
ARTIFACT_SHA = "9a88fe3914b7df0765b5f7368c4eed118e5725041db5dd1f79363045d16bce02"
PRODUCT = "766504a02aaeb9dda339d588172dd7d5bdbd2b3f"
TREE = "6f1ae4a5707f2344bbeb4c15efdb823480866feb"
PACKAGE = "packages/aitm-usage"
WORKFLOW = ".github/workflows/ci.yml"
POLICY = "tools/ci/policy.json"
GATE = "tools/ci/python_gate.py"
FIELDS = {
    "inventory": "pytest.json", "outcomes": "pytest.json", "coverage": "product-coverage.json",
    "product-inventory": "product-inventory.json", "helpers": "helper-coverage.json",
    "child-evidence": "children.json", "capability": "capability.json",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def capture(command, **kwargs):
    return subprocess.check_output(command, **kwargs)


def github(path):
    return capture(("gh", "api", f"repos/{REPO}/{path}"))


def git(root, *args):
    return capture(("git", "-C", str(root), *args))


def gate_inputs(root, fixture):
    pins = {}
    for path in (WORKFLOW, POLICY, GATE):
        data = git(root, "show", f"{PRODUCT}:{path}")
        (fixture / Path(path).name).write_bytes(data)
        pins[path] = sha(data)
    return pins


def admit_ci(root, fixture):
    live = json.loads(github("branches/trunk"))["commit"]["sha"]
    require(live == PRODUCT and git(root, "rev-parse", f"{PRODUCT}^{{tree}}").decode().strip() == TREE,
            "live trunk or pinned tree differs")
    meta = json.loads(github(f"actions/runs/{RUN_ID}/attempts/1"))
    require((meta["id"], meta["run_attempt"], meta["head_sha"], meta["workflow_id"], meta["path"],
             meta["event"], meta["head_branch"], meta["status"], meta["conclusion"],
             meta["repository"]["id"], meta["head_repository"]["id"]) ==
            (RUN_ID, 1, PRODUCT, WORKFLOW_ID, WORKFLOW, "push", "trunk", "completed", "success", REPO_ID, REPO_ID),
            "canonical run identity differs")
    all_runs = json.loads(capture(("gh", "api", f"repos/{REPO}/actions/workflows/{WORKFLOW_ID}/runs",
                                  "--method", "GET", "-f", "branch=trunk", "-f", "event=push",
                                  "-f", f"head_sha={PRODUCT}")))
    latest = max(all_runs["workflow_runs"], key=lambda item: (item["run_number"], item["run_attempt"]))
    require(all_runs["total_count"] == len(all_runs["workflow_runs"])
            and (latest["id"], latest["run_attempt"]) == (RUN_ID, 1), "canonical run no longer latest")
    jobs = json.loads(github(f"actions/runs/{RUN_ID}/attempts/1/jobs"))["jobs"]
    lanes = ("python", "quality", "file-checks", "collect-evidence")
    for lane in lanes:
        matching = [job for job in jobs if job["name"] == lane]
        require(len(matching) == 1, f"missing or duplicate CI lane {lane}")
        job = matching[0]
        require((job["run_id"], job["run_attempt"], job["head_sha"], job["status"], job["conclusion"]) ==
                (RUN_ID, 1, PRODUCT, "completed", "success"), f"CI lane {lane} differs")
    artifact = json.loads(github(f"actions/artifacts/{ARTIFACT_ID}"))
    provenance = artifact["workflow_run"]
    require((artifact["id"], artifact["name"], artifact["expired"], artifact["digest"],
             provenance["id"], provenance["head_sha"], provenance["head_branch"],
             provenance["repository_id"], provenance["head_repository_id"]) ==
            (ARTIFACT_ID, f"aitm-ci-python-a1", False, f"sha256:{ARTIFACT_SHA}",
             RUN_ID, PRODUCT, "trunk", REPO_ID, REPO_ID), "artifact provenance differs")
    data = github(f"actions/artifacts/{ARTIFACT_ID}/zip")
    require(sha(data) == ARTIFACT_SHA, "downloaded artifact digest differs")
    with ZipFile(BytesIO(data)) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), "duplicate archive members")
        for name in set(FIELDS.values()):
            (fixture / name).write_bytes(archive.read(name))
    pins = gate_inputs(root, fixture)
    policy = json.loads((fixture / "policy.json").read_bytes())
    require(set(policy["required_children"]) == set(CHILDREN), "required child labels differ")
    require(SERVICE_TEST in policy["required_tests"] and CLI_TEST not in policy["required_tests"],
            "required ID mapping differs")
    gate = run_gate(fixture, fixture / "pytest.json")
    require(gate["passed"], "exact pinned full gate refused baseline")
    require(json.loads(github("branches/trunk"))["commit"]["sha"] == PRODUCT, "trunk moved during read")
    return {"repo": REPO, "run": RUN_ID, "attempt": 1, "product_commit": PRODUCT, "tree": TREE,
            "workflow_id": WORKFLOW_ID, "job_ids": {job["name"]: job["id"] for job in jobs},
            "artifact": ARTIFACT_ID, "artifact_sha256": ARTIFACT_SHA, "tracked_input_hashes": pins,
            "required_test_ids": policy["required_tests"], "required_children": policy["required_children"],
            "gate": gate}


def run_gate(fixture, outcomes):
    command = [sys.executable, str(fixture / "python_gate.py"), "--policy", str(fixture / "policy.json"),
               "--mode", "push"]
    for key, name in FIELDS.items():
        path = outcomes if key in {"inventory", "outcomes"} else fixture / name
        command.extend((f"--{key}", str(path)))
    run = subprocess.run(command, check=False, capture_output=True, timeout=15)
    require(run.returncode in (0, 1), "gate command errored")
    return json.loads(run.stdout)


def negative_ci(fixture):
    document = json.loads((fixture / "pytest.json").read_bytes())
    path = fixture / "changed-outcomes.json"
    result = {}
    for case in ("omitted-required-id", "renamed-required-id", "required-skip", "required-xfail"):
        altered = deepcopy(document)
        if case == "omitted-required-id":
            altered["collected"].remove(SERVICE_TEST)
            altered["reports"] = [row for row in altered["reports"] if row["nodeid"] != SERVICE_TEST]
        if case == "renamed-required-id":
            renamed = SERVICE_TEST + "_renamed"
            altered["collected"][altered["collected"].index(SERVICE_TEST)] = renamed
            for row in altered["reports"]:
                if row["nodeid"] == SERVICE_TEST:
                    row["nodeid"] = renamed
        if case in {"required-skip", "required-xfail"}:
            [report] = [row for row in altered["reports"] if row["nodeid"] == SERVICE_TEST and row["when"] == "call"]
            report.update(outcome="skipped", skip_reason="synthetic #276 control")
            if case == "required-xfail":
                report["wasxfail"] = True
        path.write_text(json.dumps(altered))
        disposition = run_gate(fixture, path)
        require(not disposition["passed"] and f"required test did not pass: {SERVICE_TEST}" in disposition["failures"],
                f"required ID control escaped refusal: {case}")
        if case == "required-xfail":
            require(any("unexpected xfail" in error for error in disposition["failures"]), "xfail reason missing")
        result[case] = disposition
    return result


def materialize(root, scratch, python, uv):
    archive = subprocess.Popen(("git", "-C", str(root), "archive", PRODUCT, PACKAGE), stdout=subprocess.PIPE)
    with archive:
        subprocess.run(("/usr/bin/tar", "-xf", "-", "-C", str(scratch)),
                       stdin=archive.stdout, check=True, timeout=30)
        require(archive.wait(timeout=10) == 0, "pinned Git archive failed")
    product = scratch / PACKAGE
    runtime = scratch / "runtime"
    environment = {**os.environ, "UV_PROJECT_ENVIRONMENT": str(runtime),
                   "UV_CACHE_DIR": str(scratch / "uv-cache")}
    uv_version = capture((str(uv), "--version")).decode().strip()
    require(uv_version.split()[1] == "0.10.6", "wrong uv version")
    setup = subprocess.run((str(uv), "sync", "--locked", "--no-config", "--no-dev", "--python", str(python),
                            "--project", str(product)), check=False, capture_output=True, env=environment, timeout=120)
    require(setup.returncode == 0, "isolated pinned product setup failed")
    executable = runtime / "bin/python"
    version = capture((str(executable), "-I", "-c", "import platform; print(platform.python_version())")).decode().strip()
    require(version == "3.13.9", "wrong runtime Python")
    return executable, runtime / "bin/aitm-usage", product / "tests/fixtures", uv_version


def filesystem_type(scratch):
    device = capture(("/bin/df", "-P", str(scratch))).decode().splitlines()[-1].split()[0]
    info = plistlib.loads(capture(("/usr/sbin/diskutil", "info", "-plist", device)))
    filesystem = info.get("FilesystemType")
    require(platform.system() == "Darwin" and filesystem == "apfs", "local host is not Darwin APFS")
    return filesystem


def log_outcome(label, outcome, iteration, paths):
    def process_record(process):
        stdout, stderr = (sanitized(data, paths).decode("utf-8", "replace")
                          for data in (process.stdout, process.stderr))
        return {"operation": process.operation, "pid": process.pid, "parent_pid": process.parent_pid,
                "returncode": process.returncode, "seconds": process.seconds,
                "stdout": stdout, "stderr": stderr, "sanitized_stdout_sha256": sha(stdout.encode()),
                "sanitized_stderr_sha256": sha(stderr.encode())}

    return {"iteration": iteration, "case": label, "passed": outcome.passed, "reason": outcome.reason,
            "processes": [process_record(process) for process in outcome.processes]}


def local_controls(last):
    parent = os.getpid()
    [help_process] = last["cli-help"].processes
    register, collect, status = last["service-one-shot"].processes
    missing = {**last, "service-one-shot": evaluate_service(register, None, status, parent)}
    altered = {**last, "cli-help": evaluate_help(replace(help_process, stdout=b"unexpected help output"), parent)}
    result = {"missing-process": admit_local(missing), "output-mismatch": admit_local(altered)}
    for name, disposition in result.items():
        require(not disposition["passed"] and bool(disposition["failed"]), f"local control accepted: {name}")
    return result


def rehearse(args):
    with TemporaryDirectory(prefix="aitm276-", dir="/private/tmp") as folder:
        scratch = Path(folder)
        volume = filesystem_type(scratch)
        ci_files = scratch / "ci-evidence"
        ci_files.mkdir()
        canonical = admit_ci(args.repo, ci_files)
        negative = negative_ci(ci_files)
        executable, console, fixtures, uv = materialize(args.repo, scratch, args.python, args.uv)
        results = []
        last = None
        with args.diagnostics.open("w") as stream:
            for number in range(1, args.repetitions + 1):
                root = scratch / f"case-{number:02}"
                root.mkdir(mode=0o700)
                last = run_behaviors(executable, console, root, fixtures, number, os.getpid())
                results.append(admit_local(last))
                for label, outcome in last.items():
                    row = log_outcome(label, outcome, number, [(root, "<case>"), (scratch, "<scratch>")])
                    stream.write(json.dumps(row, sort_keys=True) + "\n")
                stream.flush()
        require(all(row["passed"] for row in results), "an honest repetition failed")
        require(last is not None, "no repetitions ran")
        negative.update(local_controls(last))
        return {"spike": 276, "status": "catalog-shadow-pass", "production_qualification": "unqualified",
                "exact_ci": canonical, "local_host": {"os": platform.system(), "release": platform.mac_ver()[0],
                "arch": platform.machine(), "filesystem": volume, "python": "3.13.9", "uv": uv},
                "catalog": CHILDREN, "repetitions": len(results), "passing_repetitions": sum(row["passed"] for row in results),
                "passing_behavior_invocations": sum(row["passed"] for row in results) * len(CHILDREN),
                "negative": negative, "diagnostics_sha256": sha(args.diagnostics.read_bytes())}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--python", required=True, type=Path)
    parser.add_argument("--uv", required=True, type=Path)
    parser.add_argument("--repetitions", type=int, default=20)
    parser.add_argument("--diagnostics", required=True, type=Path)
    args = parser.parse_args()
    require(args.repetitions > 0, "repetitions must be positive")
    print(json.dumps(rehearse(args), indent=2, sort_keys=True))
