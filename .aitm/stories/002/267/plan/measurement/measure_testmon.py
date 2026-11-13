"""Record Testmon's exposed stable sets without changing selection or execution."""
import json
import os
from pathlib import Path

import pytest


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_sessionfinish(session):
    result = yield
    selection = session.config.pluginmanager.get_plugin("TestmonSelect")
    data = session.config.testmon_data
    mode = session.config.testmon_config
    evidence = {
        "history_was_new": data.new_db,
        "collect_history": mode.collect,
        "select": mode.select,
        "stable_test_names": sorted(data.stable_test_names),
        "eligible_deselections": sorted(selection.deselected_tests),
        "ignored_file_candidates": sorted(selection.deselected_files),
        "unstable_files": sorted(data.unstable_files),
        "selected": [item.nodeid for item in session.items],
        "exit": int(session.exitstatus),
    }
    Path(os.environ["MEASURE_TESTMON_RECEIPT"]).write_text(json.dumps(evidence) + "\n")
    return result
