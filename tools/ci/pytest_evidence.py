"""Capture pytest inventory, phase outcomes and explicitly witnessed child exits."""

import json
import os
from pathlib import Path

import pytest

_OBSERVER = pytest.StashKey()


def pytest_configure(config):
    destination = os.environ.get("AITM_CI_PYTEST_EVIDENCE")
    if destination:
        observer = EvidenceObserver(Path(destination))
        config.stash[_OBSERVER] = observer
        config.pluginmanager.register(observer, "aitm-ci-evidence-observer")


def record_child(config, label, pid, returncode):
    """Record the PID and exit returned by the test's real subprocess."""
    config.stash[_OBSERVER].children.append(
        {"label": label, "pid": pid, "returncode": returncode}
    )


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
            "schema": "aitm.pytest-evidence/v1",
            "exit_code": int(session.exitstatus),
            "collected": [item.nodeid for item in session.items],
            "deselected": self.deselected,
            "reports": self.reports,
            "children": self.children,
        }
        self.destination.write_text(json.dumps(evidence) + "\n", encoding="utf-8")
        return result
