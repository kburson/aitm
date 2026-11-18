"""Exercise the bounded advisory runner and its cooperative receipt."""

import json
import os
import sys
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools.ci.tia import working_tree_report, working_tree_run
from tools.ci.tia.local import _Copy, _Invocation, _Runtime

NODES = ["tests/test_scoped.py::test_one", "tests/test_scoped.py::test_two"]


def evidence(exit_code=0):
    return {
        "schema": "aitm.pytest-evidence/v1",
        "exit_code": exit_code,
        "collected": NODES.copy(),
        "deselected": [],
        "children": [],
        "reports": [
            {"nodeid": node, "when": phase, "outcome": "passed", "wasxfail": False}
            for node in NODES
            for phase in ("setup", "call", "teardown")
        ],
    }


def invocation(receipt, exit_code):
    return _Invocation(exit_code, 0.25, json.dumps(receipt).encode(), "")


@pytest.mark.parametrize("phase", [None, "call", "setup", "teardown"])
def test_complete_pass_and_failure(phase):
    exit_code = int(phase is not None)
    receipt = evidence(exit_code)
    if phase:
        failed = next(row for row in receipt["reports"] if row["when"] == phase)
        failed["outcome"] = "failed"
        if phase == "setup":
            receipt["reports"].pop(1)

    assert working_tree_run._validate(invocation(receipt, exit_code), NODES) == receipt


@pytest.mark.parametrize(
    ("change", "exit_code"),
    [
        (lambda data: data["collected"].pop(), 0),
        (lambda data: data["collected"].append(NODES[0]), 0),
        (lambda data: data["collected"].append("tests/test_extra.py::test_extra"), 0),
        (lambda data: data["reports"].pop(), 0),
        (lambda data: data["reports"].append(data["reports"][0]), 0),
        (lambda data: data["reports"][0].update(when="call"), 0),
        (lambda data: data["reports"][0].update(outcome="skipped"), 0),
        (lambda data: data["reports"][0].update(outcome="failed"), 0),
        (lambda data: data["reports"][0].update(wasxfail=True), 0),
        (lambda data: data.update(exit_code=1), 1),
        (lambda data: data.update(exit_code=2), 2),
    ],
)
def test_inconsistent_evidence_is_refused(change, exit_code):
    receipt = evidence()
    change(receipt)
    with pytest.raises(working_tree_run.Refusal):
        working_tree_run._validate(invocation(receipt, exit_code), NODES)


def test_missing_evidence_is_refused():
    with pytest.raises(working_tree_run.Refusal):
        working_tree_run._validate(_Invocation(0, 0.25, None, ""), NODES)


@pytest.mark.parametrize(
    ("initially_available", "drift", "launched", "status", "code"),
    [
        (False, None, 0, "unavailable", 2),
        (True, 1, 0, "unavailable", 2),
        (True, 2, 1, "unavailable", 2),
        (True, None, 1, "passed", 0),
    ],
)
def test_run_checks_snapshot_before_and_after(
    monkeypatch, tmp_path, initially_available, drift, launched, status, code
):
    report = {"mode": "pinned-mapped-obligations", "node_ids": NODES}
    snapshot = object()
    calls = []
    readbacks = iter(
        [
            report | {"snapshot_sha256": "changed" if drift == i else "original"}
            for i in range(3)
        ]
    )

    def inspect(repo, base):
        assert repo == tmp_path and base == "base"
        current = next(readbacks)
        if not initially_available:
            return working_tree_report._unavailable("unsupported-change"), None
        return current, snapshot

    def execute(profile, targets, *, collect):
        calls.append((profile, targets, collect))
        return invocation(evidence(), 0)

    def prepare(admitted, directory):
        assert admitted is snapshot
        assert not directory.is_relative_to(tmp_path)
        return SimpleNamespace(pytest=execute, verify=lambda: None)

    monkeypatch.setattr(working_tree_report, "_report_with_snapshot", inspect)
    monkeypatch.setattr(working_tree_run, "_capabilities", lambda directory: None)
    monkeypatch.setattr(working_tree_run, "_prepare", prepare)

    result = working_tree_run.run(tmp_path, "base")
    assert result["provenance"] == "local_advisory"
    assert (result["status"], result["exit_code"]) == (status, code)
    assert calls == [("pinned", NODES, False)] * launched
    if launched:
        assert result["pytest_returncode"] == 0
        assert result["worker_receipt"] == evidence()


def test_real_subprocess_reports_failure_and_runs_only_the_named_node(tmp_path):
    source = tmp_path / "source"
    config = source / "packages/aitm-usage/pyproject.toml"
    config.parent.mkdir(parents=True)
    files = {
        config.relative_to(source).as_posix(): "[tool.pytest.ini_options]\n",
        "test_scoped.py": (
            "import os\n"
            f"def test_selected():\n    assert os.getpid() == {os.getpid()}\n"
            "def test_outside_assignment():\n    raise AssertionError('unassigned')\n"
        ),
    }
    entries = {}
    directories = set()
    for name, content in files.items():
        path = source / name
        path.write_text(content)
        entries[name.encode()] = ("100644", sha256(path.read_bytes()).hexdigest())
        directories.update(
            folder.relative_to(source).as_posix().encode()
            for folder in path.parents
            if folder != source and folder.is_relative_to(source)
        )

    observer = tmp_path / "observer/pytest_evidence.py"
    observer.parent.mkdir()
    observer.write_bytes(
        (Path(__file__).resolve().parents[1] / observer.name).read_bytes()
    )
    (tmp_path / "venv").symlink_to(sys.prefix, target_is_directory=True)
    runtime = _Runtime(
        _Copy(source, frozenset(directories), entries),
        tmp_path,
        observer,
        sha256(observer.read_bytes()).hexdigest(),
    )

    assigned = ["test_scoped.py::test_selected"]
    child = runtime.pytest("pinned", assigned, collect=False)
    receipt = working_tree_run._validate(child, assigned)
    assert child.returncode == 1
    assert receipt["collected"] == assigned
    assert [row["outcome"] for row in receipt["reports"]] == [
        "passed",
        "failed",
        "passed",
    ]
    assert "unassigned" not in child.diagnostic
