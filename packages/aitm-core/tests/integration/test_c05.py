"""Run the C04 contract against temporary Git repositories and exercise ref CAS."""

from subprocess import check_output

import pytest

from aitm_core.models.common import LocalOutcome
from aitm_core.store.git_backend import GitBackend, UnknownTree
from aitm_core.store.objects import Repository
from tests.support.c05 import REF, FixtureGate
from tests.unit import test_c04 as _contract


def git(root, *args):
    return check_output(("git", "-C", str(root), *args)).strip()


@pytest.fixture
def make_backend(tmp_path):
    counter = 0

    def create(files=None, *, ports=_contract.PORTS, categories=None, gate=None):
        nonlocal counter
        counter += 1
        root = tmp_path / f"store {counter}"
        root.mkdir()
        git(root, "init", "-q", "-b", "scratch")
        git(root, "config", "user.name", "AITM contract fixture")
        git(root, "config", "user.email", "fixture@example.invalid")
        for name, value in (files or {}).items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(value)
        git(root, "add", "-A")
        git(root, "commit", "-qm", "Seed test repository", "--allow-empty")
        git(root, "branch", "planning")
        repo = Repository(root=root, ref=REF)
        return GitBackend(
            repo, gate or FixtureGate(), ports=ports, categories=categories
        )

    return create


@pytest.fixture
def backend(make_backend):
    return make_backend({_contract.BODY: b"old", _contract.RELATED: b"related before"})


def test_git_transaction(backend, tmp_path, monkeypatch):
    repo = backend.repository
    root = repo.root
    scratch = git(root, "rev-parse", "HEAD")
    index = root / ".git/index"
    (root / "scratch.txt").write_bytes(b"staged outside the store")
    git(root, "add", "scratch.txt")
    index_before = index.read_bytes()
    (root / _contract.BODY).write_bytes(b"user edit in the working tree")
    caller_index = tmp_path / "caller.index"
    caller_index.write_bytes(index_before)

    _contract.test_tree_and_preconditions_reject_an_invalid_update_atomically(backend)
    start = backend.snapshot()
    assert backend.read_tree(start.tree).tree == start.tree
    with pytest.raises(UnknownTree):
        backend.read_tree("0" * repo.oid_length)
    note = _contract.EventAppend(story=9, records=(_contract.wire(9, "store-op", 1),))
    request = _contract.proposal(
        backend,
        start,
        "store-op",
        changes=((_contract.BODY, b"new\0value"), (_contract.RELATED, b"updated")),
        events=(note,),
    ).model_copy(update={"pending_actions": ("project.readback",)})
    with monkeypatch.context() as env:
        env.setenv("GIT_INDEX_FILE", str(caller_index))
        result = backend.transact(request, start)

    assert result.command.local == LocalOutcome.COMPLETED
    assert result.command.pending == ("project.readback",)
    assert result.snapshot == backend.snapshot()
    assert backend.read(start, (_contract.BODY, note.path)) == {
        _contract.BODY: b"old",
        note.path: None,
    }
    assert backend.read(result.snapshot, (_contract.BODY, _contract.RELATED)) == {
        _contract.BODY: b"new\0value",
        _contract.RELATED: b"updated",
    }
    assert git(root, "rev-parse", REF) == result.snapshot.revision.encode()
    assert git(root, "rev-parse", "HEAD") == scratch
    assert (
        git(root, "rev-parse", result.snapshot.revision + "^")
        == start.revision.encode()
    )
    assert index.read_bytes() == index_before
    assert caller_index.read_bytes() == index_before
    assert (root / _contract.BODY).read_bytes() == b"user edit in the working tree"
    assert (root / "scratch.txt").read_bytes() == b"staged outside the store"

    next_request = _contract.proposal(backend, result.snapshot, "later")
    assert (
        backend.transact(next_request, result.snapshot).command.local
        == LocalOutcome.COMPLETED
    )
    reopened = GitBackend(repo, FixtureGate(), ports=_contract.PORTS)
    assert reopened.transact(request, reopened.snapshot()) == result


class Interrupted(RuntimeError):
    pass


def test_git_interruption_recovers_by_operation_identity(backend, monkeypatch):
    for index, after_cas in enumerate((False, True)):
        before = backend.snapshot()
        request = _contract.proposal(backend, before, f"interrupted-{index}")
        update = Repository.compare_and_swap

        def interrupt(repo, new, expected):
            if after_cas:
                assert update(repo, new, expected)
            raise Interrupted("simulated process interruption")

        with monkeypatch.context() as error:
            error.setattr(Repository, "compare_and_swap", interrupt)
            with pytest.raises(Interrupted):
                backend.transact(request, before)

        observed = backend.snapshot()
        assert (observed != before) == after_cas
        reopened = GitBackend(backend.repository, FixtureGate(), ports=_contract.PORTS)
        recovered = reopened.transact(request, before)
        assert recovered.command.local == LocalOutcome.COMPLETED
        if after_cas:
            assert recovered.snapshot == observed
        assert reopened.transact(request, reopened.snapshot()) == recovered
        assert (
            git(
                backend.repository.root,
                "rev-list",
                "--count",
                f"{before.revision}..{REF}",
            )
            == b"1"
        )
        backend = reopened


def test_ref_cas_preserves_a_competing_update(backend, monkeypatch):
    root = backend.repository.root
    start = backend.snapshot()
    competitor = backend.repository.create_commit(
        start, {_contract.BODY: b"competing change"}, "competitor"
    )
    request = _contract.proposal(backend, start)
    update = Repository.compare_and_swap

    def compete(repo, new, expected):
        git(root, "update-ref", REF, competitor.revision, expected)
        return update(repo, new, expected)

    monkeypatch.setattr(Repository, "compare_and_swap", compete)
    result = backend.transact(request, start)
    assert result.command.local == LocalOutcome.CONFLICT
    assert backend.snapshot() == competitor
    assert (
        backend.read(competitor, (_contract.BODY,))[_contract.BODY]
        == b"competing change"
    )


def test_symbolic_planning_ref_is_refused(backend):
    root = backend.repository.root
    start = backend.snapshot()
    request = _contract.proposal(backend, start)
    scratch = git(root, "rev-parse", "refs/heads/scratch")
    git(root, "symbolic-ref", REF, "refs/heads/scratch")

    result = backend.transact(request, start)

    assert result.command.local == LocalOutcome.INTEGRITY_ERROR
    assert git(root, "symbolic-ref", REF) == b"refs/heads/scratch"
    assert git(root, "rev-parse", "refs/heads/scratch") == scratch
