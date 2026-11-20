"""Collect per-phase durations for the #357 measurement."""

import json
import os
from pathlib import Path

from _pytest.subtests import SubtestReport

measurements = []


def pytest_runtest_logreport(report):
    if isinstance(report, SubtestReport):
        return
    measurements.append(
        [report.nodeid, report.when, report.outcome, round(report.duration * 1e6)]
    )


def pytest_sessionfinish(session):
    Path(os.environ["AITM_357_PHASE_TIMING"]).write_text(
        json.dumps({"exit_code": int(session.exitstatus), "measurements": measurements}) + "\n",
        encoding="utf-8",
    )
