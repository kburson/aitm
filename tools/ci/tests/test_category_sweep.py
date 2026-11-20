import json
import os
import signal
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools.ci import category_sweep as sweep

UNIT = "packages/aitm-usage/tests/test_fixture.py::test_unit"
SYSTEM = "packages/aitm-usage/tests/test_fixture.py::test_system"


def test_partition_preserves_collection_order_and_empty_categories():
    lanes = sweep.assign(
        {"product": [SYSTEM, UNIT]}, {UNIT: "fast-unit", SYSTEM: "systems-integration"}
    )
    assert lanes == {
        "fast-unit": {"product": [UNIT]},
        "slow-unit": {},
        "local-integration": {},
        "systems-integration": {"product": [SYSTEM]},
    }


def test_inventory_drift_or_duplicate_refuses():
    for inventory in ([UNIT], [UNIT, SYSTEM, UNIT], [UNIT, SYSTEM, "extra"]):
        with pytest.raises(sweep.Refusal):
            sweep.assign(
                {"product": inventory},
                {UNIT: "fast-unit", SYSTEM: "systems-integration"},
            )


@pytest.mark.parametrize("host", ["linux", "darwin"])
def test_workspace_uses_private_platform_roots(tmp_path, monkeypatch, host):
    monkeypatch.setattr(sweep, "sys", SimpleNamespace(platform=host))
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("UV_PYTHON_INSTALL_DIR", raising=False)
    monkeypatch.delenv("UV_MANAGED_PYTHON", raising=False)
    source = {"commit": "commit", "tree": "tree"}
    monkeypatch.setattr(sweep, "identity", lambda _: source)
    monkeypatch.setattr(
        sweep,
        "git",
        lambda _, command, *args: {
            "checkout": "",
            "rev-parse": "false"
            if args == ("--is-shallow-repository",)
            else str(tmp_path),
            "cat-file": "commit",
        }[command],
    )

    def run(args, *, env, check, cwd=None):
        if args[0] == "git":
            args[-1].mkdir(parents=True)
        elif host == "linux":
            managed_python = Path(env["UV_PYTHON_INSTALL_DIR"])
            assert managed_python == scratch / "python"
            assert managed_python.stat().st_mode & 0o777 == 0o700
            assert env["UV_MANAGED_PYTHON"] == "1"
        else:
            assert "UV_PYTHON_INSTALL_DIR" not in env
            assert "UV_MANAGED_PYTHON" not in env

    monkeypatch.setattr(sweep, "subprocess", SimpleNamespace(run=run))
    with sweep.isolated_roots() as (scratch, short_scratch):
        parent = (
            Path("/var/tmp")
            if host == "linux"
            else tmp_path / ".cache/aitm-category-sweep"
        )
        assert scratch.parent == parent.resolve()
        assert scratch.stat().st_mode & 0o777 == 0o700
        assert short_scratch.parent == Path("/tmp").resolve()
        target = scratch / "collect" / "nested" / "checkout"
        sweep.workspace(
            tmp_path, target, source, short_scratch / "collect", scratch=scratch
        )


def stock(node=UNIT, *, outcome="passed", exit_code=0):
    return {
        "schema": "aitm.pytest-evidence/v1",
        "exit_code": exit_code,
        "collected": [node],
        "deselected": [],
        "reports": [
            {
                "nodeid": node,
                "when": phase,
                "outcome": outcome if phase == "call" else "passed",
                "wasxfail": False,
                "skip_reason": None,
            }
            for phase in ("setup", "call", "teardown")
        ],
        "children": [],
    }


def test_failed_and_missing_pytest_reports_refuse():
    with pytest.raises(sweep.Refusal):
        sweep.validate(stock(outcome="failed", exit_code=1), [UNIT], "darwin")
    evidence = stock()
    evidence["reports"].pop()
    with pytest.raises(sweep.Refusal):
        sweep.validate(evidence, [UNIT], "darwin")


def test_unexpected_skip_refuses_even_with_pytest_exit_zero():
    receipt = stock()
    receipt["reports"][1].update(outcome="skipped", skip_reason="some reason")
    with pytest.raises(sweep.Refusal, match="skip"):
        sweep.validate(receipt, [UNIT], "darwin")


def test_reconciliation_requires_exact_worker_and_run_binding(tmp_path):
    plan = {
        "schema": "aitm.category-sweep-plan/v1",
        "source": {"commit": "source", "tree": "tree"},
        "run": "this-run",
        "host": "darwin",
        "lanes": {"fast-unit": {"product": [UNIT]}},
    }
    receipts = tmp_path / "fast-unit"
    receipts.mkdir()
    (receipts / "product.json").write_text(json.dumps(stock()))
    seal = receipts / "worker.json"
    for binding in ("previous-run", None):
        if binding:
            seal.write_text(
                json.dumps(
                    {"run": binding, "source": plan["source"], "lane": "fast-unit"}
                )
            )
        with pytest.raises(sweep.Refusal):
            sweep.verify(plan, tmp_path, require_children=False)
    sweep.seal(plan, "fast-unit", receipts)
    assert sweep.verify(plan, tmp_path, require_children=False)["tested"] == 1
    (receipts / "product.json").write_text(json.dumps(stock(SYSTEM)))
    with pytest.raises(sweep.Refusal):
        sweep.verify(plan, tmp_path, require_children=False)


def test_worker_preserves_default_sigint_in_the_service_process(tmp_path):
    log = tmp_path / "signal.log"
    sweep.supervise(
        {
            log: [
                sys.executable,
                "-c",
                "import signal; assert signal.getsignal(signal.SIGINT) == signal.default_int_handler",
            ]
        },
        cwd=tmp_path,
        environment=os.environ.copy(),
    )
    assert signal.getsignal(signal.SIGINT) != signal.SIG_IGN


def test_supervisor_surfaces_real_pytest_failure(tmp_path):
    case = tmp_path / "test_red.py"
    case.write_text("def test_regression():\n    assert False\n")
    with pytest.raises(sweep.Refusal, match="failed"):
        sweep.supervise(
            {tmp_path / "red.log": [sys.executable, "-m", "pytest", "-q", str(case)]},
            cwd=tmp_path,
            environment={**os.environ, "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
        )
