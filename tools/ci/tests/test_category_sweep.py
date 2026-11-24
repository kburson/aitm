import json
import os
import signal
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools.ci import category_sweep as sweep
from tools.ci import product_shards

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


def test_product_shards_assign_exact_selection_and_keep_cli_separate():
    cli = "tools/ci/tests/test_cli_evidence.py::test_usage_console_help"
    catalog = {
        UNIT: "fast-unit",
        SYSTEM: "local-integration",
        cli: "systems-integration",
    }
    assert product_shards.partition([SYSTEM, cli, UNIT], catalog) == {
        "fast-unit": [UNIT],
        "local-integration": [SYSTEM],
        "systems-integration": [cli],
    }
    assert product_shards.partition([UNIT], {UNIT: "fast-unit"}) == {
        "fast-unit": [UNIT]
    }
    for collected in ([UNIT], [UNIT, SYSTEM, cli, UNIT], [UNIT, SYSTEM, "extra"]):
        with pytest.raises(sweep.Refusal, match="product collection"):
            product_shards.partition(collected, catalog)


def test_product_shard_receipt_preserves_phases_and_child_proofs():
    collection = [SYSTEM, UNIT]
    lanes = {"fast-unit": [UNIT], "systems-integration": [SYSTEM]}
    unit = stock()
    system = stock(SYSTEM)
    system["children"] = [{"label": "cli-help", "pid": 434, "returncode": 0}]
    combined = product_shards.merge_receipts(
        collection, lanes, {"fast-unit": unit, "systems-integration": system}
    )
    assert combined["collected"] == collection
    assert combined["reports"] == unit["reports"] + system["reports"]
    assert combined["children"] == system["children"]
    with pytest.raises(sweep.Refusal, match="shard receipts"):
        product_shards.merge_receipts(collection, lanes, {"fast-unit": unit})
    with pytest.raises(sweep.Refusal, match="systems-integration"):
        product_shards.merge_receipts(
            collection, lanes, {"fast-unit": unit, "systems-integration": unit}
        )


def test_product_shard_coverage_keeps_originals_and_excludes_other_shards(
    tmp_path, monkeypatch
):
    from coverage import CoverageData

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("COVERAGE_RCFILE", raising=False)
    source = tmp_path / "example_module.py"
    source.write_text("if __name__:\n    a = 1\nelse:\n    a = 2\n", encoding="utf-8")
    first, other = tmp_path / ".product.first", tmp_path / ".product.other"
    for path, line in ((first, 2), (other, 4)):
        data = CoverageData(basename=str(path))
        data.add_arcs({str(source): {(-1, 1), (1, line), (line, -1)}})
        data.write()

    report = tmp_path / "unit.json"
    counts = product_shards.write_shard_coverage([first], tmp_path / ".unit", report)
    assert counts == {"covered_lines": 2, "covered_branches": 1}
    assert sweep.read(report)["files"]["example_module.py"]["executed_lines"] == [1, 2]
    assert first.is_file() and other.is_file()


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
