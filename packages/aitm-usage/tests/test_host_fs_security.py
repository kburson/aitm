import errno
import os
import pwd
import stat
import sys
from types import SimpleNamespace

import pytest

from aitm_usage import ledger

ACCESS_ACL = "system.posix_acl_access"
DEFAULT_ACL = "system.posix_acl_default"
# POSIX ACL granting rwx to the owner and to one named user through the mask.
NAMED_ACL = bytes.fromhex(
    "02000000 01000700ffffffff 02000700fdff0000 04000000ffffffff"
    " 10000700ffffffff 20000000ffffffff"
)


@pytest.mark.parametrize(
    ("result", "message"),
    [
        (errno.ENODATA, None),
        (NAMED_ACL, "Unsafe private ACL"),
        (b"", "Unsafe private ACL"),
        (errno.EOPNOTSUPP, "Unable to validate private ACL"),
        (errno.EACCES, "Unable to validate private ACL"),
        (errno.ENOENT, "Unable to validate private ACL"),
    ],
    ids=["absent", "default-acl", "empty", "unsupported", "unreadable", "vanished"],
)
def test_private_acl_rejects_linux_default_acl_and_unknown_enforcement(
    tmp_path, monkeypatch, result, message
):
    directory = tmp_path / "project"
    directory.mkdir(mode=0o700)

    def getxattr(target, name, *, follow_symlinks=True):
        assert not follow_symlinks
        assert name in (ACCESS_ACL, DEFAULT_ACL)
        if target == directory and name == DEFAULT_ACL:
            if isinstance(result, bytes):
                return result
            raise OSError(result, "test xattr result")
        raise OSError(errno.ENODATA, "test xattr absence")

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(os, "getxattr", getxattr, raising=False)
    assert stat.S_IMODE(directory.stat().st_mode) == 0o700
    if message is None:
        ledger.validate_private_path(directory, directory=True)
    else:
        with pytest.raises(ledger.LedgerError, match=message):
            ledger.validate_private_path(directory, directory=True)
        # Default ACLs on an ancestor can propagate into new private state.
        with pytest.raises(ledger.LedgerError, match=message):
            ledger.validate_private_path(directory / "future", allow_missing=True)


def test_linux_without_xattr_api_refuses_state_admission(tmp_path, monkeypatch):
    directory = tmp_path / "project"
    directory.mkdir(mode=0o700)
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delattr(os, "getxattr", raising=False)
    with pytest.raises(
        ledger.LedgerError, match="Private ACL validation is unavailable"
    ):
        ledger.validate_private_path(directory, directory=True)


@pytest.mark.parametrize("name", [ACCESS_ACL, DEFAULT_ACL])
def test_linux_pinned_directory_refuses_acl_on_its_descriptor(
    tmp_path, monkeypatch, name
):
    directory = tmp_path / "project"
    directory.mkdir(mode=0o700)
    identity = directory.stat()

    def getxattr(target, attribute, *, follow_symlinks=True):
        if isinstance(target, int):
            assert follow_symlinks
            assert os.path.samestat(os.fstat(target), identity)
            if attribute == name:
                return NAMED_ACL
        else:
            assert not follow_symlinks
        raise OSError(errno.ENODATA, "test xattr absence")

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(os, "getxattr", getxattr, raising=False)
    with pytest.raises(ledger.LedgerError, match="Unsafe private ACL"):
        with ledger._pin_directory(directory):
            pytest.fail("admitted a directory with an ACL on its descriptor")


def test_linux_private_regular_file_checks_only_access_acl(tmp_path, monkeypatch):
    path = tmp_path / "private"
    path.touch(mode=0o600)

    def getxattr(target, name, *, follow_symlinks=True):
        assert not follow_symlinks
        if target == path:
            assert name == ACCESS_ACL
        raise OSError(errno.ENODATA, "test xattr absence")

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(os, "getxattr", getxattr, raising=False)
    ledger.validate_private_path(path)


def test_unsupported_platform_refuses_acl_admission(tmp_path, monkeypatch):
    directory = tmp_path / "project"
    directory.mkdir(mode=0o700)
    monkeypatch.setattr(sys, "platform", "freebsd")
    with pytest.raises(
        ledger.LedgerError, match="Private ACL validation is unavailable"
    ):
        ledger.validate_private_path(directory, directory=True)
    with pytest.raises(ledger.LedgerError, match="Unable to resolve private account"):
        ledger._control_root()


def test_pinned_path_rejects_symlink_and_wrong_owner(tmp_path, monkeypatch):
    directory = tmp_path / "project"
    directory.mkdir(mode=0o700)
    real_fstat = os.fstat
    with ledger._pin_directory(directory) as pinned:
        moved = directory.rename(tmp_path / "moved")
        directory.symlink_to(moved, target_is_directory=True)
        with pytest.raises(ledger.LedgerError, match="Unsafe private ledger path"):
            pinned.check()
        directory.unlink()
        moved.rename(directory)

        def foreign_fstat(fd):
            info = real_fstat(fd)
            if fd == pinned.fd:
                fields = list(info)
                fields[stat.ST_UID] = os.geteuid() + 1
                return os.stat_result(fields)
            return info

        monkeypatch.setattr(os, "fstat", foreign_fstat)
        with pytest.raises(ledger.LedgerError, match="Unsafe private ledger path"):
            pinned.check()


@pytest.mark.parametrize(
    ("platform", "guard_suffix"),
    [
        ("linux", ".local/state/aitm-usage-control"),
        ("darwin", "Library/Application Support/aitm-usage-control"),
    ],
)
def test_uid_guard_ignores_home_override(tmp_path, monkeypatch, platform, guard_suffix):
    account = tmp_path / "account"
    uid = 65534

    def getpwuid(requested_uid):
        assert requested_uid == uid
        return SimpleNamespace(pw_dir=str(account))

    monkeypatch.setattr(sys, "platform", platform)
    monkeypatch.setattr(os, "geteuid", lambda: uid)
    monkeypatch.setattr(pwd, "getpwuid", getpwuid)
    expected = account / guard_suffix
    assert ledger._control_root() == expected
    monkeypatch.setenv("HOME", str(tmp_path / "wrong-home"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "wrong-state"))
    assert ledger._control_root() == expected


@pytest.mark.parametrize("home", [None, "", "relative/home"])
def test_linux_guard_refuses_unknown_or_nonabsolute_account_home(monkeypatch, home):
    def getpwuid(uid):
        if home is None:
            raise KeyError(uid)
        return SimpleNamespace(pw_dir=home)

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(pwd, "getpwuid", getpwuid)
    with pytest.raises(ledger.LedgerError, match="Unable to resolve private account"):
        ledger._control_root()
