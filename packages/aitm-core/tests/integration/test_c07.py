"""Resolve effective policy through the installed service in a real Git clone."""

import subprocess
from dataclasses import replace

import pytest

from aitm_core.config import PolicyUnavailable, classify_change
from aitm_core.models.common import RefObservation, RefreshResult, StoreAnchor
from aitm_core.models.config import BacklogIssuer
from aitm_core.services import policy
from aitm_core.store.installation import Installation
from aitm_core.store.objects import Repository

DEFAULT = "refs/heads/trunk"
PLANNING = "refs/heads/records"
WORKFLOW = ".aitm/workflows/fixture.toml"


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
    anchor = Installation(
        repository=repository,
        store=StoreAnchor(
            store_uuid="fixture-store",
            code_default_ref=DEFAULT,
            planning_ref=PLANNING,
            planning_remote=None,
            root_commit=genesis,
        ),
        code_repository="fixture-code",
        planning_repository="fixture-records",
        issuer=BacklogIssuer(
            backlog="local",
            backlog_repository="fixture-issues",
            numbering_namespace="fixture-ids",
        ),
        bootstrap_source="explicit-default",
    )
    settings = f"""
[store]
branch = "records"
trunk = "trunk"
uuid = "fixture-store"
root_commit = "{genesis}"
code_repository = "fixture-code"
repository = "fixture-records"

[enforcement]
mode = "enforce"

[limits]
leaf_agent_hours = 4
expansions_per_attempt = 1
idle_gap_minutes = 15

[providers]
backlog = "local"
backlog_repository = "fixture-issues"
numbering_namespace = "fixture-ids"
githost = "none"

[extensions]
enabled = []

[test]
command = "uv run pytest"
inputs = []
assurance = "captured-export"
prepare_network = "deny"

[review]
schema = "aitm.review-policy/v1"
id = "explicit-fixture"

[review.documents]
binding = "exact-content"
design_coverage = "own-document"
design = ["xpr"]
plan = ["sar"]
assurances = ["declared-manual"]

[review.source]
record_schema = "aitm.source-review/v1"
independence = "distinct-session"
assurances = ["declared-manual"]

[review.exceptions]
enabled = false

[workflow]
file = "{WORKFLOW}"
"""
    return root, anchor, settings


def commit_policy(root, settings, workflow=b"id = 'fixture-workflow'\n"):
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
    changed = (
        settings.replace('mode = "enforce"', 'mode = "advisory"')
        .replace("leaf_agent_hours = 4", "leaf_agent_hours = 2")
        .replace("uv run pytest", "false")
        .replace('githost = "none"', 'githost = "github"')
    )
    git(root, "switch", "-qc", "story")
    commit_policy(root, changed, b"story workflow")
    assert policy(anchor, old) == pinned
    assert pinned.config.enforcement.mode == "enforce"
    assert pinned.config.limits.leaf_agent_hours == 4
    assert pinned.config.test.command == "uv run pytest"
    assert pinned.workflow.content == b"id = 'fixture-workflow'\n"
    git(root, "switch", "-q", "trunk")
    new = commit_policy(root, changed, b"new committed workflow")
    latest = policy(anchor, new)
    assert latest.revision == new.local.observed_commit
    assert latest.config.enforcement.mode == "advisory"
    assert latest.config.limits.leaf_agent_hours == 2
    assert latest.config.test.command == "false"
    assert latest.config.providers.githost == "github"
    assert latest.workflow.content == b"new committed workflow"
    assert latest.routing == pinned.routing
    change = classify_change(pinned, latest)
    assert change.tip_effective
    assert not change.requires_reconfigure
    assert policy(anchor, old) == pinned


@pytest.mark.parametrize("mode", ["advisory", "enforce"])
@pytest.mark.parametrize(
    ("old_value", "new_value"),
    [
        ('code_repository = "fixture-code"', 'code_repository = "another-code"'),
        ('trunk = "trunk"', 'trunk = "other-default"'),
        ('branch = "records"', 'branch = "other-records"'),
        ('repository = "fixture-records"', 'repository = "new-store"'),
        ('uuid = "fixture-store"', 'uuid = "other-store-id"'),
        ('backlog = "local"', 'backlog = "github"'),
        ('numbering_namespace = "fixture-ids"', 'numbering_namespace = "other-ids"'),
    ],
)
def test_delivered_anchor_change_fences_both_modes(setup, mode, old_value, new_value):
    root, anchor, settings = setup
    settings = settings.replace('mode = "enforce"', f'mode = "{mode}"')
    old = policy(anchor, commit_policy(root, settings))
    latest = policy(anchor, commit_policy(root, settings.replace(old_value, new_value)))
    change = classify_change(old, latest)
    assert change.requires_reconfigure
    assert latest.adoption_pending
    assert latest.writes_fenced
    assert latest.routing == old.routing
    assert latest.proposed_routing != old.routing


@pytest.mark.parametrize(
    ("old_value", "new_value"),
    [
        ('design_coverage = "own-document"', ""),
        ('design_coverage = "own-document"', 'design_coverage = "inherited"'),
        ('record_schema = "aitm.source-review/v1"', ""),
        ('independence = "distinct-session"', 'independence = "self"'),
        ('assurances = ["declared-manual"]', "assurances = []"),
        ("idle_gap_minutes = 15", ""),
        ('schema = "aitm.review-policy/v1"', 'schema = "aitm.review-policy/v8"'),
        (f'file = "{WORKFLOW}"', 'file = "../story.toml"'),
        (f'file = "{WORKFLOW}"', 'file = ".aitm/workflows/missing.toml"'),
    ],
)
def test_missing_or_unsupported_committed_settings_are_unavailable(
    setup, old_value, new_value
):
    root, anchor, settings = setup
    obs = commit_policy(root, settings.replace(old_value, new_value))
    with pytest.raises(PolicyUnavailable):
        policy(anchor, obs)


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
    with pytest.raises(PolicyUnavailable, match="anchored local"):
        policy(installation, RefreshResult(local=candidate))
    with pytest.raises(PolicyUnavailable, match="anchored code-default history"):
        policy(installation, replacement)
    with pytest.raises(PolicyUnavailable, match="anchored local"):
        policy(
            installation,
            RefreshResult(
                local=RefObservation(ref=DEFAULT, observed_commit=None),
                candidate=candidate,
            ),
        )


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


def test_selection_is_pinned_tip_effective_policy(setup):
    root, anchor, settings = setup
    first = policy(anchor, commit_policy(root, settings))
    next_settings = (
        settings + '\n[test.selection]\nstrategy = "tia"\non_unavailable = "hold"\n'
    )
    second = policy(anchor, commit_policy(root, next_settings))
    assert first.config.test.selection is None
    assert second.config.test.selection.strategy == "tia"
    assert classify_change(first, second).tip_effective


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
