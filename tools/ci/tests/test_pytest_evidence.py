import json
import os
import subprocess
import sys
from pathlib import Path

CI_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = CI_ROOT.parents[1]


def run_observed(tmp_path, *args, child_evidence=False, cwd=None):
    evidence = tmp_path / "evidence.json"
    env = {
        **os.environ,
        "PYTHONPATH": str(CI_ROOT),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "AITM_CI_PYTEST_EVIDENCE": str(evidence),
    }
    env.pop("PYTEST_ADDOPTS", None)
    env.pop("AITM_CI_CHILD_EVIDENCE", None)
    if child_evidence:
        env["AITM_CI_CHILD_EVIDENCE"] = "1"
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "pytest_evidence", "-q", *args],
        cwd=cwd or tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=45,
        check=False,
    )
    assert evidence.is_file(), result.stdout + result.stderr
    return result, json.loads(evidence.read_bytes())


def test_base_records_actual_phase_outcomes_and_deselection(tmp_path):
    (tmp_path / "test_sample.py").write_text(
        """\
import pytest

@pytest.mark.parametrize("value", [1, 2])
def test_pass(value):
    assert value > 0

def test_fail():
    assert False

@pytest.mark.skip(reason="host capability missing")
def test_skip():
    pass

@pytest.mark.xfail(reason="known failure")
def test_xfail():
    assert False

def test_deselect():
    assert False
""",
        encoding="utf-8",
    )
    result, evidence = run_observed(tmp_path, "test_sample.py", "-k", "not deselect")
    selected = [
        "test_sample.py::test_pass[1]",
        "test_sample.py::test_pass[2]",
        "test_sample.py::test_fail",
        "test_sample.py::test_skip",
        "test_sample.py::test_xfail",
    ]
    assert result.returncode == evidence["exit_code"] == 1
    assert evidence["schema"] == "aitm.pytest-evidence/v1"
    assert evidence["collected"] == selected
    assert evidence["deselected"] == ["test_sample.py::test_deselect"]
    assert evidence["children"] == []
    reports = {(item["nodeid"], item["when"]): item for item in evidence["reports"]}
    assert len(reports) == len(evidence["reports"]) == 14
    for nodeid in selected:
        assert reports[nodeid, "teardown"]["outcome"] == "passed"
    assert reports[selected[0], "call"]["outcome"] == "passed"
    assert reports[selected[2], "call"]["outcome"] == "failed"
    assert reports[selected[3], "setup"] == {
        "nodeid": selected[3],
        "when": "setup",
        "outcome": "skipped",
        "wasxfail": False,
        "skip_reason": "host capability missing",
    }
    assert (selected[3], "call") not in reports
    assert reports[selected[4], "call"]["wasxfail"] is True
    assert reports[selected[4], "call"]["outcome"] == "skipped"


def test_retains_duplicate_real_phase_reports(tmp_path):
    (tmp_path / "test_sample.py").write_text(
        "def test_pass():\n    assert True\n", encoding="utf-8"
    )
    (tmp_path / "conftest.py").write_text(
        """\
import pytest

@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    report = yield
    if report.when == "call":
        item.ihook.pytest_runtest_logreport(report=report)
    return report
""",
        encoding="utf-8",
    )
    result, evidence = run_observed(tmp_path, "test_sample.py")
    assert result.returncode == evidence["exit_code"] == 0
    assert [report["when"] for report in evidence["reports"]] == [
        "setup",
        "call",
        "call",
        "teardown",
    ]


def test_candidate_records_both_normally_exiting_subprocesses(tmp_path):
    cli = "tools/ci/tests/test_cli_evidence.py"
    service = (
        "packages/aitm-usage/tests/test_service.py"
        "::test_one_shot_status_uses_collecting_subprocess_pid"
    )
    result, evidence = run_observed(
        tmp_path,
        "--rootdir",
        str(REPO_ROOT),
        cli,
        service,
        child_evidence=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == evidence["exit_code"] == 0, (
        result.stdout + result.stderr
    )
    assert evidence["collected"] == [f"{cli}::test_usage_console_help", service]
    children = evidence["children"]
    assert {child["label"] for child in children} == {"cli-help", "service-one-shot"}
    assert len(children) == len({child["pid"] for child in children}) == 2
    assert all(type(child["pid"]) is int and child["pid"] > 0 for child in children)
    assert all(child["returncode"] == 0 for child in children)
