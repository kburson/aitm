"""Collect product-suite diagnostics on a separate macOS worker principal."""

from collections import Counter
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import plistlib
import pwd
import shutil
import stat
import subprocess
import sys
import tempfile
from time import monotonic

BASE = "766504a02aaeb9dda339d588172dd7d5bdbd2b3f"
PRODUCT = "packages/aitm-usage"
CLI = "tools/ci/tests/test_cli_evidence.py::test_usage_console_help"
SERVICE = PRODUCT + "/tests/test_service.py::test_one_shot_status_uses_collecting_subprocess_pid"
TARGETS = (PRODUCT + "/tests", CLI.partition("::")[0])
WORKER = "nobody"


def require(check, reason):
    if not check:
        raise ValueError(reason)


def hash_bytes(data):
    return sha256(data).hexdigest()


def stable_digest(data):
    return hash_bytes(json.dumps(data, sort_keys=True, separators=(",", ":")).encode())


class DiagnosticLogs:
    def __init__(self, staging, redactions):
        self.directory = staging / "diagnostics"
        self.directory.mkdir(mode=0o700)
        self.redactions = [(os.fsencode(path), replacement.encode())
                           for path, replacement in redactions]

    def retain(self, label, proc):
        timed_out = isinstance(proc, subprocess.TimeoutExpired)
        result = {"exit": None if timed_out else proc.returncode}
        if timed_out:
            result["timeout_seconds"] = proc.timeout
        for channel in ("stdout", "stderr"):
            raw = getattr(proc, channel) or b""
            retained = raw
            for path, replacement in self.redactions:
                retained = retained.replace(path, replacement)
            path = self.directory / f"{label}.{channel}.log"
            with path.open("xb") as stream:
                os.fchmod(stream.fileno(), 0o600)
                stream.write(retained)
            result[channel] = {"path": f"diagnostics/{path.name}", "bytes": len(retained),
                               "sha256": hash_bytes(retained), "raw_sha256": hash_bytes(raw)}
        return result

    def run(self, label, result, worker, *args, **kwargs):
        started = monotonic()
        try:
            proc = worker(*args, **kwargs)
        except subprocess.TimeoutExpired as error:
            result.update(self.retain(label, error), seconds=round(monotonic() - started, 3))
            raise
        result.update(self.retain(label, proc), seconds=round(monotonic() - started, 3))
        return proc


def command(args, *, cwd=None, env=None, timeout=30):
    return subprocess.run(args, cwd=cwd, env=env, capture_output=True, check=False, timeout=timeout)


def good(args, **kwargs):
    proc = command(args, **kwargs)
    if proc.returncode:
        print(proc.stderr.decode(errors="replace")[-3000:], flush=True)
        raise ValueError(f"{Path(args[0]).name} exited {proc.returncode}")
    return proc.stdout.decode().strip()


def git(*args):
    return good(("/usr/bin/git", *args))


def probe(shared, private, staging, worker, uid):
    device = good(("/bin/df", "-P", str(shared))).splitlines()[-1].split()[0]
    disk = command(("/usr/sbin/diskutil", "info", "-plist", device))
    require(disk.returncode == 0 and plistlib.loads(disk.stdout)["FilesystemType"] == "apfs", "APFS probe failed")
    worker_id = worker("/usr/bin/id", "-u")
    groups = worker("/usr/bin/id", "-G")
    environment = worker("/usr/bin/env")
    require(worker_id.returncode == groups.returncode == environment.returncode == 0, "identity probe failed")
    observed_uid = int(worker_id.stdout)
    group_ids = list(map(int, groups.stdout.split()))
    require(observed_uid == uid and observed_uid not in (0, os.getuid()), "worker not separate")
    require(not {0, 80}.intersection(group_ids), "administrative group")
    require(worker("/usr/bin/sudo", "-n", "/usr/bin/true").returncode != 0, "worker elevation available")
    keys = sorted(line.partition(b"=")[0].decode() for line in environment.stdout.splitlines())
    require(keys == ["HOME", "LC_ALL", "PATH", "PYTHONDONTWRITEBYTECODE", "TMPDIR"], "unexpected worker environment")
    marker = private / "marker"
    marker.write_bytes(b"controller only\n")
    for directory in (private, staging):
        record = directory.stat()
        require(record.st_uid == os.getuid() and stat.S_IMODE(record.st_mode) == 0o700, "receipt directory permissions differ")
        require(worker("/bin/test", "-r", str(directory)).returncode == 1, "worker can read receipt directory")
        require(worker("/bin/test", "-w", str(directory)).returncode == 1, "worker can write receipt directory")
    require(worker("/bin/cat", str(marker)).returncode != 0, "worker read marker")
    require(worker("/bin/sh", "-c", 'printf benign > "$1"', "probe", str(marker)).returncode != 0, "worker overwrote marker")
    require(worker("/bin/sh", "-c", 'printf benign > "$1"', "probe", str(staging / "receipt.json")).returncode != 0, "worker wrote staged receipt")
    require(not (staging / "receipt.json").exists(), "staged receipt unexpectedly exists")
    return {
        "filesystem": "apfs", "controller_uid": os.getuid(), "worker_uid": observed_uid,
        "worker_groups": group_ids, "worker_environment_keys": keys,
        "worker_noninteractive_elevation": "denied", "worker_marker_read_write": "denied",
        "worker_private_and_staged_directory_read_write": "denied",
        "worker_staged_receipt_create": "denied",
    }


def assess(report, reference, child_report):
    collected = report["collected"]
    rows = report["reports"]
    phases = Counter((row["nodeid"], row["when"]) for row in rows)
    exact = (len(collected) == len(set(collected)) and set(collected) == set(reference)
             and not report["deselected"])
    expected_phases = {(node, phase) for node in reference for phase in ("setup", "call", "teardown")}
    successful = set(phases) == expected_phases and all(count == 1 for count in phases.values()) and all(
        row["outcome"] == "passed" and row["wasxfail"] is False for row in rows
    )
    children = child_report["children"]
    labels = {row["label"] for row in children}
    native = (
        len(children) == 2 and labels == {"cli-help", "service-one-shot"}
        and len({row["pid"] for row in children}) == 2
        and all(type(row["pid"]) is int and row["pid"] > 0 and row["returncode"] == 0
                and row["covered_lines"] > 0 for row in children)
    )
    return {
        "collection": {"exact_reference_match": exact, "count": len(collected),
                       "ids_sha256": stable_digest(sorted(collected)),
                       "missing": sorted(set(reference) - set(collected)),
                       "extra": sorted(set(collected) - set(reference))},
        "per_test": {"complete_passing_phases": successful, "phase_rows": len(rows),
                     "outcome_counts": dict(Counter(row["outcome"] for row in rows)),
                     "exit_report": report["exit_code"]},
        "native_children": {"expected_positive_product_line_counts": native, "rows": children},
        "authority": "worker-originated pytest, PID and coverage data",
    }


def trial(shared, private, staging, receipt):
    logs = DiagnosticLogs(staging, [(str(shared), "<trial>"), (str(private), "<controller>"),
                                    (str(staging.parent), "<runner-temp>")])
    uid = pwd.getpwnam(WORKER).pw_uid & 0xFFFFFFFF
    src = shared / "source"
    runtime = shared / "runtime"
    work = shared / "worker"
    for path in (src, runtime, work):
        path.mkdir(mode=0o755)
    good(("/usr/bin/sudo", "-n", "/usr/sbin/chown", WORKER, str(work)))
    good(("/usr/bin/sudo", "-n", "/bin/chmod", "700", str(work)))
    shared.chmod(0o755)
    # The product requires every private-state ancestor to be root or worker owned.
    # The controller still owns the source and runtime directories inside this root.
    good(("/usr/bin/sudo", "-n", "/usr/sbin/chown", "root:wheel", str(shared)))

    def worker(*args, extra=None, cwd=None, timeout=30):
        env = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "HOME": str(work),
               "TMPDIR": str(work), "PYTHONDONTWRITEBYTECODE": "1"}
        env.update(extra or {})
        return command(("/usr/bin/sudo", "-n", "-u", WORKER, "/usr/bin/env", "-i",
                        *(f"{key}={value}" for key, value in env.items()), *args),
                       cwd=cwd or shared, timeout=timeout)

    receipt["boundary"] = probe(shared, private, staging, worker, uid)
    print("Controller and worker boundary verified", flush=True)
    archive = private / "source.tar"
    with archive.open("xb") as stream:
        subprocess.run(("/usr/bin/git", "archive", BASE, "packages/aitm-usage", "tools/ci"),
                       stdout=stream, check=True, timeout=30)
    good(("/usr/bin/tar", "-xf", str(archive), "-C", str(src)))
    project = src / PRODUCT
    venv = runtime / "venv"
    uv = shutil.which("uv")
    require(uv is not None and good((uv, "--version")).split()[1] == "0.10.6", "wrong uv")
    install = dict(os.environ, UV_PYTHON_INSTALL_DIR=str(runtime / "python"),
                   UV_PROJECT_ENVIRONMENT=str(venv))
    good((uv, "sync", "--locked", "--no-config", "--managed-python", "--python", "3.13.9",
          "--project", str(project)), cwd=src, env=install, timeout=130)
    good(("/bin/chmod", "-R", "a+rX,go-w", str(src), str(runtime)))
    python = str(venv / "bin/python")
    locked = worker(python, "-I", "-c", "import platform;print(platform.python_version())")
    require(locked.returncode == 0 and locked.stdout.strip() == b"3.13.9", "worker interpreter identity failed")
    ancestry = [
        {"path": "worker" if path == work else "<trial>" if path == shared else str(path),
         "uid": path.stat().st_uid, "mode": format(stat.S_IMODE(path.stat().st_mode), "04o")}
        for path in (work, *work.parents)
    ]
    receipt["boundary"]["fixture_ancestry"] = ancestry
    preflight = logs.run("fixture-ancestry", receipt.setdefault("fixture_ancestry_process", {}), worker,
                         python, "-I", "-c",
                         "import sys; from pathlib import Path; from aitm_usage.ledger import validate_private_path;"
                         "validate_private_path(Path(sys.argv[1]), directory=True, allow_missing=True)",
                         str(work / "preflight"))
    require(preflight.returncode == 0, "private fixture ancestry failed product validation")
    require(worker("/bin/test", "-w", str(src)).returncode == 1, "worker can write source directory")
    for path in (project / "uv.lock", project / "pyproject.toml", src / "tools/ci/pytest_evidence.py", venv / "bin/aitm-usage"):
        require(worker("/bin/test", "-r", str(path)).returncode == 0, "worker cannot read required input")
        require(worker("/bin/test", "-w", str(path)).returncode == 1, "worker can modify required input")
    receipt["boundary"]["worker_locked_inputs_write"] = "denied"
    receipt["identity"]["product_python"] = "3.13.9"
    receipt["identity"]["uv"] = "0.10.6"
    receipt["identity"]["lock_sha256"] = hash_bytes((project / "uv.lock").read_bytes())
    reference = json.loads(Path(__file__).with_name("reference.json").read_bytes())["ids"]
    receipt["reference"] = {"run": 43257314192, "artifact": 13962226641, "ids": len(reference),
                            "ids_sha256": stable_digest(reference), "origin": "existing CI worker report"}
    require(len(reference) == len(set(reference)), "reference contains duplicate IDs")
    console = worker(str(venv / "bin/aitm-usage"), "--help")
    receipt["external_cli_probe"] = {"returncode": console.returncode,
                                    "has_expected_help": b"usage: aitm-usage" in console.stdout and b"collect-once" in console.stdout,
                                    "stdout_sha256": hash_bytes(console.stdout)}
    common = ("-q", "--tb=long", "-p", "no:cacheprovider", "-p", "pytest_evidence", "--rootdir", str(src),
              "--confcutdir", str(src), "-c", str(project / "pyproject.toml"))
    settings = {"PYTHONPATH": str(src / "tools/ci"), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
                "AITM_CI_PYTEST_EVIDENCE": str(work / "collect.json")}
    collected = logs.run("collection", receipt.setdefault("collect_process", {}), worker,
                         python, "-m", "pytest", *common, "--collect-only", "--basetemp",
                         str(work / "collect-fixtures"), *TARGETS, extra=settings, cwd=src, timeout=80)
    collected_report = worker("/bin/cat", str(work / "collect.json"))
    require(collected_report.returncode == 0, "worker collection report unavailable")
    collect = json.loads(collected_report.stdout)
    require(collect["schema"] == "aitm.pytest-evidence/v1", "unexpected collection report")
    exact = sorted(collect["collected"]) == reference and not collect["deselected"]
    receipt["collect_process"].update(count=len(collect["collected"]), exact_reference_match=exact,
                                       ids_sha256=stable_digest(sorted(collect["collected"])))
    require(collected.returncode == collect["exit_code"] == 0 and exact, "collection differs from exact reference")
    print(f"Separate worker collection matched {len(reference)} reference IDs", flush=True)
    settings.update(AITM_CI_PYTEST_EVIDENCE=str(work / "pytest.json"), AITM_CI_CHILD_EVIDENCE="1",
                    COVERAGE_FILE=str(work / ".product"))
    full_targets = ("tests", str(src / TARGETS[1]))
    actual = logs.run("full", receipt.setdefault("full_process", {}), worker,
                      python, "-m", "coverage", "run", "-m", "pytest", *common,
                      "-p", "xdist.plugin", "-n", "3", "--dist", "worksteal", "--basetemp",
                      str(work / "runtime-fixtures"), *full_targets, extra=settings, cwd=project, timeout=430)
    summary = (
        "from pathlib import Path; import json,sys;"
        "from pytest_evidence import reconcile_workers;"
        "from python_gate import collect_child_coverage;"
        "p=Path(sys.argv[1]);"
        "r=reconcile_workers(p/'pytest.json',3);"
        "print(json.dumps([r,collect_child_coverage(r,p/'.product')]))"
    )
    examined = logs.run("full-reconciliation", receipt.setdefault("full_reconciliation", {}), worker,
                        python, "-c", summary, str(work), extra=settings, cwd=project, timeout=45)
    if examined.returncode == 0:
        report, child = json.loads(examined.stdout)
        receipt["full_diagnostics"] = assess(report, reference, child)
    require((private / "marker").read_bytes() == b"controller only\n", "controller marker changed")
    selected = sorted((CLI, SERVICE))
    selected_paths = [str(src / node) for node in selected]
    settings.update(AITM_CI_PYTEST_EVIDENCE=str(work / "selected.json"),
                    COVERAGE_FILE=str(work / ".selected"))
    selected_process = {"unobserved_count": len(reference) - len(selected)}
    receipt["selected_process"] = selected_process
    narrowed = logs.run("selected", selected_process, worker,
                        python, "-m", "coverage", "run", "-m", "pytest", *common, "--basetemp",
                        str(work / "selected-fixtures"), *selected_paths, extra=settings, cwd=project, timeout=90)
    selected_summary = summary.replace("reconcile_workers(p/'pytest.json',3)", "json.loads((p/'selected.json').read_bytes())").replace("p/'.product'", "p/'.selected'")
    examined = logs.run("selected-reconciliation", receipt.setdefault("selected_reconciliation", {}), worker,
                        python, "-c", selected_summary, str(work), extra=settings, cwd=project, timeout=35)
    if examined.returncode == 0:
        report, child = json.loads(examined.stdout)
        receipt["selected_diagnostics"] = assess(report, selected, child)
    require((private / "marker").read_bytes() == b"controller only\n", "controller marker changed")

    def matches(result):
        return result and all((
            result["collection"]["exact_reference_match"],
            result["per_test"]["complete_passing_phases"],
            result["native_children"]["expected_positive_product_line_counts"],
        ))

    if actual.returncode or narrowed.returncode or not (
        matches(receipt.get("full_diagnostics")) and matches(receipt.get("selected_diagnostics"))
    ):
        return "comparison-incomplete"
    return "comparison-complete"



def main():
    out = Path(sys.argv[1])
    out.parent.mkdir(mode=0o700)
    os.chmod(out.parent, 0o700)
    require(git("merge-base", "HEAD", BASE) == BASE, "product reference base drift")
    require(git("diff", "--name-only", BASE, "HEAD").splitlines() == [
        ".github/spikes/146/controller.py", ".github/spikes/146/reference.json",
        ".github/workflows/aitm-146-product-observation-trial.yml"
    ], "unexpected trial diff")
    receipt = {
        "schema": "aitm.146-product-comparison/v2", "status": "refused",
        "production_qualification": "unqualified",
        "identity": {"repository": os.environ["GITHUB_REPOSITORY"], "head": git("rev-parse", "HEAD"),
                     "tree": git("rev-parse", "HEAD^{tree}"), "product_commit": BASE,
                     "product_tree": git("rev-parse", BASE+"^{tree}"), "run": int(os.environ["GITHUB_RUN_ID"]),
                     "attempt": int(os.environ["GITHUB_RUN_ATTEMPT"]), "ref": os.environ["GITHUB_REF"],
                     "runner": os.environ["RUNNER_NAME"], "image": os.environ["ImageVersion"],
                     "platform": platform.platform(),
                     "controller_sha256": hash_bytes(Path(__file__).read_bytes()),
                     "reference_sha256": hash_bytes(Path(__file__).with_name("reference.json").read_bytes())},
        "limits": ["Reference is an earlier same-tree worker report, not an independent completeness oracle",
                   "Per-test and native coverage reports are worker-generated",
                   "External CLI probe observes one direct product process, not native descendants or source-line coverage"],
    }
    with tempfile.TemporaryDirectory(prefix="aitm146-controller-", dir=out.parent) as private:
        shared = Path(tempfile.mkdtemp(prefix="aitm146-product-", dir="/Users/Shared"))
        try:
            receipt["status"] = trial(shared, Path(private), out.parent, receipt)
        except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
            receipt["reason"] = str(error).replace(str(shared), "<trial>").replace(private, "<controller>")
        finally:
            with out.open("xb") as file:
                os.fchmod(file.fileno(), 0o600)
                file.write((json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode())
            print(f"Controller receipt SHA-256: {hash_bytes(out.read_bytes())}", flush=True)
            print(f"Product observation status: {receipt['status']}", flush=True)
            command(("/usr/bin/sudo", "-n", "/bin/rm", "-rf", str(shared)))
    return 0 if receipt["status"] == "comparison-complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
