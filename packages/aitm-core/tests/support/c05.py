"""Recording fixture validation gate for the Git backend."""

from contextlib import contextmanager
from threading import Lock

from aitm_core.store.backend import Snapshot
from aitm_core.store.objects import UnknownTree

REF = "refs/heads/planning"


class FixtureGate:
    def __init__(self):
        self.lock = Lock()
        self.observed = []

    @contextmanager
    def __call__(self, repo, target):
        assert repo.ref == target == REF
        with self.lock:
            yield self.validate

    def validate(self, before, candidate):
        self.observed.append((before, candidate))
        if candidate is not None:
            assert before.store == candidate.store
            assert before.revision != candidate.revision


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
