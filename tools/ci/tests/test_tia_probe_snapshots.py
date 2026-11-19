"""Check advisory probe endpoints against actual Git objects and index bytes."""

from dataclasses import replace
from hashlib import sha256

import pytest
from test_tia_snapshot import blob, commit, git, tree
from tia import snapshot
from tia.selection import _endpoint, _entries, _pair_changes
from tia.snapshot import (
    GitEndpoint,
    IndexEndpoint,
    ProbeRequest,
    SnapshotUncertain,
    resolve,
)

_REPOSITORY = "owner/project"


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q", "-b", "trunk")
    git(tmp_path, "config", "user.name", "Fixture")
    git(tmp_path, "config", "user.email", "fixture@example.test")
    return tmp_path


def _tree(repo, **files):
    return tree(
        repo,
        [
            (name.encode(), "100644", "blob", blob(repo, data))
            for name, data in files.items()
        ],
    )


def _history(repo):
    original = _tree(repo, kept=b"same", changed=b"original")
    divergence = commit(repo, original)
    parent = commit(repo, _tree(repo, parent_only=b"other branch"), divergence)
    head_tree = _tree(repo, kept=b"same", changed=b"committed")
    head = commit(repo, head_tree, divergence)
    git(repo, "checkout", "-q", "--detach", head)
    return divergence, parent, GitEndpoint(head, head_tree)


def test_probe_index_and_head_use_divergence_and_keep_distinct_endpoints(repo):
    divergence, parent, head = _history(repo)
    (repo / "changed").write_bytes(b"staged")
    git(repo, "add", "changed")
    (repo / "changed").write_bytes(b"unstaged")
    (repo / "untracked").write_bytes(b"untracked")
    index_path = repo / ".git/index"
    index_before = sha256(index_path.read_bytes()).hexdigest()
    for kind, expected in (("index", b"staged"), ("head", b"committed")):
        before, after = resolve(repo, ProbeRequest(_REPOSITORY, kind, parent))
        assert (before.mode, after.mode, after.ref_role) == ("local", "local", kind)
        assert before.baseline_identity.commit == divergence
        assert after.provenance.merge_base == before.baseline_identity
        assert after.provenance.head == head
        assert after.provenance.parent_commit == parent
        assert after.read_content(b"changed") == expected
        assert before.read_content(b"changed") == b"original"
        assert [entry.path for entry in after.entries] == [b"changed", b"kept"]
        assert [(item.status, item.new.path) for item in after.changes] == [
            ("M", b"changed")
        ]
        if kind == "head":
            assert after.endpoint_identity == head
        else:
            assert isinstance(after.endpoint_identity, IndexEndpoint)
        _endpoint(before, baseline=True)
        _endpoint(after, baseline=False)
        _pair_changes(before, after, _entries(before), _entries(after))
        with pytest.raises(ValueError, match="change records do not match"):
            _pair_changes(
                replace(before, changes=()),
                replace(after, changes=()),
                _entries(before),
                _entries(after),
            )
    assert sha256(index_path.read_bytes()).hexdigest() == index_before
    assert (repo / "changed").read_bytes() == b"unstaged"


def test_probe_pr_binds_literal_base_and_ordered_tested_tree(repo):
    divergence, parent, head = _history(repo)
    tested_tree = _tree(repo, merged=b"tested merge")
    tested = commit(repo, tested_tree, parent, head.commit)
    request = ProbeRequest(_REPOSITORY, "pr", parent, head.commit, tested, tested_tree)
    before, after = resolve(repo, request)
    assert before.endpoint_identity.commit == parent
    assert before.read_content(b"parent_only") == b"other branch"
    assert after.ref_role == "pr-tested" and after.mode == "local"
    assert after.endpoint_identity == GitEndpoint(tested, tested_tree)
    assert after.provenance.merge_base.commit == divergence
    assert after.provenance.head == head
    assert after.read_content(b"merged") == b"tested merge"
    _endpoint(before, baseline=True)
    _endpoint(after, baseline=False)
    _pair_changes(before, after, _entries(before), _entries(after))
    backwards = commit(repo, tested_tree, head.commit, parent)
    for bad in (
        replace(request, tested_commit=backwards),
        replace(request, tested_tree=head.tree),
    ):
        with pytest.raises(SnapshotUncertain, match="identity_mismatch"):
            resolve(repo, bad)


def test_index_refuses_intent_to_add_while_head_ignores_index(repo):
    _, parent, head = _history(repo)
    (repo / "intent").write_bytes(b"uncommitted")
    git(repo, "add", "--intent-to-add", "intent")
    with pytest.raises(SnapshotUncertain, match="intent_to_add"):
        resolve(repo, ProbeRequest(_REPOSITORY, "index", parent))
    _, after = resolve(repo, ProbeRequest(_REPOSITORY, "head", parent))
    assert after.endpoint_identity == head
    assert [entry.path for entry in after.entries] == [b"changed", b"kept"]


def test_probe_refuses_ambiguous_divergence(repo):
    empty = _tree(repo)
    root = commit(repo, empty)
    first = commit(repo, empty, root, message="first")
    second = commit(repo, empty, root, message="second")
    head = commit(repo, empty, first, second)
    parent = commit(repo, empty, second, first)
    git(repo, "checkout", "-q", "--detach", head)
    with pytest.raises(SnapshotUncertain, match="ambiguous_merge_base"):
        resolve(repo, ProbeRequest(_REPOSITORY, "head", parent))


def test_probe_refuses_history_that_becomes_shallow_during_observation(
    repo, monkeypatch
):
    _, parent, head = _history(repo)
    original = snapshot._Git.require_blobs

    def capture(git_reader, *entries):
        original(git_reader, *entries)
        (repo / ".git/shallow").write_text(f"{head.commit}\n", encoding="ascii")

    monkeypatch.setattr(snapshot._Git, "require_blobs", capture)
    with pytest.raises(SnapshotUncertain, match="shallow_history"):
        resolve(repo, ProbeRequest(_REPOSITORY, "head", parent))


@pytest.mark.parametrize("kind", ["index", "head"])
def test_probe_refuses_changed_mutable_input_during_blob_verification(
    repo, monkeypatch, kind
):
    _, parent, head = _history(repo)
    updated = commit(repo, head.tree, head.commit, message="new head")
    original = snapshot._Git.require_blobs

    def capture(git_reader, *entries):
        original(git_reader, *entries)
        if kind == "head":
            git(repo, "update-ref", "HEAD", updated, head.commit)
        else:
            (repo / "changed").write_bytes(b"new staged blob")
            git(repo, "add", "changed")

    monkeypatch.setattr(snapshot._Git, "require_blobs", capture)
    with pytest.raises(SnapshotUncertain, match="observation_drift"):
        resolve(repo, ProbeRequest(_REPOSITORY, kind, parent))


def test_index_retains_both_rename_paths_and_deletion(repo):
    original = _tree(repo, old=b"exact renamed bytes", removed=b"deleted")
    base = commit(repo, original)
    git(repo, "checkout", "-q", "--detach", base)
    git(repo, "mv", "old", "new")
    git(repo, "rm", "removed")
    before, after = resolve(repo, ProbeRequest(_REPOSITORY, "index", base))
    assert [(c.status, c.old.path, c.new and c.new.path) for c in after.changes] == [
        ("R", b"old", b"new"),
        ("D", b"removed", None),
    ]
    assert before.read_content(b"old") == after.read_content(b"new")


def test_head_snapshot_is_insulated_from_unmerged_index(repo):
    _, parent, head = _history(repo)
    record = blob(repo, b"unmerged")
    git(
        repo,
        "update-index",
        "--index-info",
        data=f"0 {'0' * 40}\tchanged\n100644 {record} 1\tchanged\n".encode(),
    )
    with pytest.raises(SnapshotUncertain, match="unmerged_index"):
        resolve(repo, ProbeRequest(_REPOSITORY, "index", parent))
    _, after = resolve(repo, ProbeRequest(_REPOSITORY, "head", parent))
    assert after.endpoint_identity == head
    assert after.read_content(b"changed") == b"committed"


def test_probe_pr_inventory_requires_a_well_formed_tested_endpoint(repo):
    _, parent, head = _history(repo)
    tested = commit(repo, head.tree, parent, head.commit)
    _, candidate = resolve(
        repo, ProbeRequest(_REPOSITORY, "pr", parent, head.commit, tested, head.tree)
    )
    malformed = GitEndpoint("invalid commit", head.tree)
    candidate = replace(
        candidate,
        endpoint_identity=malformed,
        provenance=replace(candidate.provenance, tested=malformed),
    )
    with pytest.raises(ValueError, match="probe snapshot provenance"):
        _endpoint(candidate, baseline=False)
