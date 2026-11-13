"""Emit pytest phase failures as they arrive, including before a driver timeout."""


def pytest_runtest_logreport(report):
    if report.failed:
        print(f"\n=== {report.when} failure: {report.nodeid} ===", flush=True)
        print(report.longreprtext, flush=True)
