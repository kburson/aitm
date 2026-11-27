"""Verify the Core test harness rejects processes, sockets and foreign imports."""

import subprocess
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]


def test_unit_guards_and_qualified_test_imports(tmp_path):
    tests = tmp_path / "tests"
    unit = tests / "unit"
    support = tests / "support"
    unit.mkdir(parents=True)
    support.mkdir()
    for directory in (tests, unit, support):
        (directory / "__init__.py").touch()
    (tests / "conftest.py").write_bytes(
        (PACKAGE / "tests" / "conftest.py").read_bytes()
    )
    (unit / "conftest.py").write_bytes(
        (PACKAGE / "tests" / "unit" / "conftest.py").read_bytes()
    )
    (support / "example.py").write_text("VALUE = 31\n")
    (unit / "test_tripwires.py").write_text("""
import socket
import subprocess
import sys
from pathlib import Path

from tests.support.example import VALUE

def test_qualified_import():
    assert VALUE == 31
    assert not any(Path(path).name == "src" for path in sys.path if path)

def test_process():
    subprocess.run(["missing-process"])

def test_network():
    socket.socket()
""")
    run = subprocess.run(
        (sys.executable, "-m", "pytest", "--import-mode=importlib", "-q", unit),
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.returncode == 1, run.stdout + run.stderr
    assert "2 failed, 1 passed" in run.stdout
    assert "subprocess forbidden in unit tests" in run.stdout
    assert "network forbidden in unit tests" in run.stdout

    foreign_probe = """
import sys
from types import ModuleType

import pytest

foreign = ModuleType("tests")
foreign.__file__ = "foreign/tests/__init__.py"
foreign.__path__ = ["foreign/tests"]
sys.modules["tests"] = foreign
raise SystemExit(pytest.main(["--import-mode=importlib", "-q", "tests/unit"]))
"""
    blocked = subprocess.run(
        (sys.executable, "-c", foreign_probe),
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert blocked.returncode != 0
    assert "a foreign tests package is already loaded" in blocked.stderr
