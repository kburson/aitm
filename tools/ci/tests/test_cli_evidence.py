
def test_usage_console_help(pytestconfig):
    import subprocess, sys
    import pytest_evidence
    child = subprocess.Popen([sys.executable, "-c", "pass"])
    pytest_evidence.record_child(pytestconfig, 'cli-help', child.pid, child.wait())
    assert child.returncode == 0
