"""Run the synthetic Stage A boundary and observer check on the dedicated hosted job."""

from collections import Counter
from hashlib import sha256
import importlib
import json
import os
from pathlib import Path
import plistlib
import pwd
import re
import select
import socket
import stat
import subprocess
import sys
import tarfile


BASE = "8218a69ad6d9d9f33c6383bd5a6cd4930bef21d7"
TREE = "90f2cc4007a82493029799d1a1cec10a855cc4a7"
REFERENCE = "16df827e8335ecb876826f830a8f82a22ae57c28"
BRANCH = "refs/heads/codex/368-hosted-qualification"
PLAN = "51f56908994e273e9adce20f5d60813cb7b45cddd52051580241f9119e47bba9"
ROOT = Path("/Users/Shared/aitm368-hosted")
STAGED = ROOT / "admitted"
SCRATCH = ROOT / "worker"
WORKER = "_aitm368"
HERE = Path(__file__).resolve().parent
ALLOWED = (
    ".github/spikes/368/admission.py",
    ".github/spikes/368/qualification.c",
    ".github/spikes/368/qualification.d",
    ".github/spikes/368/test_admission.py",
    ".github/workflows/aitm-368-hosted-qualification.yml",
)
PRECEDENT = ("bounded.py", "controller.py", "full_suite.py", "selected_suite.py")
TOKEN = re.compile(rb"(?i)github_pat_|gh[oprsu]_[A-Za-z0-9]{20,}|authorization:\s*(bearer|basic)|-----BEGIN [A-Z ]*PRIVATE KEY-----")


def digest(path):
    with path.open("rb") as stream:
        return sha256(stream.read()).hexdigest()


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def run(*args, timeout=30, **kwargs):
    return subprocess.run(args, capture_output=True, timeout=timeout, **kwargs)


def good(*args, timeout=30, **kwargs):
    result = run(*args, timeout=timeout, **kwargs)
    require(result.returncode == 0, f"{Path(args[0]).name} exited {result.returncode}")
    return result.stdout


def output(folder, name, result):
    (folder / f"{name}.stdout").write_bytes(result.stdout)
    (folder / f"{name}.stderr").write_bytes(result.stderr)
    return result.returncode


def reconcile(trace, wait, target):
    match = re.fullmatch(r"WAIT (\d+) (\d+) 0", wait.strip())
    require(match is not None and int(match[1]) == target, "direct wait status lacks exact identity")
    child = int(match[2])
    require(child > 0 and child != target, "child identity invalid")
    expected = {
        ("READY", str(target)),
        ("U", str(target), "368"),
        ("P", str(target), str(child)),
        ("X", str(target), str(child)),
        ("S", str(target), str(child), "0"),
    }
    rows = [tuple(line.split()) for line in trace.splitlines() if line.strip()]
    exits = [r for r in rows if len(r) == 4 and r[:3] == ("R", str(target), str(child)) and r[3].isdigit()]
    require(len(exits) == 1 and Counter(rows) == Counter([*expected, exits[0]]),
            "missing, duplicate or unbound process trace record")
    return child


def put_root(path, mode, source=None):
    if source is None:
        good("/usr/bin/sudo", "-n", "/usr/bin/install", "-d", "-o", "root", "-g", "wheel", "-m", mode, str(path))
    else:
        good("/usr/bin/sudo", "-n", "/usr/bin/install", "-o", "root", "-g", "wheel", "-m", mode, str(source), str(path))


def verify_job(receipt):
    head = good("/usr/bin/git", "rev-parse", "HEAD").decode().strip()
    tree = good("/usr/bin/git", "rev-parse", "HEAD^{tree}").decode().strip()
    require(head == os.environ["GITHUB_SHA"] and os.environ["GITHUB_REF"] == BRANCH
            and os.environ["GITHUB_REPOSITORY"] == "kburson/aitm"
            and os.environ["GITHUB_ACTOR"] == "kburson", "workflow job identity differs")
    require(good("/usr/bin/git", "rev-parse", BASE + "^{tree}").decode().strip() == TREE, "product tree differs")
    additions = good("/usr/bin/git", "diff", "--name-status", BASE, head).decode().splitlines()
    require(sorted(additions) == sorted(f"A\t{path}" for path in ALLOWED), "unexpected experimental tree changes")
    identities = {path: digest(Path(path)) for path in ALLOWED}
    image = os.environ.get("ImageVersion") or os.environ.get("IMAGE_VERSION")
    require(bool(image), "runner image version unavailable")
    info = {
        "sha": head, "tree": tree, "repository": os.environ["GITHUB_REPOSITORY"],
        "ref": BRANCH, "workflow": os.environ["GITHUB_WORKFLOW_REF"],
        "run": int(os.environ["GITHUB_RUN_ID"]), "attempt": int(os.environ["GITHUB_RUN_ATTEMPT"]),
        "image": image, "image_label": os.environ.get("ImageOS") or os.environ.get("IMAGE_OS"),
        "architecture": good("/usr/bin/uname", "-m").decode().strip(),
        "os": good("/usr/bin/sw_vers").decode().splitlines(),
        "sip": good("/usr/bin/csrutil", "status").decode().strip(),
        "base": BASE, "base_tree": TREE, "source_sha256": identities,
        "compiler": good("/usr/bin/xcrun", "clang", "--version").decode().splitlines(),
        "xcode": good("/usr/bin/xcodebuild", "-version").decode().splitlines(),
        "sdk": good("/usr/bin/xcrun", "--sdk", "macosx", "--show-sdk-version").decode().strip(),
    }
    require(info["architecture"] == "arm64" and "ProductName:" in info["os"][0], "wrong hosted platform")
    receipt["identity"] = info


def worker_command(profile=None):
    args = ["/usr/bin/sudo", "-n", "-u", WORKER, "/usr/bin/env", "-i",
            "PATH=/usr/bin:/bin", "LC_ALL=C", f"HOME={SCRATCH}", f"TMPDIR={SCRATCH}"]
    if profile is not None:
        args.extend(("/usr/bin/sandbox-exec", "-f", str(profile)))
    return args


def prepare_boundary(private, raw, receipt):
    require(not ROOT.exists() and WORKER not in {row.pw_name for row in pwd.getpwall()}, "prior worker state present")
    put_root(ROOT, "0755")
    put_root(STAGED, "0755")
    uid = next(uid for uid in range(550, 600) if uid not in {row.pw_uid for row in pwd.getpwall()})
    account = f"/Users/{WORKER}"
    create = ("/usr/bin/sudo", "-n", "/usr/bin/dscl", ".", "-create", account)
    good(*create)
    for key, value in (("UniqueID", str(uid)), ("PrimaryGroupID", "20"), ("IsHidden", "1"),
                       ("NFSHomeDirectory", str(SCRATCH)), ("UserShell", "/usr/bin/false"), ("Password", "*")):
        good(*create, key, value)
    good("/usr/bin/sudo", "-n", "/usr/bin/install", "-d", "-o", WORKER, "-g", "staff", "-m", "0700", str(SCRATCH))
    device = good("/bin/df", "-P", str(ROOT)).decode().splitlines()[-1].split()[0]
    volume = plistlib.loads(good("/usr/sbin/diskutil", "info", "-plist", device))
    mounts = good("/sbin/mount")
    (raw / "mounts.stdout").write_bytes(mounts)
    require(not re.search(rb"\b(smbfs|nfs|webdav|virtiofs|prl_fs)\b", mounts, re.I), "unexpected shared mount")
    require(volume["FilesystemType"] == "apfs", "runner staging is not APFS")
    base = worker_command()
    worker_uid = int(good(*base, "/usr/bin/id", "-u"))
    groups = list(map(int, good(*base, "/usr/bin/id", "-G").split()))
    require(worker_uid == uid and uid not in (0, os.getuid()) and not {0, 80}.intersection(groups), "worker is privileged")
    elevated = run(*base, "/usr/bin/sudo", "-n", "/usr/bin/true")
    require(elevated.returncode != 0, "worker elevation available")
    keys = sorted(row.partition(b"=")[0].decode() for row in good(*base, "/usr/bin/env").splitlines())
    require(keys == ["HOME", "LC_ALL", "PATH", "TMPDIR"], "unexpected worker environment keys")

    markers = {
        "input": (STAGED / "input", "0444"),
        "outside": (ROOT / "outside", "0666"),
        "controller": (private / "controller", "0600"),
        "credential": (private / "credential-canary", "0600"),
        "checkout": (Path.cwd() / ".aitm368-checkout-canary", "0644"),
        "controller_home": (Path.home() / ".aitm368-controller-canary", "0644"),
    }
    for name, (path, mode) in markers.items():
        local = private / f"{name}.sample"
        local.write_text("public synthetic marker\n")
        if path.parent in (ROOT, STAGED):
            put_root(path, mode, local)
        else:
            with path.open("xb") as stream:
                stream.write(local.read_bytes())
            path.chmod(int(mode, 8))

    profile_src = private / "worker.sb"
    roots = ("/usr", "/System", "/Library/Apple", "/private/etc", "/dev", str(STAGED), str(SCRATCH))
    allowed_reads = "\n".join(f'(allow file-read* (subpath {json.dumps(path)}))' for path in roots)
    profile_src.write_text(
        '(version 1)\n(allow default)\n(deny file-read*)\n'
        '(allow file-read-data (literal "/"))\n' + allowed_reads +
        '\n(deny network*)\n(deny file-write*)\n' +
        f'(allow file-write* (subpath {json.dumps(str(SCRATCH))}) (literal "/dev/null"))\n'
    )
    profile = STAGED / "worker.sb"
    put_root(profile, "0444", profile_src)
    (raw / "worker.sb").write_bytes(profile_src.read_bytes())
    staged_probe = STAGED / "qualification"
    header = private / "qualification.h"
    source = private / "qualification.c"
    source.write_bytes((HERE / "qualification.c").read_bytes())
    good("/usr/sbin/dtrace", "-h", "-s", str(HERE / "qualification.d"), "-o", str(header))
    build = run("/usr/bin/clang", "-Wall", "-Wextra", "-Werror", "-O2", str(source), "-o", str(private / "qualification"))
    require(output(raw, "probe-build", build) == 0, "benign probe build failed")
    put_root(staged_probe, "0555", private / "qualification")

    receipt["boundary"] = {
        "filesystem": "apfs", "controller_uid": os.getuid(), "worker_uid": uid, "worker_groups": groups,
        "worker_environment_keys": keys, "worker_sudo_denied": True, "profile_sha256": digest(profile),
        "probe_sha256": digest(staged_probe), "inherited_socket_descriptors": False,
        "markers": {name: {"uid": path.stat().st_uid, "mode": f"{stat.S_IMODE(path.stat().st_mode):04o}",
                           "sha256": digest(path)} for name, (path, _) in markers.items()},
    }
    command = worker_command(profile)
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        listener.settimeout(3)
        address = listener.getsockname()
        with socket.create_connection(address, timeout=3) as positive:
            server, _ = listener.accept()
            with server:
                positive.sendall(b"qualification")
                require(server.recv(13) == b"qualification", "controller loopback positive control failed")
        result = run(*command, str(staged_probe), "check", str(markers["input"][0]), str(SCRATCH / "written"),
                     str(markers["outside"][0]), str(markers["controller"][0]), str(markers["credential"][0]),
                     str(address[1]), str(markers["checkout"][0]), str(markers["controller_home"][0]), timeout=12)
        require(output(raw, "worker-boundary", result) == 0, f"worker boundary controls refused at {result.returncode}")
        require(b"DENY socket creation" in result.stdout or b"DENY loopback connect" in result.stdout,
                "missing explicit network denial")
        require(not select.select([listener], [], [], 0.2)[0], "worker connected to protected listener")
    for name, (path, mode) in markers.items():
        require(f"{stat.S_IMODE(path.stat().st_mode):04o}" == mode and
                path.stat().st_uid == receipt["boundary"]["markers"][name]["uid"] and
                digest(path) == receipt["boundary"]["markers"][name]["sha256"], "sentinel metadata or bytes drifted")
    receipt["boundary"]["passed"] = True
    receipt["boundary"]["loopback_controller_positive"] = True
    receipt["boundary"]["worker_loopback_denied"] = True
    return uid, command, staged_probe


def one_line(process):
    require(select.select([process.stdout], [], [], 14)[0], "diagnostic readiness timeout")
    return process.stdout.readline()


def bind_process(pid, launcher, uid, binary):
    checked = []
    for _ in range(8):
        current = good("/bin/ps", "-o", "ppid=", "-o", "uid=", "-o", "comm=", "-p", str(pid)).decode().strip()
        parent, owner, image = current.split(maxsplit=2)
        if not checked:
            require(int(owner) == uid and Path(image).name == binary.name, "target identity differs")
        checked.append(pid)
        if pid == launcher:
            return checked
        pid = int(parent)
    raise ValueError("target process does not descend from the launched child")


def trace_attempt(private, raw, receipt, uid, command, binary):
    stat_result = run("/usr/bin/sudo", "-n", "/usr/sbin/dtrace", "-l")
    require(output(raw, "provider-inventory", stat_result) == 0, "stock DTrace inventory unavailable")
    probes = [row.split() for row in stat_result.stdout.decode().splitlines()]
    providers = dict(sorted(Counter(row[1] for row in probes if len(row) > 1 and row[0].isdigit()).items()))
    receipt["trace"] = {"static_providers": providers, "passed": False}
    require("proc" in providers and "syscall" in providers, "required stock process or syscall provider unavailable")

    program = private / "early.d"
    program.write_text(f"""
dtrace:::BEGIN {{ printf("READY %d\\n", $target); }}
aitmqual$target:::phase
/pid == $target && uid == {uid}/
{{ printf("U %d %d\\n", pid, arg0); }}
proc:::create
/pid == $target && uid == {uid}/
{{ printf("P %d %d\\n", pid, args[0]->pr_pid); }}
proc:::exec-success
/ppid == $target && uid == {uid}/
{{ printf("X %d %d\\n", ppid, pid); }}
syscall::exit:entry
/ppid == $target && uid == {uid}/
{{ printf("S %d %d %d\\n", ppid, pid, arg0); }}
proc:::exit
/ppid == $target && uid == {uid}/
{{ printf("R %d %d %d\\n", ppid, pid, arg0); }}
""")
    (raw / "early.d").write_bytes(program.read_bytes())
    worker = subprocess.Popen([*command, str(binary), "trace"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, start_new_session=True)
    tracer = None
    target_line = trace_ready = b""
    result = None
    trace_result = None
    try:
        target_line = one_line(worker)
        target_match = re.fullmatch(rb"TARGET (\d+)\n", target_line)
        require(target_match is not None, "benign worker target handshake invalid")
        pid = int(target_match[1])
        receipt["trace"]["lineage"] = bind_process(pid, worker.pid, uid, binary)
        tracer = subprocess.Popen(["/usr/bin/sudo", "-n", "/usr/sbin/dtrace", "-Z", "-q", "-x", "switchrate=50hz",
                                   "-p", str(pid), "-s", str(program)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        trace_ready = one_line(tracer)
        require(trace_ready.strip() == f"READY {pid}".encode(), "controller trace was not ready")
        result = worker.communicate(b"\n", timeout=15)
        trace_result = tracer.communicate(timeout=25)
        require(worker.returncode == 0 and tracer.returncode == 0, "worker or observer returned failure")
        require(not re.search(rb"\b(error|drops?|failed|fault)\b", trace_result[1], re.I), "observer reported loss")
        child = reconcile((trace_ready + trace_result[0]).decode(), result[0].decode(), pid)
        receipt["trace"].update(passed=True, observed_pid=pid, child_pid=child, controller_wait_status=worker.returncode)
    finally:
        if result is None:
            if worker.poll() is None:
                run("/usr/bin/sudo", "-n", "/bin/kill", "-KILL", f"-{worker.pid}", timeout=5)
            result = worker.communicate(timeout=10)
        (raw / "benign-worker.stdout").write_bytes(target_line + result[0])
        (raw / "benign-worker.stderr").write_bytes(result[1])
        if tracer is not None:
            if trace_result is None:
                if tracer.poll() is None:
                    run("/usr/bin/sudo", "-n", "/bin/kill", "-INT", str(tracer.pid), timeout=5)
                trace_result = tracer.communicate(timeout=10)
            (raw / "early-trace.stdout").write_bytes(trace_ready + trace_result[0])
            (raw / "early-trace.stderr").write_bytes(trace_result[1])


def load_precedent(private):
    fetched = run("/usr/bin/git", "fetch", "--no-tags", "origin", REFERENCE, timeout=60)
    require(fetched.returncode == 0, "pinned #146 harness unavailable")
    sources = private / "precedent"
    sources.mkdir()
    for name in PRECEDENT:
        path = f".github/spikes/146/{name}"
        (sources / name).write_bytes(good("/usr/bin/git", "show", f"{REFERENCE}:{path}"))
    sys.path.insert(0, str(sources))
    return importlib.import_module("controller"), {name: digest(sources / name) for name in PRECEDENT}


def runtime_manifest(*directories):
    files = {}
    for root in directories:
        for path in (root, *sorted(root.rglob("*"))):
            info = path.lstat()
            relative = str(path.relative_to(ROOT))
            row = {"mode": f"{stat.S_IMODE(info.st_mode):04o}"}
            if path.is_symlink():
                target = path.resolve(strict=True)
                require(any(target == parent or target.is_relative_to(parent) for parent in directories),
                        "runtime has a link to a Stage A-only path")
                row.update(kind="symlink", target=os.readlink(path))
            elif path.is_dir():
                row["kind"] = "directory"
            else:
                require(path.is_file(), "runtime has an unsupported entry")
                row.update(kind="file", sha256=digest(path))
            files[relative] = row
    return files


def build_runtime(private, raw, receipt):
    old, identities = load_precedent(private)
    receipt["build"] = {"precedent": REFERENCE, "precedent_sha256": identities, "passed": False}
    logs = old.DiagnosticLogs(raw, ())
    src = ROOT / "source"
    locked = ROOT / "build-lock"
    for path in (src, locked):
        good("/usr/bin/sudo", "-n", "/usr/bin/install", "-d", "-o", str(os.getuid()), "-m", "0755", str(path))
    data = good("/usr/bin/git", "archive", BASE, "packages/aitm-usage", "tools/ci", timeout=30)
    proc = subprocess.run(["/usr/bin/tar", "-xf", "-", "-C", str(src)], input=data, capture_output=True, timeout=60)
    require(output(raw, "product-archive", proc) == 0, "pinned product source staging failed")
    project = src / "packages/aitm-usage"
    uv = run("uv", "--version")
    require(output(raw, "uv-identity", uv) == 0 and uv.stdout.startswith(b"uv 0.10.6"), "uv identity differs")
    env = dict(os.environ, UV_PYTHON_INSTALL_DIR=str(locked / "python"),
               UV_PROJECT_ENVIRONMENT=str(locked / "venv"))
    sync = run("uv", "sync", "--locked", "--no-config", "--managed-python", "--python", "3.13.9",
               "--project", str(project), cwd=src, env=env, timeout=170)
    require(output(raw, "runtime-lock-sync", sync) == 0, "pinned product lock could not be staged")
    receipt["build"]["lock_sha256"] = digest(project / "uv.lock")
    backend = old.build_trace_python(ROOT, logs, receipt, full=True)
    install = ROOT / "observed-venv"
    locked_site = locked / "venv/lib/python3.13/site-packages"

    def logged(*args, **kwargs):
        argv = args[0]
        if argv[0] == "/usr/bin/make":
            result = run(*argv, **kwargs)
            require(output(raw, "trace-install", result) == 0, "instrumented install failed")
            return result.stdout.decode().strip()
        return old.good(*args, **kwargs)

    binary, patches = old.full_suite.install_runtime(backend, install, locked_site, src, logged)
    directories = (backend.parent / "installed", install)
    good("/bin/chmod", "-R", "a+rX,go-w", *map(str, directories))
    good("/usr/bin/sudo", "-n", "/usr/sbin/chown", "-Rh", "root:wheel", *map(str, directories))
    version = run(str(install / "bin/python"), "-I", "-B", "-m", "pytest", "--version",
                  env={"PATH": "/usr/bin:/bin", "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"})
    require(output(raw, "instrumented-pytest-identity", version) == 0 and b"pytest 9.2.0" in version.stdout,
            "patched pytest identity differs")
    probes = run("/usr/bin/otool", "-s", "__TEXT", "__dof_python", str(binary))
    require(output(raw, "installed-probe-table", probes) == 0 and b"__dof_python" in probes.stdout,
            "installed CPython probe table missing")
    manifest = runtime_manifest(*directories)
    (raw / "runtime-manifest.json").write_text(json.dumps(manifest, sort_keys=True) + "\n")
    bundle = raw / "runtime.tar.gz"
    with tarfile.open(bundle, "w:gz") as stream:
        for path in directories:
            stream.add(path, arcname=str(path.relative_to(ROOT)))
    receipt["build"].update(
        passed=True, python_sha256=digest(binary), pytest_patches=patches,
        probe_table_sha256=digest(raw / "installed-probe-table.stdout"),
        manifest_sha256=digest(raw / "runtime-manifest.json"), runtime_archive_sha256=digest(bundle),
        runtime_prefix=str(ROOT),
    )


def publish(raw, exported, receipt):
    # Stage only explicit harness evidence. The job environment itself is never exported.
    candidates = {
        "worker.sb", "early.d", "runtime.tar.gz", "runtime-manifest.json",
        *(f"{label}.{stream}" for label in (
            "mounts", "probe-build", "worker-boundary", "provider-inventory", "benign-worker", "early-trace",
            "product-archive", "uv-identity", "runtime-lock-sync", "trace-install",
            "instrumented-pytest-identity", "installed-probe-table",
        ) for stream in ("stdout", "stderr")),
    }
    paths = [raw / name for name in sorted(candidates) if (raw / name).is_file()]
    for label in ("download", "extract", "configure", "compile", "spawn", "dof"):
        for channel in ("stdout", "stderr"):
            path = raw / "diagnostics" / f"trace-build-{label}.{channel}.log"
            if path.is_file():
                paths.append(path)
    files = {}
    secret = False
    for path in paths:
        data = path.read_bytes()
        if TOKEN.search(data):
            secret = True
            continue
        final = exported / path.name
        final.write_bytes(data)
        files[final.name] = {"bytes": len(data), "sha256": sha256(data).hexdigest()}
    if secret:
        receipt.update(verdict="HOLD", gate="evidence-screen", failure="required evidence withheld by screening")
    receipt["export"] = files
    (exported / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"verdict": receipt["verdict"], "gate": receipt["gate"],
                      "failure": receipt.get("failure"), "receipt_sha256": digest(exported / "receipt.json")}))
    return 0 if receipt["verdict"] == "PASS" else 1


def main():
    os.umask(0o077)
    private = Path(sys.argv[1])
    require(private.parent == Path(os.environ["RUNNER_TEMP"]) and not private.exists(), "unexpected evidence directory")
    private.mkdir(mode=0o700)
    raw = private / "protected"
    exported = private / "published"
    raw.mkdir()
    exported.mkdir()
    receipt = {
        "schema": "aitm.hosted-observation-admission/v1", "story": 368, "plan_sha256": PLAN,
        "verdict": "HOLD", "gate": "job-identity", "test_mode": "synthetic-admission-and-runtime-build",
        "product_tests_executed": 0, "candidate_code_resistance": "unqualified",
    }
    try:
        verify_job(receipt)
        receipt["gate"] = "worker-boundary"
        uid, command, binary = prepare_boundary(private, raw, receipt)
        receipt["gate"] = "trace-capability"
        trace_attempt(private, raw, receipt, uid, command, binary)
        receipt["gate"] = "runtime-build"
        build_runtime(private, raw, receipt)
        receipt.update(verdict="PASS", gate="complete")
    except (ValueError, OSError, subprocess.SubprocessError, KeyError) as error:
        receipt["failure"] = str(error) if isinstance(error, ValueError) else type(error).__name__
    return publish(raw, exported, receipt)


if __name__ == "__main__":
    raise SystemExit(main())
