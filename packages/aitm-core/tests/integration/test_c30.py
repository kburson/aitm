"""Exercise expansion's reservation and child CAS against authoritative Git."""

from dataclasses import replace
from datetime import UTC, datetime
from json import dumps, loads
from pathlib import Path

import pytest

from aitm_core.cli.expand import handle
from aitm_core.drafts import CreateEntity, Intake
from aitm_core.graduation import (
    FinalizerRegistry,
    GraduationConflict,
    GraduationService,
    completed_record,
)
from aitm_core.models.binding import StoryRef
from aitm_core.models.common import LocalOutcome, PublicationOutcome
from aitm_core.models.config import DeliveryTarget
from aitm_core.models.lifecycle import StateChange, WorkflowEdge, WorkflowObservation
from aitm_core.models.operations import (
    AuthorityOrigin,
    OperationCategory,
    OperationOwner,
    PreflightOutcome,
    PreflightResult,
    story_event_path,
)
from aitm_core.providers.backlog import GraduationIntent
from aitm_core.providers.identity import IdentityAuthority
from aitm_core.providers.local import LocalBacklog
from aitm_core.relationships import EventContext, read_graph
from aitm_core.rules.expansion import expand, resolve_expansion
from aitm_core.services import ServicePorts, expansion_graduation, preflight_policy
from aitm_core.setup.init import _active_installation
from aitm_core.store.objects import Repository
from aitm_core.store.publication import Publisher
from aitm_core.store.workspace import Workspace
from tests.integration.test_c08 import DEFAULT, PLANNING, git
from tests.integration.test_c08 import topology as topology
from tests.integration.test_c09 import cloned
from tests.integration.test_c11 import RECORDS, init
from tests.integration.test_c11 import policy_inputs as policy_inputs
from tests.integration.test_c11 import repository as repository
from tests.integration.test_c16 import cli
from tests.integration.test_c20 import Issuer
from tests.integration.test_c22 import (
    OWNER,
    PROFILE,
    STAMP,
    create_draft,
    install_profile,
    with_attempt,
)
from tests.unit.test_c15 import graduated


def test_expansion_gap_and_production_finalizer_registration(
    topology, tmp_path, monkeypatch
):
    install_profile(topology)
    installation = topology.policy.installation
    repository = installation.repository
    origin = 16
    topology.advance_planning(
        story_event_path(origin), with_attempt(graduated(), origin)
    )
    draft = create_draft(installation, "Split out the blocking work")
    origin_owner = OperationOwner(
        actor=OWNER.actor, binding="fixture-binding", generation=1
    )
    preflight = []

    def permit(context):
        assert context.operation.category == OperationCategory.NORMAL
        preflight.append(context.operation.intent.kind)
        return PreflightResult(
            outcome=PreflightOutcome.PASSED, origin=AuthorityOrigin.FIXTURE
        )

    service = expansion_graduation(
        installation, origin_owner, ServicePorts(attempt_preflight=permit)
    )
    before = repository.tip()
    unregistered = replace(service, registry=FinalizerRegistry())
    missing = expand(unregistered, origin, draft.identity, "defect", "Unregistered")
    assert missing.command.local == LocalOutcome.UNAVAILABLE
    assert missing.issue is None and repository.tip() == before
    absent = replace(service, ports=ServicePorts())
    missing = expand(absent, origin, draft.identity, "defect", "Unavailable")
    assert missing.command.local == LocalOutcome.UNAVAILABLE
    assert missing.issue is None and repository.tip() == before

    competing_draft = create_draft(installation, "Concurrent ordinary story")
    other = cloned(topology, tmp_path).policy.installation
    competitor = LocalBacklog(GraduationService(other, OWNER, ports=service.ports))
    competition = competitor.service.prepare_draft(
        competing_draft.identity,
        "competing-graduation",
        DeliveryTarget(repository=other.code_repository, ref=DEFAULT),
    )
    finish = LocalBacklog.graduate
    push = Publisher._push
    attempts = []

    def lose_ack(publisher, revision, expected):
        attempts.append(revision)
        monkeypatch.setattr(Publisher, "_push", push)
        push(publisher, revision, expected)
        raise OSError("Lost response after accepted expansion push")

    def compete(publisher, revision, expected):
        from aitm_core.graduation import ordinary_finalization

        attempts.append(revision)
        monkeypatch.setattr(Publisher, "_push", push)
        winner = finish(competitor, competition, ordinary_finalization())
        assert winner.issue is not None and winner.issue.number == 17
        graph = read_graph(other.repository, other.repository.tip())
        assert (
            graph.states[origin]
            .domains["attempts"]
            .attempts["fixture-attempt"]
            .clock_mode
            == "expansion-paused"
        )
        monkeypatch.setattr(Publisher, "_push", lose_ack)
        push(publisher, revision, expected)

    def observe_gap(backlog, intent, finalization):
        state = read_graph(repository, repository.tip())
        assert set(state.stories) == {origin}
        active = state.states[origin].domains["attempts"].attempts["fixture-attempt"]
        assert active.clock_mode == "expansion-paused"
        assert state.states[origin].domains["evidence"].facts["core.expansion.reserved"]
        monkeypatch.setattr(Publisher, "_push", compete)
        return finish(backlog, intent, finalization)

    monkeypatch.setattr(LocalBacklog, "graduate", observe_gap)
    result = expand(
        service, origin, draft.identity, "defect", "Fix an implementation blocker"
    )
    assert result.command.local == LocalOutcome.COMPLETED, result.reason
    assert result.command.publication == PublicationOutcome.VERIFIED
    assert result.issue is not None and result.issue.number == 18
    graph = read_graph(repository, repository.tip())
    assert graph.stories[origin].relationships.blocked_by == (18,)
    assert graph.stories[18].relationships.blocking == (origin,)
    assert graph.stories[18].workflow_state.state_id == "backlog"
    assert (
        graph.states[origin].domains["attempts"].attempts["fixture-attempt"].clock_mode
        == "expansion-paused"
    )
    assert {"expand", "core.graduated"} <= set(preflight)
    assert len(attempts) == 2
    reserved = (
        graph.states[origin]
        .domains["evidence"]
        .facts["core.expansion.reserved"][0]
        .payload
    )
    intent = GraduationIntent.model_validate_json(reserved.intent)
    completed = completed_record(repository, repository.tip(), intent.source)
    assert completed.intent == intent and completed.issue.number == 18
    assert repository.tip().revision == attempts[-1]
    same = expand(
        service, origin, draft.identity, "defect", "Fix an implementation blocker"
    )
    assert same.issue == result.issue
    assert repository.tip().revision == attempts[-1]
    second = expand(
        service, origin, competing_draft.identity, "story", "A second request"
    )
    assert second.command.local == LocalOutcome.REFUSED
    assert preflight[-1] == "expand"
    unresolved = resolve_expansion(service, origin, reserved.reservation, child=18)
    assert unresolved.command.local == LocalOutcome.REFUSED

    child = graph.stories[18]
    current = child.workflow_state
    terminal = WorkflowObservation(
        workflow_id=current.workflow_id,
        revision=current.revision,
        state_id="done",
        label="Done",
        terminal=True,
    )
    terminal_fact = StateChange(
        **{"from": current, "to": terminal},
        edge=WorkflowEdge(
            id="terminal",
            workflow_id=current.workflow_id,
            revision=current.revision,
            source=current.state_id,
            target=terminal.state_id,
            kind="terminal",
        ),
        mode="enforce",
        reason="Explicit disposition",
        disposition="abandoned",
    )
    child_path = story_event_path(18)
    context = EventContext("fixture-child-disposition", OWNER, STAMP, "a" * 64)
    raw = (
        graph.logs[child_path]
        + context.encode(
            18, "core.state.changed", graph.states[18], terminal_fact, "terminal"
        )
        + b"\n"
    )
    git(topology.planning, "pull", "-q", "--ff-only", "origin", PLANNING)
    disposition = topology.advance_planning(child_path, raw)
    resolved = resolve_expansion(service, origin, reserved.reservation, child=18)
    assert resolved.command.publication == PublicationOutcome.VERIFIED
    assert repository.parent(repository.tip()) == disposition
    graph = read_graph(repository, repository.tip())
    assert graph.stories[origin].relationships.blocked_by == ()
    assert graph.stories[18].relationships.blocking == ()
    assert (
        graph.states[origin].domains["attempts"].attempts["fixture-attempt"].clock_mode
        == "active"
    )


def test_installed_local_expansion_fences_proposed_child_on_no_issuance(
    repository, policy_inputs, monkeypatch
):
    root = repository
    profile = Path(policy_inputs[-1]).with_name("expansion-workflow.toml")
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
    origin_path = story_event_path(16)
    initial = repo.tip()
    seeded = repo.create_commit(
        initial, {origin_path: with_attempt(graduated(), 16)}, "fixture origin"
    )
    repo._git("update-ref", repo.ref, seeded.revision, initial.revision)
    policy = preflight_policy(installation).policy
    assert policy is not None
    draft = Intake(
        installation,
        repo.tip(),
        policy.source.digest,
        OWNER,
        datetime(2026, 11, 27, tzinfo=UTC),
    ).create_draft(
        CreateEntity("Cancel a provisional child", "Retain the local draft.")
    )
    binding = cli(root, "bind", "16", "--session", "writer")
    assert binding["local"] == "completed"
    workspace = Workspace(installation)
    with workspace.lock():
        lease = workspace.lookup(StoryRef(story=16))
        assert lease.identity == loads(binding["evidence"][0])["identity"]
        workspace.persist(lease.model_copy(update={"identity": "fixture-binding"}))
    owner = OperationOwner(actor=OWNER.actor, binding="fixture-binding", generation=1)
    ports = ServicePorts(
        attempt_preflight=lambda _context: PreflightResult(
            outcome=PreflightOutcome.PASSED, origin=AuthorityOrigin.FIXTURE
        )
    )
    service = expansion_graduation(installation, owner, ports)
    monkeypatch.chdir(root)
    args = (
        "16",
        "--kind",
        "story",
        "--draft",
        draft.identity,
        "--reason",
        "Resolve a blocker",
        "--binding",
        "fixture-binding",
        "--generation",
        "1",
        "--session",
        "writer",
    )
    pin = repo.tip()
    assert handle(("expand",), args).local == LocalOutcome.UNAVAILABLE
    assert repo.tip() == pin

    build = GraduationService.build

    def fail_construction(*_args, **_kwargs):
        raise GraduationConflict("Induced construction refusal")

    with monkeypatch.context() as patch:
        patch.setattr(GraduationService, "build", fail_construction)
        assert handle(("expand",), args, ports=ports).local == LocalOutcome.CONFLICT
    graph = read_graph(repo, repo.tip())
    assert set(graph.stories) == {16}
    reserved = (
        graph.states[16].domains["evidence"].facts["core.expansion.reserved"][0].payload
    )
    intent = GraduationIntent.model_validate_json(reserved.intent)
    assert completed_record(repo, repo.tip(), intent.source) is None
    service = replace(service, stamp=datetime.now(UTC).isoformat())
    result = resolve_expansion(service, 16, reserved.reservation)
    assert result.command.local == LocalOutcome.COMPLETED, result.reason
    assert result.command.publication == PublicationOutcome.NOT_APPLICABLE
    assert (
        read_graph(repo, repo.tip())
        .states[16]
        .domains["attempts"]
        .attempts["fixture-attempt"]
        .clock_mode
        == "active"
    )
    assert repo.read_blobs(repo.tip().tree, (draft.document,))[draft.document]
    assert GraduationService.build is build
    with pytest.raises(GraduationConflict, match="no longer pending"):
        LocalBacklog(service).graduate(intent, intent.finalization.to_intent())
    assert set(read_graph(repo, repo.tip()).stories) == {16}
    assert handle(("expand",), args, ports=ports).local == LocalOutcome.REFUSED

    another_origin = 17
    initial = loads(graduated())
    initial["story"] = another_origin
    pin = repo.tip()
    active = with_attempt(dumps(initial).encode() + b"\n", another_origin)
    seeded = repo.create_commit(
        pin, {story_event_path(another_origin): active}, "another local attempt"
    )
    repo._git("update-ref", repo.ref, seeded.revision, pin.revision)
    another_draft = Intake(
        installation,
        repo.tip(),
        policy.source.digest,
        OWNER,
        datetime(2026, 11, 27, tzinfo=UTC),
    ).create_draft(
        CreateEntity("Allocate a verified local child", "Reach the local authority.")
    )
    service = expansion_graduation(installation, owner, ports)
    finalized = expand(
        service, another_origin, another_draft.identity, "story", "Local allocation"
    )
    assert finalized.command.local == LocalOutcome.COMPLETED
    assert finalized.command.publication == PublicationOutcome.NOT_APPLICABLE
    assert finalized.issue is not None and finalized.issue.number == 18
    final_graph = read_graph(repo, repo.tip())
    assert final_graph.stories[another_origin].relationships.blocked_by == (18,)
    assert final_graph.stories[18].relationships.blocking == (another_origin,)
    pending = read_graph(repo, repo.read_tree(repo.parent(repo.tip())))
    assert 18 not in pending.stories
    attempt = (
        pending.states[another_origin].domains["attempts"].attempts["fixture-attempt"]
    )
    assert attempt.clock_mode == "expansion-paused"


def test_external_expansion_keeps_pause_through_lost_issuance_response(topology):
    install_profile(topology)
    installation = topology.policy.installation
    repo = installation.repository
    origin = story_event_path(16)
    topology.advance_planning(origin, with_attempt(graduated(), 16))
    draft = create_draft(installation, "External expansion source")
    owner = OperationOwner(actor=OWNER.actor, binding="fixture-binding", generation=1)
    ports = ServicePorts(
        attempt_preflight=lambda context: PreflightResult(
            outcome=PreflightOutcome.PASSED, origin=AuthorityOrigin.FIXTURE
        )
    )
    service = expansion_graduation(installation, owner, ports)
    issuer = Issuer(installation.issuer)
    issuer.lose_reply = True
    authority = IdentityAuthority(installation, issuer)
    args = (service, 16, draft.identity, "defect", "External issue creation")
    pending = expand(*args, external=authority)
    assert pending.issue is None
    assert pending.command.publication == PublicationOutcome.PENDING
    graph = read_graph(repo, repo.tip())
    assert set(graph.stories) == {16}
    assert (
        graph.states[16].domains["attempts"].attempts["fixture-attempt"].clock_mode
        == "expansion-paused"
    )
    reserved = (
        graph.states[16].domains["evidence"].facts["core.expansion.reserved"][0].payload
    )
    current = repo.tip()
    refused = resolve_expansion(service, 16, reserved.reservation)
    assert refused.command.local == LocalOutcome.REFUSED
    assert repo.tip() == current
    issuer.lose_reply = False
    finished = expand(*args, external=authority)
    assert finished.issue is not None and finished.issue.number == 42
    assert finished.command.publication == PublicationOutcome.VERIFIED
    assert len(issuer.sent) == 1
    graph = read_graph(repo, repo.tip())
    assert graph.stories[16].relationships.blocked_by == (42,)
    assert graph.stories[42].relationships.blocking == (16,)
    assert (
        graph.states[16].domains["attempts"].attempts["fixture-attempt"].clock_mode
        == "expansion-paused"
    )
