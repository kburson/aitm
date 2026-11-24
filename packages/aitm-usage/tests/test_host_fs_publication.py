import ctypes
import errno
import os
import sys
from contextlib import nullcontext
from pathlib import Path
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
        assert not scopes._publish(parent, destination.name, b"ignored")
    assert set(tmp_path.iterdir()) == {source, destination}
    assert os.path.samestat(source_before, source.stat())
    assert os.path.samestat(destination_before, destination.stat())
    assert source.read_bytes() == b"source"
    assert destination.read_bytes() == b"destination"


def test_directory_exchange_and_durability(monkeypatch):
    project = SimpleNamespace(fd=11)
    staged = SimpleNamespace(fd=12)
    live_entry = (project.fd, b"state")
    candidate_entry = (staged.fd, b"state")
    directories = {live_entry: "live directory", candidate_entry: "candidate directory"}

    def rename(source_fd, source, destination_fd, destination, flags):
        assert (source_fd, source) == candidate_entry
        assert (destination_fd, destination) == live_entry
        assert flags == 0x2
        directories[live_entry], directories[candidate_entry] = (
            directories[candidate_entry],
            directories[live_entry],
        )
        return 0

    def sync(_fd):
        assert directories == {
            live_entry: "candidate directory",
            candidate_entry: "live directory",
        }

    resolve_rename = Mock(return_value=rename)
    fsync = Mock(side_effect=sync)
    monkeypatch.setattr(host_fs, "_native_rename", resolve_rename)
    monkeypatch.setattr(backup, "os", SimpleNamespace(fsync=fsync))

    backup._swap_store(project, staged)

    symbol = "renameatx_np" if sys.platform == "darwin" else "renameat2"
    resolve_rename.assert_called_once_with(symbol)
    assert fsync.call_args_list == [call(staged.fd), call(project.fd)]


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


def test_publication_failure_preserves_caller_errors_and_cleans_stage(monkeypatch):
    def refused(*args):
        ctypes.set_errno(errno.EACCES)
        return -1

    rename = Mock(side_effect=refused)
    monkeypatch.setattr(host_fs, "_native_rename", lambda symbol: rename)
    parent = SimpleNamespace(fd=11, path=Path("/fixture"), check=Mock())
    file = Mock()
    unlink = Mock()
    open_stage = Mock(return_value=12)
    monkeypatch.setattr(scopes, "_private", Mock())
    monkeypatch.setattr(scopes, "_check_acl", Mock())
    monkeypatch.setattr(
        scopes,
        "os",
        SimpleNamespace(
            O_WRONLY=os.O_WRONLY,
            O_CREAT=os.O_CREAT,
            O_EXCL=os.O_EXCL,
            O_NOFOLLOW=os.O_NOFOLLOW,
            open=open_stage,
            fdopen=Mock(return_value=nullcontext(file)),
            fchmod=Mock(),
            fstat=Mock(),
            fsync=Mock(),
            unlink=unlink,
        ),
    )
    with pytest.raises(LedgerError, match="Unable to publish private inbox file"):
        scopes._publish(parent, "inbox-entry", b"new")
    staging = open_stage.call_args.args[0]
    file.write.assert_called_once_with(b"new")
    unlink.assert_called_once_with(staging, dir_fd=parent.fd)

    container = SimpleNamespace(
        fd=13, path=parent.path / ".export", identities=((1, 1), (1, 2))
    )
    staged = SimpleNamespace(fd=14)
    private_child = Mock(return_value=nullcontext(staged))
    write_snapshot = Mock()
    monkeypatch.setattr(export, "_new_private_child", private_child)
    monkeypatch.setattr(export, "_write_snapshot", write_snapshot)
    unlink.reset_mock()
    monkeypatch.setattr(export, "os", SimpleNamespace(unlink=unlink))
    files = {"manifest.json": b"data"}
    with pytest.raises(export.ExportError, match="Unable to publish export snapshot"):
        export._publish_staged(
            container, parent.fd, parent.path / "snapshot", ((1, 1),), files
        )
    private_child.assert_called_once_with(
        container.fd, container.path / "snapshot", container.identities
    )
    write_snapshot.assert_called_once_with(staged, files)
    unlink.assert_called_once_with("manifest.json", dir_fd=staged.fd)
    assert rename.call_count == 2
