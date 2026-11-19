import pytest


@pytest.fixture
def legacy_monitor_qualification(tmp_path, monkeypatch):
    """Retain the older native substrate behaviors inside these tests only."""
    from aitm_usage.monitor_registry import Registry

    require = Registry._require_live_source
    fixture_authority = object()

    def require_live_source(writer, approved, **kwargs):
        if writer.root.is_relative_to(tmp_path):
            return fixture_authority
        return require(writer, approved, **kwargs)

    monkeypatch.setattr(Registry, "_require_live_source", require_live_source)
    return require


@pytest.fixture
def grant_extra_acl(monkeypatch):
    """Expose a grant at the ACL reader boundary for one private inode."""
    import errno
    import os
    import sys
    from pathlib import Path

    from aitm_usage import host_fs

    def grant(path, attribute):
        if sys.platform == "linux":
            # A named-user entry with a zero mask leaves private mode bits intact.
            acl = bytes.fromhex(
                "02000000 01000700ffffffff 02000400fdff0000 04000000ffffffff"
                " 10000000ffffffff 20000000ffffffff"
                if attribute == "system.posix_acl_default"
                else "02000000 01000600ffffffff 02000400fdff0000 04000000ffffffff"
                " 10000000ffffffff 20000000ffffffff"
            )
            os.setxattr(path, attribute, acl, follow_symlinks=False)
            return
        identity = path.stat()
        check_private_acl = host_fs.check_private_acl
        getxattr = getattr(os, "getxattr", None)

        def same_inode(target):
            info = target.lstat() if isinstance(target, Path) else os.fstat(target)
            return os.path.samestat(info, identity)

        def read_acl(target, name, *, follow_symlinks=True):
            if same_inode(Path(target) if not isinstance(target, int) else target):
                if name == attribute:
                    return b"extra ACL grant"
                raise OSError(errno.ENODATA, "no other ACL")
            if getxattr is None:
                raise AssertionError("unexpected ACL read")
            return getxattr(target, name, follow_symlinks=follow_symlinks)

        def check(target, *, ancestor=False):
            if same_inode(target):
                host_fs._check_linux_acl(target)
            else:
                check_private_acl(target, ancestor=ancestor)

        monkeypatch.setattr(os, "getxattr", read_acl, raising=False)
        monkeypatch.setattr("aitm_usage.ledger.check_private_acl", check)

    return grant


@pytest.fixture
def mac_acl_text(monkeypatch):
    """Supply the ACL text that the Darwin libc reader would return."""
    import ctypes
    import errno
    import os
    from types import SimpleNamespace

    from aitm_usage import host_fs

    def provide(acl_path, text):
        acl = ctypes.create_string_buffer(text)

        def read_path(path, _kind):
            if path == os.fsencode(acl_path):
                return ctypes.addressof(acl)
            ctypes.set_errno(errno.ENOENT)
            return None

        native = SimpleNamespace(
            acl_get_link_np=read_path,
            acl_to_text=lambda pointer, _: pointer,
            acl_free=lambda _: None,
        )
        monkeypatch.setattr(host_fs, "_mac_acl", lambda: native)

    return provide


@pytest.fixture
def alias_directory_identity(monkeypatch):
    """Expose a second directory spelling at the filesystem metadata boundary."""
    from pathlib import Path

    lstat = Path.lstat

    def alias_directory(alias, physical):
        alias.mkdir(mode=0o700)

        def observed_path(path):
            return lstat(physical if path == alias else path)

        monkeypatch.setattr(Path, "lstat", observed_path)

    return alias_directory

# Shadow qualification shared pytest input.
