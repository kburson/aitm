"""Run a reviewed, exact assignment against an admitted hosted runtime."""

from collections import Counter
from copy import deepcopy
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from admission import (
    ALLOWED, BASE, HERE, PLAN, ROOT, SCRATCH, STAGED, TREE, WORKER,
    digest, good, load_precedent, output, prepare_boundary, publish, put_root,
    require, run, runtime_manifest, trace_attempt, verify_job, worker_command,
)

PRODUCT = ROOT / "source"
PREFIX = ROOT / "trace-build"
INSTALL = PREFIX / "installed"
VENV = PREFIX / "observed-venv"
EXTRAS = ("calibration.py", "integrated.py", "observed.py", "stage-b-inputs.json", "test_integrated.py")
FILES = ALLOWED + tuple(f".github/spikes/368/{name}" for name in EXTRAS)
BUNDLE = ("runtime.tar.gz", "runtime-manifest.json", "receipt.json")
COMMENT = b"\n# Scratch-only local selection probe for #352.\n"
KEYGEN = "/usr/bin/ssh-keygen"
NAMESPACE = "aitm-isolated-owner-proposal-v1"
PRINCIPAL = "aitm-qualification-owner"
LABELS = ("calibrate-positive", "calibrate-failure", "calibrate-missing", "scoped-product")
INPUTS = (str(PRODUCT), str(INSTALL), str(VENV))
EXECUTABLES = (KEYGEN, str(INSTALL / "bin/python3.13"), str(VENV / "bin/python"))


def arguments():
    return json.loads((HERE / "stage-b-inputs.json").read_bytes())


def github_json(path):
    return json.loads(good("gh", "api", f"repos/kburson/aitm/actions/{path}", timeout=45))


def receive(bundle_path, admission):
    run_id, attempt, artifact_id = (admission[k] for k in ("run", "attempt", "artifact"))
    run_record = github_json(f"runs/{run_id}/attempts/{attempt}")
    require(
        run_record["id"] == run_id and run_record["run_attempt"] == attempt
        and run_record["head_sha"] == admission["head"] and run_record["conclusion"] == "success"
        and run_record["head_branch"] == "codex/368-hosted-qualification"
        and run_record["actor"]["login"] == "kburson",
        "Stage A run authority differs",
    )
    artifact = github_json(f"artifacts/{artifact_id}")
    require(
        artifact["id"] == artifact_id and artifact["name"] == f"aitm368-admission-{run_id}-a{attempt}"
        and artifact["workflow_run"]["id"] == run_id and artifact["workflow_run"]["head_sha"] == admission["head"]
        and artifact["digest"] == "sha256:" + admission["archive_sha256"] and not artifact["expired"],
        "Stage A artifact authority differs",
    )
    with bundle_path.open("xb") as target:
        capture = subprocess.run(
            ("gh", "api", f"repos/kburson/aitm/actions/artifacts/{artifact_id}/zip"),
            stdout=target, stderr=subprocess.PIPE, timeout=180,
        )
    require(capture.returncode == 0 and digest(bundle_path) == admission["archive_sha256"],
            "Stage A artifact bytes differ")


def install_bundle(path, private, raw, admission):
    require(digest(path) == admission["archive_sha256"], "transferred archive differs")
    with zipfile.ZipFile(path) as archive:
        require(len(archive.namelist()) == len(set(archive.namelist())), "duplicate Stage A export")
        for name in BUNDLE:
            with archive.open(name) as origin, (private / name).open("xb") as dest:
                shutil.copyfileobj(origin, dest)
    previous = json.loads((private / "receipt.json").read_bytes())
    require(previous["verdict"] == "PASS" and digest(private / "receipt.json") == admission["receipt_sha256"],
            "Stage A receipt differs")
    manifest_path = private / "runtime-manifest.json"
    runtime_path = private / "runtime.tar.gz"
    require(digest(manifest_path) == admission["manifest_sha256"]
            and digest(runtime_path) == admission["runtime_archive_sha256"], "Stage A runtime bytes differ")
    manifest = json.loads(manifest_path.read_bytes())
    temp = private / "extracted"
    temp.mkdir(mode=0o700)
    roots = [install.relative_to(ROOT) for install in (INSTALL, VENV)]
    links = []
    modes = {}
    paths = set()
    with tarfile.open(runtime_path, "r:gz") as archive:
        for entry in archive:
            relative = Path(entry.name)
            require(not relative.is_absolute() and ".." not in relative.parts and str(relative) == entry.name
                    and any(relative.is_relative_to(root) for root in roots), "unadmitted runtime path")
            require(relative not in paths and entry.name in manifest, "unexpected runtime entry")
            paths.add(relative)
            expected = manifest[entry.name]
            target = temp / relative
            modes[target] = int(expected["mode"], 8)
            if entry.isdir():
                require(expected["kind"] == "directory", "runtime directory mismatch")
                target.mkdir(mode=0o700, parents=True, exist_ok=True)
            elif entry.issym():
                require(expected["kind"] == "symlink" and entry.linkname == expected["target"],
                        "runtime symlink mismatch")
                links.append((target, entry.linkname))
            else:
                require(expected["kind"] == "file" and (entry.isfile() or entry.islnk()), "runtime file mismatch")
                with archive.extractfile(entry) as origin, target.open("xb") as dest:
                    shutil.copyfileobj(origin, dest)
                require(digest(target) == expected["sha256"], "runtime file bytes differ")
    require({str(path) for path in paths} == set(manifest), "runtime manifest entry missing")
    for target, text in links:
        target.symlink_to(text)
    for target, mode in reversed(list(modes.items())):
        if not target.is_symlink():
            target.chmod(mode)
    put_root(PREFIX, "0755")
    for relative in roots:
        good("/usr/bin/sudo", "-n", "/usr/bin/ditto", str(temp / relative), str(ROOT / relative), timeout=80)
    good("/usr/bin/sudo", "-n", "/usr/sbin/chown", "-Rh", "root:wheel", str(PREFIX))
    require(runtime_manifest(INSTALL, VENV) == manifest, "installed runtime differs")
    python = INSTALL / "bin/python3.13"
    require(digest(python) == admission["python_sha256"], "installed interpreter differs")
    probes = run("/usr/bin/otool", "-s", "__TEXT", "__dof_python", str(python))
    require(output(raw, "installed-probe-table", probes) == 0
            and digest(raw / "installed-probe-table.stdout") == admission["probe_table_sha256"],
            "installed probe table differs")
    version = run(str(VENV / "bin/python"), "-I", "-B", "-m", "pytest", "--version",
                  env={"PATH": "/usr/bin:/bin", "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"})
    require(output(raw, "instrumented-pytest-identity", version) == 0 and b"pytest 9.2.0" in version.stdout,
            "installed pytest identity differs")
    return manifest


def replay_report(private, tooling, target, expected):
    environment = {"PATH": "/usr/bin:/bin", "HOME": str(private), "LC_ALL": "C"}
    result = run(sys.executable, "-B", "-E", "-s", "-m", "tools.ci.tia.working_tree_report",
                 "--repo", str(target), "--base", BASE, cwd=tooling, env=environment, timeout=45)
    require(result.returncode == expected and result.stderr == b"", "trusted report replay refused")
    return result.stdout


def archive_products(private, raw, packet):
    info = packet["scope"]
    checkouts = {}
    for role in ("tooling", "candidate", "extra"):
        checkpoint = private / role
        good("/usr/bin/git", "clone", "--quiet", "--shared", "--no-checkout", str(Path.cwd()), str(checkpoint), timeout=60)
        good("/usr/bin/git", "-C", str(checkpoint), "checkout", "--quiet", "--detach", BASE, timeout=45)
        require(good("/usr/bin/git", "-C", str(checkpoint), "rev-parse", "HEAD^{tree}").decode().strip() == TREE,
                "hosted checkout tree differs")
        checkouts[role] = checkpoint
    tooling, candidate, extra = (checkouts[role] for role in ("tooling", "candidate", "extra"))
    for path in (candidate, extra):
        with (path / info["path"]).open("ab") as stream:
            stream.write(COMMENT)
        require(digest(path / info["path"]) == info["content_sha256"], "scratch bytes differ")
    (extra / "aitm-368-extra.txt").write_text("synthetic extra path\n")
    for number, target in enumerate((candidate, candidate, extra), 1):
        data = replay_report(private, tooling, target, 2 if target == extra else 0)
        (raw / f"hosted-report-{number}.json").write_bytes(data)
    first, second, negative = ((raw / f"hosted-report-{num}.json").read_bytes() for num in (1, 2, 3))
    report = json.loads(first)
    identity = {key: value for key, value in report.items() if key != "snapshot_sha256"}
    expected_report = {key: value for key, value in info["report"].items() if key != "snapshot_sha256"}
    require(first == second and identity == expected_report and re.fullmatch("[0-9a-f]{64}", report["snapshot_sha256"]),
            "hosted report differs from approved assignment")
    require(json.loads(negative) == info["extra_refusal"], "hosted extra-path refusal differs")
    root = private / "product"
    root.mkdir(mode=0o700)
    archive = good("/usr/bin/git", "archive", BASE, "packages/aitm-usage", "tools/ci")
    copied = subprocess.run(("/usr/bin/tar", "-xf", "-", "-C", str(root)), input=archive,
                            capture_output=True, timeout=35)
    require(copied.returncode == 0, "execution source archive could not be staged")
    with (root / info["path"]).open("ab") as stream:
        stream.write(COMMENT)
    require(product_manifest(root) == packet["product_manifest"], "execution input manifest differs")
    put_root(PRODUCT, "0755")
    good("/usr/bin/sudo", "-n", "/usr/bin/ditto", str(root), str(PRODUCT), timeout=30)
    good("/usr/bin/sudo", "-n", "/usr/sbin/chown", "-Rh", "root:wheel", str(PRODUCT))
    good("/usr/bin/sudo", "-n", "/bin/chmod", "-R", "a+rX,go-w", str(PRODUCT))
    require(product_manifest(PRODUCT) == packet["product_manifest"], "installed execution input manifest differs")
    put_root(PRODUCT / "calibration", "0755")
    put_root(PRODUCT / "calibration" / "test_probe.py", "0444", HERE / "calibration.py")
    put_root(STAGED / "observed.py", "0444", HERE / "observed.py")
    return checkouts, report["snapshot_sha256"]


def product_manifest(root):
    parts = (root / "packages/aitm-usage", root / "tools/ci")
    return {
        str(path.relative_to(root)): {"sha256": digest(path), "executable": bool(path.stat().st_mode & stat.S_IXUSR)}
        for parent in parts for path in sorted(parent.rglob("*")) if path.is_file()
    }


def read_native(full, original):
    def parse(data, pid, product):
        events, children = original(data, pid, product)
        phase = None
        markers = {"start": "setup", "setup-ok": "call", "call-ok": "teardown",
                   "setup-failed": "teardown", "call-failed": "teardown", "end": None}
        rows = [line.split(" ", 3) for line in data.decode().splitlines() if line.strip()]
        for _, kind, _, value in sorted(rows, key=lambda row: int(row[0])):
            if kind == "E":
                stage = value.split(" ", 1)[0]
                if stage in markers:
                    phase = markers[stage]
            elif kind == "P":
                children[int(value)]["phase"] = phase
        return events, children
    full.parse_trace = parse


def allow_observed(full):
    built_in = full.dtrace_program

    def program(*args):
        body = built_in(*args)
        existing = '&& copyinstr(arg0) == "child-argument")'
        added = (
            '|| (copyinstr(arg2) == ' + json.dumps(str(STAGED / "observed.py"))
            + ' && copyinstr(arg3) == "observed_init" && copyinstr(arg0) == "child-argument")'
        )
        require(body.count(existing) == 1, "pinned observer source changed")
        return body.replace(existing, existing + "\n      " + added)

    full.dtrace_program = program
    read_native(full, full.parse_trace)


def native_shape(argv):
    require(argv[0] == KEYGEN, "unexpected native executable")

    def worker_file(path, suffix):
        candidate = Path(path)
        return candidate.is_absolute() and ".." not in candidate.parts and candidate.is_relative_to(SCRATCH) and (
            tuple(candidate.parts[-len(suffix):]) == suffix
        )

    if len(argv) == 8 and argv[1:7] == ["-q", "-t", "ed25519", "-N", "", "-f"] and worker_file(argv[7], ("owner",)):
        return "generate"
    if len(argv) == 7 and argv[1:6] == ["-Y", "sign", "-n", NAMESPACE, "-f"] and worker_file(argv[6], ("control", "owner")):
        return "sign"
    if (len(argv) == 11 and argv[1:4] == ["-Y", "verify", "-f"] and argv[5:10] == ["-I", PRINCIPAL, "-n", NAMESPACE, "-s"]
            and worker_file(argv[4], ("allowed",)) and worker_file(argv[10], ("signature",))
            and Path(argv[4]).parent == Path(argv[10]).parent and Path(argv[4]).parent.parent.name == "control"):
        return "verify"
    raise ValueError("unapproved native argument shape")


def validate_children(children, allowed):
    actual = Counter()
    for child in children.values():
        arguments = child.get("arguments", [])
        images = child.get("exec", [])
        require(len(arguments) == len(images) == 1 and child.get("os_exit_status") == 0
                and child.get("os_exit_reason") == 1, "incomplete native lifecycle")
        argv = json.loads(arguments[0]["argument"])
        require(isinstance(argv, list) and argv and all(isinstance(arg, str) for arg in argv)
                and arguments[0]["executable"] == argv[0] == KEYGEN
                and images[0].split()[0] in (KEYGEN, Path(KEYGEN).name), "native argv and kernel exec identity disagree")
        actual[(child.get("test"), child.get("phase"), native_shape(argv))] += 1
    require(actual == allowed, "native test, phase or multiplicity differs")
    return [[*key, count] for key, count in sorted(actual.items())]


def processes(uid):
    data = good("/bin/ps", "-axo", "uid=,pid=").decode().splitlines()
    return {int(pid) for owner, pid in (line.split() for line in data) if int(owner) == uid}


def clear_worker(uid, label):
    require(not processes(uid), "worker process survived an invocation")
    good("/usr/bin/sudo", "-n", "/bin/mv", str(SCRATCH), str(STAGED / ("retired-" + label)))
    # The retired directory is inaccessible before a fresh launch.
    good("/usr/bin/sudo", "-n", "/usr/sbin/chown", "root:wheel", str(STAGED / ("retired-" + label)))
    good("/usr/bin/sudo", "-n", "/bin/chmod", "0700", str(STAGED / ("retired-" + label)))
    good("/usr/bin/sudo", "-n", "/usr/bin/install", "-d", "-o", WORKER, "-g", "staff", "-m", "0700", str(SCRATCH))


def calibrate_intake(selected, assignment, catalog, passing, expected_native):
    evaluate = selected.evaluate
    require(evaluate(assignment, catalog, {"exit_code": 0}).get("reason") == "untrusted-origin",
            "worker-only evidence was accepted")
    for field, value in (("invocation", "stale"), ("head", "wrong-head"), ("attempt", -1),
                         ("snapshot_sha256", "wrong-digest"), ("observed_pid", -1)):
        refusal = evaluate({**assignment, field: value}, catalog, passing)
        require(refusal.get("reason") == "assignment-identity-mismatch", "identity mutation was accepted")
    for active_event in ("collect", "dispatch", "body-enter", "teardown-ok"):
        index = next(index for index, event in enumerate(passing.events) if event[0] == active_event)
        original = passing.events
        variants = (
            original[:index] + original[index + 1:],
            original[:index] + [original[index]] + original[index:],
        )
        for events in variants:
            modified = selected.Trace(assignment, events, passing.children, True, 0)
            require(not evaluate(assignment, catalog, modified)["accepted"], "incomplete or duplicate event accepted")
    for events, clean in (([], True), (passing.events, False),
                          ([*passing.events, ("start", "extra")], True)):
        require(not evaluate(assignment, catalog, selected.Trace(assignment, events, {}, clean, 0))["accepted"],
                "observer failure or extra assignment accepted")
    child, = passing.children
    bad = deepcopy(passing.children)
    bad[child]["test"] = "not-assigned"
    for children in ({}, bad):
        try:
            validate_children(children, expected_native)
        except ValueError:
            continue
        raise ValueError("missing or unassigned native child was accepted")


def run_scope(private, raw, receipt, uid, packet, old, snapshot):
    full, selected = old.full_suite, old.selected_suite
    worker = worker_command(STAGED / "worker.sb")
    allow_observed(full)
    logs = old.DiagnosticLogs(raw, ())
    bootstrap = (
        f"exec(compile(open({str(STAGED / 'observed.py')!r}, 'rb').read(), "
        f"{str(STAGED / 'observed.py')!r}, 'exec'))\n" + full.BOOTSTRAP
    )
    args = (str(VENV / "bin/python"), "-I", "-B", "-c", bootstrap)

    def worker_args(*passed, extra):
        return (*worker[:10], *(f"{key}={value}" for key, value in sorted(extra.items())), *worker[10:], *passed)

    require(worker[10] == "/usr/bin/sandbox-exec", "worker launch shape drifted")
    common_identity = dict(
        head=receipt["identity"]["sha"],
        run=receipt["identity"]["run"], attempt=receipt["identity"]["attempt"],
        tree=receipt["identity"]["tree"], base=BASE,
        snapshot_sha256=snapshot,
        assignment_input_sha256=digest(HERE / "stage-b-inputs.json"),
        runtime_sha256=packet["admission"]["runtime_archive_sha256"],
    )
    # The invocation label is bound before launch, and the PID comes from the controller handshake.
    def observe(label, module, catalog, nodes, *, options=(), product=False):
        clear_worker(uid, label)
        details = receipt["invocations"][label] = {}
        if product:
            receipt["product_invocation_started"] = True
        events, children = full.observe(
            label, (*args, "-p", "no:cacheprovider", "--rootdir", str(PRODUCT), "--basetemp", str(SCRATCH / "pytest"),
                    *options, str(PRODUCT / module)),
            worker_args, uid, PRODUCT, PRODUCT / "packages/aitm-usage/src/aitm_usage",
            private, logs, old.command, details, timeout=180, assignment=nodes,
            expected_inventory=selected.digest(sorted(catalog)),
        )
        require(not processes(uid), "worker process survived an invocation")
        assignment = selected.authorize({**common_identity, "invocation": label,
                                         "observed_pid": details["ready_pid"]}, catalog, nodes)
        observation = selected.Trace(assignment, events, children, details["trace_clean"], details["driver"]["exit"])
        details["assignment"] = assignment
        details["reconciliation"] = result = selected.evaluate(assignment, catalog, observation)
        return details, observation, result

    receipt["invocations"] = {}
    fixture = "calibration/test_probe.py"
    failed_id, pass_id = (f"{fixture}::test_{name}" for name in ("failure", "success"))
    controls = [failed_id, pass_id]
    details, positive, observed = observe(LABELS[0], fixture, controls, [pass_id])
    calibration = Counter({(pass_id, "call", "generate"): 1})
    require(observed["accepted"], "positive observer calibration did not pass")
    details["native"] = validate_children(positive.children, calibration)
    for label, nodes, expected_missing in (
        (LABELS[1], [failed_id], []), (LABELS[2], controls, [pass_id]),
    ):
        details, failure, observed = observe(label, fixture, controls, nodes, options=("--maxfail=1",))
        require(failure.clean and failure.exit_code == 1 and observed["dispatch_matches"]
                and observed["collection_matches"] and observed["failed"] == [failed_id]
                and observed["missing_or_inconsistent"] == expected_missing and not observed["accepted"],
                "failure calibration lost the independently observed failure")
        details["native"] = validate_children(failure.children, Counter())
    calibrate_intake(selected, positive.assignment, controls, positive, calibration)
    scope = packet["scope"]
    nodes = scope["report"]["node_ids"]
    details, observation, result = observe(LABELS[3], scope["module"], nodes, nodes, product=True)
    receipt["observed_product_outcomes"] = len(result["passed"]) + len(result["failed"])
    verified = Counter({(node, phase, kind): count for node, phase, kind, count in scope["native_children"]})
    details["native"] = validate_children(observation.children, verified)
    require(result["accepted"], "product observation did not reconcile")


def main(private, bundle):
    require(private.parent == Path(os.environ["RUNNER_TEMP"]) and not private.exists(), "unexpected evidence directory")
    require(bundle.parent == private.parent and bundle.is_file(), "runtime export unavailable")
    os.umask(0o077)
    private.mkdir(mode=0o700)
    raw = private / "protected"
    export = private / "published"
    raw.mkdir()
    export.mkdir()
    receipt = {"schema": "aitm.hosted-observation-integrated/v1", "story": 368, "plan_sha256": PLAN,
               "stage": "B", "gate": "job-identity", "verdict": "HOLD", "candidate_code_resistance": "unqualified",
               "candidate_inventory": "unqualified", "impact_completeness": "unqualified",
               "product_invocation_started": False, "observed_product_outcomes": 0}
    try:
        packet = arguments()
        verify_job(receipt, FILES)
        require(all(receipt["identity"][key] == expected for key, expected in packet["image_identity"].items()),
                "authenticated runner image or toolchain drifted")
        receipt["admission"] = packet["admission"]
        receipt["gate"] = "worker-boundary"
        uid, command, binary = prepare_boundary(private, raw, receipt, INPUTS, EXECUTABLES)
        receipt["gate"] = "trace-capability"
        trace_attempt(private, raw, receipt, uid, command, binary)
        receipt["gate"] = "runtime-install"
        runtime = install_bundle(bundle, private, raw, packet["admission"])
        receipt["gate"] = "assignment-replay"
        checkouts, snapshot = archive_products(private, raw, packet)
        receipt["snapshot_sha256"] = snapshot
        old, source_sha256 = load_precedent(private)
        require(source_sha256 == packet["precedent_sha256"], "#146 harness bytes differed")
        receipt["gate"] = "calibration-and-scoped-observation"
        run_scope(private, raw, receipt, uid, packet, old, snapshot)
        receipt["gate"] = "post-run-input-custody"
        scope = packet["scope"]
        require(product_manifest(PRODUCT) == packet["product_manifest"] and runtime_manifest(INSTALL, VENV) == runtime,
                "executed source or runtime drifted")
        require(digest(checkouts["candidate"] / scope["path"]) == scope["content_sha256"], "candidate bytes drifted")
        replay = replay_report(private, checkouts["tooling"], checkouts["candidate"], 0)
        (raw / "hosted-report-after.json").write_bytes(replay)
        require(replay == (raw / "hosted-report-1.json").read_bytes(), "candidate snapshot changed")
        receipt.update(verdict="PASS", gate="complete")
    except Exception as error:
        receipt["failure_type"] = type(error).__name__
        receipt["failure"] = str(error) if isinstance(error, ValueError) else type(error).__name__
    for name in LABELS:
        program = private / f"{name}.d"
        if program.is_file():
            (raw / program.name).write_bytes(program.read_bytes())
        for label in (name, name + "-dtrace"):
            for stream in ("stdout", "stderr"):
                evidence = raw / "diagnostics" / f"{label}.{stream}.log"
                if evidence.is_file():
                    (raw / evidence.name).write_bytes(evidence.read_bytes())
    return publish(raw, export, receipt, extra=(
        *(f"hosted-report-{name}.json" for name in (1, 2, 3, "after")),
        *(f"{label}.d" for label in LABELS),
        *(f"{label}{tail}.{stream}.log" for label in LABELS for tail in ("", "-dtrace") for stream in ("stdout", "stderr")),
    ))


if __name__ == "__main__":
    if sys.argv[1] == "--fetch":
        receive(Path(sys.argv[2]), arguments()["admission"])
    else:
        raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
