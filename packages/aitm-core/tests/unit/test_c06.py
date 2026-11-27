"""Exercise planning decisions on in-memory paths, trees and history."""

import json
from hashlib import sha256
from types import SimpleNamespace

import pytest

from aitm_core.models.common import LocalOutcome, StoreAnchor
from aitm_core.store.backend import Snapshot
from aitm_core.store.validation import (
    PlanningPath,
    classify_planning_path,
    validate_history,
)
from tests.support.c05 import REF

DEFAULT = "refs/heads/trunk"
OUTSIDE = "outside.txt"


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


@pytest.fixture
def store():
    repo = PlanningHistory()
    return repo, StoreAnchor(
        store_uuid="c06-fixture",
        code_default_ref=DEFAULT,
        planning_ref=REF,
        planning_remote=None,
        root_commit=repo.root.revision,
    )


@pytest.mark.parametrize(
    ("path", "kind"),
    [
        pytest.param(".aitm/README.md", PlanningPath.DATA, id="store-readme"),
        pytest.param(".aitm/store.json", PlanningPath.STORE, id="store-anchor"),
        pytest.param(
            ".aitm/operations/create.json",
            PlanningPath.OPERATION,
            id="pre-story-operation",
        ),
        pytest.param(
            ".aitm/repairs/restore.json", PlanningPath.REPAIR, id="repair-receipt"
        ),
        pytest.param(
            ".aitm/stories/001/109/events.jsonl", PlanningPath.EVENTS, id="story-events"
        ),
        pytest.param(
            ".aitm/stories/001/109/description.md",
            PlanningPath.DATA,
            id="story-description",
        ),
        pytest.param(
            ".aitm/stories/001/109/plan/pickup.md", PlanningPath.DATA, id="story-plan"
        ),
        pytest.param(
            ".aitm/stories/001/109/attachments/quotes/quote.PDF",
            PlanningPath.DATA,
            id="story-attachment",
        ),
        pytest.param(
            ".aitm/stories/001/109/operations/change.json",
            PlanningPath.OPERATION,
            id="story-operation",
        ),
        pytest.param(".aitm/ideas/2026-11/proposal.md", PlanningPath.DATA, id="idea"),
        pytest.param(
            ".aitm/drafts/discarded/proposal.json",
            PlanningPath.DATA,
            id="discarded-draft",
        ),
        pytest.param(
            ".aitm/drafts/2026-11/proposal/draft.md",
            PlanningPath.DATA,
            id="active-draft",
        ),
        pytest.param(
            ".aitm/drafts/2026-11/proposal/attachments/reference.png",
            PlanningPath.DATA,
            id="draft-attachment",
        ),
    ],
)
def test_classifies_declared_planning_paths(path, kind):
    assert classify_planning_path(path) == kind


@pytest.mark.parametrize(
    ("path", "reason"),
    [
        pytest.param(
            "../outside", "normalized repository-relative", id="parent-traversal"
        ),
        pytest.param(
            ".aitm/../outside", "normalized repository-relative", id="nested-traversal"
        ),
        pytest.param(
            ".aitm//README.md",
            "normalized repository-relative",
            id="noncanonical-separator",
        ),
        pytest.param(
            ".aitm/unknown.py", "unauthorized planning data path", id="undeclared-code"
        ),
        pytest.param("README.md", "outside planning data paths", id="outside-store"),
        pytest.param(
            ".aitm/stories/001/109/attachments/.GiT/config.txt",
            "outside planning data paths",
            id="git-directory",
        ),
        pytest.param(
            ".aitm/ideas/2026-13/proposal.md",
            "unauthorized planning data path",
            id="invalid-idea-month",
        ),
        pytest.param(
            ".aitm/ideas/2026-11/archive/proposal.md",
            "unauthorized planning data path",
            id="nested-idea",
        ),
        pytest.param(
            ".aitm/drafts/2026-11/proposal/notes.txt",
            "unauthorized planning data path",
            id="undeclared-draft-content",
        ),
        pytest.param(
            ".aitm/stories/000/109/events.jsonl",
            "invalid story path identity",
            id="wrong-story-bucket",
        ),
        pytest.param(
            ".aitm/stories/001/0109/events.jsonl",
            "invalid story path identity",
            id="noncanonical-story-number",
        ),
        pytest.param(
            ".aitm/stories/001/109/events.txt",
            "unauthorized planning data path",
            id="wrong-event-extension",
        ),
        pytest.param(
            ".aitm/stories/001/109/operations/change.md",
            "unauthorized planning data path",
            id="untyped-operation",
        ),
    ],
)
def test_layout_rejects_unnormalized_and_undeclared_paths(path, reason):
    with pytest.raises(ValueError, match=reason):
        classify_planning_path(path)


def test_history_rejects_regular_blob_outside_data_policy(store):
    repo, anchor = store
    path = ".aitm/attachments/tool.py"
    candidate = repo.create_commit(repo.tip(), {path: b"text fixture"}, "invalid path")
    result = validate_history(anchor, candidate.revision, repository=repo)
    assert result.outcome == LocalOutcome.INTEGRITY_ERROR
    assert path in result.reason


def test_core_transaction_record_is_bound_to_its_operation_and_parent(store):
    repo, anchor = store
    start = repo.tip()
    path = ".aitm/operations/unbound.json"
    content = json.dumps(
        {
            "schema_version": "aitm.operation-record/v1",
            "base": start.revision,
            "request_digest": "a" * 64,
            "command": {"operation_id": "fixture", "local": "completed"},
        }
    ).encode()
    candidate = repo.create_commit(start, {path: content}, "record")
    result = validate_history(anchor, candidate.revision, repository=repo)
    assert result.outcome == LocalOutcome.INTEGRITY_ERROR
    assert path in result.reason
    assert result.valid_prefix == start.revision


@pytest.mark.parametrize(
    ("schema", "record_story", "expected"),
    [
        ("aitm.operation-record/v1", 9, LocalOutcome.COMPLETED),
        ("aitm.operation-record/v1", 10, LocalOutcome.INTEGRITY_ERROR),
        ("aitm.unregistered/v1", 9, LocalOutcome.INTEGRITY_ERROR),
    ],
)
def test_story_owned_operation_requires_a_bound_record(
    store, schema, record_story, expected
):
    repo, anchor = store
    start = repo.tip()
    operation_id = "story-fixture"
    identity = sha256(operation_id.encode()).hexdigest()
    path = f".aitm/stories/000/9/operations/{identity}.json"
    content = json.dumps(
        {
            "schema_version": schema,
            "story": record_story,
            "base": start.revision,
            "request_digest": "a" * 64,
            "command": {"operation_id": operation_id, "local": "completed"},
        }
    ).encode()
    candidate = repo.create_commit(start, {path: content}, "story record")

    result = validate_history(anchor, candidate.revision, repository=repo)

    assert result.outcome == expected
    if expected == LocalOutcome.INTEGRITY_ERROR:
        assert path in result.reason
        assert result.valid_prefix == start.revision
