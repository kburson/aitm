"""Policy parsing, adoption and effective settings with pinned in-memory blobs."""

from hashlib import sha256
from operator import attrgetter
from tomllib import TOMLDecodeError
from types import SimpleNamespace

import pytest

from aitm_core.config import CONFIG_PATH, PolicyUnavailable, classify_change
from aitm_core.models.common import RefObservation, RefreshResult
from aitm_core.services import policy
from aitm_core.store.backend import Snapshot
from aitm_core.store.objects import GitCommandError, Repository, UnknownTree
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

        oid_length = 40
        _oid = Repository._oid

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


def test_policy_observation_requires_full_commit_identity(committed_policy):
    anchor, settings, observe = committed_policy
    accepted = observe(settings)
    abbreviated = accepted.local.model_copy(update={"observed_commit": "0010abc"})
    with pytest.raises(PolicyUnavailable, match="unavailable at 0010abc") as error:
        policy(anchor, RefreshResult(local=abbreviated))
    assert "full Git object identity" in str(error.value.__cause__)


def test_symbolic_default_ref_cannot_nominate_its_own_anchor(
    committed_policy, monkeypatch
):
    anchor, settings, observe = committed_policy
    accepted = observe(settings)

    def symbolic_ref(*args):
        assert args == ("symbolic-ref", "-q", DEFAULT)
        return SimpleNamespace(returncode=0, stdout=b"refs/heads/story\n")

    monkeypatch.setattr(anchor.repository, "_run", symbolic_ref)
    with pytest.raises(PolicyUnavailable, match="direct anchored code-default ref"):
        policy(anchor, accepted)


def test_missing_code_default_ref_does_not_use_retained_observation_alone(
    committed_policy, monkeypatch
):
    anchor, settings, observe = committed_policy
    accepted = observe(settings)

    def missing_ref(*args):
        assert args == ("show-ref", "--verify", "--hash", DEFAULT)
        raise GitCommandError("show-ref", b"not a valid ref")

    monkeypatch.setattr(anchor.repository, "_git", missing_ref)
    with pytest.raises(
        PolicyUnavailable, match=f"unavailable at {accepted.local.observed_commit}"
    ) as error:
        policy(anchor, accepted)
    assert isinstance(error.value.__cause__, GitCommandError)


def test_anchored_observation_cannot_use_a_tree_instead_of_a_commit(
    committed_policy, monkeypatch
):
    anchor, settings, observe = committed_policy
    accepted = observe(settings)
    git = anchor.repository._git

    def tree_object(command, *args):
        if (command, args) == ("cat-file", ("-t", accepted.local.observed_commit)):
            return b"tree\n"
        return git(command, *args)

    monkeypatch.setattr(anchor.repository, "_git", tree_object)
    with pytest.raises(PolicyUnavailable, match="observation does not name a commit"):
        policy(anchor, accepted)


def test_unreadable_pinned_tree_does_not_fall_back_to_later_default(
    committed_policy, monkeypatch
):
    anchor, settings, observe = committed_policy
    pinned = observe(settings)
    observe(updated_effective_settings(settings))

    def missing_tree(revision):
        assert revision == pinned.local.observed_commit
        raise UnknownTree("pinned tree unavailable")

    monkeypatch.setattr(anchor.repository, "read_tree", missing_tree)
    with pytest.raises(
        PolicyUnavailable, match=f"unavailable at {pinned.local.observed_commit}"
    ) as error:
        policy(anchor, pinned)
    assert isinstance(error.value.__cause__, UnknownTree)


def test_commit_without_config_cannot_inherit_config_from_later_tree(
    committed_policy, monkeypatch
):
    anchor, settings, observe = committed_policy
    pinned = observe(settings)
    observe(updated_effective_settings(settings))
    git = anchor.repository._git

    def missing_entry(command, *args):
        if (command, args) == (
            "--literal-pathspecs",
            ("ls-tree", "-z", pinned.local.observed_commit, "--", CONFIG_PATH),
        ):
            return b""
        return git(command, *args)

    monkeypatch.setattr(anchor.repository, "_git", missing_entry)
    with pytest.raises(
        PolicyUnavailable, match=r"lacks a regular file at \.aitm\.toml"
    ):
        policy(anchor, pinned)


@pytest.mark.parametrize(
    ("content", "diagnostic", "cause"),
    [
        pytest.param(
            None, r"lacks file contents at \.aitm\.toml", None, id="unavailable-blob"
        ),
        pytest.param(
            b"\xffunsupported encoding",
            "policy is unavailable",
            UnicodeDecodeError,
            id="invalid-utf8",
        ),
        pytest.param(
            b"[review\n", "policy is unavailable", TOMLDecodeError, id="invalid-toml"
        ),
    ],
)
def test_config_blob_must_supply_readable_committed_policy(
    committed_policy, monkeypatch, content, diagnostic, cause
):
    anchor, settings, observe = committed_policy
    pinned = observe(settings)

    def invalid_blob(tree, paths):
        assert (tree, paths) == (pinned.local.observed_commit, (CONFIG_PATH,))
        return {CONFIG_PATH: content}

    monkeypatch.setattr(anchor.repository, "read_blobs", invalid_blob)
    with pytest.raises(PolicyUnavailable, match=diagnostic) as error:
        policy(anchor, pinned)
    if cause is not None:
        assert isinstance(error.value.__cause__, cause)


def test_workflow_only_change_requires_tip_policy_reevaluation(committed_policy):
    anchor, settings, observe = committed_policy
    previous = policy(anchor, observe(settings))
    current = policy(anchor, observe(settings, b"[opaque workflow change]\n"))
    assert previous.config == current.config
    assert previous.routing == current.routing
    assert current.workflow.digest != previous.workflow.digest
    change = classify_change(previous, current)
    assert change.tip_effective
    assert not change.requires_reconfigure


def test_nonsemantic_toml_edit_changes_retained_digest_without_policy_change(
    committed_policy,
):
    anchor, settings, observe = committed_policy
    previous = policy(anchor, observe(settings))
    with_comment = "# clarification only\n" + settings
    current = policy(anchor, observe(with_comment))
    assert current.source.digest == sha256(with_comment.encode()).hexdigest()
    assert current.source.digest != previous.source.digest
    assert current.config == previous.config
    change = classify_change(previous, current)
    assert not change.tip_effective
    assert not change.requires_reconfigure


@pytest.mark.parametrize(
    ("old_setting", "new_setting", "field", "expected"),
    [
        pytest.param(
            'backlog_repository = "fixture-issues"',
            'backlog_repository = "other-issues"',
            "issuer.backlog_repository",
            "other-issues",
            id="backlog-repository",
        ),
        pytest.param(
            'root_commit = "' + "a" * 40 + '"',
            'root_commit = "' + "b" * 40 + '"',
            "store.root_commit",
            "b" * 40,
            id="store-genesis",
        ),
        pytest.param(
            "[store]",
            '[store]\nremote = "shared"',
            "store.planning_remote",
            "shared",
            id="planning-remote",
        ),
    ],
)
def test_identity_only_policy_changes_preserve_anchored_routing(
    committed_policy, old_setting, new_setting, field, expected
):
    anchor, settings, observe = committed_policy
    previous = policy(anchor, observe(settings))
    latest = policy(anchor, observe(settings.replace(old_setting, new_setting)))
    assert latest.writes_fenced
    assert latest.routing == previous.routing
    assert attrgetter(field)(latest.proposed_routing) == expected
    change = classify_change(previous, latest)
    assert change.requires_reconfigure
    assert not change.tip_effective


def test_repeated_evaluation_does_not_adopt_pending_route(committed_policy):
    anchor, settings, observe = committed_policy
    first_observation = observe(
        settings.replace('branch = "records"', 'branch = "other-records"')
    )
    pending = policy(anchor, first_observation)
    same_proposal = policy(anchor, first_observation)
    assert pending == same_proposal
    assert pending.writes_fenced
    assert classify_change(pending, same_proposal).requires_reconfigure


def test_legacy_policy_cannot_declare_a_different_root_than_store(committed_policy):
    anchor, settings, observe = committed_policy
    source = settings + (
        f'\n[store.legacy_root]\nroot_commit = "{"b" * 40}"\n'
        f'approved_tip = "{"c" * 40}"\n'
        'adapter_version = "v0"\nallowed_deviations = ["root-readme"]\n'
    )
    with pytest.raises(
        PolicyUnavailable, match="legacy declaration must name the committed store root"
    ):
        policy(anchor, observe(source))


def test_malformed_authoritative_ref_output_cannot_qualify_a_valid_observation(
    committed_policy, monkeypatch
):
    anchor, settings, observe = committed_policy
    accepted = observe(settings)

    def malformed_ref(*args):
        assert args == ("show-ref", "--verify", "--hash", DEFAULT)
        return b"0000000\n"

    monkeypatch.setattr(anchor.repository, "_git", malformed_ref)
    with pytest.raises(
        PolicyUnavailable, match=f"unavailable at {accepted.local.observed_commit}"
    ) as error:
        policy(anchor, accepted)
    assert "full Git object identity" in str(error.value.__cause__)
