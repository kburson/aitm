"""Measure serial and isolated worker execution on a fixed projected workload."""

from collections import Counter, defaultdict
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from time import monotonic

PROFILES = {"product": "packages/aitm-usage/tests/", "helpers": "tools/ci/tests/"}
CONFIG = """[run]
branch = True
parallel = True
relative_files = True
source =
    packages/aitm-usage/src/aitm_usage
    tools/ci
omit =
    tools/ci/tests/*
patch = subprocess
"""
NATIVE_SOURCE = "packages/aitm-usage/src/aitm_usage/"


def digest_text(items):
    return sha256(("\n".join(items) + "\n").encode()).hexdigest()


def required_ids(root):
    policy = json.loads((root / "tools/ci/policy.json").read_bytes())
    return set(policy["required_tests"]) | {
        "tools/ci/tests/test_cli_evidence.py::test_usage_console_help",
    }


def build_manifest(root, receipt, added):
    sha = (root / "source-sha").read_text().strip()
    assert sha == receipt["sha"]
    profiles = {}
    for name, base in PROFILES.items():
        collected = [
            row for row in (root / f"{name}.log").read_text().splitlines()
            if row.startswith(base) and "::" in row
        ]
        assert len(collected) == receipt["inventory"][name]["count"]
        assert digest_text(collected) == receipt["inventory"][name]["ordered_ids_sha256"]
        profiles[name] = collected
    full = [node for rows in profiles.values() for node in rows]
    assert len(full) == len(set(full))
    families = defaultdict(list)
    for node in full:
        families[node.split("::", 1)[0]].append(node)
    required = required_ids(root)
    assert required <= set(full)
    base = {
        family: max(1, len(set(nodes) & required))
        for family, nodes in families.items()
    }
    minimum = sum(base.values())
    if not minimum <= added < len(full):
        raise ValueError("Projected workload cannot preserve exact native witnesses and every family")
    quotas = {}
    capacity = len(full) - minimum
    for family, nodes in families.items():
        quotas[family] = divmod((added - minimum) * (len(nodes) - base[family]), capacity)
    lengths = {family: base[family] + quota[0] for family, quota in quotas.items()}
    left = added - sum(lengths.values())
    for family in sorted(quotas, key=lambda path: (-quotas[path][1], path))[:left]:
        lengths[family] += 1
    selected = set()
    for family, nodes in families.items():
        ordered = sorted(
            nodes,
            key=lambda node: (node not in required, sha256(f"aitm-290/v1:{node}".encode()).digest()),
        )
        selected.update(ordered[:lengths[family]])
    assert len(selected) == added and required <= selected
    projected = [node for node in full if node in selected]
    return {
        "source_sha": sha,
        "assignment_count": len(full) + len(projected),
        "family_counts": {
            family: {"full": len(nodes), "projected": lengths[family]}
            for family, nodes in families.items()
        },
        "cohorts": {"full": full, "projected": projected},
    }


def run_logged(args, cwd, env, log, timeout=1800):
    start = monotonic()
    with log.open("wb") as stream:
        result = subprocess.run(
            args, cwd=cwd, env=env, stdout=stream, stderr=subprocess.STDOUT, timeout=timeout,
        )
    elapsed = round(monotonic() - start, 3)
    if result.returncode:
        raise RuntimeError(f"Exit {result.returncode} after {elapsed}s. See {log}")
    return elapsed


def attest_run(root, out, width, expected):
    sys.path.insert(0, str(root / "tools/ci"))
    from coverage import CoverageData
    from pytest_evidence import reconcile_workers
    from python_gate import _outcomes

    evidence_path = out / "pytest.json"
    evidence = (
        reconcile_workers(evidence_path, width)
        if width > 1 else json.loads(evidence_path.read_bytes())
    )
    policy = json.loads((root / "tools/ci/policy.json").read_bytes())
    outcomes, errors = _outcomes(evidence, policy["optional_skips"])
    assert not errors, errors
    assert evidence["collected"] == expected
    assert set(outcomes) == set(expected)
    labels = []
    children = []
    for child in evidence["children"]:
        lines = defaultdict(set)
        for shard in out.glob(f".coverage.*.pid{child['pid']}.*"):
            data = CoverageData(basename=str(shard))
            data.read()
            for name in data.measured_files():
                if name.startswith(NATIVE_SOURCE):
                    lines[name].update(data.lines(name) or ())
        count = sum(map(len, lines.values()))
        assert child["returncode"] == 0 and child["pid"] > 0 and count > 0
        labels.append(child["label"])
        children.append({**child, "covered_product_lines": count})
    assert Counter(labels) == Counter(policy["required_children"])
    assert len({child["pid"] for child in children}) == len(children)
    return {
        "children": sorted(children, key=lambda child: child["label"]),
        "inventory_sha256": digest_text(expected),
        "outcome_counts": dict(Counter(outcomes.values())),
        "node_outcomes_sha256": sha256(json.dumps(outcomes, sort_keys=True).encode()).hexdigest(),
    }


def measure(root, work, manifest, width, cache):
    directory = work / f"workers-{width}-{cache}"
    directory.mkdir()
    assert (root / "source-sha").read_text().strip() == manifest["source_sha"]
    deps = work / f"cache-workers-{width}"
    env = {
        **os.environ, "UV_CACHE_DIR": str(deps), "PYTHONPATH": str(root / "tools/ci"),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1", "AITM_CI_CHILD_EVIDENCE": "1",
    }
    env.pop("PYTEST_ADDOPTS", None)
    py = root / "packages/aitm-usage/.venv/bin/python"
    assert deps.exists() == py.exists() == (cache == "warm")
    assert subprocess.check_output(["gh", "--version"], text=True).splitlines()[0].startswith("gh version 2.97.0 ")
    setup = run_logged(
        ["uv", "sync", "--project", "packages/aitm-usage", "--locked", "--python", "3.13.9"],
        root, env, directory / "setup.log", timeout=300,
    )
    storage = work / "native-fixtures" / directory.name
    storage.mkdir(parents=True)
    (storage / "scratch").mkdir()
    for cohort_name in manifest["cohorts"]:
        (storage / cohort_name).mkdir()
    start = monotonic()
    result = {}
    for cohort_name, nodes in manifest["cohorts"].items():
        out = directory / cohort_name
        out.mkdir()
        args = out / "assigned.txt"
        args.write_text("\n".join(nodes) + "\n")
        config = out / "coverage.rc"
        config.write_text(CONFIG)
        cell_env = {
            **env, "COVERAGE_FILE": str(out / ".coverage"), "COVERAGE_RCFILE": str(config),
            "AITM_CI_PYTEST_EVIDENCE": str(out / "pytest.json"),
            "TMPDIR": str(storage / "scratch"),
        }
        command = [
            str(py), "-m", "coverage", "run", "-m", "pytest", "-c", "packages/aitm-usage/pyproject.toml",
            "--rootdir", str(root), "-p", "no:cacheprovider", "-p", "pytest_evidence",
            "--basetemp", str(storage / cohort_name / "pytest"), "--durations=20", "--tb=long", "-q",
        ]
        if width > 1:
            command.extend(["-p", "xdist.plugin", "-n", str(width), "--dist", "worksteal"])
        test_wall = run_logged([*command, f"@{args}"], root, cell_env, out / "test.log")
        attest_started = monotonic()
        evidence = attest_run(root, out, width, nodes)
        coverage = [str(py), "-m", "coverage"]
        run_logged([*coverage, "combine", "--keep"], root, cell_env, out / "coverage-combine.log")
        run_logged([*coverage, "json", "--keep-combined", "-o", str(out / "coverage.json")], root, cell_env, out / "coverage-json.log")
        report = json.loads((out / "coverage.json").read_bytes())
        evidence["coverage"] = {
            category: {
                key: sum(row["summary"][key] for name, row in report["files"].items() if name.startswith(prefix))
                for key in ("covered_lines", "num_statements", "covered_branches", "num_branches")
            }
            for category, prefix in (("product", NATIVE_SOURCE), ("helper", "tools/ci/"))
        }
        assert all(metric["covered_lines"] > 0 for metric in evidence["coverage"].values())
        evidence["test_seconds"] = test_wall
        evidence["reconcile_seconds"] = round(monotonic() - attest_started, 3)
        (out / "evidence.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
        result[cohort_name] = evidence
        print(f"{width} {cache} {cohort_name}: {test_wall}s tests, {evidence['outcome_counts']}", flush=True)

    summary = {
        "sha": manifest["source_sha"], "assignments": manifest["assignment_count"],
        "workers": width, "cache": cache, "machine": platform.platform(),
        "cores": os.cpu_count(), "setup_seconds": setup, "queue_seconds": 0,
        "elapsed_seconds": round(setup + monotonic() - start, 3), "cohorts": result,
    }
    (directory / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    mode, *arguments = sys.argv[1:]
    if mode == "manifest":
        source, receipt = map(Path, arguments)
        print(json.dumps(build_manifest(source, json.loads(receipt.read_bytes()), 1203), indent=2, sort_keys=True))
    elif mode == "measure":
        source, out, manifest = map(Path, arguments[:3])
        measure(source, out, json.loads(manifest.read_bytes()), int(arguments[3]), arguments[4])
    else:
        raise ValueError(f"Unknown mode {mode}")
