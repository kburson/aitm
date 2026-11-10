"""Exercise the public snapshot contract against actual Git repositories."""

import base64
import hashlib
import json
import os
import subprocess
from dataclasses import replace

import pytest
from tia import snapshot
from tia.snapshot import (
    HostedBinding,
    HostedRequest,
    LocalRequest,
    SnapshotUncertain,
    resolve,
)

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
        ("missing-path", "malformed_data"),
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
        elif damage == "missing-path":
            result.stdout = first.partition(b"\0")[0] + b"\0"
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


def write(repo, name, content):
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def commit_files(repo, message):
    git(repo, "add", "--all")
    git(repo, "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD").decode().strip()


def local_request(base, *ignored):
    return LocalRequest("owner/project", "local-effective", base, ignored)


def local_pair(repo, request):
    pair = resolve(repo, request)
    assert len(pair) == 2, "a stable local checkout yields both exact endpoints"
    return pair


def local_refusal(repo, request, reason):
    with pytest.raises(SnapshotUncertain) as caught:
        resolve(repo, request)
    assert (caught.value.mode, caught.value.reason) == ("local", reason)


@pytest.mark.parametrize("delete_destination", [False, True])
def test_local_staged_untracked_rename_and_deleted_paths(repo, delete_destination):
    original = b"four lines of unchanged content\n" * 8
    write(repo, "former", original)
    write(repo, "removed", b"old deleted bytes")
    base = commit_files(repo, "story base")
    base_tree = git(repo, "rev-parse", "HEAD^{tree}").decode().strip()
    write(repo, "committed", b"committed after story base")
    head = commit_files(repo, "committed layer")
    git(repo, "mv", "former", "destination")
    write(repo, "destination", original + b"staged\n")
    git(repo, "add", "destination")
    staged_oid = git(repo, "rev-parse", ":destination").decode().strip()
    if delete_destination:
        (repo / "destination").unlink()
    else:
        write(repo, "destination", b"effective worktree bytes")
    (repo / "removed").unlink()
    write(repo, "untracked", b"new local bytes")
    index_before = (repo / ".git" / "index").read_bytes()

    before, after = local_pair(repo, local_request(base))
    assert (repo / ".git" / "index").read_bytes() == index_before
    assert before.read_content(b"former") == original
    assert before.read_content(b"removed") == b"old deleted bytes"
    assert after.read_content(b"committed") == b"committed after story base"
    assert after.read_content(b"untracked") == b"new local bytes"
    assert [
        (c.status, c.old and c.old.path, c.new and c.new.path) for c in after.changes
    ] == [
        ("A", None, b"committed"),
        ("D", b"former", None)
        if delete_destination
        else ("R", b"former", b"destination"),
        ("D", b"removed", None),
        ("A", None, b"untracked"),
    ]
    if delete_destination:
        with pytest.raises(SnapshotUncertain, match="absent_path"):
            after.read_content(b"destination")
        assert b"destination" in after.provenance.observation.observed_absent
    else:
        assert after.read_content(b"destination") == b"effective worktree bytes"
        rename = after.changes[1]
        assert (
            rename.new.content_id
            == hashlib.sha256(b"effective worktree bytes").hexdigest()
        )
    assert b"removed" in after.provenance.observation.observed_absent
    assert [c.new.path for c in after.provenance.committed_changes] == [b"committed"]
    [staged] = after.provenance.staged_changes
    assert (staged.status, staged.old.path, staged.new.path, staged.new.content_id) == (
        "R",
        b"former",
        b"destination",
        staged_oid,
    )
    [destination] = [
        c
        for c in after.provenance.unstaged_changes
        if c.old and c.old.path == b"destination"
    ]
    assert destination.status == ("D" if delete_destination else "M")
    assert destination.old.content_id == staged_oid
    assert after.provenance.observation.head.commit == head
    assert after.provenance.observation.untracked_paths == (b"untracked",)
    for endpoint, role in ((before, "baseline"), (after, "local-effective")):
        assert (endpoint.repository, endpoint.mode, endpoint.ref_role) == (
            "owner/project",
            "local",
            role,
        )
        assert endpoint.baseline_identity == before.endpoint_identity
        assert endpoint.changes == before.changes
        record = json.loads(endpoint.canonical_bytes())
        assert (record["repository"], record["mode"], record["ref_role"]) == (
            "owner/project",
            "local",
            role,
        )
        assert record["baseline_identity"] == {"commit": base, "tree": base_tree}
    assert json.loads(before.canonical_bytes())["endpoint_identity"] == {
        "commit": base,
        "tree": base_tree,
    }
    assert json.loads(after.canonical_bytes())["endpoint_identity"] == {
        "worktree_digest": after.endpoint_identity.worktree_digest,
    }


def test_local_clean_and_cancelled_layers_bind_observation(repo):
    write(repo, "tracked", b"base")
    base = commit_files(repo, "base")
    base_tree = git(repo, "rev-parse", "HEAD^{tree}").decode().strip()
    alternate = commit(repo, base_tree, message="another commit with identical tree")

    before, clean = local_pair(repo, local_request(base))
    assert clean.changes == before.changes == ()
    assert clean.provenance.committed_changes == ()
    assert clean.provenance.staged_changes == ()
    assert clean.provenance.unstaged_changes == ()
    write(repo, "tracked", b"new in HEAD")
    commit_files(repo, "changed HEAD")
    write(repo, "tracked", b"staged now")
    git(repo, "add", "tracked")
    write(repo, "tracked", b"base")

    before, cancelled = local_pair(repo, local_request(base))
    assert cancelled.changes == before.changes == ()
    assert len(cancelled.provenance.committed_changes) == 1
    assert len(cancelled.provenance.staged_changes) == 1
    assert len(cancelled.provenance.unstaged_changes) == 1
    assert cancelled.endpoint_identity != clean.endpoint_identity
    assert cancelled.read_content(b"tracked") == b"base"
    different_before, other = local_pair(repo, local_request(alternate))
    assert other.endpoint_identity == cancelled.endpoint_identity
    assert other.changes == cancelled.changes
    assert other.baseline_identity == different_before.endpoint_identity
    assert other.baseline_identity != cancelled.baseline_identity
    assert other.digest != cancelled.digest


@pytest.mark.parametrize(
    "change", ["head", "index", "bytes", "mode", "membership", "ignore"]
)
def test_local_observation_drift_refuses(repo, monkeypatch, change):
    file = write(repo, "tracked", b"old")
    write(repo, ".gitignore", b"ignored\n")
    base = commit_files(repo, "base")
    other = commit(
        repo,
        git(repo, "rev-parse", "HEAD^{tree}").decode().strip(),
        message="same tree, different HEAD",
    )
    observe = snapshot._observe_local
    mutated = False

    def mutate_after_observation(git_profile, worktree, request):
        nonlocal mutated
        observed = observe(git_profile, worktree, request)
        if mutated:
            return observed
        mutated = True
        if change == "head":
            git(repo, "update-ref", "HEAD", other)
        elif change == "index":
            oid = blob(repo, b"index only")
            git(repo, "update-index", "--cacheinfo", f"100644,{oid},tracked")
        elif change == "bytes":
            stat = file.stat()
            file.write_bytes(b"new")
            os.utime(file, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        elif change == "mode":
            file.chmod(0o755)
        elif change == "membership":
            write(repo, "new", b"arrived during capture")
        elif change == "ignore":
            write(repo, ".gitignore", b"ignorex\n")
        return observed

    monkeypatch.setattr(snapshot, "_observe_local", mutate_after_observation)
    local_refusal(repo, local_request(base), "observation_drift")


def test_local_captures_bytes_regardless_of_cached_stat(repo):
    file = write(repo, "tracked", b"old")
    base = commit_files(repo, "base")
    git(repo, "update-index", "--assume-unchanged", "tracked")
    prior = file.stat()
    file.write_bytes(b"new")
    os.utime(file, ns=(prior.st_atime_ns, prior.st_mtime_ns))
    assert git(repo, "status", "--porcelain") == b""
    before, after = local_pair(repo, local_request(base))
    assert before.read_content(b"tracked") == b"old"
    assert after.read_content(b"tracked") == b"new"
    assert [c.status for c in after.changes] == ["M"]
    file.write_bytes(b"later")
    assert after.read_content(b"tracked") == b"new"


def test_local_git_config_and_path_identity(repo, monkeypatch, tmp_path):
    marker = tmp_path / "unexpected-executable"
    hook = write(tmp_path, "hook.sh", f"#!/bin/sh\ntouch '{marker}'\n".encode())
    hook.chmod(0o755)
    excludes = write(tmp_path, "excludes", b"global-only\n")
    global_config = write(
        tmp_path,
        "gitconfig",
        f"[diff]\nrenames = false\n[core]\nexcludesFile = {excludes}\n".encode(),
    )
    git(repo, "config", "core.fsmonitor", str(hook))
    git(repo, "config", "diff.external", str(hook))
    git(repo, "config", "core.precomposeUnicode", "true")
    git(repo, "config", "core.ignoreCase", "true")
    write(repo, ".git/info/exclude", b"info-only\n")
    write(repo, ".gitignore", b"hidden\nexcluded/\n")
    write(repo, "ignored-only/.gitignore", b"*\n")
    write(repo, "ignored-only/other", b"also ignored")
    write(repo, "excluded/.gitignore", b"irrelevant inside excluded subtree\n")
    write(repo, "former", b"rename")
    base = commit_files(repo, "base")
    marker.unlink(missing_ok=True)
    git(repo, "mv", "former", "renamed")
    marker.unlink(missing_ok=True)
    write(repo, "global-only", b"global excludes must not apply")
    write(repo, "info-only", b"info excludes must not apply")
    write(repo, "hidden", b"repo ignores normally apply")
    write(repo, "nested/hidden", b"declared ignored input")
    decomposed = "e\u0301.txt"
    write(repo, decomposed, b"decomposed bytes")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(global_config))
    monkeypatch.setenv("GIT_DIR", str(tmp_path / "invalid"))
    monkeypatch.setenv("GIT_EXTERNAL_DIFF", str(hook))

    _, after = local_pair(repo, local_request(base, b"nested/hidden"))
    assert [e.path for e in after.entries] == [
        b".gitignore",
        decomposed.encode(),
        b"global-only",
        b"info-only",
        b"nested/hidden",
        b"renamed",
    ]
    assert after.read_content(decomposed.encode()) == b"decomposed bytes"
    assert after.read_content(b"nested/hidden") == b"declared ignored input"
    assert [c.status for c in after.provenance.staged_changes] == ["R"]
    ignore = dict(after.provenance.observation.ignore_sources)
    assert ignore[b".gitignore"] == hashlib.sha256(b"hidden\nexcluded/\n").hexdigest()
    assert ignore[b"ignored-only/.gitignore"] == hashlib.sha256(b"*\n").hexdigest()
    assert not marker.exists()

    alias = "é.txt".encode()
    # An exact Git spelling distinct from the only physical directory entry.
    index = b"100644 " + blob(repo, b"alias").encode() + b"\t" + alias + b"\0"
    git(
        repo,
        "-c",
        "core.precomposeUnicode=false",
        "-c",
        "core.ignoreCase=false",
        "update-index",
        "-z",
        "--index-info",
        data=index,
    )
    if not (repo / alias.decode()).exists():
        pytest.skip("filesystem has no normalization aliases")
    marker.unlink(missing_ok=True)
    local_refusal(repo, local_request(base, b"nested/hidden"), "unsafe_path")


def test_local_unaccounted_ignore_inputs_refuse(repo, monkeypatch):
    write(repo, ".gitignore", b"private/\n")
    write(repo, "private/declared", b"declared")
    base = commit_files(repo, "base")
    real_read = snapshot._CheckedTree.read
    for unreadable in (b".gitignore", b"private/declared"):

        def deny(worktree, path):
            if path == unreadable:
                raise PermissionError("fixture refuses read")
            return real_read(worktree, path)

        with monkeypatch.context() as patch:
            patch.setattr(snapshot._CheckedTree, "read", deny)
            local_refusal(
                repo, local_request(base, b"private/declared"), "unreadable_input"
            )

    _, after = local_pair(repo, local_request(base, b"private/absent"))
    assert b"private/absent" in after.provenance.observation.observed_absent
    assert b"private/absent" not in [e.path for e in after.entries]
    assert after.changes == ()


@pytest.mark.parametrize("fault", ["unmerged", "fifo", "ancestor", "escape", "target"])
def test_local_unsafe_inputs_refuse(repo, tmp_path, fault):
    old = write(repo, "folder/leaf", b"old")
    base = commit_files(repo, "base")
    request = local_request(base)
    if fault == "unmerged":
        oid = git(repo, "rev-parse", ":folder/leaf").strip()
        stage_records = (
            b"0 "
            + b"0" * len(oid)
            + b"\tfolder/leaf\0"
            + b"100644 "
            + oid
            + b" 1\tfolder/leaf\0"
            + b"100644 "
            + oid
            + b" 2\tfolder/leaf\0"
        )
        git(repo, "update-index", "-z", "--index-info", data=stage_records)
        local_refusal(repo, request, "unmerged_index")
    elif fault == "fifo":
        old.unlink()
        os.mkfifo(old)
        local_refusal(repo, request, "unsupported_object")
    elif fault == "ancestor":
        old.unlink()
        old.parent.rmdir()
        old.parent.symlink_to(tmp_path)
        local_refusal(repo, request, "unsafe_path")
    elif fault == "escape":
        local_refusal(repo, local_request(base, b"../outside"), "unsafe_path")
    elif fault == "target":
        outside = write(tmp_path, "outside", b"outside")
        (repo / "link").symlink_to(outside)
        local_refusal(repo, request, "unsafe_path")


def test_local_binds_a_symlink_to_observed_target(repo):
    write(repo, "target", b"before")
    base = commit_files(repo, "base")
    (repo / "link").symlink_to("target")
    write(repo, "target", b"after")
    _, after = local_pair(repo, local_request(base))
    assert after.read_content(b"link") == b"target"
    assert after.read_content(b"target") == b"after"
    link = next(entry for entry in after.entries if entry.path == b"link")
    assert link.mode == "120000"
    assert dict(after.provenance.observation.symlink_targets) == {b"link": b"target"}


@pytest.mark.parametrize("damage", ["ref", "boolean"])
def test_hosted_refuses_wrong_trunk_ref_and_boolean_binding(repo, damage):
    base_tree = tree(repo, [])
    base = commit(repo, base_tree)
    request = rebind(hosted_request(base, base, base_tree), run_attempt=1)
    if damage == "ref":
        request = rebind(request, ref="refs/heads/unrelated")
    else:
        request = replace(request, binding=replace(request.binding, run_attempt=True))
    assert_refusal(repo, request, "identity_mismatch")


def test_hosted_refuses_duplicate_tree_commit_header(repo):
    tree_id = tree(repo, [])
    base = commit(repo, tree_id)
    malformed = (
        git(
            repo,
            "hash-object",
            "-t",
            "commit",
            "--literally",
            "-w",
            "--stdin",
            data=(
                f"tree {tree_id}\ntree {tree_id}\n"
                "author Fixture <fixture@example.test> 1234 +0000\n"
                "committer Fixture <fixture@example.test> 1234 +0000\n\nmessage\n"
            ).encode(),
        )
        .decode()
        .strip()
    )
    assert_refusal(repo, hosted_request(base, malformed, tree_id), "malformed_data")


@pytest.mark.parametrize("damage", ["wrong-type", "split-modification"])
def test_hosted_refuses_diff_records_that_misstate_change(repo, monkeypatch, damage):
    old = blob(repo, b"old")
    new = blob(repo, b"new")
    base_tree = tree(repo, [(b"tracked", "100644", "blob", old)])
    tested_tree = tree(repo, [(b"tracked", "100644", "blob", new)])
    request = hosted_request(
        commit(repo, base_tree), commit(repo, tested_tree), tested_tree
    )
    run = snapshot._run_git

    def damage_diff(repo, command, env, data=None):
        result = run(repo, command, env, data)
        if "diff-tree" in command:
            if damage == "wrong-type":
                result.stdout = result.stdout.replace(b" M\0", b" T\0")
            else:
                zero = "0" * len(old)
                result.stdout = (
                    f":100644 000000 {old} {zero} D\0tracked\0"
                    f":000000 100644 {zero} {new} A\0tracked\0"
                ).encode()
        return result

    monkeypatch.setattr(snapshot, "_run_git", damage_diff)
    assert_refusal(repo, request, "malformed_data")


def test_local_ignored_parent_identity_is_rechecked(repo, monkeypatch):
    write(repo, ".gitignore", b"private/\n")
    base = commit_files(repo, "base")
    leaf = write(repo, "private/parent/leaf", b"same inode and bytes")
    replacement = repo / "private" / "replacement"
    replacement.mkdir()
    os.link(leaf, replacement / "leaf")
    observe = snapshot._observe_local
    mutated = False

    def replace_parent(git_profile, worktree, request):
        nonlocal mutated
        observed = observe(git_profile, worktree, request)
        if not mutated:
            mutated = True
            leaf.parent.rename(replacement.with_name("former"))
            replacement.rename(leaf.parent)
        return observed

    monkeypatch.setattr(snapshot, "_observe_local", replace_parent)
    local_refusal(
        repo, local_request(base, b"private/parent/leaf"), "observation_drift"
    )


def test_local_relative_symlink_reaches_checked_parent(repo):
    write(repo, "target", b"target")
    write(repo, "folder/tracked", b"tracked")
    base = commit_files(repo, "base")
    (repo / "folder" / "link").symlink_to("../target")
    _, after = local_pair(repo, local_request(base))
    assert after.read_content(b"folder/link") == b"../target"
    assert dict(after.provenance.observation.symlink_targets) == {
        b"folder/link": b"target"
    }


def test_local_directory_and_file_replacement_bind_effective_leaves(repo):
    write(repo, "old-file", b"was a file")
    write(repo, "old-directory/leaf", b"was in a directory")
    base = commit_files(repo, "base")
    (repo / "old-file").unlink()
    (repo / "old-directory" / "leaf").unlink()
    (repo / "old-directory").rmdir()
    write(repo, "old-directory", b"now a file")
    write(repo, "old-file/leaf", b"now in a directory")

    before, after = local_pair(repo, local_request(base))
    assert before.read_content(b"old-file") == b"was a file"
    assert after.read_content(b"old-file/leaf") == b"now in a directory"
    assert after.read_content(b"old-directory") == b"now a file"
    assert [(c.status, (c.old or c.new).path) for c in after.changes] == [
        ("A", b"old-directory"),
        ("D", b"old-directory/leaf"),
        ("D", b"old-file"),
        ("A", b"old-file/leaf"),
    ]


def test_hosted_refuses_noncanonical_tree_order(repo):
    content = blob(repo, b"payload")
    payload = b"".join(
        b"100644 " + name + b"\0" + bytes.fromhex(content) for name in (b"z", b"a")
    )
    malformed = (
        git(
            repo,
            "hash-object",
            "-t",
            "tree",
            "--literally",
            "-w",
            "--stdin",
            data=payload,
        )
        .decode()
        .strip()
    )
    tested = commit(repo, malformed)
    assert_refusal(repo, hosted_request(tested, tested, malformed), "malformed_data")
