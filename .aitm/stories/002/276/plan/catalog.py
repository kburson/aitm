"""A local catalog feasibility probe for reviewed AITM product inputs."""

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from time import monotonic
from uuid import UUID

CLI_TEST = "tools/ci/tests/test_cli_evidence.py::test_usage_console_help"
SERVICE_TEST = (
    "packages/aitm-usage/tests/test_service.py::test_one_shot_status_uses_collecting_subprocess_pid"
)
CHILDREN = {"cli-help": CLI_TEST, "service-one-shot": SERVICE_TEST}
CUTOFF = "2026-11-09T16:00:00+00:00"
PROVIDERS = ("codex", "claude")


@dataclass(frozen=True)
class Process:
    operation: str
    pid: int
    parent_pid: int
    returncode: int
    stdout: bytes
    stderr: bytes
    seconds: float


@dataclass(frozen=True)
class Outcome:
    passed: bool
    reason: str
    processes: tuple[Process, ...] = ()


def sha(data):
    return sha256(data).hexdigest()


def sanitized(data, paths):
    for path, label in paths:
        data = data.replace(str(path).encode(), label.encode())
    return data


def launch(operation, command, root):
    env = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "HOME": str(root), "TMPDIR": str(root)}
    started = monotonic()
    with subprocess.Popen(command, cwd=root, env=env, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE) as child:
        parent = subprocess.run(("/bin/ps", "-o", "ppid=", "-p", str(child.pid)),
                                check=False, capture_output=True, timeout=5)
        try:
            stdout, stderr = child.communicate(timeout=20)
        except subprocess.TimeoutExpired:
            child.kill()
            stdout, stderr = child.communicate()
            stderr += b"\ncontroller timeout\n"
    return Process(operation, child.pid, int(parent.stdout) if parent.stdout.strip() else -1,
                   child.returncode, stdout, stderr, round(monotonic() - started, 6))


def real_process(record, parent_pid):
    return (
        isinstance(record, Process)
        and type(record.pid) is int and record.pid > 0 and record.pid != parent_pid
        and record.parent_pid == parent_pid and record.returncode == 0
    )


def evaluate_help(process, parent_pid):
    if not real_process(process, parent_pid):
        return Outcome(False, "missing or failed direct CLI process")
    markers = (b"usage: aitm-usage", b"--help", b"collect-once")
    if not all(marker in process.stdout for marker in markers):
        return Outcome(False, "CLI help output mismatch", (process,))
    return Outcome(True, "CLI output and direct process match", (process,))


def evaluate_service(registered, collected, status, parent_pid):
    records = (registered, collected, status)
    if not all(real_process(process, parent_pid) for process in records):
        return Outcome(False, "missing or failed registration, collection or status process")
    if len({process.pid for process in records}) != len(records):
        return Outcome(False, "reused process identity", records)
    try:
        collected_output = json.loads(collected.stdout)
        status_output = json.loads(status.stdout)
    except (ValueError, UnicodeError):
        return Outcome(False, "invalid service JSON output", records)
    if (
        not isinstance(collected_output, dict) or not isinstance(status_output, dict)
        or type(collected_output.get("sequence")) is not int or collected_output["sequence"] <= 0
        or status_output.get("producer_mode") != "one-shot"
        or type(status_output.get("producer_pid")) is not int or status_output["producer_pid"] != collected.pid
    ):
        return Outcome(False, "service sequence, mode or producer PID mismatch", records)
    return Outcome(True, "service output and direct producer PID match", records)


def admit_local(outcomes):
    missing = sorted(set(CHILDREN) - set(outcomes))
    extra = sorted(set(outcomes) - set(CHILDREN))
    invalid = sorted(key for key, outcome in outcomes.items() if not isinstance(outcome, Outcome))
    failed = {
        key: outcome.reason for key, outcome in outcomes.items()
        if isinstance(outcome, Outcome) and not outcome.passed
    }
    return {"passed": not (missing or extra or invalid or failed), "missing": missing,
            "extra": extra, "invalid": invalid, "failed": failed}


BOOTSTRAP = r"""
import sys
from pathlib import Path
case = Path.cwd().resolve()
guard = (case / "control").resolve()
if guard.parent != case or not (case / "catalog-fixture").is_file():
    raise SystemExit("fixture guard is not inside the controller case directory")
from aitm_usage import ledger
ledger._control_root = lambda: guard
from aitm_usage.cli import main
sys.argv = ["aitm-usage", *sys.argv[1:]]
raise SystemExit(main())
"""


def fixture(root, fixture_dir, iteration):
    sources, checkout, state = (root / name for name in ("sources", "checkout", "state"))
    sources.mkdir(mode=0o700)
    checkout.mkdir(mode=0o700)
    for provider in PROVIDERS:
        data = (fixture_dir / provider / "usage.jsonl").read_bytes()
        (sources / f"{provider}.jsonl").write_bytes(data.replace(b"CHECKOUT", str(checkout).encode()))
    config = root / "register.json"
    config.write_text(json.dumps({"project_id": str(UUID(int=276_000 + iteration)),
                                 "source_roots": [str(sources)], "checkout_anchors": [str(checkout)],
                                 "cutoff": CUTOFF}))
    (root / "catalog-fixture").touch()
    return state, config


def run_behaviors(python, console, root, fixture_dir, iteration, parent_pid):
    state, config = fixture(root, fixture_dir, iteration)
    help_process = launch("help", (str(console), "--help"), root)

    def run(operation, *args):
        return launch(operation, (str(python), "-I", "-B", "-c", BOOTSTRAP,
                                  "--project", str(state), *args, "--json"), root)

    register = run("register", "register", "--config", str(config))
    if not real_process(register, parent_pid):
        return {"cli-help": evaluate_help(help_process, parent_pid),
                "service-one-shot": Outcome(False, "registration failed", (register,))}
    collect = run("collect-once", "collect-once")
    status = run("status", "status")
    return {"cli-help": evaluate_help(help_process, parent_pid),
            "service-one-shot": evaluate_service(register, collect, status, parent_pid)}
