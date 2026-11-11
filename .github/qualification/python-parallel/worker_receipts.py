"""Local trial that gives the existing observer a separate file in each process."""

import os
from pathlib import Path

import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    worker = getattr(config, "workerinput", {}).get("workerid", "controller")
    directory = Path(os.environ["AITM_CI_XDIST_DIR"])
    os.environ["AITM_CI_PYTEST_EVIDENCE"] = str(directory / f"{worker}.json")
