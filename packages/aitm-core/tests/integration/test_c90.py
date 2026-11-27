"""Load ordered workflow profiles from the Git snapshot admitted by C07."""

import subprocess
from hashlib import sha256

import pytest

from aitm_core.config import PolicyUnavailable, resolve_policy
from aitm_core.machine.profile import ProfileUnavailable, load_profile
from aitm_core.models.common import RefObservation, RefreshResult
from aitm_core.store.objects import Repository
from tests.support.c07 import DEFAULT, PLANNING, WORKFLOW, installation, settings_at


def git(root, *args):
    return subprocess.check_output(
        ("git", "-C", str(root), *args), stderr=subprocess.PIPE, text=True
    ).strip()


@pytest.fixture
def policy_repository(tmp_path):
    root = tmp_path / "default"
    root.mkdir()
    git(root, "init", "-q", "-b", "trunk")
    git(root, "config", "user.name", "C90 fixture")
    git(root, "config", "user.email", "fixture@example.invalid")
    git(root, "commit", "--allow-empty", "-qm", "Fixture root")
    return root, git(root, "rev-parse", "HEAD")


def workflow_document(profile_id, states):
    terminal = states[-1]
    header = f"""\
schema = "aitm.workflow/v1"
id = "{profile_id}"
contract = "core.hosted-delivery/v1"

[lifecycle]
terminal = "{terminal}"
non_delivery = "{terminal}"
reopen_design = "design"
reopen_plan = "plan"

[recovery]
design_rework = "design"
implementation_rework = "dev"
trip = "plan"
scope_pivot = "plan"
"""
    entries = [
        f"""
[[states]]
id = "{state}"
label = "{state.title()}"
onEnter = []
action = []
onExit = []
"""
        for state in states
    ]
    return (header + "".join(entries)).encode()


def write_file(root, path, content):
    destination = root / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)


def commit_policy(root, settings, workflow_path, workflow):
    write_file(root, ".aitm.toml", settings.encode())
    write_file(root, workflow_path, workflow)
    git(root, "add", ".aitm.toml", workflow_path)
    git(root, "commit", "-qm", "Commit workflow policy")
    return git(root, "rev-parse", "HEAD")


def observation(revision):
    return RefreshResult(local=RefObservation(ref=DEFAULT, observed_commit=revision))


def test_profiles_follow_literal_default_history_from_a_story_worktree(
    policy_repository,
):
    root, genesis = policy_repository
    settings = settings_at(genesis)
    original = workflow_document(
        "delivery", ("backlog", "design", "plan", "dev", "review", "done")
    )
    original_commit = commit_policy(root, settings, WORKFLOW, original)

    story = root.parent / "story"
    git(root, "worktree", "add", "-qb", "story", str(story), DEFAULT)
    story_path = ".aitm/workflows/story.toml"
    story_workflow = workflow_document(
        "story", ("design", "plan", "dev", "review", "story-done")
    )
    write_file(story, WORKFLOW, story_workflow)
    git(story, "add", WORKFLOW)
    story_commit = commit_policy(
        story, settings.replace(WORKFLOW, story_path), story_path, story_workflow
    )
    anchor = installation(Repository(story, PLANNING), genesis)

    revised_path = ".aitm/workflows/revised.toml"
    revised = workflow_document(
        "revised-delivery", ("design", "plan", "park", "dev", "review", "closed")
    )
    revised_commit = commit_policy(
        root, settings.replace(WORKFLOW, revised_path), revised_path, revised
    )

    for revision, path, revision_bytes, profile_id, state_ids in (
        (
            original_commit,
            WORKFLOW,
            original,
            "delivery",
            ("backlog", "design", "plan", "dev", "review", "done"),
        ),
        (
            revised_commit,
            revised_path,
            revised,
            "revised-delivery",
            ("design", "plan", "park", "dev", "review", "closed"),
        ),
    ):
        loaded = load_profile(resolve_policy(anchor, observation(revision)))
        assert loaded.id == profile_id
        assert tuple(state.id for state in loaded.states) == state_ids
        assert loaded.lifecycle.terminal == state_ids[-1]
        assert loaded.source.path == path
        assert loaded.source.revision == revision
        assert loaded.source.tree == git(root, "rev-parse", f"{revision}^{{tree}}")
        assert loaded.source.digest == sha256(revision_bytes).hexdigest()

    with pytest.raises(PolicyUnavailable, match="anchored code-default history"):
        resolve_policy(anchor, observation(story_commit))


@pytest.mark.parametrize("defect", ["duplicate-state", "unsupported-version"])
def test_invalid_workflow_is_refused_after_c07_resolves_its_committed_bytes(
    policy_repository, defect
):
    root, genesis = policy_repository
    states = ("design", "plan", "dev", "review", "done")
    if defect == "duplicate-state":
        states = ("design", *states)
    workflow = workflow_document("delivery", states)
    if defect == "unsupported-version":
        workflow = workflow.replace(b"aitm.workflow/v1", b"aitm.workflow/v9")
    revision = commit_policy(root, settings_at(genesis), WORKFLOW, workflow)
    anchor = installation(Repository(root, PLANNING), genesis)

    pinned = resolve_policy(anchor, observation(revision))
    with pytest.raises(ProfileUnavailable) as failure:
        load_profile(pinned)
    assert WORKFLOW in str(failure.value)
