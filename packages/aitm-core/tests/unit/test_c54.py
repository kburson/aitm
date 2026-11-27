"""Exercise the C54 schema mapping through the causal C02 fold."""

from hashlib import sha256
from json import dumps

import pytest

from aitm_core.events import ReducerRegistry, fold
from aitm_core.reducers.lifecycle import (
    LifecycleIntegrityError,
    fold_lifecycle,
    lifecycle_schemas,
)

DIGEST = "a" * 64
NEWER = "b" * 64
COMMIT = "c" * 40
INITIAL = {
    "workflow_id": "sdlc",
    "revision": DIGEST,
    "state_id": "legacy-backlog",
    "label": "Old queue",
    "capability": {
        "id": "core.plan.admission",
        "version": "1",
        "status": "unavailable",
    },
}
REFINE = {
    "workflow_id": "sdlc",
    "revision": NEWER,
    "state_id": "refine",
    "label": "Define scope",
    "capability": {"id": "core.plan.admission", "version": "2", "status": "available"},
}
GRADUATION = (
    "core.story.graduated",
    {
        "kind": "story",
        "source_kind": "plan-entry",
        "source_id": "entry:c54",
        "source_digest": DIGEST,
        "issue": "owner/repo#6",
        "parent": 470,
        "initial_state": INITIAL,
    },
)


def move(source=INITIAL, target=REFINE, **fields):
    change = {
        "from": source,
        "to": target,
        "mode": "enforce",
        "edge": {
            "id": "workflow-edge",
            "workflow_id": target["workflow_id"],
            "revision": target["revision"],
            "source": source["state_id"],
            "target": target["state_id"],
            "kind": "normal",
        },
    }
    change.update(fields)
    return "core.state.changed", change


def replay(*facts):
    registry = ReducerRegistry()
    for event_type in lifecycle_schemas():
        registry.register(event_type, fold_lifecycle)
    prior = sha256()
    records = []
    for sequence, (event_type, data) in enumerate(facts, 1):
        event = dumps(
            {
                "v": 1,
                "id": f"event-{sequence}",
                "ts": "2026-11-27T08:00:00Z",
                "type": event_type,
                "story": 6,
                "operation_id": f"op-{sequence}",
                "actor": {"kind": "agent"},
                "sequence": sequence,
                "prior_log_digest": prior.hexdigest(),
                "data": data,
            }
        ).encode()
        records.append(event)
        prior.update(event + b"\n")
    return fold(records, registry).domains["lifecycle"]


def estimate(phase, hours):
    return "core.estimate.set", {
        "phase": phase,
        "agent_hours": hours,
        "size": "S",
        "priority": "P1",
    }


def acceptance(role, digest):
    return "core.doc.accepted", {
        "role": role,
        "path": f"{role}.md",
        "canonical_version": "aitm.authored-content/v1",
        "canonical_digest": digest,
        "raw_digest": DIGEST,
        "review_refs": ["sar-1"],
        "levels": ["sar"],
        "policy_digest": DIGEST,
        "source_planning_sha": COMMIT,
        "plan_generation": 1,
    }


def deliverable(**changes):
    data = {
        "deliverable_id": "receipt-1",
        "path": "proof/result.json",
        "raw_digest": DIGEST,
        "canonical_digest": NEWER,
        "attempt": "a1",
        "source_snapshot": COMMIT,
    }
    return "core.deliverable.added", {**data, **changes}


def test_lifecycle_reducers():
    links = (
        "core.link.changed",
        {
            "before": {"parent": 470},
            "after": {"parent": 470, "blocked_by": [4, 5], "blocking": [8]},
        },
    )
    description = (
        "core.description.set",
        {
            "title": "Lifecycle reducer",
            "as": "developer",
            "want": "typed replay",
            "so_that": "the result is deterministic",
            "scope": "bounded lifecycle",
            "content_hash": DIGEST,
        },
    )
    jit = (
        "core.jit.recorded",
        {
            "plan_digest": NEWER,
            "plan_generation": 1,
            "attempt": "a1",
            "code_baseline": COMMIT,
            "coverage_paths": ["src"],
            "coverage_status": "complete",
            "outcome": "accepted",
            "reviewed_revisions": [COMMIT],
        },
    )
    signoff = (
        "core.signoff.recorded",
        {
            "retro": "retro/signed.md",
            "confidence": 5,
            "verdict": "delivered",
            "by": "actor-1",
        },
    )
    observed = replay(
        GRADUATION,
        move(),
        links,
        description,
        estimate("decomposition", 4),
        estimate("refine", 3.5),
        estimate("plan", 3),
        estimate("jit", 2.5),
        acceptance("design", DIGEST),
        acceptance("plan", NEWER),
        jit,
        deliverable(),
        signoff,
    )
    assert observed.graduation.source_kind == "plan-entry"
    assert observed.graduation.source_id == "entry:c54"
    assert [entry.label for entry in observed.state_history] == [
        "Old queue",
        "Define scope",
    ]
    assert observed.state_history[0].state_id == "legacy-backlog"
    assert [entry.capability.status for entry in observed.state_history] == [
        "unavailable",
        "available",
    ]
    assert observed.relationships.blocked_by == (4, 5)
    assert observed.description.title == "Lifecycle reducer"
    assert {
        phase: value.agent_hours for phase, value in observed.estimates.items()
    } == {
        "decomposition": 4,
        "refine": 3.5,
        "plan": 3,
        "jit": 2.5,
    }
    assert observed.accepted_documents["plan"].canonical_digest == NEWER
    assert observed.jit.code_baseline == COMMIT
    assert observed.deliverables["receipt-1"].source_snapshot == COMMIT
    assert observed.signoff.confidence == 5


def test_split_invalidates_without_adopting_decomposition_as_refinement():
    proposal = replay(GRADUATION, estimate("decomposition", 4))
    assert set(proposal.estimates) == {"decomposition"}
    assert not proposal.accepted_documents
    split = (
        "core.kind.changed",
        {
            "from": "story",
            "to": "epic",
            "reason": "needs decomposition",
            "scope_digest": DIGEST,
            "invalidated_acceptances": [DIGEST],
            "invalidated_estimates": ["decomposition"],
            "decomposition_required": True,
        },
    )
    result = replay(
        GRADUATION, estimate("decomposition", 4), acceptance("design", DIGEST), split
    )
    assert result.kind == "epic" and result.split.decomposition_required
    assert not result.accepted_documents and not result.estimates


@pytest.mark.parametrize(
    "fact",
    [
        move(source={**INITIAL, "label": "wrong previously recorded observation"}),
        move(
            edge={
                "id": "bad",
                "workflow_id": "sdlc",
                "revision": NEWER,
                "source": "legacy-backlog",
                "target": "wrong",
                "kind": "normal",
            }
        ),
        move(disposition="duplicate", replacement_story=6),
        move(target={**REFINE, "terminal": True}),
        ("core.link.changed", {"before": {}, "after": {"parent": 470}}),
        (
            "core.link.changed",
            {"before": {"parent": 470}, "after": {"blocked_by": [6]}},
        ),
        (
            "core.link.changed",
            {"before": {"parent": 470}, "after": {"blocked_by": [4, 4]}},
        ),
        ("core.doc.accepted", {"role": "design", "path": "design.md"}),
        deliverable(path="../outside"),
    ],
)
def test_invalid_lifecycle_facts_are_refused(fact):
    with pytest.raises(LifecycleIntegrityError):
        replay(GRADUATION, fact)


def test_deliverable_binding_is_immutable():
    assert len(replay(GRADUATION, deliverable(), deliverable()).deliverables) == 1
    with pytest.raises(LifecycleIntegrityError, match="deliverable identity"):
        replay(GRADUATION, deliverable(), deliverable(raw_digest=NEWER))


def test_terminal_disposition_history_survives_reopen():
    terminal = {
        **REFINE,
        "state_id": "closed-legacy",
        "label": "Retired",
        "terminal": True,
    }
    edge = {
        "id": "finish",
        "workflow_id": "sdlc",
        "revision": NEWER,
        "source": INITIAL["state_id"],
        "target": terminal["state_id"],
        "kind": "terminal",
    }
    retired = move(
        target=terminal, edge=edge, disposition="duplicate", replacement_story=45
    )
    reopened = move(
        source=terminal,
        edge={
            **edge,
            "id": "resume",
            "source": terminal["state_id"],
            "target": REFINE["state_id"],
            "kind": "reopen",
        },
    )
    result = replay(GRADUATION, retired, reopened)
    assert result.transitions[0].disposition == "duplicate"
    assert result.transitions[0].replacement_story == 45
    assert result.state_history[-2].state_id == "closed-legacy"
    assert result.workflow_state.state_id == "refine"

    for replacement in (None, 6):
        with pytest.raises(LifecycleIntegrityError, match="replacement"):
            replay(
                GRADUATION,
                move(
                    target=terminal,
                    edge=edge,
                    disposition="duplicate",
                    replacement_story=replacement,
                ),
            )
