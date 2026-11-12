"""Plan or run advisory test impact analysis against a local Git checkout."""

import argparse
import json
import os
import platform
import plistlib
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import asdict, dataclass, replace
from hashlib import sha256
from pathlib import Path
from time import monotonic

from tools.ci.python_gate import _outcomes

from . import inventory as t02
from .inventory import SuitePolicy, classify
from .python_graph import ProviderPolicy, PytestScope
from .selection import InventoryExpectation, InventoryPair, SelectionPolicy, select
from .snapshot import LocalRequest, SnapshotUncertain, _check_path, resolve

_PRODUCT = "packages/aitm-usage"
_CONFIG = f"{_PRODUCT}/pyproject.toml"
_LOCK = f"{_PRODUCT}/uv.lock"
_OBSERVER = "tools/ci/pytest_evidence.py"
_POLICY = "tools/ci/policy.json"
_SUITES = "tools/ci/tia/suites.json"
_EDGES = "tools/ci/tia/edges.json"
_PLATFORM = "darwin-apfs"
_CAPABILITIES = ("apfs", "darwin", "native-acl")
_SCHEMA = "aitm.tia-local/v1"
_PROVENANCE = "local_advisory"


class Refusal(Exception):
    """An exact local observation could not be established."""


def _canonical(value):
    return t02._canonical(value)


def _digest(data):
    return sha256(data).hexdigest()


def _checked(condition, detail):
    if not condition:
        raise Refusal(detail)


def _capture(args, *, cwd, env=None):
    return subprocess.run(args, cwd=cwd, env=env, capture_output=True, check=False)


def _git(cwd, *args):
    env = {
        name: value for name, value in os.environ.items() if not name.startswith("GIT_")
    }
    return _capture(["/usr/bin/git", "-C", cwd, *args], cwd=cwd, env=env)


def _request(base):
    cwd = Path.cwd()
    root = _git(cwd, "rev-parse", "--show-toplevel")
    _checked(
        root.returncode == 0 and root.stdout.endswith(b"\n"),
        "repository: Git checkout required",
    )
    repo = Path(os.fsdecode(root.stdout[:-1])).resolve()
    resolved = _git(
        repo, "rev-parse", "--verify", "--end-of-options", base + "^{commit}"
    )
    oid = resolved.stdout.decode("ascii", errors="replace").strip()
    _checked(
        resolved.returncode == 0 and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", oid),
        "base-ref: cannot resolve a commit",
    )
    remote = _git(repo, "config", "--get", "remote.origin.url")
    url = remote.stdout.decode("utf-8", errors="replace").strip()
    github = re.fullmatch(
        r"(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)"
        r"([\w.-]+/[\w.-]+?)(?:\.git)?/?",
        url,
        re.ASCII,
    )
    return repo, LocalRequest(
        github[1] if github else "local/checkout", "local-effective", oid
    )


def _capabilities(private):
    _checked(platform.system() == "Darwin", "capability: Darwin is required")
    disk = _capture(["/bin/df", "-P", private], cwd=private)
    lines = disk.stdout.splitlines()
    _checked(
        disk.returncode == 0 and len(lines) == 2 and lines[1].split(),
        "capability: cannot identify the private test volume",
    )
    info = _capture(
        ["/usr/sbin/diskutil", "info", "-plist", os.fsdecode(lines[1].split()[0])],
        cwd=private,
    )
    _checked(info.returncode == 0, "capability: cannot inspect the private test volume")
    try:
        filesystem = plistlib.loads(info.stdout)["FilesystemType"]
    except (ValueError, KeyError, plistlib.InvalidFileException) as error:
        raise Refusal("capability: cannot establish filesystem type") from error
    _checked(filesystem == "apfs", "capability: APFS is required")
    probe = private / "acl-probe"
    probe.touch()
    try:
        result = _capture(
            ["/bin/chmod", "+a", "everyone allow read", probe], cwd=private
        )
        _checked(result.returncode == 0, "capability: native ACL support is required")
    finally:
        probe.unlink()


def _link_destination(path, data, directories, files):
    _checked(
        bool(data) and b"\0" not in data and not data.startswith(b"/"),
        "copy: unsupported symlink target",
    )
    parts = path.split(b"/")[:-1]
    tokens = data.split(b"/")
    for index, token in enumerate(tokens):
        if token == b"..":
            _checked(parts, "copy: symlink escapes the snapshot")
            parts.pop()
        elif token != b".":
            _check_path(token, "local")
            parts.append(token)
        if parts and index < len(tokens) - 1:
            _checked(
                b"/".join(parts) in directories,
                "copy: symlink traverses an unobserved directory",
            )
    _checked(b"/".join(parts) in files, "copy: symlink has no observed regular target")


@dataclass(frozen=True)
class _Copy:
    root: Path
    directories: frozenset[bytes]
    entries: dict[bytes, tuple[str, str]]

    def verify(self):
        directories = set()
        entries = {}
        try:
            _checked(
                stat.S_ISDIR(self.root.lstat().st_mode),
                "copy-drift: source root replaced",
            )
            for directory, children, files in os.walk(
                self.root, followlinks=False, onerror=_walk_error
            ):
                parent = Path(directory)
                if parent != self.root:
                    directories.add(
                        os.fsencode(parent.relative_to(self.root).as_posix())
                    )
                for name in (*children, *files):
                    path = parent / name
                    raw = os.fsencode(path.relative_to(self.root).as_posix())
                    mode = path.lstat().st_mode
                    if stat.S_ISDIR(mode):
                        continue
                    if stat.S_ISLNK(mode):
                        entries[raw] = (
                            "120000",
                            _digest(os.fsencode(os.readlink(path))),
                        )
                    else:
                        _checked(stat.S_ISREG(mode), "copy-drift: non-regular source")
                        flag = "100755" if mode & stat.S_IXUSR else "100644"
                        entries[raw] = (flag, _digest(path.read_bytes()))
        except OSError as error:
            raise Refusal("copy-drift: cannot read materialized source") from error
        _checked(
            directories == self.directories and entries == self.entries,
            "copy-drift: materialized source changed",
        )


def _walk_error(error):
    raise error


def _freeze(snapshot, root):
    root.mkdir()
    directories = set()
    regular = set()
    entries = {}
    links = []
    for entry in snapshot.entries:
        raw = entry.path
        _check_path(raw, "local")
        _checked(raw not in entries, "copy: duplicate source path")
        path = root / raw.decode("utf-8")
        data = snapshot.read_content(raw)
        entries[raw] = (entry.mode, _digest(data))
        parents = raw.split(b"/")[:-1]
        directories.update(
            b"/".join(parents[:index]) for index in range(1, len(parents) + 1)
        )
        if entry.mode == "120000":
            links.append((raw, path, data))
            continue
        _checked(entry.mode in {"100644", "100755"}, "copy: unsupported source mode")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(data)
        path.chmod(0o755 if entry.mode == "100755" else 0o644)
        regular.add(raw)
    for raw, path, data in links:
        _link_destination(raw, data, directories, regular)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(os.fsdecode(data))
    copy = _Copy(root, frozenset(directories), entries)
    copy.verify()
    return copy


def _env():
    return {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("PYTEST_", "PYTHON", "UV_", "GIT_", "AITM_CI_"))
        and key not in {"VIRTUAL_ENV", "__PYVENV_LAUNCHER__"}
    }


@dataclass(frozen=True)
class _Runtime:
    source: _Copy
    directory: Path
    observer: Path
    observer_sha256: str

    @property
    def root(self):
        return self.source.root

    def verify(self):
        self.source.verify()
        try:
            intact = (
                stat.S_ISREG(self.observer.lstat().st_mode)
                and _digest(self.observer.read_bytes()) == self.observer_sha256
            )
        except OSError:
            intact = False
        _checked(intact, "copy-drift: bound pytest observer changed")

    def pytest(self, profile, targets, *, collect):
        self.verify()
        task = self.directory / ("collect-" if collect else "run-") / profile
        task.mkdir(parents=True)
        receipt = task / "receipt.json"
        env = _env() | {
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPATH": os.pathsep.join(
                map(
                    str,
                    (
                        self.observer.parent,
                        self.root / "tools/ci",
                        self.root / _PRODUCT / "src",
                    ),
                )
            ),
            "AITM_CI_PYTEST_EVIDENCE": str(receipt),
        }
        if not collect:
            env["AITM_CI_CHILD_EVIDENCE"] = "1"
        args = [
            self.directory / "venv/bin/python",
            "-P",
            "-m",
            "pytest",
            "-q",
            "-p",
            "pytest_evidence",
            "-p",
            "no:cacheprovider",
            "-c",
            self.root / _CONFIG,
            "-o",
            "addopts=",
            "--rootdir",
            self.root,
            "--confcutdir",
            self.root,
            "--basetemp",
            task / "fixtures",
        ]
        if collect:
            args.append("--collect-only")
        started = monotonic()
        process = _capture([*args, "--", *targets], cwd=self.root, env=env)
        elapsed = round(monotonic() - started, 3)
        try:
            raw = (
                receipt.read_bytes() if stat.S_ISREG(receipt.lstat().st_mode) else None
            )
        except OSError:
            raw = None
        diagnostic = (process.stdout + process.stderr).decode(errors="replace").strip()
        return _Invocation(process.returncode, elapsed, raw, diagnostic)


@dataclass(frozen=True)
class _Invocation:
    returncode: int
    seconds: float
    raw: bytes | None
    diagnostic: str

    def receipt(self):
        try:
            evidence = t02._read(self.raw, "aitm.pytest-evidence/v1")
            nodes = evidence.get("collected")
            _checked(
                type(evidence.get("exit_code")) is int
                and evidence["exit_code"] == self.returncode
                and isinstance(nodes, list)
                and bool(nodes)
                and all(isinstance(node, str) and node for node in nodes)
                and len(set(nodes)) == len(nodes)
                and evidence.get("deselected") == []
                and isinstance(evidence.get("reports"), list)
                and isinstance(evidence.get("children"), list),
                "pytest-evidence: inconsistent status, collection or reports",
            )
            return evidence
        except ValueError as error:
            raise Refusal("pytest-evidence: missing or malformed receipt") from error


def _prepare(snapshot, directory):
    directory.mkdir()
    copy = _freeze(snapshot, directory / "source")
    # A helper can launch its own pytest, whose built-in cache is independent
    # of our outer invocation. Keep that cache in runner scratch and seal the
    # link alongside the captured files. Preserve any existing source entry.
    entries = dict(copy.entries)
    for name, source in (("repo", copy.root), ("product", copy.root / _PRODUCT)):
        cache = source / ".pytest_cache"
        if source.is_dir() and not os.path.lexists(cache):
            scratch = directory / f"pytest-cache-{name}"
            scratch.mkdir()
            destination = os.path.relpath(scratch, source)
            cache.symlink_to(destination, target_is_directory=True)
            path = os.fsencode(cache.relative_to(copy.root).as_posix())
            entries[path] = ("120000", _digest(os.fsencode(destination)))
    copy = replace(copy, entries=entries)
    raw = (copy.root / _OBSERVER).read_bytes()
    observer = directory / "observer" / "pytest_evidence.py"
    observer.parent.mkdir()
    observer.write_bytes(raw)
    runtime = _Runtime(copy, directory, observer, _digest(raw))
    uv = shutil.which("uv")
    _checked(uv is not None, "runtime: uv is required")
    install = _capture(
        [
            uv,
            "sync",
            "--no-config",
            "--locked",
            "--python",
            "3.13.9",
            "--project",
            copy.root / _PRODUCT,
        ],
        cwd=copy.root,
        env=_env() | {"UV_PROJECT_ENVIRONMENT": str(directory / "venv")},
    )
    runtime.verify()
    _checked(
        install.returncode == 0,
        "runtime: locked uv sync failed\n"
        + install.stderr.decode(errors="replace").strip(),
    )
    return runtime


@dataclass(frozen=True)
class _Collected:
    runtime: _Runtime
    raw: bytes
    expected: InventoryExpectation
    rows: tuple[dict, ...]
    targets: dict[str, tuple[str, ...]]


def _collect(snapshot, directory):
    runtime = _prepare(snapshot, directory)
    root = runtime.root
    policy = SuitePolicy(
        (root / _SUITES).read_bytes(), (root / _POLICY).read_bytes(), "full"
    )
    rules = t02._policy(policy)
    binding = {
        "kind": _PROVENANCE,
        "repository": snapshot.repository,
        "snapshot": {"content_digest": snapshot.digest},
    }
    controls = {
        name: _digest((root / path).read_bytes())
        for name, path in (
            ("configuration", _CONFIG),
            ("lock", _LOCK),
            ("policy", _POLICY),
            ("suites", _SUITES),
        )
    }
    scopes = []
    targets = {}
    for profile, platform_scope in sorted(rules.workloads["full"]["required_pairs"]):
        _checked(
            platform_scope == _PLATFORM,
            f"capability: no local runner for {platform_scope}",
        )
        targets[profile] = tuple(rules.profiles[profile]["targets"])
        invocation = runtime.pytest(profile, targets[profile], collect=True)
        runtime.verify()
        _checked(
            invocation.returncode == 0,
            f"collection: {profile} exited {invocation.returncode}\n{invocation.diagnostic}",
        )
        receipt = invocation.receipt()
        _checked(
            receipt["reports"] == [] and receipt["children"] == [],
            "collection: collect-only receipt includes execution",
        )
        for node in receipt["collected"]:
            source = node.partition("::")[0].encode()
            _checked(
                runtime.source.entries.get(source, ("", ""))[0] in {"100644", "100755"},
                "collection: test source is not a regular snapshot entry",
            )
        scopes.append(
            {
                "profile": profile,
                "platform_scope": platform_scope,
                "runner": {
                    "profile": _PLATFORM,
                    "name": "local",
                    "os": "Darwin",
                    "filesystem": "apfs",
                },
                "capabilities": list(_CAPABILITIES),
                "observer": runtime.observer_sha256,
                "controls": controls,
                "receipt_sha256": _digest(invocation.raw),
                "binding": binding,
                "exit_code": 0,
                "complete": True,
                "deselected": [],
                "items": [
                    {"nodeid": node, "disposition": "collected"}
                    for node in receipt["collected"]
                ],
            }
        )
    raw = classify(
        _canonical(
            {"schema": "aitm.tia-collection/v1", "binding": binding, "scopes": scopes}
        ),
        policy,
    )
    inventory = json.loads(raw)
    expected = InventoryExpectation(
        _digest(raw),
        policy,
        tuple(map(_canonical, inventory["scopes"])),
    )
    return _Collected(runtime, raw, expected, tuple(inventory["obligations"]), targets)


def _provider(targets):
    config = (_CONFIG.encode(),)
    scopes = []
    for name, paths in targets.items():
        explicit = tuple(
            path.partition("::")[0].encode() for path in paths if not path.endswith("/")
        )
        roots = tuple(path.rstrip("/").encode() for path in paths if path.endswith("/"))
        scopes.append(PytestScope(name, explicit, roots, b"", config))
    return ProviderPolicy(
        (f"{_PRODUCT}/src".encode(), f"{_PRODUCT}/tests".encode(), b"tools/ci"),
        tuple(
            sorted(sys.stdlib_module_names | {"pytest", "_pytest", "coverage", "xdist"})
        ),
        tuple(scopes),
        (),
        (),
        (),
    )


def _path(raw):
    return (
        None
        if raw is None
        else {"hex": raw.hex(), "display": raw.decode("utf-8", errors="replace")}
    )


def _json_value(value):
    if isinstance(value, bytes):
        return _path(value)
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_value(item) for item in value]
    return value


def _snapshot_data(before, after):
    return {
        "repository": after.repository,
        "base": before.baseline_identity.commit,
        "base_tree": before.baseline_identity.tree,
        "before": before.digest,
        "after": after.digest,
        "worktree": after.endpoint_identity.worktree_digest,
    }


def _key(row):
    return tuple(
        row[field] for field in ("provider", "owner", "platform_scope", "nodeid")
    )


def _unavailable(reason):
    return {
        "provenance": _PROVENANCE,
        "mode": "unavailable",
        "selected": [],
        "reasons": [str(reason)],
    }


def _plan(before, after, private):
    plan = _unavailable("candidate inventory unavailable")
    plan.update(
        snapshot=_snapshot_data(before, after),
        changes=[
            {
                "status": change.status,
                "old": _path(change.old.path if change.old else None),
                "new": _path(change.new.path if change.new else None),
            }
            for change in after.changes
        ],
    )
    try:
        candidate = _collect(after, private / "candidate")
    except (Refusal, SnapshotUncertain, OSError, ValueError) as error:
        plan["reasons"] = [f"candidate-inventory: {error}"]
        return plan, None
    plan["inventory"] = {
        "candidate_sha256": candidate.expected.inventory_sha256,
        "candidate_suite_policy_sha256": _digest(
            candidate.expected.suite_policy.suites
        ),
        "candidate_ci103_policy_sha256": _digest(candidate.expected.suite_policy.ci103),
        "candidate_observer_sha256": candidate.runtime.observer_sha256,
    }
    full = {_key(row): row for row in candidate.rows}
    try:
        baseline = _collect(before, private / "baseline")
    except (Refusal, SnapshotUncertain, OSError, ValueError) as error:
        plan.update(
            mode="full",
            selected=list(full.values()),
            reasons=[f"baseline-inventory: {error}"],
        )
        return plan, candidate
    plan["inventory"].update(
        baseline_sha256=baseline.expected.inventory_sha256,
        baseline_suite_policy_sha256=_digest(baseline.expected.suite_policy.suites),
        baseline_ci103_policy_sha256=_digest(baseline.expected.suite_policy.ci103),
        baseline_observer_sha256=baseline.runtime.observer_sha256,
    )
    try:
        decision = select(
            before,
            after,
            InventoryPair(baseline.raw, candidate.raw),
            SelectionPolicy(
                baseline.expected,
                candidate.expected,
                _provider(candidate.targets),
                (candidate.runtime.root / _EDGES).read_bytes(),
            ),
        )
        _checked(
            decision.mode in {"selected", "full", "no-tests", "unavailable"},
            "selector returned an unknown mode",
        )
        details = _json_value(asdict(decision))
        keys = tuple(dict.fromkeys(decision.selected))
        _checked(
            all(key in full for key in keys),
            "selector returned a key outside the candidate inventory",
        )
        if decision.mode == "full":
            keys = tuple(full)
        elif decision.mode == "unavailable":
            keys = ()
        reasons = list(decision.reasons)
        if decision.mode == "full":
            uncertain = [path for path in decision.paths if path.uncertainties]
            if uncertain:
                kinds = sorted(
                    {reason.code for path in uncertain for reason in path.uncertainties}
                )
                reasons.append(
                    f"uncertain impact for {len(uncertain)} changed path(s): {', '.join(kinds)}"
                )
        plan.update(
            mode=decision.mode,
            reasons=reasons,
            selected=[full[key] for key in keys],
            selection=details,
        )
    except Exception as error:
        # Advisory selection failures may use the already verified complete inventory.
        plan.update(
            mode="full", selected=list(full.values()), reasons=[f"selector: {error}"]
        )
    return plan, candidate


def _recheck(repo, request, expected):
    try:
        current = resolve(repo, request)
    except (SnapshotUncertain, OSError) as error:
        raise Refusal(f"snapshot-drift: {error}") from error
    _checked(
        tuple(item.digest for item in current) == expected,
        "snapshot-drift: checkout changed after inspection",
    )


def _profile_result(invocation, rows):
    expected = {row["nodeid"] for row in rows}
    result = {
        "returncode": invocation.returncode,
        "seconds": invocation.seconds,
        "executed": 0,
        "outcomes": [],
        "children": [],
        "errors": [],
    }
    if invocation.returncode:
        result["diagnostic"] = invocation.diagnostic
    try:
        receipt = invocation.receipt()
    except Refusal as error:
        result["errors"].append(str(error))
        return result
    if set(receipt["collected"]) != expected:
        result["errors"].append(
            "pytest-evidence: runtime collection differs from the plan"
        )
    optional = {
        row["nodeid"]: row["optional_skip_reason"]
        for row in rows
        if row["optional_skip_reason"] is not None
    }
    try:
        outcomes, errors = _outcomes(receipt, optional)
    except (KeyError, TypeError, ValueError):
        outcomes, errors = {}, ["pytest-evidence: malformed phase reports"]
    result["errors"].extend(errors)
    observed = {}
    for report in receipt["reports"]:
        if isinstance(report, dict) and isinstance(report.get("nodeid"), str):
            node = report["nodeid"]
            if node in expected:
                observed[node] = (
                    observed.get(node, False) or report.get("outcome") == "failed"
                )
    result["executed"] = len(observed)
    result["outcomes"] = [
        {
            "nodeid": node,
            "outcome": "failed"
            if observed.get(node)
            else outcomes.get(node, "unknown"),
        }
        for node in sorted(expected)
    ]
    required = Counter(label for row in rows for label in row["required_children"])
    observed_children = Counter()
    child_pids = set()
    for child in receipt["children"]:
        if (
            isinstance(child, dict)
            and isinstance(child.get("label"), str)
            and type(child.get("pid")) is int
            and child["pid"] > 0
            and child["pid"] not in child_pids
            and type(child.get("returncode")) is int
            and child["returncode"] == 0
        ):
            result["children"].append(child)
            child_pids.add(child["pid"])
            observed_children[child["label"]] += 1
        else:
            result["errors"].append("pytest-evidence: invalid child process receipt")
    if observed_children != required:
        result["errors"].append(
            f"pytest-evidence: child receipts differ from plan (expected {', '.join(sorted(required)) or 'none'})"
        )
    return result


def _run(repo, request, identity, plan, candidate):
    started = monotonic()
    profiles = []
    errors = []
    status, code = "passed", 0
    try:
        _checked(
            plan["mode"] != "unavailable" and candidate is not None,
            "no applicable verified candidate inventory",
        )
        _recheck(repo, request, identity)
        for profile, targets in candidate.targets.items():
            rows = [row for row in plan["selected"] if row["profile"] == profile]
            if not rows:
                continue
            _recheck(repo, request, identity)
            args = (
                targets
                if plan["mode"] == "full"
                else tuple(row["nodeid"] for row in rows)
            )
            invocation = candidate.runtime.pytest(profile, args, collect=False)
            result = _profile_result(invocation, rows)
            profiles.append({"profile": profile, **result})
            if result["errors"] or invocation.returncode:
                status = "failed"
                if not code:
                    code = invocation.returncode or 2
                    code = 128 - code if code < 0 else code
            candidate.runtime.verify()
            _recheck(repo, request, identity)
    except (Refusal, SnapshotUncertain, OSError, ValueError) as error:
        status, code = "refused", 2
        errors.append(str(error))
    return {
        "provenance": _PROVENANCE,
        "plan_sha256": _digest(_canonical(plan)),
        "status": status,
        "exit_code": code,
        "seconds": round(monotonic() - started, 3),
        "profiles": profiles,
        "executed": sum(profile["executed"] for profile in profiles),
        "errors": errors,
    }


def _emit(plan, result):
    print(
        json.dumps(
            {"schema": _SCHEMA, "plan": plan, "result": result}, ensure_ascii=True
        )
    )
    counts = Counter((row["owner"], row["suite"]) for row in plan["selected"])
    scopes = ", ".join(
        f"{owner}/{suite} {count}" for (owner, suite), count in sorted(counts.items())
    )
    print(
        f"Local TIA {plan['mode']}: {len(plan['selected'])} selected"
        + (f" ({scopes})" if scopes else ""),
        file=sys.stderr,
    )
    for reason in plan["reasons"]:
        print(reason, file=sys.stderr)
    if result is not None:
        print(
            f"Local pytest {result['status']}: {result['executed']} executed in {result['seconds']:.3f}s (exit {result['exit_code']})",
            file=sys.stderr,
        )
        for profile in result["profiles"]:
            if profile["errors"]:
                print(f"{profile['profile']}: {profile['errors'][0]}", file=sys.stderr)
        for error in result["errors"]:
            print(error, file=sys.stderr)


def main(argv=None):
    """Use an explicit Git base to inspect, then optionally run, local obligations."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, metavar="REF")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument(
        "--plan", action="store_true", help="describe advisory selection"
    )
    modes.add_argument(
        "--run", action="store_true", help="execute and report advisory selection"
    )
    args = parser.parse_args(argv)
    repo, request, identity, candidate = None, None, (), None
    plan, result = None, None
    try:
        repo, request = _request(args.base)
        before, after = resolve(repo, request)
        identity = (before.digest, after.digest)
        temp_root = Path(tempfile.gettempdir()).resolve()
        _checked(
            not temp_root.is_relative_to(repo),
            "runtime: temporary directory must be outside the checkout",
        )
        with tempfile.TemporaryDirectory(
            prefix="aitm-tia-local-", dir=temp_root
        ) as path:
            private = Path(path)
            _capabilities(private)
            plan, candidate = _plan(before, after, private)
            if args.run:
                result = _run(repo, request, identity, plan, candidate)
            else:
                _recheck(repo, request, identity)
    except (Refusal, SnapshotUncertain, OSError, ValueError) as error:
        if plan is None:
            plan = _unavailable(error)
            if identity:
                plan["snapshot"] = _snapshot_data(before, after)
        else:
            plan.update(
                mode="unavailable", selected=[], reasons=[*plan["reasons"], str(error)]
            )
        if args.run:
            result = _run(repo, request, identity, plan, None)
    _emit(plan, result)
    return (
        result["exit_code"] if result else (2 if plan["mode"] == "unavailable" else 0)
    )


if __name__ == "__main__":
    raise SystemExit(main())
