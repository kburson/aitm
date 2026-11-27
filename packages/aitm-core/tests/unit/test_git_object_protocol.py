"""Check the object adapter's parsing and failure decisions without invoking Git."""

import os
from contextlib import nullcontext
from pathlib import Path
from subprocess import CompletedProcess

import pytest

from aitm_core.store import objects
from aitm_core.store.backend import Snapshot
from aitm_core.store.objects import GitCommandError, Repository, UnknownTree
from tests.support.c05 import REF

ROOT = Path("/fixture")
TREE = "a" * 40
TIP = "b" * 40
PARENT = "c" * 40


def reply(stdout=b"", *, status=0, stderr=b""):
    return CompletedProcess(("git",), status, stdout, stderr)


def repository_at(monkeypatch, format_=b"sha1"):
    def git(_repository, *args):
        return {
            ("check-ref-format", REF): b"",
            (
                "rev-parse",
                "--path-format=absolute",
                "--git-common-dir",
            ): b"/fixture/.git\n",
            ("rev-parse", "--show-object-format"): format_ + b"\n",
        }[args]

    with monkeypatch.context() as patches:
        patches.setattr(Repository, "_git", git)
        return Repository(ROOT, REF)


@pytest.fixture
def repository(monkeypatch):
    return repository_at(monkeypatch)


@pytest.mark.parametrize(
    "format_,length,other_length",
    [
        pytest.param(b"sha1", 40, 64, id="sha1"),
        pytest.param(b"sha256", 64, 40, id="sha256"),
    ],
)
def test_repository_uses_its_own_object_format(
    monkeypatch, format_, length, other_length
):
    repository = repository_at(monkeypatch, format_)
    assert repository.oid_length == length
    assert repository._oid("f" * length) == "f" * length
    with pytest.raises(ValueError, match="full Git object identity"):
        repository._oid("f" * other_length)


def test_repository_refuses_an_unrecognized_object_format(monkeypatch):
    with pytest.raises(ValueError, match="unsupported Git object format"):
        repository_at(monkeypatch, b"fixture")


def test_repository_refuses_an_explicit_tag_as_the_planning_target(monkeypatch):
    def unexpected_git(*_args):
        pytest.fail("invalid planning target should be refused before invoking Git")

    monkeypatch.setattr(Repository, "_git", unexpected_git)
    with pytest.raises(ValueError, match="fully qualified local branch"):
        Repository(ROOT, "refs/tags/planning")


def test_isolated_git_command_keeps_transport_environment_without_inheriting_repo_overrides(
    repository, monkeypatch
):
    repository_overrides = {
        "GIT_DIR",
        "GIT_COMMON_DIR",
        "GIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_NAMESPACE",
        "GIT_PREFIX",
    }
    for key in repository_overrides:
        monkeypatch.setenv(key, "untrusted")
    monkeypatch.setenv("GIT_NO_REPLACE_OBJECTS", "0")
    monkeypatch.setenv("GIT_SSH_COMMAND", "fixture-transport")
    seen = {}

    def run(argv, *, input, env, capture_output, check):
        seen.update(
            argv=argv, input=input, env=env, capture_output=capture_output, check=check
        )
        return reply(b"output")

    monkeypatch.setattr(objects.subprocess, "run", run)
    index = ROOT / "private-index"
    result = repository._run("update-index", "--stdin", data=b"payload", index=index)

    assert result.stdout == b"output"
    assert seen["argv"] == (
        "git",
        "-C",
        os.fspath(repository.root),
        "update-index",
        "--stdin",
    )
    assert seen["input"] == b"payload" and seen["capture_output"] and not seen["check"]
    assert seen["env"]["GIT_INDEX_FILE"] == str(index)
    assert seen["env"]["GIT_NO_REPLACE_OBJECTS"] == "1"
    assert seen["env"]["GIT_SSH_COMMAND"] == "fixture-transport"
    assert (repository_overrides - {"GIT_INDEX_FILE"}).isdisjoint(seen["env"])
    assert os.environ["GIT_INDEX_FILE"] == "untrusted"


def test_batch_read_preserves_blob_bytes_and_distinguishes_missing_tree_and_empty(
    repository, monkeypatch
):
    raw = (
        f"{TREE}:.aitm/missing.md missing\n".encode()
        + f"{PARENT} tree 3\nxyz\n".encode()
        + f"{TIP} blob 4\n".encode()
        + b"x\x00\ny\n"
        + f"{PARENT} blob 0\n\n".encode()
    )

    def git(_repository, *args, data):
        assert args == ("cat-file", "--batch")
        assert (
            data
            == (
                f"{TREE}:.aitm/missing.md\n{TREE}:.aitm/subdir\n"
                f"{TREE}:.aitm/body.md\n{TREE}:.aitm/empty.md\n"
            ).encode()
        )
        return raw

    monkeypatch.setattr(Repository, "_git", git)
    assert repository.read_blobs(
        TREE, (".aitm/missing.md", ".aitm/subdir", ".aitm/body.md", ".aitm/empty.md")
    ) == {
        ".aitm/missing.md": None,
        ".aitm/subdir": None,
        ".aitm/body.md": b"x\x00\ny",
        ".aitm/empty.md": b"",
    }


@pytest.mark.parametrize(
    "response,diagnostic",
    [
        pytest.param(
            b"other-request missing\n",
            "unsupported planning object",
            id="missing-for-a-different-request",
        ),
        pytest.param(
            f"{TIP} commit 0\n\n".encode(),
            "unsupported planning object",
            id="commit-instead-of-tree-or-blob",
        ),
        pytest.param(
            f"{TIP} blob -1\n".encode(), "invalid object size", id="negative-frame-size"
        ),
        pytest.param(
            f"{TIP} blob 3\nxy".encode(),
            "incomplete Git batch object",
            id="truncated-frame",
        ),
        pytest.param(
            f"{TIP} blob 1\nxy".encode(),
            "incomplete Git batch object",
            id="missing-frame-delimiter",
        ),
        pytest.param(
            f"{TIP} blob 1\nx\nsurplus".encode(),
            "unexpected data",
            id="unrequested-frame",
        ),
    ],
)
def test_bad_batch_response_cannot_be_used_as_authoritative_blob_evidence(
    repository, monkeypatch, response, diagnostic
):
    monkeypatch.setattr(Repository, "_git", lambda *_args, **_kwargs: response)
    with pytest.raises(ValueError, match=diagnostic):
        repository.read_blobs(TREE, (".aitm/body.md",))


def test_empty_blob_request_does_not_start_a_batch_process(repository, monkeypatch):
    def unexpected_git(*_args, **_kwargs):
        pytest.fail("empty batch should not invoke Git")

    monkeypatch.setattr(Repository, "_git", unexpected_git)
    assert repository.read_blobs(TREE, ()) == {}


def test_tree_resolution_reports_missing_object_as_unknown_tree(
    repository, monkeypatch
):
    def run(_repository, *args):
        assert args == ("rev-parse", "--quiet", "--verify", f"{TIP}^{{tree}}")
        return reply(status=1)

    monkeypatch.setattr(Repository, "_run", run)
    with pytest.raises(UnknownTree, match="does not resolve to a local tree"):
        repository.read_tree(TIP)


def test_tree_resolution_preserves_command_failure_instead_of_reporting_absence(
    repository, monkeypatch
):
    def run(_repository, *args):
        assert args == ("rev-parse", "--quiet", "--verify", f"{TIP}^{{tree}}")
        return reply(status=128, stderr=b"object directory unreadable\n")

    monkeypatch.setattr(Repository, "_run", run)
    with pytest.raises(
        GitCommandError, match="rev-parse failed: object directory unreadable"
    ):
        repository.read_tree(TIP)


def test_tip_symbolic_ref_query_error_does_not_authorize_direct_ref_path(
    repository, monkeypatch
):
    def run(_repository, *args):
        assert args == ("symbolic-ref", "-q", REF)
        return reply(status=128, stderr=b"reference database unavailable\n")

    monkeypatch.setattr(Repository, "_run", run)
    with pytest.raises(
        GitCommandError, match="symbolic-ref failed: reference database unavailable"
    ):
        repository.tip()


def test_ref_failure_with_unchanged_tip_is_an_error_instead_of_competing_update(
    repository, monkeypatch
):
    def run(_repository, *args):
        assert args == ("update-ref", "--no-deref", REF, TIP, PARENT)
        return reply(status=128, stderr=b"unable to lock reference\n")

    monkeypatch.setattr(Repository, "_run", run)
    monkeypatch.setattr(
        Repository, "tip", lambda actual: Snapshot(actual.identity, PARENT, TREE)
    )
    with pytest.raises(
        GitCommandError, match="update-ref failed: unable to lock reference"
    ):
        repository.compare_and_swap(TIP, PARENT)


@pytest.mark.parametrize(
    "parents",
    [
        pytest.param(TIP, id="parentless-commit"),
        pytest.param(f"{TIP} {PARENT} {TREE}", id="merge-commit"),
    ],
)
def test_operation_commit_must_have_one_parent(repository, monkeypatch, parents):
    def git(_repository, *args):
        assert args == ("rev-list", "--parents", "-n", "1", TIP)
        return parents.encode() + b"\n"

    monkeypatch.setattr(Repository, "_git", git)
    with pytest.raises(
        ValueError, match="operation commit must have exactly one parent"
    ):
        repository.parent(Snapshot(repository.identity, TIP, TREE))


def test_operation_record_origin_is_read_from_the_pinned_revision(
    repository, monkeypatch
):
    path = ".aitm/operations/operation.json"
    origin = Snapshot(repository.identity, PARENT, TREE)

    def git(_repository, *args):
        assert args == ("log", "-1", "--format=%H", TIP, "--", path)
        return PARENT.encode() + b"\n"

    def read_tree(_repository, revision):
        assert revision == PARENT
        return origin

    monkeypatch.setattr(Repository, "_git", git)
    monkeypatch.setattr(Repository, "read_tree", read_tree)
    assert (
        repository.record_origin(Snapshot(repository.identity, TIP, TREE), path)
        == origin
    )


@pytest.mark.parametrize(
    "changed,observed",
    [
        pytest.param(b".aitm/undeclared.md\x00", None, id="unapproved-path"),
        pytest.param(b".aitm/approved.md\x00", b"wrong", id="unapproved-content"),
    ],
)
def test_staging_mismatch_stops_before_building_a_commit(
    repository, monkeypatch, changed, observed
):
    path = ".aitm/approved.md"
    base = Snapshot(repository.identity, TIP, TREE)
    monkeypatch.setattr(
        objects,
        "TemporaryDirectory",
        lambda **_kwargs: nullcontext("/fixture/isolated"),
    )

    def git(_repository, command, *_args, **_kwargs):
        assert command != "commit-tree"
        return {
            "read-tree": b"",
            "hash-object": TIP.encode() + b"\n",
            "update-index": b"",
            "write-tree": PARENT.encode() + b"\n",
            "diff-tree": changed,
        }[command]

    def read_blobs(_repository, tree, paths):
        assert observed is not None, (
            "an unapproved path was already sufficient to reject"
        )
        assert tree == PARENT and paths == (path,)
        return {path: observed}

    monkeypatch.setattr(Repository, "_git", git)
    monkeypatch.setattr(Repository, "read_blobs", read_blobs)
    with pytest.raises(
        ValueError, match="staged Git tree differs from the approved writes"
    ):
        repository.create_commit(base, {path: b"approved"}, "approved")
