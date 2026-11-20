"""Run the reviewed category inventory in isolated pytest processes."""

import argparse
import csv
import hashlib
import json
import os
import secrets
import signal
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory

PROFILES = {
    "product": "packages/aitm-usage/tests",
    "ci": "tools/ci/tests",
    "board": "tools/board_sync/tests",
    "dashboard": "tools/story_dashboard/tests",
    "native": "packages/aitm-usage/native-tests",
}
CATEGORIES = ("fast-unit", "slow-unit", "local-integration", "systems-integration")
CATALOG = "tools/ci/category_sweep_catalog.tsv"
CONFIG = "packages/aitm-usage/pyproject.toml"
PLAN_SCHEMA = "aitm.category-sweep-plan/v1"
PYTEST_SCHEMA = "aitm.pytest-evidence/v1"
HISTORICAL_PIN = "17761cc1928fd916cf32a9c078d4a742bfcb32b8"
REQUIRED_CHILDREN = Counter({"cli-help": 1, "service-one-shot": 1})


class Refusal(ValueError):
    """The sweep lacks evidence required for a pass."""


def require(condition, message):
    if not condition:
        raise Refusal(message)


def assign(collections, catalog):
    lanes = {category: {} for category in CATEGORIES}
    all_ids = [node for ids in collections.values() for node in ids]
    observed = set(all_ids)
    require(len(observed) == len(all_ids), "duplicate collected test")
    missing = sorted(set(catalog) - observed)
    extra = sorted(observed - set(catalog))
    require(
        not missing and not extra,
        f"collection drift; missing={missing[:8]} extra={extra[:8]}",
    )
    for profile, ids in collections.items():
        require(profile in PROFILES, f"unknown profile {profile}")
        for node in ids:
            require(
                node.startswith(PROFILES[profile] + "/")
                and "::" in node
                and "\n" not in node
                and "\r" not in node,
                f"invalid node ID for {profile}: {node}",
            )
            category = catalog[node]
            require(category in lanes, f"unsupported category: {category}")
            lanes[category].setdefault(profile, []).append(node)
    return lanes


def expected_skip(node, host):
    if host == "darwin" and node.startswith(
        PROFILES["product"]
        + "/test_grok_scope_receipts.py::test_linux_scope_staging_and_hook_recheck_external_process_incarnation["
    ):
        return "Requires the Linux proc filesystem"
    if host == "linux" and node.startswith(
        PROFILES["native"] + "/test_darwin_acl.py::"
    ):
        return "requires macOS ACLs"
    if host == "linux" and node.startswith(
        PROFILES["native"] + "/test_darwin_watch.py::"
    ):
        return "requires FSEvents"
    if host == "linux" and node == (
        PROFILES["ci"]
        + "/test_tia_snapshot.py::test_local_git_config_and_path_identity"
    ):
        return "filesystem has no normalization aliases"
    return None


def validate(evidence, expected, host):
    require(evidence["schema"] == PYTEST_SCHEMA, "unknown pytest evidence schema")
    require(
        type(evidence["exit_code"]) is int and evidence["exit_code"] == 0,
        "pytest failed",
    )
    collected = evidence["collected"]
    require(
        not evidence["deselected"]
        and len(collected) == len(expected)
        and set(collected) == set(expected),
        "pytest assignment differs from plan",
    )
    phases = defaultdict(Counter)
    for report in evidence["reports"]:
        node, phase, outcome = (report[key] for key in ("nodeid", "when", "outcome"))
        require(
            node in expected and phase in {"setup", "call", "teardown"},
            "unexpected phase report",
        )
        require(
            not report["wasxfail"] and outcome in {"passed", "skipped"},
            f"failed phase: {node}",
        )
        if outcome == "skipped":
            require(
                expected_skip(node, host) is not None
                and report["skip_reason"] == expected_skip(node, host)
                and phase in {"setup", "call"},
                f"unexpected skip: {node}",
            )
        phases[node][phase] += 1
        if outcome == "skipped" and phase == "setup":
            phases[node]["setup-skip"] += 1
    for node in expected:
        counts = phases[node]
        require(
            counts["setup"] == counts["teardown"] == 1
            and (counts["call"] == 0 if counts["setup-skip"] else counts["call"] >= 1),
            f"incomplete phases: {node}",
        )
    children = Counter()
    for entry in evidence["children"]:
        require(
            entry["label"] in REQUIRED_CHILDREN
            and type(entry["pid"]) is int
            and entry["pid"] > 0
            and type(entry["returncode"]) is int
            and entry["returncode"] == 0,
            "unexpected or failed child process",
        )
        children[entry["label"]] += 1
    return children


def read(path):
    return json.loads(path.read_bytes())


def encoded(data):
    return (json.dumps(data, sort_keys=True, indent=2) + "\n").encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def seal(plan, lane, folder):
    files = {
        profile: digest((folder / f"{profile}.json").read_bytes())
        for profile in plan["lanes"][lane]
    }
    result = {
        "lane": lane,
        "source": plan["source"],
        "plan_sha256": digest(encoded(plan)),
        "profiles": files,
    }
    (folder / "worker.json").write_bytes(encoded(result))


def verify(plan, output, *, require_children=True):
    require(plan["schema"] == PLAN_SCHEMA, "unknown plan schema")
    lanes = plan["lanes"]
    active = {lane for lane, profiles in lanes.items() if profiles}
    actual = {folder.name for folder in output.iterdir() if folder.is_dir()}
    require(
        actual == active,
        f"missing or unexpected worker output: {sorted(active ^ actual)}",
    )
    children = Counter()
    tested = 0
    for lane in sorted(active):
        folder = output / lane
        metadata = folder / "worker.json"
        require(metadata.is_file(), f"missing worker seal: {lane}")
        receipt = read(metadata)
        require(
            receipt.get("plan_sha256") == digest(encoded(plan))
            and receipt.get("lane") == lane
            and receipt.get("source") == plan["source"]
            and set(receipt["profiles"]) == set(lanes[lane]),
            f"stale or incomplete worker seal: {lane}",
        )
        for profile, expected in lanes[lane].items():
            contents = (folder / f"{profile}.json").read_bytes()
            require(
                digest(contents) == receipt["profiles"][profile],
                "pytest receipt digest mismatch",
            )
            children.update(validate(json.loads(contents), expected, plan["host"]))
            tested += len(expected)
    if require_children:
        require(
            children == REQUIRED_CHILDREN,
            "required child results are missing or duplicated",
        )
    return {
        "status": "pass",
        "tested": tested,
        "children": dict(children),
        "plan_sha256": digest(encoded(plan)),
    }


def environment():
    return {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(
            ("PYTEST_", "PYTHON", "UV_", "GIT_", "AITM_CI_", "COVERAGE_")
        )
        and key
        not in {"VIRTUAL_ENV", "__PYVENV_LAUNCHER__", "GH_TOKEN", "GITHUB_TOKEN"}
    }


def supervise(commands, *, cwd, environment):
    processes = []
    original = signal.signal(signal.SIGINT, signal.default_int_handler)
    try:
        for log, command in commands.items():
            with log.open("wb") as out:
                process = subprocess.Popen(
                    command,
                    cwd=cwd,
                    env=environment,
                    stdout=out,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
            processes.append((log, process))
        failed = [str(log) for log, process in processes if process.wait()]
        require(not failed, "worker failed; see " + ", ".join(failed))
    finally:
        for _, process in processes:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
        signal.signal(signal.SIGINT, original)


def git(repository, *args):
    return subprocess.check_output(
        ["git", "-C", repository, *args], env=environment(), text=True
    ).strip()


def identity(repository):
    commit, tree = git(repository, "rev-parse", "HEAD", "HEAD^{tree}").splitlines()
    require(
        not git(repository, "status", "--porcelain", "--untracked-files=no"),
        "the tracked checkout is dirty",
    )
    return {"commit": commit, "tree": tree}


def workspace(repository, target, source):
    subprocess.run(
        [
            "git",
            "clone",
            "--quiet",
            "--local",
            "--no-hardlinks",
            "--no-checkout",
            "--",
            repository,
            target,
        ],
        env=environment(),
        check=True,
    )
    git(target, "checkout", "--quiet", "--detach", source["commit"])
    require(identity(target) == source, "worker checkout differs from source")
    objects = Path(
        git(target, "rev-parse", "--path-format=absolute", "--git-path", "objects")
    )
    require(
        git(target, "rev-parse", "--is-shallow-repository") == "false"
        and not (objects / "info/alternates").exists()
        and not any((objects / "pack").glob("*.promisor")),
        "the sweep needs standalone, complete Git history",
    )
    require(
        git(target, "cat-file", "-t", HISTORICAL_PIN) == "commit",
        "historical planning object is missing",
    )
    temp = target.parent / f"t-{target.name}"
    temp.mkdir(mode=0o700)
    env = environment() | {
        "TMPDIR": str(temp),
        "TMP": str(temp),
        "TEMP": str(temp),
        "UV_CACHE_DIR": str(temp / "uv"),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
    }
    subprocess.run(
        [
            "uv",
            "sync",
            "--project",
            "packages/aitm-usage",
            "--python",
            "3.13.9",
            "--locked",
        ],
        cwd=target,
        env=env,
        check=True,
    )
    return env, temp


def pytest_profile(repository, temp, env, output, profile, target, *, collect=False):
    paths = [repository, repository / "tools/ci"]
    if profile == "native":
        paths.append(repository / PROFILES["product"])
    receipt = output / f"{profile}.json"
    args = [
        repository / "packages/aitm-usage/.venv/bin/python",
        "-m",
        "pytest",
        "-c",
        CONFIG,
        "--rootdir",
        repository,
        "-p",
        "no:cacheprovider",
        "-p",
        "pytest_evidence",
        "--basetemp",
        temp / profile,
        "-q",
    ]
    if collect:
        args.append("--collect-only")
    args.append(target)
    with (output / f"{profile}.log").open("wb") as log:
        process = subprocess.run(
            args,
            cwd=repository,
            env=env
            | {
                "PYTHONPATH": os.pathsep.join(map(str, paths)),
                "AITM_CI_PYTEST_EVIDENCE": str(receipt),
                "AITM_CI_CHILD_EVIDENCE": "0" if collect else "1",
            },
            stdout=log,
            stderr=subprocess.STDOUT,
            check=False,
        )
    require(process.returncode == 0, f"pytest failed: {output / (profile + '.log')}")
    return read(receipt)


def run_worker(repository, scratch, output, plan, lane):
    target = scratch / lane
    output.mkdir(mode=0o700)
    env, temp = workspace(repository, target, plan["source"])
    assigned = plan["lanes"][lane]
    for profile in PROFILES:
        if profile not in assigned:
            continue
        nodes = assigned[profile]
        if lane == "serial":
            argument = PROFILES[profile]
        else:
            selection = output / f"{profile}.ids"
            selection.write_text("\n".join(nodes) + "\n", encoding="utf-8")
            argument = "@" + str(selection)
        pytest_profile(target, temp, env, output, profile, argument)
    require(
        identity(target) == plan["source"], "worker source changed during execution"
    )
    seal(plan, lane, output)


def read_catalog(path, host):
    require(host in {"darwin", "linux"}, f"unsupported host: {host}")
    result = {}
    with path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            node = row["nodeid"]
            require(row[host] in {"yes", "no"}, f"invalid host assignment: {node}")
            if row[host] == "yes":
                require(
                    node not in result and row["category"] in CATEGORIES,
                    f"invalid catalog entry: {node}",
                )
                result[node] = row["category"]
    return result


def sweep(repository, output, *, serial=False):
    source = identity(repository)
    host = sys.platform
    with TemporaryDirectory(prefix="as-", dir="/tmp") as directory:
        scratch = Path(directory).resolve()
        collector = scratch / "collect"
        env, temp = workspace(repository, collector, source)
        catalog = read_catalog(collector / CATALOG, host)
        collect_out = scratch / "observations"
        collect_out.mkdir(mode=0o700)
        collections = {}
        for profile, path in PROFILES.items():
            data = pytest_profile(
                collector, temp, env, collect_out, profile, path, collect=True
            )
            require(
                data["schema"] == PYTEST_SCHEMA
                and data["exit_code"] == 0
                and not data["deselected"],
                f"invalid collection receipt: {profile}",
            )
            collections[profile] = data["collected"]
        lanes = assign(collections, catalog)
        if serial:
            lanes = {"serial": collections}
        plan = {
            "schema": PLAN_SCHEMA,
            "source": source,
            "run": secrets.token_hex(16),
            "host": host,
            "lanes": lanes,
        }
        (output / "plan.json").write_bytes(encoded(plan))
        commands = {
            output / f"{lane}.log": [
                sys.executable,
                "-m",
                "tools.ci.category_sweep",
                "worker",
                str(repository),
                str(scratch),
                str(output),
                lane,
            ]
            for lane, profiles in lanes.items()
            if profiles
        }
        supervise(commands, cwd=repository, environment=environment())
    return verify(plan, output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    run.add_argument(
        "--output", type=Path, required=True, help="new directory for local receipts"
    )
    run.add_argument(
        "--serial", action="store_true", help="run the unsharded full reference"
    )
    worker = commands.add_parser("worker", help=argparse.SUPPRESS)
    for name in ("repository", "scratch", "output"):
        worker.add_argument(name, type=Path)
    worker.add_argument("lane", choices=(*CATEGORIES, "serial"))
    args = parser.parse_args()
    try:
        if args.command == "worker":
            plan = read(args.output / "plan.json")
            run_worker(
                args.repository, args.scratch, args.output / args.lane, plan, args.lane
            )
        else:
            output = args.output.resolve()
            repository = Path(git(Path.cwd(), "rev-parse", "--show-toplevel"))
            require(
                not output.is_relative_to(repository),
                "output must be outside the source checkout",
            )
            output.mkdir(mode=0o700)
            result = sweep(repository, output, serial=args.serial)
            (output / "result.json").write_bytes(encoded(result))
            print(
                f"Passed full sweep of {result['tested']} tests. Receipts at {output}."
            )
    except (
        ValueError,
        KeyError,
        TypeError,
        OSError,
        subprocess.CalledProcessError,
    ) as exc:
        print(f"Category sweep failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
