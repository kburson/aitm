"""Read-only Git history port for isolated C06 validation cases."""

from hashlib import sha256
from types import SimpleNamespace

import pytest

from aitm_core.models.common import StoreAnchor
from aitm_core.store.backend import Snapshot
from tests.support.c05 import REF

DEFAULT = "refs/heads/trunk"


class PlanningHistory:
    """Expose the fixed linear tree records consumed by the history validator."""

    ref = REF

    def __init__(self):
        self.root = Snapshot("fixture", "root", "empty")
        self.commits = {self.root.revision: self.root}
        self.trees = {self.root.tree: {}}
        self.parents = {}

    def tip(self):
        return self.root

    def _oid(self, revision):
        return revision

    def _run(self, command, *args):
        assert command == "merge-base"
        assert args[0] in self.commits and args[1] == "code-root"
        return SimpleNamespace(returncode=1)

    def _git(self, command, *args):
        if (command, args) == ("rev-parse", ("--is-shallow-repository",)):
            return b"false"
        if (command, args) == ("rev-parse", ("--verify", f"{DEFAULT}^{{commit}}")):
            return b"code-root"
        if (command, args[:3]) == (
            "rev-list",
            ("--reverse", "--topo-order", "--parents"),
        ):
            history = [args[3]]
            while parent := self.parents.get(history[-1]):
                history.append(parent)
            return "\n".join(
                f"{commit} {self.parents.get(commit, '')}".rstrip()
                for commit in reversed(history)
            ).encode()
        if command == "cat-file" and args[0] == "commit":
            parent = self.parents.get(args[1])
            return f"parent {parent}\n\n".encode() if parent else b""
        if (command, args) == ("show", ("-s", "--format=%B", self.root.revision)):
            return b"aitm-planning-root: v1\n"
        if command == "ls-tree" and args[:3] == ("-r", "-z", "--full-tree"):
            return b"".join(
                f"100644 blob {sha256(data).hexdigest()}\t{path}\0".encode()
                for path, data in self.trees[args[3]].items()
            )
        pytest.fail(f"unexpected repository invocation: {command} {args}")

    def create_commit(self, before, writes, _message):
        index = len(self.commits)
        candidate = Snapshot(before.store, f"commit-{index}", f"tree-{index}")
        self.commits[candidate.revision] = candidate
        self.trees[candidate.tree] = {
            path: data
            for path, data in (self.trees[before.tree] | writes).items()
            if data is not None
        }
        self.parents[candidate.revision] = before.revision
        return candidate

    def read_tree(self, revision):
        return self.commits[revision]

    def read_blobs(self, tree, paths):
        return {path: self.trees[tree].get(path) for path in paths}


def planning_history():
    repo = PlanningHistory()
    return repo, StoreAnchor(
        store_uuid="c06-fixture",
        code_default_ref=DEFAULT,
        planning_ref=REF,
        planning_remote=None,
        root_commit=repo.root.revision,
    )
