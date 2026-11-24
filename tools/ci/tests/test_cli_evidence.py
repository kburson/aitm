import os
import subprocess
import sys
from pathlib import Path


def test_usage_console_help(pytestconfig, tmp_path):
    console = Path(sys.executable).with_name("aitm-usage")
    with subprocess.Popen(
        [str(console), "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ) as process:
        try:
            output, error = process.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            raise
        if os.environ.get("AITM_CI_CHILD_EVIDENCE") == "1":
            observer = pytestconfig.pluginmanager.get_plugin("pytest_evidence")
            assert observer is not None, (
                "CI child evidence requires the pytest observer"
            )
            observer.record_child(
                pytestconfig, "cli-help", process.pid, process.returncode
            )
        assert process.returncode == 0, error
        assert "usage: aitm-usage" in output
        assert "--help" in output
        assert "collect-once" in output

    missing = tmp_path / "missing-project"
    refused = subprocess.run(
        [
            str(console),
            "--project",
            str(missing),
            "item",
            "alias",
            "--draft",
            "00000000-0000-0000-0000-000000000054",
            "--issue",
            "85",
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert refused.returncode == 1
    assert refused.stdout == ""
    assert refused.stderr == "aitm-usage: invalid private inbox command or project\n"
    assert not missing.exists()
