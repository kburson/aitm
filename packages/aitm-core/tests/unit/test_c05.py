"""Exercise GitBackend's transaction decisions across an in-memory repository port."""

import pytest

from aitm_core.store.backend import Snapshot
from aitm_core.store.git_backend import GitBackend
from aitm_core.store.objects import UnknownTree
from tests.support.c05 import REF, FixtureGate
from tests.unit import test_c04 as _contract


class CommitStore:
    """Represent pinned snapshots and operation records without Git or disk access."""

    ref = REF

    def __init__(self, files):
        self.current = Snapshot("fixture", "root", "root-tree")
        self.commits = {self.current.revision: self.current}
        self.trees = {self.current.tree: dict(files or {})}
        self.origins = {self.current.revision: {}}
        self.parents = {}

    def tip(self):
        return self.current

    def read_tree(self, revision):
        try:
            return self.commits[revision]
        except KeyError as error:
            raise UnknownTree(revision) from error

    def read_blobs(self, tree, paths):
        return {path: self.trees[tree].get(path) for path in paths}

    def create_commit(self, base, writes, _operation_id):
        sequence = len(self.commits)
        candidate = Snapshot(base.store, f"commit-{sequence}", f"tree-{sequence}")
        self.commits[candidate.revision] = candidate
        self.trees[candidate.tree] = self.trees[base.tree] | writes
        self.origins[candidate.revision] = self.origins[base.revision] | dict.fromkeys(
            writes, candidate
        )
        self.parents[candidate.revision] = base.revision
        return candidate

    def compare_and_swap(self, new, expected):
        if self.current.revision != expected:
            return False
        self.current = self.commits[new]
        return True

    def record_origin(self, snapshot, path):
        return self.origins[snapshot.revision][path]

    def parent(self, snapshot):
        return self.parents[snapshot.revision]


@pytest.fixture
def make_backend():
    def create(files=None, *, ports=_contract.PORTS, categories=None, gate=None):
        return GitBackend(
            CommitStore(files),
            gate or FixtureGate(),
            ports=ports,
            categories=categories,
        )

    return create


@pytest.fixture
def backend(make_backend):
    return make_backend({_contract.BODY: b"old", _contract.RELATED: b"related before"})


@pytest.mark.parametrize(
    "name",
    [
        "test_operation_cas",
        "test_refusal_retains_guards_without_applying_effects",
        "test_append_validates_all_streams_before_commit",
        "test_same_snapshot_has_one_concurrent_winner",
    ],
)
def test_c04_mutation_contract_with_repository_port(backend, name):
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
def test_c04_service_contract_with_repository_port(make_backend, name, arguments):
    getattr(_contract, name)(*arguments, backend_factory=make_backend)
