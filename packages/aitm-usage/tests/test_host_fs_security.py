import errno
import os
import pwd
import stat
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from aitm_usage import host_fs, ledger

ACCESS_ACL = "system.posix_acl_access"
DEFAULT_ACL = "system.posix_acl_default"
# POSIX ACL granting rwx to the owner and to one named user through the mask.
NAMED_ACL = bytes.fromhex(
    "02000000 01000700ffffffff 02000700fdff0000 04000000ffffffff"
    " 10000700ffffffff 20000000ffffffff"
)


@pytest.fixture
def private_path_metadata(monkeypatch):
    uid = 501

    class ObservedPath(type(Path())):
        def lstat(self):
            if str(self) == "/fixture/private":
                mode, inode = stat.S_IFREG | 0o600, 4
            else:
                directories = {"/": 1, "/fixture": 2, "/fixture/project": 3}
                if str(self) not in directories:
                    raise FileNotFoundError(self)
                mode, inode = stat.S_IFDIR | 0o700, directories[str(self)]
            return os.stat_result((mode, inode, 1, 1, uid, 0, 0, 0, 0, 0))

    monkeypatch.setattr(
        ledger, "os", SimpleNamespace(path=os.path, geteuid=lambda: uid)
    )
    return ObservedPath("/fixture")


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
    private_path_metadata, monkeypatch, result, message
):
    directory = private_path_metadata / "project"

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
    if message is None:
        ledger.validate_private_path(directory, directory=True)
    else:
        with pytest.raises(ledger.LedgerError, match=message):
            ledger.validate_private_path(directory, directory=True)
        # Default ACLs on an ancestor can propagate into new private state.
        with pytest.raises(ledger.LedgerError, match=message):
            ledger.validate_private_path(directory / "future", allow_missing=True)


@pytest.mark.parametrize(
    "text",
    [
        b"!#acl 1\n",
        b"!#acl 1\ngroup:ABCDEFAB-CDEF-ABCD-EFAB-CDEF0000000C:everyone:12:allow:read\n",
    ],
    ids=["empty", "grant"],
)
def test_darwin_acl_reader_refuses_a_grant(
    private_path_metadata, monkeypatch, mac_acl_text, text
):
    directory = private_path_metadata / "project"
    mac_acl_text(directory, text)
    monkeypatch.setattr(sys, "platform", "darwin")
    if text == b"!#acl 1\n":
        ledger.validate_private_path(directory, directory=True)
    else:
        with pytest.raises(ledger.LedgerError, match="Unsafe private ACL"):
            ledger.validate_private_path(directory / "future", allow_missing=True)


def test_linux_without_xattr_api_refuses_state_admission(
    private_path_metadata, monkeypatch
):
    directory = private_path_metadata / "project"
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delattr(os, "getxattr", raising=False)
    with pytest.raises(
        ledger.LedgerError, match="Private ACL validation is unavailable"
    ):
        ledger.validate_private_path(directory, directory=True)


@pytest.mark.parametrize("name", [ACCESS_ACL, DEFAULT_ACL])
def test_linux_pinned_directory_refuses_acl_on_its_descriptor(
    request, monkeypatch, name
):
    if name == ACCESS_ACL:
        directory = request.getfixturevalue("tmp_path") / "project"
        directory.mkdir(mode=0o700)
        identity = directory.stat()
    else:
        directory = request.getfixturevalue("private_path_metadata") / "project"
        identity = directory.lstat()
        open_directory = Mock(return_value=11)
        descriptor_info = Mock(return_value=identity)
        close_directory = Mock()
        monkeypatch.setattr(
            ledger,
            "os",
            SimpleNamespace(
                **vars(ledger.os),
                O_RDONLY=os.O_RDONLY,
                O_DIRECTORY=os.O_DIRECTORY,
                O_NOFOLLOW=os.O_NOFOLLOW,
                open=open_directory,
                fstat=descriptor_info,
                close=close_directory,
            ),
        )

    descriptor_lookups = []

    def getxattr(target, attribute, *, follow_symlinks=True):
        if isinstance(target, int):
            assert follow_symlinks
            assert os.path.samestat(ledger.os.fstat(target), identity)
            descriptor_lookups.append(attribute)
            if attribute == name:
                return NAMED_ACL
        else:
            assert not follow_symlinks
        raise OSError(errno.ENODATA, "test xattr absence")

    monkeypatch.setattr(sys, "platform", "linux")
    if name == ACCESS_ACL:
        monkeypatch.setattr(os, "getxattr", getxattr, raising=False)
    else:
        monkeypatch.setattr(
            host_fs, "os", SimpleNamespace(fstat=descriptor_info, getxattr=getxattr)
        )
    with pytest.raises(ledger.LedgerError, match="Unsafe private ACL"):
        with ledger._pin_directory(directory):
            pytest.fail("admitted a directory with an ACL on its descriptor")
    if name == DEFAULT_ACL:
        assert descriptor_lookups == [ACCESS_ACL, DEFAULT_ACL]
        open_directory.assert_called_once_with(
            directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        )
        close_directory.assert_called_once_with(11)


def test_linux_private_regular_file_checks_only_access_acl(
    private_path_metadata, monkeypatch
):
    path = private_path_metadata / "private"

    def getxattr(target, name, *, follow_symlinks=True):
        assert not follow_symlinks
        if target == path:
            assert name == ACCESS_ACL
        raise OSError(errno.ENODATA, "test xattr absence")

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(os, "getxattr", getxattr, raising=False)
    ledger.validate_private_path(path)


def test_unsupported_platform_refuses_acl_admission(private_path_metadata, monkeypatch):
    directory = private_path_metadata / "project"
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
def test_uid_guard_ignores_home_override(monkeypatch, platform, guard_suffix):
    root = Path("/fixture")
    account = root / "account"
    uid = 65534

    def getpwuid(requested_uid):
        assert requested_uid == uid
        return SimpleNamespace(pw_dir=str(account))

    monkeypatch.setattr(sys, "platform", platform)
    monkeypatch.setattr(os, "geteuid", lambda: uid)
    monkeypatch.setattr(pwd, "getpwuid", getpwuid)
    expected = account / guard_suffix
    assert ledger._control_root() == expected
    monkeypatch.setenv("HOME", str(root / "wrong-home"))
    monkeypatch.setenv("XDG_STATE_HOME", str(root / "wrong-state"))
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
