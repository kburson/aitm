"""Opt-in checks of the real Darwin ACL reader."""

import subprocess
import sys
from pathlib import Path

import pytest

from aitm_usage.ledger import LedgerError, validate_private_path

pytestmark = pytest.mark.skipif(sys.platform != "darwin", reason="requires macOS ACLs")


@pytest.mark.parametrize("directory", [True, False], ids=["ancestor", "file"])
def test_native_grant_is_refused(tmp_path, directory):
    private = tmp_path / "private"
    if directory:
        private.mkdir(mode=0o700)
        target = private / "future"
        grant = "everyone allow list,read,file_inherit,directory_inherit"
    else:
        private.touch(mode=0o600)
        target = private
        grant = "everyone allow read"
    validate_private_path(target, directory=False, allow_missing=directory)
    subprocess.run(["/bin/chmod", "+a", grant, private], check=True)
    try:
        with pytest.raises(LedgerError, match="Unsafe private ACL"):
            validate_private_path(target, directory=False, allow_missing=directory)
    finally:
        subprocess.run(["/bin/chmod", "-N", private], check=True)


def test_native_home_ancestry_retains_standard_deny_delete_behavior():
    parent = Path.home() / "Library" / "Application Support"
    validate_private_path(
        parent / "aitm-usage-ancestry-probe", directory=True, allow_missing=True
    )
