"""Prove the installed shared allocator against racing real Git clones."""

from dataclasses import replace
from datetime import UTC, datetime
from json import loads
from pathlib import Path

import pytest

from aitm_core.drafts import CreateEntity, Intake
from aitm_core.graduation import (
    FinalizerRegistry,
    GraduationService,
    ordinary_finalization,
)
from aitm_core.models.common import LocalOutcome, PublicationOutcome
from aitm_core.models.config import DeliveryTarget
from aitm_core.models.identity import FrozenFinalization
from aitm_core.models.lifecycle import Estimate
from aitm_core.models.operations import (
    EventAppend,
    FinalizationIntent,
    PreflightOutcome,
    ReadExpectation,
    RelatedWriteSet,
    story_event_path,
)
from aitm_core.providers.backlog import ActionKey, PublishedStory
from aitm_core.providers.local import LocalBacklog
from aitm_core.relationships import read_graph
from aitm_core.services import preflight_policy
from aitm_core.setup.init import _active_installation, _record_installation
from aitm_core.store.objects import Repository
from aitm_core.store.publication import Publisher
from tests.integration.test_c08 import DEFAULT, PLANNING, PLANNING_REMOTE, git
from tests.integration.test_c08 import topology as topology
from tests.integration.test_c09 import cloned
from tests.integration.test_c11 import RECORDS, init
from tests.integration.test_c11 import policy_inputs as policy_inputs
from tests.integration.test_c11 import repository as repository
from tests.integration.test_c16 import cli
from tests.integration.test_c22 import (
    OWNER,
    PROFILE,
    STAMP,
    create_draft,
    graduation_preflight,
    install_profile,
    with_attempt,
)


def test_allocator_two_clones(topology, tmp_path, monkeypatch):
    install_profile(topology)
    installation = topology.policy.installation
    policy = preflight_policy(installation).policy
    assert policy is not None
    _record_installation(installation, policy.revision)
    repo = installation.repository
    target = DeliveryTarget(repository=installation.code_repository, ref=DEFAULT)
    remote = Path(git(repo.root, "remote", "get-url", PLANNING_REMOTE))

    left_draft = create_draft(installation, "Left draft")
    right_draft = create_draft(installation, "Right draft")
    rival = cloned(topology, tmp_path).policy.installation
    service = GraduationService(installation, OWNER, stamp=STAMP)
    right = LocalBacklog(GraduationService(rival, OWNER, stamp=STAMP))
    right_intent = right.service.prepare_draft(
        right_draft.identity, "right-intent", target
    )
    left_intent = service.prepare_draft(left_draft.identity, "left-intent", target)
    pristine = repo.tip()

    build = GraduationService.build

    def fail_after_proposal(_service, _intent, issue, *_args, **_kwargs):
        assert issue.number == 1
        raise RuntimeError("Injected after proposal")

    with monkeypatch.context() as patch:
        patch.setattr(GraduationService, "build", fail_after_proposal)
        with pytest.raises(RuntimeError, match="Injected"):
            LocalBacklog(service).graduate(left_intent, ordinary_finalization())
    assert repo.tip() == pristine
    assert git(remote, "rev-parse", PLANNING) == pristine.revision
    assert not git(repo.root, "ls-tree", "-r", pristine.tree, ".aitm/stories")
    assert GraduationService.build is build

    choices = []
    semantic = FinalizationIntent(
        kind="fixture.candidate", version=1, related_preconditions=(), payload=b"typed"
    )

    def finalize(request, candidate):
        assert request == semantic
        child = candidate.child
        choices.append((child, candidate.snapshot.revision, candidate.events.operation))
        estimate = Estimate(phase="refine", agent_hours=1, size="S", priority="P1")
        event = candidate.events.encode(
            child,
            "core.estimate.set",
            candidate.tails[child],
            estimate,
            "candidate-estimate",
        )
        return RelatedWriteSet(
            read_set=(ReadExpectation(path=story_event_path(child), digest=None),),
            events=(EventAppend(story=child, records=(event,)),),
        )

    registry = FinalizerRegistry().register_candidate_finalizer(
        semantic.kind, 1, finalize
    )
    left = LocalBacklog(replace(service, registry=registry))
    left_intent = left_intent.model_copy(
        update={"finalization": FrozenFinalization.from_intent(semantic)}
    )
    push = Publisher._push

    def compete(publisher, revision, expected):
        assert repo.tip().revision == expected
        assert revision != repo.tip().revision
        assert not git(repo.root, "ls-tree", "-r", repo.tip().tree, ".aitm/stories")
        monkeypatch.setattr(Publisher, "_push", push)
        winner = right.graduate(right_intent, ordinary_finalization())
        assert winner.issue is not None and winner.issue.number == 1
        push(publisher, revision, expected)

    monkeypatch.setattr(Publisher, "_push", compete)
    landed = left.graduate(left_intent, semantic)
    assert landed.command.publication == PublicationOutcome.VERIFIED
    assert landed.issue is not None and landed.issue.number == 2
    assert [number for number, _, _ in choices] == [1, 2]
    assert choices[0][1] != choices[1][1]
    assert choices[0][2] != choices[1][2]
    assert "refine" not in read_graph(repo, repo.tip()).stories[1].estimates
    assert read_graph(repo, repo.tip()).stories[2].estimates["refine"].agent_hours == 1
    assert left.graduate(left_intent, semantic).issue == landed.issue
    assert cli(repo.root, "graduate", "resume", "left-intent")["issue"] == 2
    assert cli(repo.root, "graduate", "--draft", left_draft.identity)["issue"] == 2

    third = create_draft(installation, "Lost acknowledgement")
    origin_path = story_event_path(1)
    original = repo.read_blobs(repo.tip().tree, (origin_path,))[origin_path]
    git(topology.planning, "pull", "--ff-only", "-q")
    topology.advance_planning(origin_path, with_attempt(original, 1))
    request = service.prepare_draft(third.identity, "third", target)
    request = request.model_copy(
        update={"finalization": FrozenFinalization.from_intent(semantic)}
    )
    before_attempt = repo.tip()
    blocked_calls = []

    def unexpected_push(*_args):
        pytest.fail("Refused graduation attempted shared publication")

    with monkeypatch.context() as patch:
        patch.setattr(Publisher, "_push", unexpected_push)
        unavailable = LocalBacklog(replace(service, registry=registry)).graduate(
            request, semantic
        )
        denied_service = replace(
            service,
            registry=registry,
            ports=graduation_preflight(blocked_calls, PreflightOutcome.BLOCKED),
        )
        denied = LocalBacklog(denied_service).graduate(request, semantic)
    assert unavailable.issue is None and denied.issue is None
    assert blocked_calls
    assert repo.tip() == before_attempt
    assert git(remote, "rev-parse", PLANNING) == before_attempt.revision
    preflight_calls = []
    lost_ack_service = replace(
        service, registry=registry, ports=graduation_preflight(preflight_calls)
    )

    def lost_ack(publisher, revision, expected):
        monkeypatch.setattr(Publisher, "_push", push)
        push(publisher, revision, expected)
        raise OSError("Lost response after accepted push")

    monkeypatch.setattr(Publisher, "_push", lost_ack)
    third_result = LocalBacklog(lost_ack_service).graduate(request, semantic)
    assert third_result.issue is not None and third_result.issue.number == 3
    assert preflight_calls == [choices[-1][2]]
    assert read_graph(repo, repo.tip()).stories[3].estimates["refine"].agent_hours == 1
    assert cli(repo.root, "graduate", "resume", "third")["issue"] == 3

    action = LocalBacklog(service).project_latest(
        PublishedStory(issue=third_result.issue, planning_commit=repo.tip().revision),
        ActionKey(operation_id="third", action_id="project-backlog"),
    )
    assert action.status == "completed"
    assert cli(repo.root, "graduate", "resume", "third")["pending"] == []

    offline = create_draft(installation, "Offline")
    request = service.prepare_draft(offline.identity, "offline", target)
    before = repo.tip()
    git(repo.root, "remote", "set-url", PLANNING_REMOTE, str(tmp_path / "not-found"))
    try:
        result = LocalBacklog(service).graduate(request, ordinary_finalization())
        assert result.issue is None
        assert result.command.publication == PublicationOutcome.PENDING
        assert result.command.local in {LocalOutcome.UNAVAILABLE, LocalOutcome.CONFLICT}
        assert repo.tip() == before
    finally:
        git(repo.root, "remote", "set-url", PLANNING_REMOTE, str(remote))
    assert (
        git(repo.root, "for-each-ref", "--format=%(refname)", "refs/heads")
        == "refs/heads/records\nrefs/heads/trunk"
    )


def test_local_only_graduation_is_one_planning_commit(repository, policy_inputs):
    root = repository
    profile = Path(policy_inputs[-1]).with_name("graduation-workflow.toml")
    profile.write_text(PROFILE.replace('"plan"', '"backlog"'))
    _, proposal = init(
        root,
        "--local",
        "--default-branch",
        "trunk",
        "--planning-branch",
        "project/records",
        *policy_inputs[:-1],
        str(profile),
    )
    assert proposal["publication"] == "pending"
    git(root, "add", ".aitm.toml", "aitm-workflow.toml", ".gitignore")
    git(root, "commit", "-qm", "Land local policy")
    assert init(root)[1]["local"] == "completed"
    installation, _ = _active_installation(Repository(root, RECORDS))
    repo = installation.repository
    policy = preflight_policy(installation).policy
    assert policy is not None
    created = Intake(
        installation,
        repo.tip(),
        policy.source.digest,
        OWNER,
        datetime(2026, 11, 27, tzinfo=UTC),
    ).create_draft(CreateEntity("Local epic", "Original local body\n"))
    assert created.command.publication == PublicationOutcome.NOT_APPLICABLE
    before = repo.tip()
    head = cli(repo.root, "graduate", "--draft", created.identity, "--kind", "epic")
    assert head["issue"] == 1
    assert head["publication"] == PublicationOutcome.NOT_APPLICABLE
    after = repo.tip()
    assert git(repo.root, "rev-parse", f"{after.revision}^") == before.revision
    moved = ".aitm/stories/000/1/draft.md"
    event = story_event_path(1)
    bodies = repo.read_blobs(after.tree, (created.document, moved, event))
    assert bodies[created.document] is None
    assert (
        bodies[moved]
        == repo.read_blobs(before.tree, (created.document,))[created.document]
    )
    facts = loads(bodies[event].splitlines()[0])["data"]
    assert facts["kind"] == "epic"
    assert facts["initial_state"]["state_id"] == "backlog"
    assert facts["delivery_target"]["ref"] == DEFAULT
    assert cli(repo.root, "graduate", "--draft", created.identity)["issue"] == 1
    assert cli(repo.root, "graduate", "resume", head["operation_id"])["issue"] == 1
    assert repo.tip() == after

    origin = story_event_path(1)
    baseline = repo.read_blobs(after.tree, (origin,))[origin]
    attempt_tip = repo.create_commit(
        after, {origin: with_attempt(baseline, 1)}, "fixture attempt"
    )
    repo._git("update-ref", repo.ref, attempt_tip.revision, after.revision)
    second = Intake(
        installation,
        repo.tip(),
        policy.source.digest,
        OWNER,
        datetime(2026, 11, 27, tzinfo=UTC),
    ).create_draft(CreateEntity("Local attempt preflight", "Original local body\n"))
    assert second.command.publication == PublicationOutcome.NOT_APPLICABLE
    service = GraduationService(installation, OWNER)
    request = service.prepare_draft(
        second.identity,
        "local-preflight",
        DeliveryTarget(repository=installation.code_repository, ref=DEFAULT),
    )
    pin = repo.tip()
    blocked_calls = []
    denied_service = replace(
        service, ports=graduation_preflight(blocked_calls, PreflightOutcome.BLOCKED)
    )
    for graduation_service in (service, denied_service):
        result = LocalBacklog(graduation_service).graduate(
            request, ordinary_finalization()
        )
        assert result.issue is None
        assert repo.tip() == pin
    assert blocked_calls
    passed_calls = []
    ready = replace(service, ports=graduation_preflight(passed_calls))
    result = LocalBacklog(ready).graduate(request, ordinary_finalization())
    assert result.issue is not None and result.issue.number == 2
    assert len(passed_calls) == 1
    assert repo.parent(repo.tip()) == pin.revision
