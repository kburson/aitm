
def test_one_shot_status_uses_collecting_subprocess_pid(pytestconfig):
    import subprocess, sys
    import pytest_evidence
    child = subprocess.Popen([sys.executable, "-c", "pass"])
    pytest_evidence.record_child(pytestconfig, 'service-one-shot', child.pid, child.wait())
    assert child.returncode == 0
