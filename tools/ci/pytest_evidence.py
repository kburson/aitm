"""Capture pytest inventory, phase outcomes and explicitly witnessed child exits."""

import json
import os
from collections import Counter
from pathlib import Path

import pytest

_OBSERVER = pytest.StashKey()
_SCHEMA = "aitm.pytest-evidence/v1"


def _worker_receipt(destination, worker_id):
    return destination.with_name(f"{destination.stem}-{worker_id}{destination.suffix}")


def pytest_configure(config):
    destination = os.environ.get("AITM_CI_PYTEST_EVIDENCE")
    if destination:
        destination = Path(destination)
        if hasattr(config, "workerinput"):
            destination = _worker_receipt(destination, config.workerinput["workerid"])
        observer = EvidenceObserver(destination)
        config.stash[_OBSERVER] = observer
        config.pluginmanager.register(observer, "aitm-ci-evidence-observer")


def record_child(config, label, pid, returncode):
    """Record the PID and exit returned by the test's real subprocess."""
    config.stash[_OBSERVER].children.append(
        {"label": label, "pid": pid, "returncode": returncode}
    )


def reconcile_workers(destination, worker_count):
    """Reconcile the xdist controller and the exact expected worker receipts."""
    controller = json.loads(destination.read_bytes())
    if (
        controller["schema"] != _SCHEMA
        or controller["exit_code"] != 0
        or controller["collected"] != []
        or controller["deselected"] != []
        or controller["children"] != []
    ):
        raise ValueError("inconsistent pytest controller evidence")

    expected = [
        _worker_receipt(destination, f"gw{index}") for index in range(worker_count)
    ]
    observed = set(
        destination.parent.glob(f"{destination.stem}-gw*{destination.suffix}")
    )
    if not expected or observed != set(expected):
        raise ValueError("missing or unexpected pytest worker receipts")

    workers = [json.loads(receipt.read_bytes()) for receipt in expected]
    collected = workers[0]["collected"]
    if not collected or any(
        worker["schema"] != _SCHEMA
        or worker["exit_code"] != 0
        or worker["collected"] != collected
        or worker["deselected"] != []
        for worker in workers
    ):
        raise ValueError("incomplete or inconsistent pytest worker inventory")

    worker_reports = Counter(
        json.dumps(report, sort_keys=True)
        for worker in workers
        for report in worker["reports"]
    )
    if worker_reports != Counter(
        json.dumps(report, sort_keys=True) for report in controller["reports"]
    ):
        raise ValueError("pytest controller and worker phase reports disagree")
    children = [child for worker in workers for child in worker["children"]]
    return dict(controller, collected=collected, children=children)


class EvidenceObserver:
    def __init__(self, destination):
        self.destination = destination
        self.deselected = []
        self.reports = []
        self.children = []

    def pytest_deselected(self, items):
        self.deselected.extend(item.nodeid for item in items)

    def pytest_runtest_logreport(self, report):
        xfail_reason = getattr(report, "wasxfail", None)
        skip_reason = None
        if report.skipped:
            skip_reason = xfail_reason
            if isinstance(report.longrepr, tuple):
                skip_reason = report.longrepr[2].removeprefix("Skipped: ")
        self.reports.append(
            {
                "nodeid": report.nodeid,
                "when": report.when,
                "outcome": report.outcome,
                "wasxfail": xfail_reason is not None,
                "skip_reason": skip_reason,
            }
        )

    @pytest.hookimpl(wrapper=True, tryfirst=True)
    def pytest_sessionfinish(self, session):
        result = yield
        evidence = {
            "schema": _SCHEMA,
            "exit_code": int(session.exitstatus),
            "collected": [item.nodeid for item in session.items],
            "deselected": self.deselected,
            "reports": self.reports,
            "children": self.children,
        }
        self.destination.write_text(json.dumps(evidence) + "\n", encoding="utf-8")
        return result
