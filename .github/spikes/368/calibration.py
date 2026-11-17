"""Public synthetic cases for calibration under the same hosted observer."""

import subprocess


def test_failure():
    assert False, "independently observed calibration failure"


def test_success(tmp_path):
    subprocess.run(
        ["/usr/bin/ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(tmp_path / "owner")],
        capture_output=True,
        check=True,
    )
    assert (tmp_path / "owner.pub").is_file()
