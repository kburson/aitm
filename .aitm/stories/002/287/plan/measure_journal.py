"""Record direct journal snapshot cost from the single selected behavior test."""
import inspect
import json
from pathlib import Path
from time import perf_counter

import pytest

from aitm_usage.monitor_journal import RoutingJournal

TEST = "test_pair_settles_two_frontiers_and_preserves_first_ownership"


@pytest.hookimpl(wrapper=True)
def pytest_runtest_call(item):
    if item.originalname != TEST:
        yield
        return
    original = RoutingJournal.as_of
    reads = []

    def observed(self, sequence=None):
        frame = inspect.currentframe().f_back
        direct = frame.f_code.co_name == TEST or (
            frame.f_code.co_name == "<genexpr>" and frame.f_back.f_code.co_name == TEST
        )
        start = perf_counter()
        try:
            return original(self, sequence)
        finally:
            if direct:
                reads.append([sequence, perf_counter() - start])

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(RoutingJournal, "as_of", observed)
        try:
            yield
        finally:
            print("AUDIT_OBSERVATION=" + json.dumps(reads))
