"""Exercise the public snapshot contract against actual Git repositories."""

import base64
import hashlib
import json
import os
import subprocess
from dataclasses import replace

import pytest
from tia import snapshot
from tia.snapshot import HostedBinding, HostedRequest, SnapshotUncertain, resolve

GIT = "/usr/bin/git"


def git(repo, *args, data=None):
    env = {
        name: value for name, value in os.environ.items() if not name.startswith("GIT_")
    }
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    return subprocess.run(
        [GIT, "-C", str(repo), *args],
        input=data,
        check=True,
        capture_output=True,
        env=env,
    ).stdout


@pytest.fixture
def repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "trunk")
    git(repo, "config", "user.name", "Fixture")
    git(repo, "config", "user.email", "fixture@example.test")
    return repo


def blob(repo, content):
    return git(repo, "hash-object", "-w", "--stdin", data=content).decode().strip()


def tree(repo, entries):
    records = b"".join(
        f"{mode} {kind} {oid}\t".encode() + name + b"\0"
        for name, mode, kind, oid in entries
    )
    return git(repo, "mktree", "-z", "--missing", data=records).decode().strip()


def commit(repo, tree_id, *parents, message="fixture"):
    args = [value for parent in parents for value in ("-p", parent)]
    return git(repo, "commit-tree", tree_id, *args, "-m", message).decode().strip()


def hosted_request(base, tested, tested_tree, head=None):
    role, ref = (
        ("pr-tested", "refs/pull/40/merge")
        if head
        else (
            "trunk-tested",
            "refs/heads/trunk",
        )
    )
    binding = HostedBinding(
        "owner/project", ref, 987, 2, base, tested, tested_tree, head
    )
    return HostedRequest(
        "owner/project", role, ref, 987, 2, base, tested, tested_tree, head, binding
    )


def rebind(request, **values):
    return replace(request, **values, binding=replace(request.binding, **values))


def assert_refusal(repo, request, reason):
    with pytest.raises(SnapshotUncertain) as caught:
        resolve(repo, request)
    assert (caught.value.mode, caught.value.reason) == ("hosted", reason)


def test_hosted_diff_matches_tested_tree(repo):
    old = blob(repo, b"deleted in the tested merge")
    base_tree = tree(repo, [(b"deleted.txt", "100644", "blob", old)])
    base = commit(repo, base_tree)
    head_tree = tree(repo, [(b"head.txt", "100644", "blob", blob(repo, b"head only"))])
    head = commit(repo, head_tree, base)
    tested_tree = tree(
        repo, [(b"merge.txt", "100644", "blob", blob(repo, b"tested only"))]
    )
    tested = commit(repo, tested_tree, base, head)
    request = hosted_request(base, tested, tested_tree, head)

    pair = resolve(repo, request)
    assert len(pair) == 2, "a valid hosted binding yields both exact endpoints"
    before, after = pair
    assert before.read_content(b"deleted.txt") == b"deleted in the tested merge"
    assert after.read_content(b"merge.txt") == b"tested only"
    assert before.changes == after.changes
    assert [
        (c.status, c.old and c.old.path, c.new and c.new.path) for c in after.changes
    ] == [
        ("D", b"deleted.txt", None),
        ("A", None, b"merge.txt"),
    ]
    for endpoint, role, commit_id, tree_id in (
        (before, "baseline", base, base_tree),
        (after, "pr-tested", tested, tested_tree),
    ):
        assert (endpoint.repository, endpoint.mode, endpoint.ref_role) == (
            "owner/project",
            "hosted",
            role,
        )
        assert (endpoint.endpoint_identity.commit, endpoint.endpoint_identity.tree) == (
            commit_id,
            tree_id,
        )
        assert endpoint.baseline_identity == before.endpoint_identity
        record = json.loads(endpoint.canonical_bytes())
        assert (record["repository"], record["mode"], record["ref_role"]) == (
            "owner/project",
            "hosted",
            role,
        )
        assert record["endpoint_identity"] == {"commit": commit_id, "tree": tree_id}
        assert record["baseline_identity"] == {"commit": base, "tree": base_tree}
        assert record["provenance"]["binding"]["ref"] == "refs/pull/40/merge"
        assert record["provenance"]["binding"]["run_id"] == 987
        assert record["provenance"]["binding"]["run_attempt"] == 2
    retry = resolve(repo, rebind(request, run_attempt=3))[1]
    assert retry.digest != after.digest
    assert retry.entries == after.entries
    assert retry.changes == after.changes
    assert retry.read_content(b"merge.txt") == b"tested only"

    reversed_parents = commit(repo, tested_tree, head, base)
    extra = commit(repo, base_tree, message="unrelated third parent")
    extra_parent = commit(repo, tested_tree, base, head, extra)
    for wrong in (
        rebind(request, base_commit=head),
        rebind(request, pr_head=base),
        rebind(request, tested_commit=reversed_parents),
        rebind(request, tested_commit=extra_parent),
        rebind(request, tested_tree=head_tree),
        replace(request, repository="other/project"),
        replace(request, run_id=988),
        replace(request, run_attempt=3),
        replace(request, ref="refs/pull/41/merge"),
        rebind(request, ref="refs/heads/trunk"),
    ):
        assert_refusal(repo, wrong, "identity_mismatch")
    for unbound in (
        replace(request, binding=None),
        rebind(request, run_id=0),
        rebind(request, run_attempt=0),
        rebind(request, ref=""),
    ):
        assert_refusal(repo, unbound, "missing_authority")


def test_hosted_full_uses_explicit_baseline(repo):
    base_tree = tree(repo, [])
    base = commit(repo, base_tree)
    tested_tree = tree(repo, [(b"new", "100644", "blob", blob(repo, b"new"))])
    tested = commit(repo, tested_tree, message="independent tested commit")
    request = hosted_request(base, tested, tested_tree)
    before, after = resolve(repo, request)
    assert before.entries == ()
    assert after.ref_role == "trunk-tested"
    assert after.read_content(b"new") == b"new"
    assert_refusal(repo, rebind(request, base_commit=None), "missing_baseline")


def test_hosted_object_failures_and_raw_paths(repo):
    moved = blob(repo, b"unchanged rename contents")
    mode = blob(repo, b"unchanged mode contents")
    old = blob(repo, b"deleted bytes")
    base_tree = tree(
        repo,
        [
            (b"removed", "100644", "blob", old),
            (b"previous", "100644", "blob", moved),
            (b"executable", "100644", "blob", mode),
        ],
    )
    names = [b"tab\tnewline\n", "é".encode(), b"\xff"]
    tested_tree = tree(
        repo,
        [(name, "100644", "blob", blob(repo, b"content " + name)) for name in names]
        + [
            (b"renamed", "100644", "blob", moved),
            (b"executable", "100755", "blob", mode),
        ],
    )
    base = commit(repo, base_tree)
    tested = commit(repo, tested_tree, base)
    request = hosted_request(base, tested, tested_tree)
    # A replacement can hide the deletion or substitute bytes without changing a pinned ID.
    git(repo, "replace", base, commit(repo, tested_tree))
    git(repo, "replace", old, blob(repo, b"replacement bytes"))

    before, after = resolve(repo, request)
    assert before.read_content(b"removed") == b"deleted bytes"
    assert [e.path for e in after.entries] == sorted(
        [b"executable", b"renamed", *names]
    )
    record = json.loads(after.canonical_bytes())
    assert [base64.b64decode(e["path"]) for e in record["entries"]] == [
        e.path for e in after.entries
    ]
    for name in names:
        assert after.read_content(name) == b"content " + name
    assert [
        (c.status, c.old and c.old.path, c.new and c.new.path) for c in after.changes
    ] == [
        ("M", b"executable", b"executable"),
        ("R", b"previous", b"renamed"),
        ("D", b"removed", None),
        ("A", None, b"tab\tnewline\n"),
        ("A", None, "é".encode()),
        ("A", None, b"\xff"),
    ]
    executable = after.changes[0]
    assert (executable.old.mode, executable.new.mode) == ("100644", "100755")
    assert executable.old.content_id == executable.new.content_id == mode
    assert after.digest == hashlib.sha256(after.canonical_bytes()).hexdigest()
    assert resolve(repo, request)[1].digest == after.digest
    same_tree = commit(repo, tested_tree, base, message="different tested endpoint")
    assert (
        resolve(repo, rebind(request, tested_commit=same_tree))[1].digest
        != after.digest
    )

    assert_refusal(repo, rebind(request, tested_commit="1" * 40), "missing_object")
    missing_blob = tree(repo, [(b"missing", "100644", "blob", "1" * 40)])
    assert_refusal(
        repo,
        rebind(
            request, tested_tree=missing_blob, tested_commit=commit(repo, missing_blob)
        ),
        "missing_object",
    )
    gitlink = tree(repo, [(b"nested", "160000", "commit", base)])
    assert_refusal(
        repo,
        rebind(request, tested_tree=gitlink, tested_commit=commit(repo, gitlink)),
        "unsupported_object",
    )


@pytest.mark.parametrize(
    ("damage", "reason"),
    [
        ("failed", "command_failure"),
        ("truncated", "malformed_data"),
        ("valid-prefix", "malformed_data"),
        ("duplicate", "malformed_data"),
        ("escape", "unsafe_path"),
        ("rename-limit", "rename_limit"),
    ],
)
def test_hosted_refuses_invalid_diff_output(repo, monkeypatch, damage, reason):
    base_tree = tree(repo, [])
    base = commit(repo, base_tree)
    content = blob(repo, b"content")
    tested_tree = tree(
        repo,
        [(b"one", "100644", "blob", content), (b"two", "100644", "blob", content)],
    )
    request = hosted_request(base, commit(repo, tested_tree), tested_tree)
    run = snapshot._run_git

    def damage_diff(repo, command, env, data=None):
        result = run(repo, command, env, data)
        if "diff-tree" not in command:
            return result
        first = b"\0".join(result.stdout.split(b"\0")[:2]) + b"\0"
        if damage == "failed":
            result.returncode = 1
        elif damage == "truncated":
            result.stdout = result.stdout[:-1]
        elif damage == "valid-prefix":
            result.stdout = first
        elif damage == "duplicate":
            result.stdout = first + result.stdout
        elif damage == "escape":
            result.stdout = result.stdout.replace(b"\0one\0", b"\0../one\0")
        elif damage == "rename-limit":
            result.stderr = b"warning: exhaustive rename detection was skipped due to too many files.\n"
        return result

    monkeypatch.setattr(snapshot, "_run_git", damage_diff)
    assert_refusal(repo, request, reason)


def test_hosted_unsupported_offline_profile_refuses(repo, monkeypatch):
    base_tree = tree(repo, [])
    base = commit(repo, base_tree)
    git(repo, "config", "remote.origin.promisor", "true")
    request = hosted_request(base, base, base_tree)
    run = snapshot._run_git

    def refuse_offline(repo, command, env, data=None):
        if "--no-lazy-fetch" in command:
            return subprocess.CompletedProcess(
                command, 129, b"", b"unknown option: --no-lazy-fetch"
            )
        assert not any(name in command for name in ("cat-file", "ls-tree", "diff-tree"))
        return run(repo, command, env, data)

    monkeypatch.setattr(snapshot, "_run_git", refuse_offline)
    assert_refusal(repo, request, "unsupported_profile")
