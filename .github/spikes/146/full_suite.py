"""Trace a fixed reviewed pytest suite through controller-owned DTrace."""

from collections import Counter, defaultdict
from hashlib import sha256
import ast
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor

from bounded import lineage, ready, process_result

PYTEST_FILES = {
    "main": "e30aebb8ee741d2cc085012dee508c1a592697d4282acd00d161a01ba8e8c308",
    "runner": "4c296563915287ad67e3f7c6680fe9a302612d00c2752ae6ba9b86d04acdcbe7",
    "python": "9553fbb38363c987f59b1de522142a9dc0e9f6191cd1f173a6bee21140d4c887",
}
PHASES = ("start", "setup-ok", "body-enter", "body-return", "call-ok", "teardown-ok", "end")
CHILDREN = {
    "tools/ci/tests/test_cli_evidence.py::test_usage_console_help": ("cli.py", 417, "--help"),
    "packages/aitm-usage/tests/test_service.py::test_one_shot_status_uses_collecting_subprocess_pid":
        ("service.py", 1052, "collect-once"),
}
ROOT = "packages/aitm-usage"
BOOTSTRAP = r"""
import os, sys
print(os.getpid(), flush=True)
if sys.stdin.buffer.read(1) != b"\n":
    raise SystemExit("controller did not release pytest")
import pytest
raise SystemExit(pytest.main(sys.argv[1:]))
"""
SITE = """
import os
import sys
invocation = sys.orig_argv[1:]
if os.environ.get("AITM146_CHILD_LINES") == "1" and (
    any(arg.endswith("/aitm-usage") for arg in invocation) and "--help" in invocation
    or any(arg.endswith("/run_cli.py") for arg in invocation) and "collect-once" in invocation
):
    monitor = sys.monitoring
    monitor.use_tool_id(4, "aitm146-line-probe")
    monitor.register_callback(4, monitor.events.PY_START, lambda code, offset:
        monitor.set_local_events(4, code, monitor.events.LINE)
        if "/aitm_usage/" in code.co_filename else None)
    monitor.set_events(4, monitor.events.PY_START)
"""


def patch(path, digest, replacements):
    original = path.read_bytes()
    if sha256(original).hexdigest() != digest:
        raise ValueError(f"unexpected source for {path.name}")
    data = original
    for old, new in replacements:
        if data.count(old) != 1:
            raise ValueError(f"ambiguous patch anchor in {path.name}")
        data = data.replace(old, new, 1)
    path.write_bytes(data)
    return sha256(data).hexdigest()


def patch_cpython(build):
    declaration = b"    probe line(const char *, const char *, int);"
    source = b"""
static PyObject *
aitm146_event(PyObject *module, PyObject *args)
{
    const char *kind, *data;
    if (!PyArg_ParseTuple(args, "ss:_aitm146_event", &kind, &data)) {
        return NULL;
    }
    if (PyDTrace_TEST_EVENT_ENABLED()) {
        PyFrameObject *frame = PyEval_GetFrame();
        if (frame == NULL) {
            Py_RETURN_NONE;
        }
        PyCodeObject *code = PyFrame_GetCode(frame);
        const char *file = PyUnicode_AsUTF8(code->co_filename);
        const char *name = PyUnicode_AsUTF8(code->co_qualname);
        if (file != NULL && name != NULL) {
            PyDTrace_TEST_EVENT(kind, data, file, name);
        }
        Py_DECREF(code);
        if (PyErr_Occurred()) {
            return NULL;
        }
    }
    Py_RETURN_NONE;
}

"""
    table = b"static PyMethodDef sys_methods[] = {\n"
    executed = b"                                start_new_session, process_group)\n"
    return {
        "pydtrace": patch(build / "Include/pydtrace.d",
                          "9dd7071fac51ba3a1cf21cd24183d285d46176f795fce62c3575555f10f4cad0",
                          [(declaration, declaration + b"\n    probe test__event(const char *, const char *, const char *, const char *);")]),
        "sysmodule": patch(build / "Python/sysmodule.c",
                            "82d36f5cfa6a75d13a1960f11e3faf45677bacc8d1b86df995156432d69aa295",
                            [(table, source + table +
                              b'    {"_aitm146_event", aitm146_event, METH_VARARGS, NULL},\n')]),
        "subprocess": patch(build / "Lib/subprocess.py",
                             "21ecc4c8f4fcf641974fc0d9cc28e97b07670ed1cef7e9d96769b31bb8345586",
                             [(executed, executed + b'            if hasattr(sys, "_aitm146_event"):\n'
                               b'                command = args if isinstance(args, (tuple, list)) else (args,)\n'
                               b'                for marker in ("--help", "collect-once"):\n'
                               b'                    if marker in command:\n'
                               b'                        sys._aitm146_event("child-argument", f"{self.pid} {marker} {command[0]}")\n')]),
    }


def instrument_pytest(site):
    emit = b'__import__("sys")._aitm146_event'
    collection = b"            hook.pytest_collection_modifyitems(\n"
    final = b"        return items\n\n    def _collect_one_node("
    start = b"    hasrequest = hasattr(item, \"_request\")\n"
    end = b"    return reports\n\n\ndef show_test_item"
    raw = b"    report: TestReport = ihook.pytest_runtest_makereport(item=item, call=call)\n"
    body = b"    result = testfunction(**testargs)\n"
    edits = {
        "main": [
            (collection, b'            for observed in items:\n                ' + emit
             + b'("discovered", observed.nodeid)\n' + collection),
            (final, b'        for observed in items:\n            ' + emit
             + b'("collect", observed.nodeid)\n        ' + emit
             + b'("collection-end", str(len(items)))\n' + final),
        ],
        "runner": [
            (start, b'    ' + emit + b'("start", item.nodeid)\n' + start),
            (end, b'    ' + emit + b'("end", item.nodeid)\n' + end),
            (raw, b'    ' + emit + b'(when + ("-ok" if call.excinfo is None else "-failed"), item.nodeid)\n' + raw),
        ],
        "python": [(body, b'    if (testfunction.__code__.co_filename != str(pyfuncitem.path)\n'
                    b'            or testfunction.__code__.co_name != pyfuncitem.originalname):\n'
                    b'        raise RuntimeError("test function source identity differs from assignment")\n'
                    b'    ' + emit + b'("body-enter", pyfuncitem.nodeid)\n' + body
                    + b'    ' + emit + b'("body-return", pyfuncitem.nodeid)\n')],
    }
    return {name: patch(site / "_pytest" / f"{name}.py", digest, edits[name])
            for name, digest in PYTEST_FILES.items()}


def independently_check_groups(src, expected):
    files = sorted((src / ROOT / "tests").rglob("test_*.py"))
    files.append(src / next(iter(CHILDREN)).partition("::")[0])
    groups = {}
    matrices = {}
    trees = {file: ast.parse(file.read_bytes()) for file in files}
    for file, tree in trees.items():
        for node in tree.body:
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.List):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "_COMPLETION_NATIVE_DISPROOFS":
                        matrices[target.id] = len(node.value.elts)
    for file, tree in trees.items():
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
                raise ValueError("unexpected pytest class")
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if node.name.startswith("pytest_"):
                raise ValueError("unexpected collection hook")
            if not node.name.startswith("test_"):
                continue
            count = 1
            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call):
                    raise ValueError("unsupported pytest decorator")
                name = ast.unparse(decorator.func)
                if name == "pytest.mark.skipif":
                    continue
                if name != "pytest.mark.parametrize":
                    raise ValueError("unsupported pytest decorator")
                values = decorator.args[1]
                count *= len(values.elts) if isinstance(values, ast.List) else matrices[values.id]
            key = f"{file.relative_to(src)}::{node.name}"
            if key in groups:
                raise ValueError("duplicate test definition")
            groups[key] = count
    reference_groups = Counter(node.split("[", 1)[0] for node in expected)
    if groups != reference_groups or len(expected) != len(set(expected)):
        raise ValueError("source catalog and expected inventory disagree")
    return len(files), len(groups)


def reconcile(events, expected, selected=None):
    assignment = set(expected if selected is None else selected)
    collection = [data for kind, data in events if kind == "collect"]
    complete = [data for kind, data in events if kind == "collection-end"] == [str(len(expected))]
    phases = defaultdict(list)
    problems = []
    active = None
    for kind, data in events:
        if kind not in {"collect", "collection-end", "discovered"}:
            phases[data].append(kind)
            if kind == "start":
                if active is not None:
                    problems.append(active)
                active = data
            elif data != active:
                problems.append(data)
            if kind == "end":
                active = None
    failure_prefixes = (("start", "setup-failed"),
                        ("start", "setup-ok", "body-enter", "call-failed"),
                        ("start", "setup-ok", "body-enter", "body-return", "call-failed"),
                        ("start", "setup-ok", "body-enter", "body-return", "call-ok", "teardown-failed"))
    failed = sorted(node for node, history in phases.items() if node in assignment
                    and any(tuple(history[:len(prefix)]) == prefix for prefix in failure_prefixes))
    passed = sorted(node for node in assignment if tuple(phases[node]) == PHASES)
    return {
        "collection_matches": complete and Counter(collection) == Counter(expected),
        "collected": len(collection),
        "passed": passed, "failed": failed,
        "missing_or_inconsistent": sorted(assignment - set(passed) - set(failed)),
        "unexpected_execution": sorted(set(phases) - assignment),
        "ordering_errors": sorted(set(problems)),
    }


def dtrace_program(uid, source, pytest_site, subprocess_file):
    target = json.dumps(str(source) + "/")
    main, runner, python = (json.dumps(str(pytest_site / "_pytest" / f"{file}.py"))
                            for file in ("main", "runner", "python"))
    valid_origins = f"""(
      (copyinstr(arg2) == {main} && copyinstr(arg3) == "Session.perform_collect")
      || (copyinstr(arg2) == {runner} && copyinstr(arg3) == "runtestprotocol")
      || (copyinstr(arg2) == {runner} && copyinstr(arg3) == "call_and_report")
      || (copyinstr(arg2) == {python} && copyinstr(arg3) == "pytest_pyfunc_call")
      || (copyinstr(arg2) == {json.dumps(str(subprocess_file))}
          && copyinstr(arg3) == "Popen.__init__" && copyinstr(arg0) == "child-argument")
    )"""
    return f'''
dtrace:::BEGIN {{ printf("READY %d\\n", $target); }}
python$target:::test-event
/pid == $target && uid == {uid} && {valid_origins}/
{{
    printf("%llu E %d %s %s\\n", timestamp, pid, copyinstr(arg0), copyinstr(arg1));
}}
proc:::create
/pid == $target && uid == {uid}/
{{ printf("%llu P %d %d\\n", timestamp, pid, args[0]->pr_pid); }}
proc:::exec-success
/uid == {uid} && ppid == $target/
{{ printf("%llu X %d %d %s\\n", timestamp, ppid, pid, curpsinfo->pr_psargs); }}
syscall::exit:entry
/uid == {uid} && ppid == $target/
{{ printf("%llu S %d %d %d\\n", timestamp, ppid, pid, arg0); }}
proc:::exit
/uid == {uid} && ppid == $target/
{{ printf("%llu R %d %d %d\\n", timestamp, ppid, pid, arg0); }}
python*:::line
/uid == {uid} && ppid == $target && substr(copyinstr(arg0), 0, {len(str(source)) + 1}) == {target}/
{{ @lines[ppid, pid, copyinstr(arg0), arg2] = count(); }}
dtrace:::END {{ printa("0 L %d %d %s %d %@d\\n", @lines); }}
'''


def parse_trace(data, parent, product):
    events = []
    children = defaultdict(dict)
    active = None
    rows = [line.strip().split(" ", 3) for line in data.decode().splitlines() if line.strip()]
    for _, kind, owner, value in sorted(rows, key=lambda row: (row[0] == "0", int(row[0]))):
        if int(owner) != parent:
            raise ValueError("unexpected traced process")
        if kind == "E":
            event, payload = value.split(" ", 1)
            if event == "child-argument":
                pid, argument, executable = payload.split(" ", 2)
                children[int(pid)].setdefault("arguments", []).append({
                    "argument": argument, "executable": executable,
                })
                continue
            events.append((event, payload))
            if event == "start":
                active = payload
            elif event == "end":
                active = None
        elif kind == "P":
            children[int(value)]["test"] = active
        elif kind == "X":
            pid, image = value.split(" ", 1)
            children[int(pid)].setdefault("exec", []).append(image)
        elif kind == "R":
            pid, reason = map(int, value.split())
            children[pid]["os_exit_reason"] = reason
        elif kind == "S":
            pid, status = map(int, value.split())
            children[pid]["os_exit_status"] = status
        elif kind == "L":
            pid, rest = value.split(" ", 1)
            path, number, hits = rest.rsplit(" ", 2)
            path = Path(path).relative_to(product)
            if int(number) <= 0 or int(hits) <= 0:
                raise ValueError("invalid source line sample")
            children[int(pid)].setdefault("files", {}).setdefault(str(path), []).append(int(number))
        else:
            raise ValueError("unexpected trace record")
    return events, children


def install_runtime(build, destination, locked_site, src, good):
    # Install a real base prefix so the product's interpreter and venv checks use normal paths.
    good(("/usr/bin/make", "install"), cwd=build, timeout=220)
    prefix = build.parent / "installed"
    binary = prefix / "bin/python3.13"
    good((str(binary), "-I", "-m", "venv", "--without-pip", str(destination)), timeout=30)
    site = destination / "lib/python3.13/site-packages"
    for entry in locked_site.iterdir():
        if entry.name.startswith(("_virtualenv", "a1_coverage")) or entry.name == "__pycache__":
            continue
        target = site / entry.name
        if entry.is_dir():
            shutil.copytree(entry, target, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copyfile(entry, target)
    product = src / ROOT / "src"
    (site / "aitm_usage.pth").write_text(f"{product}\n")
    (site / "sitecustomize.py").write_text(SITE)
    hashes = instrument_pytest(site)
    console = destination / "bin/aitm-usage"
    console.write_text(f"#!{destination}/bin/python\nfrom aitm_usage.cli import main\nraise SystemExit(main())\n")
    console.chmod(0o755)
    return binary, hashes


def observe(label, args, worker_args, uid, project, product, private, logs, command, result, timeout=800):
    child = subprocess.Popen(worker_args(*args, extra={"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
                                                        "AITM146_CHILD_LINES": "1"}),
                             cwd=project, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    trace = None
    trace_output = b""
    run_error = None
    try:
        pid = int(ready(child))
        result["lineage"] = lineage(pid, child.pid, uid, command)
        script = private / f"{label}.d"
        site = Path(args[0]).parent.parent / "lib/python3.13/site-packages"
        stdlib = site.parents[3] / "installed/lib/python3.13/subprocess.py"
        script.write_text(dtrace_program(uid, product, site, stdlib))
        trace = subprocess.Popen(("/usr/bin/sudo", "-n", "/usr/sbin/dtrace", "-Z", "-q",
                                  "-x", "switchrate=50hz", "-x", "bufsize=16m", "-x", "aggsize=32m",
                                  "-x", "strsize=1024", "-p", str(pid), "-s", str(script)),
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ready(trace, f"READY {pid}".encode())
        result["ready_pid"] = pid
        with ThreadPoolExecutor(max_workers=2) as pool:
            trace_out = pool.submit(trace.stdout.read)
            trace_err = pool.submit(trace.stderr.read)
            try:
                out, err = child.communicate(b"\n", timeout=timeout)
                trace.wait(timeout=30)
            except subprocess.TimeoutExpired as error:
                run_error = error
                result["timeout_seconds"] = error.timeout
            finally:
                if child.poll() is None:
                    child.kill()
                if trace.poll() is None:
                    trace.terminate()
            trace_output, trace_error = trace_out.result(), trace_err.result()
    finally:
        if child.poll() is None:
            child.kill()
        if "out" not in locals():
            out, err = child.communicate(timeout=15)
        result["driver"] = logs.retain(label, process_result(child, out, err))
        if trace is not None:
            if trace.poll() is None:
                trace.terminate()
            if "trace_error" not in locals():
                trace_output, trace_error = trace.communicate(timeout=20)
            result["tracer"] = logs.retain(f"{label}-dtrace", process_result(trace, trace_output, trace_error))
    result["trace_clean"] = (run_error is None and trace.returncode == 0
                             and not re.search(rb"\b(error|drop|failed|fault)\b", trace_error, re.I))
    return parse_trace(trace_output, pid, product)


def run(src, shared, build, locked_venv, fixtures, private, logs, receipt, uid,
        worker, worker_args, command, good, require, stable_digest, expected):
    result = receipt["full_observation"] = {"status": "incomplete"}
    files, groups = independently_check_groups(src, expected)
    result["catalog"] = {"files": files, "groups": groups, "count": len(expected),
                         "ids_sha256": stable_digest(expected)}
    venv = build.parent / "suite-venv"
    binary, hashes = install_runtime(build, venv, locked_venv / "lib/python3.13/site-packages", src, good)
    result["toolchain"] = {"base_sha256": sha256(binary.read_bytes()).hexdigest(),
                           "pytest_patches": hashes}
    good(("/bin/chmod", "-R", "a+rX,go-w", str(build.parent)))
    good(("/usr/bin/sudo", "-n", "/usr/sbin/chown", "-Rh", "root:wheel", str(build.parent)))
    require(worker("/bin/test", "-w", str(binary)).returncode == 1, "trace runtime is worker-writable")
    project = src / ROOT
    product = project / "src/aitm_usage"
    args = (str(venv / "bin/python"), "-I", "-B", "-c", BOOTSTRAP, "-q", "--tb=long",
            "-o", "faulthandler_timeout=90", "-p", "no:cacheprovider", "--rootdir", str(src),
            "--confcutdir", str(src), "-c", str(project / "pyproject.toml"))
    targets = (str(project / "tests"), str(src / next(iter(CHILDREN)).partition("::")[0]))
    collected = result["collection"] = {}
    observed, _ = observe("observed-collection", (*args, "--collect-only", *targets), worker_args, uid,
                          project, product, private, logs, command, collected, timeout=90)
    inventory = reconcile(observed, expected, [])
    discovered = Counter(data for kind, data in observed if kind == "discovered")
    collected.update(inventory, discovered_matches=discovered == Counter(expected))
    require(collected["driver"]["exit"] == 0 and collected["trace_clean"] and collected["collection_matches"]
            and collected["discovered_matches"] and not collected["unexpected_execution"],
            "independent collection evidence is incomplete")
    execution = result["execution"] = {"assignment_sha256": stable_digest(expected)}
    observed, children = observe("observed-full", (*args, "--basetemp", str(fixtures / "observed-full"), *targets),
                                 worker_args, uid, project, product, private, logs, command, execution)
    execution.update(reconcile(observed, expected))
    records = result["native_children"] = {}
    for node, (file, line, argument) in CHILDREN.items():
        matches = [(pid, data) for pid, data in children.items()
                   if data.get("test") == node and line in data.get("files", {}).get(file, [])
                   and any(entry == {"argument": argument, "executable":
                                    str(venv / "bin" / ("aitm-usage" if argument == "--help" else "python"))}
                           for entry in data.get("arguments", [])) and data.get("exec")]
        records[node] = [{"pid": pid, "required_file": file, "required_line": line, **row} for pid, row in matches]
    require(execution["driver"]["exit"] == 0 and execution["trace_clean"] and execution["collection_matches"]
            and not any(execution[key] for key in ("failed", "missing_or_inconsistent", "unexpected_execution",
                                                   "ordering_errors"))
            and Counter(data for kind, data in observed if kind == "discovered") == Counter(expected)
            and all(len(rows) == 1 and rows[0].get("os_exit_status") == 0 and "os_exit_reason" in rows[0]
                    for rows in records.values()),
            "full execution or required child coverage remains incomplete")
    result["status"] = "full-observation-pass"
    return result["status"]
