"""Fail the unit lane on subprocess creation or network access."""

import sys

import pytest

_unit_active = False
_PROCESS_EVENTS = {
    "subprocess.Popen",
    "os.system",
    "os.posix_spawn",
    "os.exec",
    "os.fork",
    "os.forkpty",
}


def _reject_external_operations(event, args):
    if not _unit_active:
        return
    if event.startswith("socket."):
        raise AssertionError("network forbidden in unit tests")
    if event in _PROCESS_EVENTS:
        raise AssertionError("subprocess forbidden in unit tests")


sys.addaudithook(_reject_external_operations)


@pytest.fixture(autouse=True)
def _isolate_unit_test():
    global _unit_active
    _unit_active = True
    try:
        yield
    finally:
        _unit_active = False
