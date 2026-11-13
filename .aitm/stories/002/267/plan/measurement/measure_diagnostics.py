"""Retain setup, call, teardown, and collection failures as they happen."""
import json
import os
from pathlib import Path


def write_failure(report, phase):
    if not report.failed:
        return
    destination = Path(os.environ["MEASURE_DIAGNOSTICS_RECEIPT"])
    with destination.open("a", encoding="utf-8") as stream:
        record = {"nodeid": report.nodeid, "phase": phase, "traceback": report.longreprtext}
        stream.write(json.dumps(record) + "\n")


def pytest_runtest_logreport(report):
    write_failure(report, report.when)


def pytest_collectreport(report):
    write_failure(report, "collection")
