import ctypes
import errno
import os
import sys
from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest

from aitm_usage import backup, export, host_fs, scopes
from aitm_usage.ledger import LedgerError, _pin_directory


@pytest.mark.parametrize("directory", [False, True], ids=["file", "directory"])
def test_existing_destination_survives_noreplace(request, monkeypatch, directory):
    if directory:
        # JournalStore also exercises a real competing directory at publication.
        def occupied(*args):
            ctypes.set_errno(errno.EEXIST)
            return -1

        rename = Mock(side_effect=occupied)
        resolve_rename = Mock(return_value=rename)
        monkeypatch.setattr(host_fs, "_native_rename", resolve_rename)
        monkeypatch.setattr(host_fs, "os", SimpleNamespace(fsencode=os.fsencode))
        assert not host_fs.publish_noreplace(11, "source", 12, "destination")
        symbol = "renameatx_np" if sys.platform == "darwin" else "renameat2"
        flags = 0x4 if sys.platform == "darwin" else 0x1
        resolve_rename.assert_called_once_with(symbol)
        rename.assert_called_once_with(11, b"source", 12, b"destination", flags)
        return

    tmp_path = request.getfixturevalue("tmp_path")
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.write_bytes(b"source")
    destination.write_bytes(b"destination")
    source_before = source.stat()
    destination_before = destination.stat()
    with _pin_directory(tmp_path) as parent:
        assert not host_fs.publish_noreplace(
            parent.fd, source.name, parent.fd, destination.name
        )
    assert os.path.samestat(source_before, source.stat())
    assert os.path.samestat(destination_before, destination.stat())
    assert source.read_bytes() == b"source"
    assert destination.read_bytes() == b"destination"


def _restore_parents(tmp_path):
    project = tmp_path / "project"
    staged = tmp_path / "staged"
    for parent in (project, staged):
        parent.mkdir(mode=0o700)
        (parent / "state").mkdir(mode=0o700)
        (parent / "state" / "sentinel").write_text(parent.name)
    return project, staged


def test_directory_exchange_and_durability(tmp_path, monkeypatch):
    project, staged = _restore_parents(tmp_path)
    live_before = (project / "state").stat()
    staged_before = (staged / "state").stat()
    real_fsync = os.fsync
    synced = []

    def sync(fd):
        assert os.path.samestat(staged_before, (project / "state").stat())
        assert os.path.samestat(live_before, (staged / "state").stat())
        real_fsync(fd)
        synced.append(os.fstat(fd).st_ino)

    monkeypatch.setattr(os, "fsync", sync)
    with _pin_directory(project) as live, _pin_directory(staged) as candidate:
        backup._swap_store(live, candidate)
    assert synced == [staged.stat().st_ino, project.stat().st_ino]
    assert (project / "state" / "sentinel").read_text() == "staged"
    assert (staged / "state" / "sentinel").read_text() == "project"


@pytest.mark.parametrize(
    "failure", [errno.ENOTSUP, errno.ENOSYS, errno.EINVAL, errno.EACCES]
)
def test_unsupported_primitive_fails_without_replacement(monkeypatch, failure):
    def refused(*args):
        ctypes.set_errno(failure)
        return -1

    rename = Mock(side_effect=refused)
    monkeypatch.setattr(host_fs, "_native_rename", lambda symbol: rename)

    # Any fallback through os.rename/os.replace must fail this test.
    monkeypatch.setattr(host_fs, "os", SimpleNamespace(fsencode=os.fsencode))
    fsync = Mock(side_effect=AssertionError("refused rename reached fsync"))
    monkeypatch.setattr(backup, "os", SimpleNamespace(fsync=fsync))
    live = SimpleNamespace(fd=11)
    candidate = SimpleNamespace(fd=12)
    with pytest.raises(host_fs.HostFilesystemError, match="rename private entries"):
        host_fs.publish_noreplace(candidate.fd, "state", live.fd, "state")
    with pytest.raises(backup.BackupError, match="replace the private store"):
        backup._swap_store(live, candidate)
    assert rename.call_args_list == [
        call(
            candidate.fd,
            b"state",
            live.fd,
            b"state",
            0x4 if sys.platform == "darwin" else 0x1,
        ),
        call(candidate.fd, b"state", live.fd, b"state", 0x2),
    ]
    fsync.assert_not_called()


@pytest.mark.parametrize("platform", ["darwin", "linux", "freebsd"])
def test_unavailable_native_binding_fails_closed(monkeypatch, platform):
    load_native = Mock(return_value=object())
    monkeypatch.setattr(host_fs, "sys", SimpleNamespace(platform=platform))
    monkeypatch.setattr(host_fs, "_native_rename", host_fs._native_rename.__wrapped__)
    monkeypatch.setattr(ctypes, "CDLL", load_native)
    with pytest.raises(host_fs.HostFilesystemError, match="rename is unavailable"):
        host_fs.publish_noreplace(11, "source", 11, "missing")
    if platform == "freebsd":
        load_native.assert_not_called()
    else:
        load_native.assert_called_once_with(None, use_errno=True)


@pytest.mark.parametrize("target", ["", "..", "child/new", "/untrusted", "new\0suffix"])
def test_publication_requires_leaf_names(monkeypatch, target):
    resolve_rename = Mock(
        side_effect=AssertionError("invalid entry reached native rename")
    )
    monkeypatch.setattr(host_fs, "_native_rename", resolve_rename)
    with pytest.raises(
        host_fs.HostFilesystemError, match="rename requires entry names"
    ):
        host_fs.publish_noreplace(11, "source", 11, target)
    resolve_rename.assert_not_called()


def test_publication_failure_preserves_caller_errors_and_cleans_stage(
    tmp_path, monkeypatch
):
    def refused(*args):
        ctypes.set_errno(errno.EACCES)
        return -1

    monkeypatch.setattr(host_fs, "_native_rename", lambda symbol: refused)
    with _pin_directory(tmp_path) as parent:
        with pytest.raises(LedgerError):
            scopes._publish(parent, "inbox-entry", b"new")
    with pytest.raises(export.ExportError):
        export._publish(tmp_path / "export", {"manifest.json": b"data"})
    assert not list(tmp_path.iterdir())
