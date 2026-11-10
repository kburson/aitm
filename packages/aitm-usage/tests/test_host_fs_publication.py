import ctypes
import errno
import os
import sys

import pytest

from aitm_usage import backup, export, host_fs, scopes
from aitm_usage.ledger import LedgerError, _pin_directory


@pytest.mark.parametrize("directory", [False, True], ids=["file", "directory"])
def test_existing_destination_survives_noreplace(tmp_path, directory):
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    if directory:
        source.mkdir()
        destination.mkdir()
    else:
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
    if not directory:
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
def test_unsupported_primitive_fails_without_replacement(
    tmp_path, monkeypatch, failure
):
    project, staged = _restore_parents(tmp_path)
    live_before = (project / "state").stat()
    staged_before = (staged / "state").stat()

    def refused(*args):
        ctypes.set_errno(failure)
        return -1

    monkeypatch.setattr(host_fs, "_native_rename", lambda symbol: refused)
    with _pin_directory(project) as live, _pin_directory(staged) as candidate:
        with pytest.raises(host_fs.HostFilesystemError):
            host_fs.publish_noreplace(candidate.fd, "state", live.fd, "state")
        with pytest.raises(backup.BackupError):
            backup._swap_store(live, candidate)
    assert os.path.samestat(live_before, (project / "state").stat())
    assert os.path.samestat(staged_before, (staged / "state").stat())
    assert (project / "state" / "sentinel").read_text() == "project"
    assert (staged / "state" / "sentinel").read_text() == "staged"


@pytest.mark.parametrize("platform", ["darwin", "linux", "freebsd"])
def test_unavailable_native_binding_fails_closed(tmp_path, monkeypatch, platform):
    source = tmp_path / "source"
    source.touch()
    with _pin_directory(tmp_path) as parent, monkeypatch.context() as patch:
        patch.setattr(sys, "platform", platform)
        patch.setattr(host_fs, "_native_rename", host_fs._native_rename.__wrapped__)
        patch.setattr(ctypes, "CDLL", lambda *args, **kwargs: object())
        with pytest.raises(host_fs.HostFilesystemError):
            host_fs.publish_noreplace(parent.fd, source.name, parent.fd, "missing")
    assert source.exists()
    assert not (tmp_path / "missing").exists()


@pytest.mark.parametrize("target", ["", "..", "child/new", "/untrusted", "new\0suffix"])
def test_publication_requires_leaf_names(tmp_path, target):
    source = tmp_path / "source"
    source.touch()
    (tmp_path / "child").mkdir()
    with _pin_directory(tmp_path) as parent:
        with pytest.raises(host_fs.HostFilesystemError):
            host_fs.publish_noreplace(parent.fd, source.name, parent.fd, target)
    assert source.exists()
    assert not (tmp_path / "new").exists()
    assert not (tmp_path / "child" / "new").exists()


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
