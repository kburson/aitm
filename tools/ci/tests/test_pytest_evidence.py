import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

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


@pytest.mark.parametrize("workers", [0, 2], ids=["serial", "parallel"])
def test_candidate_records_both_normally_exiting_subprocesses(tmp_path, workers):
    cli = "tools/ci/tests/test_cli_evidence.py"
    service = (
        "packages/aitm-usage/tests/test_service.py"
        "::test_one_shot_status_uses_collecting_subprocess_pid"
    )
    result, evidence = run_observed(
        tmp_path,
        *(["-p", "xdist.plugin", "-n", str(workers)] if workers else []),
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
    if workers:
        assert {item.name for item in tmp_path.glob("evidence-gw*.json")} == {
            "evidence-gw0.json",
            "evidence-gw1.json",
        }
        from pytest_evidence import reconcile_workers

        evidence = reconcile_workers(tmp_path / "evidence.json", workers)
    assert evidence["collected"] == [f"{cli}::test_usage_console_help", service]
    children = evidence["children"]
    assert {child["label"] for child in children} == {"cli-help", "service-one-shot"}
    assert len(children) == len({child["pid"] for child in children}) == 2
    assert all(type(child["pid"]) is int and child["pid"] > 0 for child in children)
    assert all(child["returncode"] == 0 for child in children)


@pytest.mark.parametrize(
    ("fault", "message"),
    [
        ("missing", "worker receipts"),
        ("extra", "worker receipts"),
        ("collection", "worker inventory"),
        ("deselection", "worker inventory"),
        ("failed", "worker inventory"),
        ("phase", "phase reports"),
        ("controller", "controller evidence"),
    ],
)
def test_reconcile_workers_rejects_incomplete_or_inconsistent_evidence(
    tmp_path, fault, message
):
    from pytest_evidence import reconcile_workers

    node = "test_example.py::test_value"
    report = {"nodeid": node, "when": "call", "outcome": "passed"}
    controller = {
        "schema": "aitm.pytest-evidence/v1",
        "exit_code": 0,
        "collected": [],
        "deselected": [],
        "reports": [report],
        "children": [],
    }
    worker = dict(controller, collected=[node])
    records = {
        "evidence.json": controller,
        "evidence-gw0.json": worker.copy(),
        "evidence-gw1.json": dict(worker, reports=[]),
    }
    if fault == "missing":
        del records["evidence-gw1.json"]
    elif fault == "extra":
        records["evidence-gw2.json"] = worker
    elif fault == "collection":
        records["evidence-gw1.json"]["collected"] = ["test_other.py::test_value"]
    elif fault == "deselection":
        records["evidence-gw1.json"]["deselected"] = [node]
    elif fault == "failed":
        records["evidence-gw1.json"]["exit_code"] = 1
    elif fault == "phase":
        records["evidence-gw1.json"]["reports"] = [report]
    else:
        controller["collected"] = [node]
    for filename, evidence in records.items():
        (tmp_path / filename).write_text(json.dumps(evidence), encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        reconcile_workers(tmp_path / "evidence.json", 2)
