"""Controller-owned checks for two pinned product obligations."""

import ast
import json
import os
import re
import selectors
import subprocess
from hashlib import sha256
from pathlib import Path
from time import monotonic

PYTHON_ARCHIVE = "Python-3.13.9.tar.xz"
PYTHON_SHA256 = "ed5ef34cda36cfa2f3a340f07cac7e7814f91c7f3c411f6d3562323a866c5c66"
INSTRUMENTATION_SHA256 = "06c6f8b87c556d8e8f0d2c77297f43c13b12599272d5fcad9071e8ea2efe772d"
CASES = {
    "cli-help": (
        "tools/ci/tests/test_cli_evidence.py", "test_usage_console_help",
        "1574c4076f6fa957e66a264f2d3c0a11e1446e06f60249c83c14d3237fa91283",
        "cli.py", 417, "b74258da1ca51bc67344e95970f563331c017b43b02a7d357a6c44ad66be95a3",
    ),
    "service-one-shot": (
        "packages/aitm-usage/tests/test_service.py", "test_one_shot_status_uses_collecting_subprocess_pid",
        "d70c3517a60482fe67339d4f1bb454146ec369b984023fa89588d86987932995",
        "service.py", 1052, "cdb8f673c254cb5e9d4d186a18f15bab0df7bd9a059fb27900ca6b0c09c32faa",
    ),
}
BOOTSTRAP = r"""
import os, sys
print(os.getpid(), flush=True)
if sys.stdin.buffer.read(1) != b"\n":
    raise SystemExit("controller did not release product")
sys.path[0:0] = [sys.argv[1], sys.argv[2]]
sys.argv = ["aitm-usage", *sys.argv[3:]]
monitor = sys.monitoring
monitor.use_tool_id(4, "aitm146-line-probe")
monitor.set_events(4, monitor.events.LINE)
from aitm_usage.cli import main
raise SystemExit(main())
"""


def add_line_probe(build):
    path = build / "Python/instrumentation.c"
    original = path.read_bytes()
    if sha256(original).hexdigest() != INSTRUMENTATION_SHA256:
        raise ValueError("unexpected CPython instrumentation source")
    source = original.replace(b'#include "Python.h"\n', b'#include "Python.h"\n#include "pydtrace.h"\n', 1)
    anchor = b"    int line = _Py_Instrumentation_GetLine(code, i);\n    assert(line >= 0);\n"
    if source.count(anchor) != 1:
        raise ValueError("CPython line probe anchor is ambiguous")
    probe = b"""
    if (PyDTrace_LINE_ENABLED()) {
        const char *file = PyUnicode_AsUTF8(code->co_filename);
        const char *name = PyUnicode_AsUTF8(code->co_qualname);
        if (file == NULL || name == NULL) {
            return -1;
        }
        PyDTrace_LINE(file, name, line);
    }
"""
    patched = source.replace(anchor, anchor + probe, 1)
    path.write_bytes(patched)
    return {"before_sha256": sha256(original).hexdigest(), "after_sha256": sha256(patched).hexdigest()}


def inventory(src):
    result = {}
    for label, (path, function, digest, product_file, line, product_digest) in CASES.items():
        source = (src / path).read_bytes()
        if sha256(source).hexdigest() != digest:
            raise ValueError(f"reviewed inventory source changed for {label}")
        target = src / "packages/aitm-usage/src/aitm_usage" / product_file
        if sha256(target.read_bytes()).hexdigest() != product_digest:
            raise ValueError(f"reviewed coverage target changed for {label}")
        candidates = [item for item in ast.parse(source).body
                      if isinstance(item, ast.FunctionDef) and item.name == function]
        if len(candidates) != 1 or candidates[0].decorator_list:
            raise ValueError(f"expected one unparametrized test definition for {label}")
        result[label] = {"node_id": f"{path}::{function}", "source_sha256": digest,
                         "function_line": candidates[0].lineno,
                         "required_product_probe": {"file": product_file, "line": line,
                                                    "sha256": product_digest}}
    return result


def passed(label, exit_code, stdout, pid=None, status=None):
    if exit_code != 0:
        return False
    if label == "cli-help":
        return all(marker in stdout for marker in (b"usage: aitm-usage", b"--help", b"collect-once"))
    if label != "service-one-shot" or not isinstance(status, dict):
        return False
    try:
        output = json.loads(stdout)
    except ValueError:
        return False
    return (isinstance(output, dict) and type(output.get("sequence")) is int and output["sequence"] > 0
            and status.get("producer_mode") == "one-shot" and type(status.get("producer_pid")) is int
            and status["producer_pid"] == pid)


def ready(process, expected=None, timeout=20):
    deadline = monotonic() + timeout
    received = b""
    with selectors.DefaultSelector() as selector:
        selector.register(process.stdout, selectors.EVENT_READ)
        while selector.select(max(0, deadline - monotonic())):
            chunk = os.read(process.stdout.fileno(), 4096)
            if not chunk:
                break
            received += chunk
            if b"\n" in received:
                line = received.split(b"\n", 1)[0]
                if expected is None or line == expected:
                    return line
                break
    raise ValueError("process did not provide expected readiness")


def lineage(pid, launcher, uid, command):
    result = []
    while pid > 1 and len(result) < 8:
        proc = command(("/bin/ps", "-p", str(pid), "-o", "uid=", "-o", "ppid="))
        if proc.returncode != 0:
            break
        user, parent = map(int, proc.stdout.split())
        result.append({"pid": pid, "parent": parent, "uid": user})
        if pid == launcher:
            break
        pid = parent
    if not result or result[0]["uid"] != uid or result[-1]["pid"] != launcher:
        raise ValueError("OS process identity did not match the controller launch")
    return result


def line_set(data, product_path):
    prefix = b"LINE " + os.fsencode(product_path) + b" "
    lines = set()
    for record in data.splitlines():
        if not record.strip():
            continue
        if not record.startswith(prefix):
            raise ValueError("unexpected DTrace output record")
        line, count = map(int, record[len(prefix):].split())
        if line <= 0 or count <= 0:
            raise ValueError("invalid DTrace line event")
        lines.add(line)
    return sorted(lines)


def trace_script(product_path):
    path = json.dumps(str(product_path))
    return f'''
dtrace:::BEGIN {{ printf("READY %d\\n", $target); }}
python$target:::line
/pid == $target && copyinstr(arg0) == {path}/
{{ @lines[copyinstr(arg0), arg2] = count(); }}
dtrace:::END {{ printa("LINE %s %d %@d\\n", @lines); }}
'''


def process_result(proc, stdout, stderr):
    return subprocess.CompletedProcess(proc.args, proc.returncode, stdout, stderr)


def traced(label, command_line, cwd, case, product, uid, staging, logs, record, command):
    product_path = product / case["required_product_probe"]["file"]
    script = staging / f"{label}.d"
    script.write_text(trace_script(product_path))
    child = subprocess.Popen(command_line, cwd=cwd, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    tracer = None
    attach_error = None
    try:
        pid = int(ready(child))
        record["process_lineage"] = lineage(pid, child.pid, uid, command)
        tracer = subprocess.Popen(
            ("/usr/bin/sudo", "-n", "/usr/sbin/dtrace", "-q", "-x", "switchrate=10hz",
             "-x", "aggsize=8m", "-p", str(pid), "-s", str(script)),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        try:
            record["trace_ready"] = ready(tracer, f"READY {pid}".encode()).decode()
        except ValueError as error:
            attach_error = str(error)
            probe_list = logs.run(f"bounded-{label}-probe-list", record.setdefault("probe_listing", {}), command,
                                  ("/usr/bin/sudo", "-n", "/usr/sbin/dtrace", "-l", "-p", str(pid),
                                   "-P", f"python{pid}"), timeout=12)
            record["probe_listing"]["has_line_probe"] = b" line" in probe_list.stdout
        stdout, stderr = child.communicate(b"\n", timeout=30)
        trace_output, trace_error = tracer.communicate(timeout=20)
    finally:
        if child.poll() is None:
            child.kill()
        if "stdout" not in locals():
            stdout, stderr = child.communicate()
        record["process"] = logs.retain(f"bounded-{label}", process_result(child, stdout, stderr))
        if tracer is not None:
            if tracer.poll() is None:
                tracer.terminate()
            if "trace_output" not in locals():
                trace_output, trace_error = tracer.communicate(timeout=10)
            record["trace"] = logs.retain(f"bounded-{label}-dtrace", process_result(tracer, trace_output, trace_error))
    lines = [] if attach_error else line_set(trace_output, product_path)
    record["coverage"] = {
        "process_pid": pid, "source": case["required_product_probe"]["file"],
        "line_numbers": lines, "required_line": case["required_product_probe"]["line"],
        "verified": (attach_error is None and tracer.returncode == 0
                     and not re.search(rb"\b(error|drop|failed|fault)\b", trace_error, re.I)
                     and case["required_product_probe"]["line"] in lines),
    }
    if attach_error:
        record["coverage"]["attach_error"] = attach_error
    return child.returncode, stdout, pid


def run(src, build, work, private, receipt, uid, worker, worker_args, logs, command, require, stable_digest):
    result = receipt["bounded"] = {"status": "incomplete"}
    catalog = inventory(src)
    result.update(inventory=catalog, inventory_sha256=stable_digest(catalog),
                  assignment=list(catalog), outcomes={})
    interpreter = build / "python.exe"
    product = src / "packages/aitm-usage/src"
    site_packages = src.parent / "runtime/venv/lib/python3.13/site-packages"
    workspace = worker("/usr/bin/mktemp", "-d", str(work / "slice.XXXXXXXX"))
    case_root = Path(workspace.stdout.decode().strip())
    require(workspace.returncode == 0 and case_root.parent == work, "worker did not create slice workspace")
    setup = """
import json, os, sys
from pathlib import Path
from uuid import UUID
root, fixtures = map(Path, sys.argv[1:])
sources, checkout = root / "sources", root / "checkout"
sources.mkdir()
checkout.mkdir()
for provider in ("codex", "claude"):
    raw = (fixtures / provider / "usage.jsonl").read_bytes()
    (sources / f"{provider}.jsonl").write_bytes(raw.replace(b"CHECKOUT", os.fsencode(checkout)))
(root / "config.json").write_text(json.dumps({"project_id": str(UUID(int=92146)),
    "source_roots": [str(sources)], "checkout_anchors": [str(checkout)],
    "cutoff": "2026-11-09T16:00:00+00:00"}))
"""
    setup_result = logs.run("bounded-fixture", result.setdefault("fixture", {}), worker, str(interpreter),
                            "-I", "-B", "-S", "-c", setup, str(case_root),
                            str(src / "packages/aitm-usage/tests/fixtures"))
    require(setup_result.returncode == 0, "product slice fixture setup failed")

    def invocation(*args):
        return (str(interpreter), "-I", "-B", "-S", "-c", BOOTSTRAP, str(product), str(site_packages), *args)

    # Setup and readback use the installed console. The two assigned processes use the trace build.
    console = src.parent / "runtime/venv/bin/aitm-usage"
    project_args = ("--project", str(case_root / "state"))
    registration = logs.run("bounded-register", result.setdefault("registration", {}), worker,
                            str(console), *project_args, "register", "--config", str(case_root / "config.json"), "--json")
    require(registration.returncode == 0, "product slice registration failed")
    commands = {"cli-help": invocation("--help"),
                "service-one-shot": invocation(*project_args, "collect-once", "--json")}
    for label, args in commands.items():
        record = result["outcomes"][label] = {"outcome": "unobserved"}
        try:
            code, output, pid = traced(label, worker_args(*args), src, catalog[label], product / "aitm_usage",
                                       uid, private, logs, record, command)
            status = None
            if label == "service-one-shot":
                readback = logs.run("bounded-status", record.setdefault("status", {}), worker,
                                    str(console), *project_args, "status", "--json")
                if readback.returncode == 0:
                    status = json.loads(readback.stdout)
                if isinstance(status, dict):
                    record["status_witness"] = {key: status.get(key) for key in ("producer_mode", "producer_pid")}
            record["outcome"] = "passed" if passed(label, code, output, pid, status) else "failed"
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            record["reason"] = type(exc).__name__ + ": " + str(exc).splitlines()[0].replace(str(src.parent), "<trial>")
    if all(row["outcome"] == "passed" and row.get("coverage", {}).get("verified")
           for row in result["outcomes"].values()):
        result["status"] = "bounded-pass"
