"""The bounded Split operation reuses one pinned planning transaction."""

from dataclasses import replace
from hashlib import sha256
from json import dumps, loads

import pytest

from aitm_core.events import core_reducers, fold
from aitm_core.machine.profile import WorkflowProfile
from aitm_core.models.common import LocalOutcome
from aitm_core.models.events import EventEnvelope
from aitm_core.models.operations import AuthorityOrigin, WriteAuthorization
from aitm_core.services import ServicePorts
from aitm_core.splitting import SplitRequest, rework_design, split_leaf
from aitm_core.store.memory_backend import MemoryBackend
from tests.unit.test_c28_transitions import NOW, PATH
from tests.unit.test_c28_transitions import context as context
from tests.unit.test_c91 import document


def seeded(context, *, initial="refine", kind="story", hours=5.0, children=()):
    raw = document()
    raw["states"][3]["action"] = []
    raw["edges"].pop(1)
    raw["states"].insert(1, {"id": "refine", "label": "Shape scope"})
    raw["states"][0]["label"] = "Aggregate Design"
    profile = WorkflowProfile.model_validate(raw)
    initial_record = loads(
        context.backend.read(context.backend.snapshot(), (PATH,))[PATH]
    )
    initial_record["data"]["initial_state"].update(
        state_id=initial,
        label=next(state.label for state in profile.states if state.id == initial),
    )
    initial_record["data"]["kind"] = kind
    stream = dumps(initial_record).encode() + b"\n"
    events = [
        (
            "core.description.set",
            {
                "title": "Preserve numbered work",
                "as": "operator",
                "want": "clear scope",
                "so_that": "work can be divided",
                "scope": "Original",
                "content_hash": "a" * 64,
            },
        ),
        (
            "core.estimate.set",
            {"phase": "refine", "agent_hours": hours, "size": "M", "priority": "P1"},
        ),
        (
            "core.doc.accepted",
            {
                "role": "design",
                "path": ".aitm/stories/000/1/design/current.md",
                "canonical_version": "aitm.authored-content/v1",
                "canonical_digest": "a" * 64,
                "raw_digest": "a" * 64,
                "review_refs": ["current"],
                "levels": ["xpr"],
                "policy_digest": context.policy_digest,
                "source_planning_sha": "a" * 40,
                "plan_generation": 1,
            },
        ),
    ]
    if children:
        empty = {"parent": None, "children": [], "blocked_by": [], "blocking": []}
        events.append(
            (
                "core.link.changed",
                {"before": empty, "after": empty | {"children": children}},
            )
        )
    for n, (event, data) in enumerate(events, start=2):
        stream += (
            EventEnvelope(
                v=1,
                id=f"seed:{n}",
                ts=NOW,
                type=event,
                story=1,
                actor=context.owner.actor,
                operation_id=f"seed:{n}",
                sequence=n,
                prior_log_digest=sha256(stream).hexdigest(),
                data=data,
            )
            .model_dump_json(exclude_none=True)
            .encode()
            + b"\n"
        )
    ports = ServicePorts(
        write_authorization=lambda owner, change: WriteAuthorization(
            allowed=True, origin=AuthorityOrigin.REGISTERED
        )
    )
    return replace(
        context, backend=MemoryBackend({PATH: stream}, ports=ports), profile=profile
    )


def replay(request):
    store = request.backend
    raw = store.read(store.snapshot(), (PATH,))[PATH]
    return fold(raw.splitlines(keepends=True), core_reducers()).domains["lifecycle"]


@pytest.mark.parametrize("kind", ["story", "defect", "spike"])
def test_split_preserves_identity_and_invalidates_acceptance_in_one_transaction(
    context, kind
):
    request = seeded(context, kind=kind)
    first = request.backend.snapshot()
    answer = split_leaf(SplitRequest(request, "Aggregate scope", "Oversized", 4))
    assert answer.command.local == LocalOutcome.COMPLETED, answer.reason
    assert answer.snapshot != first
    story = replay(request)
    assert story.story_id == 1 and story.kind == "epic"
    assert story.description.scope == "Aggregate scope"
    assert story.workflow_state.state_id == "design"
    assert story.workflow_state.label == "Aggregate Design"
    assert story.split.invalidated_acceptances == ("a" * 64,)
    assert story.split.invalidated_estimates == ("refine",)
    assert not story.accepted_documents and not story.estimates and story.jit is None


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"hours": 4.0}, "oversized"),
        ({"initial": "plan"}, "Refine"),
        ({"children": [2]}, "children"),
        ({"kind": "epic"}, "leaf"),
    ],
)
def test_split_refusals_leave_the_pinned_tree_unchanged(context, changes, reason):
    request = seeded(context, **changes)
    first = request.backend.snapshot()
    answer = split_leaf(SplitRequest(request, "Aggregate scope", "Oversized", 4))
    assert answer.command.local == LocalOutcome.REFUSED, answer.reason
    assert reason in answer.reason
    assert request.backend.snapshot() == first


def test_plan_rework_invalidate_typed_facts_before_returning_to_design(context):
    request = seeded(context, initial="plan")
    answer = rework_design(replace(request, target="design", reason="New scope"))
    assert answer.command.local == LocalOutcome.COMPLETED, answer.reason
    story = replay(request)
    assert story.workflow_state.state_id == "design" and story.kind == "story"
    assert not story.accepted_documents and not story.estimates
    assert story.jit is None and story.split is None


def append_events(raw, owner, story, operation, rows):
    count = len(raw.splitlines())
    for index, (name, data) in enumerate(rows, 1):
        raw += (
            EventEnvelope(
                v=1,
                id=f"{operation}:{index}",
                ts=NOW,
                type=name,
                story=story,
                actor=owner.actor,
                operation_id=operation,
                sequence=count + index,
                prior_log_digest=sha256(raw).hexdigest(),
                data=data,
            )
            .model_dump_json(exclude_none=True)
            .encode()
            + b"\n"
        )
    return raw


def with_history(request, raw, **related):
    authorizer = ServicePorts(
        write_authorization=lambda owner, change: WriteAuthorization(
            allowed=True,
            origin=AuthorityOrigin.REGISTERED,
        )
    )
    return replace(
        request, backend=MemoryBackend({PATH: raw, **related}, ports=authorizer)
    )


@pytest.mark.parametrize(
    "hazard", ["attempt", "unresolved-identity", "expansion-child"]
)
def test_preimplementation_fences_refuse_split(context, hazard):
    request = seeded(context)
    raw = request.backend.read(request.backend.snapshot(), (PATH,))[PATH]
    related = {}
    if hazard == "attempt":
        operation = "started"
        evidence = [
            (
                "core.attempt.started",
                {
                    "attempt": "prior",
                    "generation": 1,
                    "plan_generation": None,
                    "source": None,
                    "binding": None,
                    "allowance_millis": 1000,
                    "provisional": True,
                },
            ),
            (
                "core.attempt.clock.changed",
                {
                    "attempt": "prior",
                    "generation": 1,
                    "cause_event_id": "started:1",
                    "from": None,
                    "to": "active",
                    "observed_at": NOW,
                    "used_millis": 0,
                },
            ),
        ]
        expected = "attempt"
    elif hazard == "unresolved-identity":
        current = replay(request).workflow_state.model_dump(mode="json")
        operation = "pending"
        evidence = [
            (
                "core.action.pending",
                {
                    "origin_operation": operation,
                    "owner": "core",
                    "action_id": "core.identity.lookup",
                    "target_version": 1,
                    "owner_version": "1",
                    "attempt": None,
                    "workflow": current,
                },
            )
        ]
        expected = "unresolved"
    else:
        initial = loads(raw.splitlines()[0])
        initial["story"] = 2
        parent = dumps(initial).encode() + b"\n"
        base = {"parent": None, "children": [], "blocked_by": [], "blocking": []}
        parent = append_events(
            parent,
            request.owner,
            2,
            "parent-link",
            [
                (
                    "core.link.changed",
                    {"before": base, "after": base | {"children": [1]}},
                ),
                (
                    "core.expansion.recorded",
                    {
                        "attempt": "parent-attempt",
                        "generation": 1,
                        "reservation": "x",
                        "child": 1,
                        "kind": "story",
                        "reason": "required expansion",
                    },
                ),
            ],
        )
        related[".aitm/stories/000/2/events.jsonl"] = parent
        operation = "child-link"
        evidence = [
            ("core.link.changed", {"before": base, "after": base | {"parent": 2}})
        ]
        expected = "expansion child"
    mutated = with_history(
        request, append_events(raw, request.owner, 1, operation, evidence), **related
    )
    before = mutated.backend.snapshot()
    result = split_leaf(SplitRequest(mutated, "Expanded aggregate", "Oversized", 4))
    assert result.command.local == LocalOutcome.REFUSED, result.reason
    assert expected in result.reason
    assert mutated.backend.snapshot() == before


def test_split_surfaces_cas_conflict_without_partial_changes(context):
    from aitm_core.models.common import CommandResult
    from aitm_core.store.backend import OperationResult

    request = seeded(context)
    before = request.backend.snapshot()
    captured = []

    def race(operation, snapshot):
        captured.append(operation)
        return OperationResult(
            CommandResult(
                operation_id=operation.operation_id,
                local=LocalOutcome.CONFLICT,
            ),
            snapshot,
            "lost exact planning CAS",
        )

    result = split_leaf(
        SplitRequest(replace(request, transact=race), "New scope", "Oversized", 4)
    )
    assert result.command.local == LocalOutcome.CONFLICT
    assert len(captured) == 1 and request.backend.snapshot() == before
    assert replay(request).description.scope == "Original"


def test_configured_design_exit_requires_a_fresh_acceptance_after_split(context):
    from types import SimpleNamespace

    from aitm_core.ext.api import CapabilitySlot
    from aitm_core.ext.registry import load_extensions
    from aitm_core.machine.guards import core_guard
    from aitm_core.machine.transitions import transition
    from tests.unit.test_c91 import BINDING, CANDIDATE, CLOSEOUT, PICKUP, TERMINAL

    request = seeded(context)
    profile = request.profile.model_dump(mode="json", by_alias=True)
    profile["states"][0]["onExit"] = ["core.design.accepted-current"]
    registry = load_extensions(
        SimpleNamespace(config=SimpleNamespace(extensions=SimpleNamespace(enabled=()))),
        builtins=[
            CapabilitySlot(
                id=rule, version=1, kind="guard", placements=("onEnter", "onExit")
            )
            for rule in (
                "core.design.accepted-current",
                PICKUP,
                BINDING,
                CANDIDATE,
                CLOSEOUT,
                TERMINAL,
            )
        ],
    )
    command = replace(
        request, profile=WorkflowProfile.model_validate(profile), registry=registry
    )
    delivered = split_leaf(
        SplitRequest(command, "Revised aggregate scope", "Oversized", 4)
    )
    assert delivered.command.local == LocalOutcome.COMPLETED, delivered.reason

    def guard(call):
        return core_guard(
            call, leaf_hours=4, kind_requirements=None, story_exit_guards=None
        )

    forward = transition(
        replace(command, operation_id="fresh-design-check", guard=guard)
    )
    assert forward.command.local == LocalOutcome.REFUSED
    assert forward.guards[0].code == "blocked:design-acceptance"
    assert replay(command).workflow_state.state_id == "design"
