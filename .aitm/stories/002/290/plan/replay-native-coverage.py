"""Retain exact-source raw coverage for both required child witnesses."""
import json
import os
from pathlib import Path
import sys

from benchmark import CONFIG, attest_run, run_logged

bench = Path(sys.argv[1])
nodes = [
    "packages/aitm-usage/tests/test_service.py::test_one_shot_status_uses_collecting_subprocess_pid",
    "tools/ci/tests/test_cli_evidence.py::test_usage_console_help",
]
storage = bench / "native-child-controls"
storage.mkdir()
for width in (1, 3):
    root = bench / f"source-{width}"
    out = bench / f"child-control-{width}"
    out.mkdir()
    tmp = storage / f"width-{width}"
    tmp.mkdir()
    config = out / "coverage.rc"
    config.write_text(CONFIG)
    env = {
        **os.environ, "COVERAGE_RCFILE": str(config), "COVERAGE_FILE": str(out / ".coverage"),
        "AITM_CI_CHILD_EVIDENCE": "1", "AITM_CI_PYTEST_EVIDENCE": str(out / "pytest.json"),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1", "PYTHONPATH": str(root / "tools/ci"),
    }
    env.pop("PYTEST_ADDOPTS", None)
    py = root / "packages/aitm-usage/.venv/bin/python"
    coverage = [str(py), "-m", "coverage"]
    options = ["-p", "xdist.plugin", "-n", "3", "--dist", "worksteal"] if width == 3 else []
    args = [
        "-c", "packages/aitm-usage/pyproject.toml", "--rootdir", str(root),
        "-p", "no:cacheprovider", "-p", "pytest_evidence", "--basetemp", str(tmp / "pytest"),
        "-q", "--tb=long",
    ]
    run_logged([*coverage, "run", "-m", "pytest", *args, *options, *nodes], root, env, out / "test.log")
    evidence = attest_run(root, out, width, nodes)
    run_logged([*coverage, "combine", "--keep"], root, env, out / "combine.log")
    run_logged([*coverage, "json", "--keep-combined", "-o", str(out / "coverage.json")], root, env, out / "json.log")
    for child in evidence["children"]:
        assert list(out.glob(f".coverage.*.pid{child['pid']}.*"))
    (out / "evidence.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print(width, evidence["children"])
