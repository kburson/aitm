"""Run the C04 contract against temporary Git repositories and exercise ref CAS."""

from dataclasses import replace
from subprocess import check_output

import pytest

from aitm_core.models.common import LocalOutcome
from aitm_core.store.git_backend import GitBackend, ValidationRejected
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

    start = backend.snapshot()
    assert backend.read_tree(start.tree).tree == start.tree
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


@pytest.mark.parametrize(
    "name",
    [
        "test_operation_cas",
        "test_refusal_retains_guards_without_applying_effects",
        "test_append_validates_all_streams_before_commit",
        "test_same_snapshot_has_one_concurrent_winner",
        "test_tree_and_preconditions_reject_an_invalid_update_atomically",
    ],
)
def test_c04_mutation_contract_on_git(backend, name):
    getattr(_contract, name)(backend)


@pytest.mark.parametrize(
    ("name", "arguments"),
    [
        (
            "test_write_authority_distinguishes_absence_refusal_and_registered_result",
            (),
        ),
        (
            "test_attempt_mutation_requires_the_installed_preflight",
            ("attempt.reconcile",),
        ),
        ("test_attempt_mutation_requires_the_installed_preflight", ("expand",)),
        (
            "test_special_categories_require_the_exact_declared_capability",
            ("authoring.sync", _contract.OperationCategory.AUTHORED_SYNC),
        ),
        (
            "test_special_categories_require_the_exact_declared_capability",
            ("stop.reconcile", _contract.OperationCategory.STOP_RECONCILIATION),
        ),
        (
            "test_special_categories_require_the_exact_declared_capability",
            ("attempt.recover", _contract.OperationCategory.RECOVERY),
        ),
    ],
)
def test_c04_service_contract_on_git(make_backend, name, arguments):
    getattr(_contract, name)(*arguments, backend_factory=make_backend)


class Interrupted(RuntimeError):
    pass


@pytest.mark.parametrize("after_cas", [False, True])
def test_git_interruption_recovers_by_operation_identity(
    backend, monkeypatch, after_cas
):
    before = backend.snapshot()
    request = _contract.proposal(backend, before, "interrupted")
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
        git(backend.repository.root, "rev-list", "--count", f"{before.revision}..{REF}")
        == b"1"
    )


def test_validation_is_mandatory_and_refusal_preserves_ref(make_backend):
    class RejectCandidate(FixtureGate):
        def validate(self, before, candidate):
            super().validate(before, candidate)
            if candidate is not None:
                raise ValidationRejected("scope denied")

    gate = RejectCandidate()
    backend = make_backend({_contract.BODY: b"old"}, gate=gate)
    start = backend.snapshot()
    op = _contract.proposal(backend, start)
    with pytest.raises(TypeError):
        GitBackend(backend.repository, None, ports=_contract.PORTS)

    result = backend.transact(op, start)
    assert result.command.local == LocalOutcome.INTEGRITY_ERROR
    assert result.reason == "scope denied"
    assert backend.snapshot() == start
    assert len(gate.observed) == 2


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


def test_advance_after_successful_cas_retains_committed_snapshot(backend, monkeypatch):
    repo = backend.repository
    start = backend.snapshot()
    request = _contract.proposal(backend, start)
    request = request.model_copy(update={"pending_actions": ("project.readback",)})
    update = Repository.compare_and_swap

    def advance(repository, new, expected):
        assert update(repository, new, expected)
        committed = repository.read_tree(new)
        later = repository.create_commit(
            committed, {_contract.RELATED: b"later update"}, "competing"
        )
        assert update(repository, later.revision, committed.revision)
        return True

    with monkeypatch.context() as race:
        race.setattr(Repository, "compare_and_swap", advance)
        result = backend.transact(request, start)

    observed = backend.snapshot()
    assert result.command.local == LocalOutcome.CONFLICT
    assert result.reason == "ref-advanced-after-cas"
    assert result.command.pending == ()
    assert repo.parent(observed) == result.snapshot.revision
    assert backend.read(result.snapshot, (_contract.BODY,))[_contract.BODY] == b"new"
    reopened = GitBackend(repo, FixtureGate(), ports=_contract.PORTS)
    retry = reopened.transact(request, observed)
    assert retry.command.local == LocalOutcome.COMPLETED
    assert retry.snapshot == result.snapshot
    assert retry.command.pending == ("project.readback",)


def test_absent_expected_revision_is_an_unknown_snapshot(backend):
    current = backend.snapshot()
    request = _contract.proposal(backend, current)
    unknown = replace(current, revision="0" * backend.repository.oid_length)

    result = backend.transact(request, unknown)

    assert result.command.local == LocalOutcome.INTEGRITY_ERROR
    assert result.reason == "unknown-snapshot"
    assert result.snapshot == current
    assert backend.snapshot() == current
