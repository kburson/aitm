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
    from pathlib import Path

    from aitm_usage import host_fs

    def grant(path, attribute):
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
