"""Resolve effective policy through the installed service in a real Git clone."""

import subprocess
from dataclasses import replace

import pytest

from aitm_core.config import PolicyUnavailable
from aitm_core.models.common import RefObservation, RefreshResult
from aitm_core.services import policy
from aitm_core.store.objects import Repository
from tests.support.c07 import (
    DEFAULT,
    PLANNING,
    WORKFLOW,
    WORKFLOW_BYTES,
    installation,
    settings_at,
    updated_effective_settings,
)


def git(root, *args):
    return subprocess.check_output(
        ("git", "-C", str(root), *args), stderr=subprocess.PIPE, text=True
    ).strip()


@pytest.fixture
def setup(tmp_path):
    root = tmp_path
    git(root, "init", "-q", "-b", "trunk")
    git(root, "config", "user.name", "C07 fixture")
    git(root, "config", "user.email", "fixture@example.invalid")
    git(root, "commit", "--allow-empty", "-qm", "Fixture root")
    genesis = git(root, "rev-parse", "HEAD")
    repository = Repository(root, PLANNING)
    return root, installation(repository, genesis), settings_at(genesis)


def commit_policy(root, settings, workflow=WORKFLOW_BYTES):
    (root / ".aitm.toml").write_text(settings)
    path = root / WORKFLOW
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(workflow)
    git(root, "add", ".aitm.toml", WORKFLOW)
    git(root, "commit", "-qm", "Commit fixture policy")
    return RefreshResult(
        local=RefObservation(
            ref=DEFAULT, observed_commit=git(root, "rev-parse", "HEAD")
        )
    )


def test_policy_authority(setup):
    root, anchor, settings = setup
    old = commit_policy(root, settings)
    pinned = policy(anchor, old)
    changed = updated_effective_settings(settings)
    git(root, "switch", "-qc", "story")
    commit_policy(root, changed, b"story workflow")
    assert policy(anchor, old) == pinned
    assert pinned.config.test.command == "uv run pytest"
    assert pinned.workflow.content == b"id = 'fixture-workflow'\n"
    git(root, "switch", "-q", "trunk")
    new = commit_policy(root, changed, b"new committed workflow")
    latest = policy(anchor, new)
    assert latest.revision == new.local.observed_commit
    assert latest.config.test.command == "false"
    assert latest.workflow.content == b"new committed workflow"
    assert policy(anchor, old) == pinned


def test_only_validated_local_observation_can_select_policy(setup):
    root, installation, settings = setup
    accepted = commit_policy(root, settings)
    pinned = policy(installation, accepted)
    git(root, "switch", "-qc", "story")
    replacement = commit_policy(root, settings.replace("uv run pytest", "false"))
    candidate = RefObservation(
        ref="refs/candidates/default",
        remote="origin",
        observed_commit=replacement.local.observed_commit,
    )
    assert (
        policy(installation, accepted.model_copy(update={"candidate": candidate}))
        == pinned
    )
    with pytest.raises(PolicyUnavailable, match="anchored code-default history"):
        policy(installation, replacement)


def test_separate_hosted_routes_never_follow_githost_provider(setup):
    root, anchor, settings = setup
    anchor = replace(
        anchor,
        store=anchor.store.model_copy(update={"planning_remote": "shared"}),
        code_remote="origin",
        code_remote_ref=DEFAULT,
    )
    settings = (
        settings.replace("[store]", '[store]\nremote = "shared"')
        .replace('trunk = "trunk"', 'trunk = "origin/trunk"')
        .replace('githost = "none"', 'githost = "github"')
    )
    accepted = commit_policy(root, settings)
    with pytest.raises(PolicyUnavailable, match="anchored"):
        policy(anchor, accepted)
    assert anchor.validated_code_ref is not None
    git(root, "update-ref", anchor.validated_code_ref, accepted.local.observed_commit)
    accepted = RefreshResult(
        local=accepted.local.model_copy(update={"remote": "origin"})
    )
    resolved = policy(anchor, accepted)
    assert not resolved.writes_fenced
    assert resolved.routing.store.planning_remote == "shared"
    assert resolved.routing.trunk == "origin/trunk"
    git(root, "switch", "-qc", "remote-candidate")
    candidate = commit_policy(
        root, settings.replace('remote = "shared"', 'remote = "origin"')
    )
    observed = RefreshResult(
        local=candidate.local.model_copy(update={"remote": "origin"})
    )
    with pytest.raises(PolicyUnavailable, match="anchored code-default history"):
        policy(anchor, observed)
    git(root, "update-ref", anchor.validated_code_ref, candidate.local.observed_commit)
    changed = policy(anchor, observed)
    assert git(root, "rev-parse", DEFAULT) == accepted.local.observed_commit
    assert policy(anchor, accepted) == resolved
    assert changed.writes_fenced
    assert changed.routing.store.planning_remote == "shared"


def test_workflow_symlink_cannot_substitute_a_path(setup):
    root, anchor, settings = setup
    commit_policy(root, settings)
    path = root / WORKFLOW
    path.unlink()
    path.symlink_to("../../story.toml")
    git(root, "add", WORKFLOW)
    git(root, "commit", "-qm", "Replace fixture file with symlink")
    local = RefObservation(ref=DEFAULT, observed_commit=git(root, "rev-parse", "HEAD"))
    with pytest.raises(PolicyUnavailable, match="regular file"):
        policy(anchor, RefreshResult(local=local))
