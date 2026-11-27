"""Exercise bound worktree ownership through the installed CLI and real Git."""

import json
from dataclasses import replace
from pathlib import Path
from subprocess import run
from sys import executable

import pytest

from aitm_core.models.attempts import BindingPurpose, RecoveryAuthority, SourceSnapshot
from aitm_core.models.binding import StoryRef
from aitm_core.setup.init import _active_installation
from aitm_core.store.objects import Repository
from aitm_core.store.workspace import (
    AuthorityRef,
    AuthorityUnavailable,
    BindRequest,
    Workspace,
)
from tests.integration.test_c11 import DEFAULT, RECORDS, git, init
from tests.integration.test_c11 import policy_inputs as policy_inputs
from tests.integration.test_c11 import repository as repository
from tests.unit.test_c15 import EVENTS, graduated

PLAN = ".aitm/stories/000/16/plan/current.md"


def cli(root, *args):
    result = run(
        (str(Path(executable).with_name("aitm")), "--json", *args),
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return json.loads(result.stdout)


def test_binding_generation(repository, policy_inputs, tmp_path_factory, monkeypatch):
    root = repository
    _, proposal = init(
        root,
        "--local",
        "--default-branch",
        "trunk",
        "--planning-branch",
        "project/records",
        *policy_inputs,
    )
    assert proposal["publication"] == "pending"
    git(root, "add", ".aitm.toml", "aitm-workflow.toml", ".gitignore")
    git(root, "commit", "-qm", "Land policy")
    assert init(root)[1]["local"] == "completed"
    store = Repository(root, RECORDS)
    prior = store.tip()
    candidate = store.create_commit(
        prior, {EVENTS: graduated(), PLAN: b"Original plan\n"}, "seed"
    )
    assert store.compare_and_swap(candidate.revision, prior.revision)
    code = git(root, "rev-parse", DEFAULT)

    author = tmp_path_factory.mktemp("author-worktree")
    other = tmp_path_factory.mktemp("another-worktree")
    git(root, "worktree", "add", "-qb", "author", str(author), "trunk")
    git(root, "worktree", "add", "-qb", "other", str(other), "trunk")
    git(root, "branch", "planning-derived", RECORDS)
    before = git(root, "worktree", "list", "--porcelain")
    claimed = cli(author, "bind", "16", "--session", "alpha", "--path", PLAN)
    assert claimed["local"] == "completed", claimed
    receipt = json.loads(claimed["evidence"][0])
    assert receipt["generation"] == 1
    mirror = author / ".aitm/.state/16.json"
    original_mirror = mirror.read_bytes()
    observed = json.loads(original_mirror)
    assert observed["binding"] == receipt["identity"]
    assert observed["generation"] == 1
    assert "active" not in observed
    assert (author / PLAN).read_bytes() == b"Original plan\n"
    (author / PLAN).write_bytes(b"Unsaved plan\n")
    competing = cli(other, "bind", "16", "--session", "beta", "--path", PLAN)
    assert competing["local"] == "conflict", competing
    assert not (other / PLAN).exists()
    absent = cli(other, "bind", "16", "--evidence", "--session", "beta")
    assert absent["local"] in {"unavailable", "refused"}, absent

    recovered = cli(
        other,
        "bind",
        "16",
        "--session",
        "beta",
        "--recover",
        receipt["identity"],
        "--generation",
        "1",
    )
    assert recovered["local"] == "completed", recovered
    receipt2 = json.loads(recovered["evidence"][0])
    assert receipt2["generation"] == 2
    assert mirror.read_bytes() == original_mirror
    assert json.loads((other / ".aitm/.state/16.json").read_bytes())["generation"] == 2
    assert (author / PLAN).read_bytes() == b"Unsaved plan\n"
    assert (other / PLAN).read_bytes() == b"Original plan\n"
    assert (Path(recovered["evidence"][1]) / PLAN).read_bytes() == b"Unsaved plan\n"
    stale = cli(
        author,
        "bind",
        "16",
        "--session",
        "alpha",
        "--recover",
        receipt["identity"],
        "--generation",
        "1",
    )
    assert stale["local"] == "conflict", stale
    assert git(root, "worktree", "list", "--porcelain") == before
    assert git(root, "rev-parse", DEFAULT) == code

    tree = git(root, "rev-parse", f"{code}^{{tree}}")
    source = ("--commit", code, "--tree", tree)
    recovered_lease = ("--recover", receipt["identity"], "--generation", "2")
    declined = cli(
        other,
        "bind",
        "16",
        "--implementation",
        "--session",
        "beta",
        "--attempt",
        "attempt-1",
        "--branch",
        DEFAULT,
        *source,
        *recovered_lease,
    )
    assert declined["local"] == "integrity-error", declined
    planning_commit = git(root, "rev-parse", RECORDS)
    planning_tree = git(root, "rev-parse", f"{planning_commit}^{{tree}}")
    wrong_history = cli(
        other,
        "bind",
        "16",
        "--implementation",
        "--session",
        "beta",
        "--attempt",
        "attempt-1",
        "--branch",
        "refs/heads/planning-derived",
        "--commit",
        planning_commit,
        "--tree",
        planning_tree,
        *recovered_lease,
    )
    assert wrong_history["local"] == "conflict", wrong_history
    implementation = cli(
        other,
        "bind",
        "16",
        "--implementation",
        "--session",
        "beta",
        "--attempt",
        "attempt-1",
        "--branch",
        "refs/heads/other",
        *source,
        *recovered_lease,
    )
    assert implementation["local"] == "completed", implementation
    claim = json.loads(implementation["evidence"][0])
    assert claim["branch"] == "refs/heads/other"
    assert claim["source"] == {"commit": code, "tree": tree}

    (other / PLAN).write_bytes(b"Refactor retains authored work\n")
    refactored = cli(
        other,
        "bind",
        "16",
        "--implementation",
        "--session",
        "beta",
        "--attempt",
        "attempt-1",
        "--branch",
        claim["branch"],
        "--branch-mode",
        "refactor",
        "--recover",
        claim["identity"],
        "--generation",
        "3",
        *source,
    )
    assert refactored["local"] == "completed", refactored
    assert (other / PLAN).read_bytes() == b"Refactor retains authored work\n"
    assert (
        Path(refactored["evidence"][1]) / PLAN
    ).read_bytes() == b"Refactor retains authored work\n"
    scrapped = cli(
        other,
        "bind",
        "16",
        "--implementation",
        "--session",
        "beta",
        "--attempt",
        "attempt-2",
        "--branch",
        "refs/heads/replacement",
        "--branch-mode",
        "scrap",
        "--recover",
        claim["identity"],
        "--generation",
        "4",
        *source,
    )
    assert scrapped["local"] == "completed", scrapped
    assert git(root, "rev-parse", "refs/heads/replacement") == code
    assert git(root, "rev-parse", claim["branch"]) == code
    assert git(root, "worktree", "list", "--porcelain") == before

    retired = json.loads(scrapped["evidence"][0])
    installation, _ = _active_installation(Repository(other, RECORDS))
    workspace = Workspace(installation)
    authority = RecoveryAuthority(
        purpose=BindingPurpose.EVIDENCE,
        authority_id="approved-recovery",
        attempt="attempt-2",
        ended_generation=retired["generation"],
        source=SourceSnapshot(commit=code, tree=tree),
        allowed=("managed-verification",),
    )
    request = BindRequest(
        installation=installation,
        scope=StoryRef(story=16),
        purpose=BindingPurpose.EVIDENCE,
        session="evidence-session",
        attempt=authority.attempt,
        source=authority.source,
        authority=AuthorityRef(
            authority.authority_id,
            lambda key: authority if key == authority.authority_id else None,
        ),
        capabilities=("managed-verification",),
    )
    with pytest.raises(AuthorityUnavailable):
        workspace.recover_binding(
            replace(request, capabilities=("expand",)),
            retired["identity"],
            retired["generation"],
        )
    from aitm_core.cli.bind import handle

    monkeypatch.chdir(other)
    result = handle(
        ("bind",),
        (
            "16",
            "--evidence",
            "--session",
            "evidence-session",
            "--attempt",
            authority.attempt,
            "--commit",
            code,
            "--tree",
            tree,
            "--authority",
            authority.authority_id,
            "--capability",
            "managed-verification",
            "--recover",
            retired["identity"],
            "--generation",
            str(retired["generation"]),
        ),
        authority_lookup=request.authority.lookup,
    )
    assert result.local == "completed", result.evidence
    effective = json.loads(result.evidence[0])
    assert effective["generation"] == retired["generation"] + 1
    assert effective["paths"] == []
    assert effective["branch"] is None
    assert effective["capabilities"] == ["managed-verification"]

    evidence_lease = (
        "16",
        "--binding",
        effective["identity"],
        "--generation",
        str(effective["generation"]),
        "--session",
        "evidence-session",
    )
    plan_before_release = git(root, "rev-parse", RECORDS)
    assert cli(other, "sync", *evidence_lease)["local"] == "integrity-error"
    selected = cli(other, "unbind", *evidence_lease, "--path", PLAN)
    assert selected["local"] == "integrity-error", selected
    assert cli(author, "unbind", *evidence_lease)["local"] == "conflict"
    released = cli(other, "unbind", *evidence_lease)
    assert released["local"] == "completed", released
    assert git(root, "rev-parse", RECORDS) == plan_before_release
    assert (other / PLAN).read_bytes() == b"Refactor retains authored work\n"
    assert cli(other, "unbind", *evidence_lease)["local"] == "conflict"
    next_holder = cli(root, "bind", "16", "--session", "new-planning-holder")
    assert next_holder["local"] == "completed", next_holder
    assert (
        json.loads(next_holder["evidence"][0])["generation"]
        == effective["generation"] + 1
    )
