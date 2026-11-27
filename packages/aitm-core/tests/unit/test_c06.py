"""Exercise planning decisions on in-memory paths, trees and history."""

import json
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace

import pytest

from aitm_core.models.common import LocalOutcome, StoreAnchor
from aitm_core.services import ServicePorts
from aitm_core.store.backend import Snapshot
from aitm_core.store.gate import Gate, RefIdentity, RefMutationKind
from aitm_core.store.validation import classify_planning_path, validate_history
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


def test_layout_rejects_unnormalized_and_undeclared_paths():
    for path in (
        "../outside",
        ".aitm/../outside",
        ".aitm//README.md",
        ".aitm/unknown.py",
    ):
        with pytest.raises(ValueError):
            classify_planning_path(path)


def test_history_rejects_regular_blob_outside_data_policy(store):
    repo, anchor = store
    path = ".aitm/attachments/tool.py"
    candidate = repo.create_commit(repo.tip(), {path: b"text fixture"}, "invalid path")
    result = validate_history(anchor, candidate.revision, repository=repo)
    assert result.outcome == LocalOutcome.INTEGRITY_ERROR
    assert path in result.reason


def test_repair_requires_the_explicit_verifier_slot(store):
    repo, anchor = store
    start = repo.tip()
    bad = repo.create_commit(start, {OUTSIDE: b"invalid"}, "invalid")
    repaired = repo.create_commit(
        bad,
        {
            OUTSIDE: None,
            ".aitm/repairs/fixture.json": b'{"schema":"aitm.forward-repair/v1"}',
        },
        "repair",
    )

    def unneeded_verifier(_anchor, _diagnosis, _candidate):
        pytest.fail("absent repair slot must remain absent")

    explicit = replace(
        ServicePorts(forward_repair_verifier=unneeded_verifier),
        forward_repair_verifier=None,
    )
    result = validate_history(
        anchor,
        repaired.revision,
        repository=repo,
        forward_repair_verifier=explicit.forward_repair_verifier,
    )
    assert repo.tip() == start
    assert result.outcome == LocalOutcome.UNAVAILABLE
    assert result.reason == "forward-repair-verifier-unavailable"
    assert result.first_invalid == bad.revision
    assert result.valid_prefix == start.revision


def test_delivery_validation_uses_its_own_content_check(store, monkeypatch):
    repo, _ = store
    start = repo.tip()
    ref = "refs/heads/candidate"
    candidate = repo.create_commit(
        start, {OUTSIDE: b"ordinary delivery content"}, "source"
    )
    checks = []

    def planning_only(_tip):
        pytest.fail("delivery target must use the content check for its own lane")

    def delivery(before, after):
        checks.append((before, after))

    observed = []

    def assert_excluded(gate):
        observed.append(gate.target.name)

    monkeypatch.setattr(Gate, "assert_excluded", assert_excluded)
    gate = Gate(
        repo,
        RefIdentity(ref),
        RefMutationKind.DELIVERY,
        Path("."),
        planning_only,
        delivery,
    )
    gate(start, candidate)
    assert checks == [(start, candidate)]
    assert observed == [ref]
    assert repo.tip() == start


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
