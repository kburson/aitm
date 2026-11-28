"""Exercise issuer ordering and closed-origin custody against authoritative Git."""

from dataclasses import replace
from datetime import UTC, datetime
from json import dumps, loads

import pytest

from aitm_core.models.attempts import AttemptClosed, ClockChanged
from aitm_core.models.common import LocalOutcome, PublicationOutcome
from aitm_core.models.operations import (
    AuthorityOrigin,
    OperationOwner,
    PreflightOutcome,
    PreflightResult,
    story_event_path,
)
from aitm_core.providers.identity import (
    DispatchClaim,
    IdentityAuthority,
    IdentityConflict,
)
from aitm_core.relationships import EventContext, read_graph
from aitm_core.rules.expansion import _append, expand, reconcile_stopped_expansion
from aitm_core.services import ServicePorts, expansion_graduation
from aitm_core.store.publication import Publisher
from tests.integration.test_c08 import PLANNING, git
from tests.integration.test_c08 import topology as topology
from tests.integration.test_c09 import cloned
from tests.integration.test_c20 import Issuer
from tests.integration.test_c22 import (
    OWNER,
    create_draft,
    install_profile,
    with_attempt,
)
from tests.unit.test_c15 import graduated


def expansion_fixture(topology):
    install_profile(topology)
    installation = topology.policy.installation
    topology.advance_planning(story_event_path(16), with_attempt(graduated(), 16))
    draft = create_draft(installation, "Retain expansion custody across stop")
    owner = OperationOwner(actor=OWNER.actor, binding="fixture-binding", generation=1)
    service = expansion_graduation(
        installation,
        owner,
        ServicePorts(
            attempt_preflight=lambda _: PreflightResult(
                outcome=PreflightOutcome.PASSED,
                origin=AuthorityOrigin.FIXTURE,
            )
        ),
    )
    return service, draft


def close_origin(topology, service, number=16):
    repository = service.installation.repository
    graph = read_graph(repository, repository.tip())
    origin = graph.states[number]
    attempt = origin.domains["attempts"].attempts["fixture-attempt"]
    assert not attempt.closed and attempt.clock_mode == "expansion-paused"
    now = datetime.now(UTC)
    context = EventContext(
        f"fixture-c595-stop-{number}", service.owner, now.isoformat(), "a" * 64
    )
    closure = AttemptClosed(
        attempt="fixture-attempt",
        generation=1,
        from_clock="expansion-paused",
        disposition="trip",
        reason="Fixture published stop",
    )
    clock = ClockChanged(
        attempt="fixture-attempt",
        generation=1,
        cause_event_id=f"fixture-c595-stop-{number}:stop:{number}",
        **{"from": "expansion-paused", "to": "terminal-closed"},
        observed_at=now,
        used_millis=attempt.used_millis,
    )
    event_path = story_event_path(number)
    appended = _append(
        context,
        origin,
        graph.logs[event_path],
        (
            ("core.attempt.closed", closure, "stop"),
            ("core.attempt.clock.changed", clock, "clock"),
        ),
    )
    git(topology.planning, "pull", "-q", "--ff-only", "origin", PLANNING)
    return topology.advance_planning(
        event_path,
        graph.logs[event_path] + b"".join(row + b"\n" for row in appended.records),
    )


def test_stop_before_claim_cannot_send_or_publish_claim(topology, tmp_path, monkeypatch):
    service, draft = expansion_fixture(topology)
    repository = service.installation.repository
    provider = Issuer(service.installation.issuer)
    authority = IdentityAuthority(service.installation, provider)
    write = IdentityAuthority._write
    stopped = []

    push = Publisher._push

    def stop_then_write(issuer, view, destination, *args, **kwargs):
        if not destination.endswith("/claim-1.json"):
            return write(issuer, view, destination, *args, **kwargs)

        def stop_before_push(publisher, candidate, expected):
            if not stopped:
                staged = repository.read_tree(candidate)
                assert repository.read_blobs(staged.tree, (destination,))[destination]
                stopped.append((close_origin(topology, service), destination))
            return push(publisher, candidate, expected)

        with monkeypatch.context() as patch:
            patch.setattr(Publisher, "_push", stop_before_push)
            return write(issuer, view, destination, *args, **kwargs)

    monkeypatch.setattr(IdentityAuthority, "_write", stop_then_write)
    outcome = expand(
        service, 16, draft.identity, "defect", "Fixture request", external=authority
    )
    assert outcome.issue is None and outcome.command.local != LocalOutcome.COMPLETED
    assert not provider.sent
    ((stop, claim),) = stopped
    pinned = repository.read_tree(stop)
    assert repository.read_blobs(pinned.tree, (claim,))[claim] is None
    latest = service.snapshot(service.policy())
    repository._git("merge-base", "--is-ancestor", stop, latest.revision)
    assert repository.read_blobs(latest.tree, (claim,))[claim] is None
    state = read_graph(repository, latest).states[16]
    first_reservation = (
        state.domains["evidence"].facts["core.expansion.reserved"][0].payload
    )
    unknown = reconcile_stopped_expansion(
        service, 16, first_reservation.reservation, external=authority
    )
    assert unknown.command.local == LocalOutcome.UNAVAILABLE
    assert unknown.command.publication == PublicationOutcome.PENDING
    state = read_graph(repository, service.snapshot(service.policy())).states[16]
    assert not state.domains["evidence"].facts.get("core.expansion.custody-recorded")

    second = loads(graduated())
    second["story"] = 17
    snapshot = service.snapshot(service.policy())
    repository._git("merge-base", "--is-ancestor", stop, snapshot.revision)
    git(topology.planning, "pull", "-q", "--ff-only", "origin", PLANNING)
    topology.advance_planning(
        story_event_path(17), with_attempt(dumps(second).encode() + b"\n", 17)
    )
    other = cloned(topology, tmp_path).policy.installation
    service = replace(service, installation=other)
    repository = other.repository
    authority = IdentityAuthority(other, provider)
    another = create_draft(other, "Stop after a claim but before send")
    stopped.clear()

    def write_then_stop(issuer, view, destination, *args, **kwargs):
        result = write(issuer, view, destination, *args, **kwargs)
        if destination.endswith("/claim-1.json"):
            assert result
            stopped.append((close_origin(topology, service, 17), destination))
        return result

    monkeypatch.setattr(IdentityAuthority, "_write", write_then_stop)
    outcome = expand(
        service, 17, another.identity, "defect", "Second fixture", external=authority
    )
    assert (
        outcome.issue is None
        and outcome.command.publication == PublicationOutcome.PENDING
    )
    assert not provider.sent
    ((stop, claim),) = stopped
    pinned = repository.read_tree(stop)
    record = DispatchClaim.model_validate_json(
        repository.read_blobs(pinned.tree, (claim,))[claim]
    )
    assert record.origin_digest


def test_lost_reply_reconciles_exact_issue_on_closed_origin(topology):
    service, draft = expansion_fixture(topology)
    repository = service.installation.repository
    provider = Issuer(service.installation.issuer)
    provider.lose_reply = True
    authority = IdentityAuthority(service.installation, provider)
    pending = expand(
        service, 16, draft.identity, "defect", "Fixture request", external=authority
    )
    assert (
        pending.issue is None
        and pending.command.publication == PublicationOutcome.PENDING
    )
    close_origin(topology, service)
    restarted = IdentityAuthority(service.installation, provider)
    state = read_graph(repository, service.snapshot(service.policy())).states[16]
    reservation = state.domains["evidence"].facts["core.expansion.reserved"][0].payload
    wrong = replace(service, owner=service.owner.model_copy(update={"generation": 2}))
    with pytest.raises(IdentityConflict, match="authorized reservation holder"):
        reconcile_stopped_expansion(
            wrong, 16, reservation.reservation, external=restarted
        )
    first = reconcile_stopped_expansion(
        service, 16, reservation.reservation, external=restarted
    )
    assert first.command.local == LocalOutcome.COMPLETED, first.reason
    assert first.command.publication == PublicationOutcome.VERIFIED
    second = reconcile_stopped_expansion(
        service, 16, reservation.reservation, external=restarted
    )
    assert second.command.local == LocalOutcome.COMPLETED
    assert len(provider.sent) == 1
    graph_snapshot = service.snapshot(service.policy())
    graph = read_graph(repository, graph_snapshot)
    state = graph.states[16]
    (row,) = state.domains["evidence"].facts["core.expansion.custody-recorded"]
    assert row.payload.issue == 42
    assert (
        set(graph.stories) == {16} and graph.stories[16].relationships.blocked_by == ()
    )
    assert (
        state.domains["attempts"].attempts["fixture-attempt"].clock_mode
        == "terminal-closed"
    )
    assert repository.read_blobs(graph_snapshot.tree, (draft.document,))[draft.document]
