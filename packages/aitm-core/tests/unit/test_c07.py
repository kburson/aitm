"""Policy parsing, adoption and effective settings with pinned in-memory blobs."""

from types import SimpleNamespace

import pytest

from aitm_core.config import CONFIG_PATH, PolicyUnavailable, classify_change
from aitm_core.models.common import RefObservation, RefreshResult
from aitm_core.services import policy
from aitm_core.store.backend import Snapshot
from tests.support.c07 import (
    DEFAULT,
    PLANNING,
    WORKFLOW,
    WORKFLOW_BYTES,
    installation,
    settings_at,
    updated_effective_settings,
)


@pytest.fixture
def committed_policy():
    genesis = "a" * 40
    snapshots = {}

    def observe(settings, workflow=WORKFLOW_BYTES):
        revision = f"{len(snapshots) + 1:040x}"
        snapshots[revision] = {CONFIG_PATH: settings.encode(), WORKFLOW: workflow}
        return RefreshResult(
            local=RefObservation(ref=DEFAULT, observed_commit=revision)
        )

    class PinnedFiles:
        ref = PLANNING

        def _oid(self, value):
            assert len(value) == 40
            return value

        def _run(self, command, option, *args):
            if (command, option, args) == ("symbolic-ref", "-q", (DEFAULT,)):
                return SimpleNamespace(returncode=1)
            if (command, option) == ("merge-base", "--is-ancestor"):
                assert all(revision in snapshots for revision in args)
                return SimpleNamespace(returncode=0)
            pytest.fail(f"unexpected repository invocation: {command} {option} {args}")

        def _git(self, command, *args):
            if command == "check-ref-format":
                return b""
            if (command, args) == ("show-ref", ("--verify", "--hash", DEFAULT)):
                return next(reversed(snapshots)).encode()
            if command == "cat-file" and args[0] == "-t":
                assert args[1] in snapshots
                return b"commit"
            if command == "--literal-pathspecs" and args[:2] == ("ls-tree", "-z"):
                return b"100644 blob " if args[-1] in snapshots[args[2]] else b""
            pytest.fail(f"unexpected repository invocation: {command} {args}")

        def read_tree(self, revision):
            assert revision in snapshots
            return Snapshot("fixture", revision, revision)

        def read_blobs(self, tree, paths):
            return {path: snapshots[tree].get(path) for path in paths}

    return installation(PinnedFiles(), genesis), settings_at(genesis), observe


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
def test_delivered_anchor_change_fences_both_modes(
    committed_policy, mode, old_value, new_value
):
    anchor, settings, observe = committed_policy
    settings = settings.replace('mode = "enforce"', f'mode = "{mode}"')
    old = policy(anchor, observe(settings))
    latest = policy(anchor, observe(settings.replace(old_value, new_value)))
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
        ("leaf_agent_hours = 4", "leaf_agent_hours = 4.01"),
        ("expansions_per_attempt = 1", "expansions_per_attempt = 2"),
        ('schema = "aitm.review-policy/v1"', 'schema = "aitm.review-policy/v8"'),
        (f'file = "{WORKFLOW}"', 'file = "../story.toml"'),
        (f'file = "{WORKFLOW}"', 'file = ".aitm/workflows/missing.toml"'),
    ],
)
def test_missing_or_unsupported_committed_settings_are_unavailable(
    committed_policy, old_value, new_value
):
    anchor, settings, observe = committed_policy
    obs = observe(settings.replace(old_value, new_value))
    with pytest.raises(PolicyUnavailable):
        policy(anchor, obs)


def test_selection_is_pinned_tip_effective_policy(committed_policy):
    anchor, settings, observe = committed_policy
    first = policy(anchor, observe(settings))
    next_settings = (
        settings + '\n[test.selection]\nstrategy = "tia"\non_unavailable = "hold"\n'
    )
    second = policy(anchor, observe(next_settings))
    assert first.config.test.selection is None
    assert second.config.test.selection.strategy == "tia"
    assert classify_change(first, second).tip_effective


@pytest.mark.parametrize(
    "unsupported",
    ["unrecognized_setting = true\n", '[unrecognized_policy]\nreview = "none"\n'],
)
def test_unknown_top_level_policy_is_unavailable(committed_policy, unsupported):
    anchor, settings, observe = committed_policy
    observed = observe(unsupported + settings)
    with pytest.raises(PolicyUnavailable, match="unrecognized_"):
        policy(anchor, observed)


def test_effective_policy_can_change_without_reconfiguring_store(committed_policy):
    anchor, settings, observe = committed_policy
    pinned = policy(anchor, observe(settings))
    changed = updated_effective_settings(settings)
    assert pinned.config.enforcement.mode == "enforce"
    assert pinned.config.limits.leaf_agent_hours == 4
    latest = policy(anchor, observe(changed, b"new committed workflow"))
    assert latest.config.enforcement.mode == "advisory"
    assert latest.config.limits.leaf_agent_hours == 2
    assert latest.config.providers.githost == "github"
    assert latest.routing == pinned.routing
    change = classify_change(pinned, latest)
    assert change.tip_effective
    assert not change.requires_reconfigure


def test_unanchored_candidate_cannot_act_as_local_observation(committed_policy):
    anchor, settings, observe = committed_policy
    local = observe(settings).local
    candidate = RefObservation(
        ref="refs/candidates/default",
        remote="origin",
        observed_commit=local.observed_commit,
    )
    with pytest.raises(PolicyUnavailable, match="anchored local"):
        policy(anchor, RefreshResult(local=candidate))


def test_candidate_cannot_supply_missing_local_commit(committed_policy):
    anchor, settings, observe = committed_policy
    local = observe(settings).local
    candidate = RefObservation(
        ref="refs/candidates/default",
        remote="origin",
        observed_commit=local.observed_commit,
    )
    with pytest.raises(PolicyUnavailable, match="anchored local"):
        policy(
            anchor,
            RefreshResult(
                local=RefObservation(ref=DEFAULT, observed_commit=None),
                candidate=candidate,
            ),
        )
