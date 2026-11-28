"""C72 freezes typed parent entries and qualifies existing child provenance."""

import json
from hashlib import sha256

import pytest

from aitm_core.decomposition import (
    assess_decomposition,
    plan_entry_applicability,
    prepare_decomposition,
    prepare_plan_entry,
    reconcile_plan_entry,
)
from aitm_core.documents import canonicalize
from aitm_core.models.documents import DocumentSchema
from aitm_core.models.events import EventActor, EventEnvelope
from aitm_core.models.operations import story_event_path
from aitm_core.store.memory_backend import MemoryBackend

PARENT = 478
STAMP = "2026-11-28T08:00:00Z"
POLICY = "e" * 64
DESIGN = ".aitm/stories/004/478/design/design.md"
PLAN = ".aitm/stories/004/478/plan/plan.md"
FIRST = {
    "kind": "story",
    "description": {"title": "First", "scope": "First deliverable"},
    "agent_hours": 3.5,
    "size": "S",
    "priority": "P1",
    "deliverable": "Planning evidence",
    "verification": "Focused unit tests",
    "acceptance_criteria": ["The obligation is present"],
    "dependencies": [],
}
SECOND = {
    **FIRST,
    "description": {"title": "Second", "scope": "Dependent deliverable"},
    "dependencies": ["first"],
}
ENTRIES = {"first": FIRST, "second": SECOND}


def authored(role, body, map_value=None):
    fields = {"schema": "aitm.doc/v1", "story": PARENT, "role": role}
    if map_value is not None:
        fields["decomposition"] = map_value
    header = "".join(f"{key}: {json.dumps(value)}\n" for key, value in fields.items())
    return f"---\n{header}---\n{body}\n".encode()


def inputs(
    entries=ENTRIES,
    *,
    design_body="Design",
    plan_body="Plan",
    current_plan=None,
    issuance=None,
):
    design = authored("design", design_body)
    plan = authored("plan", plan_body, entries)
    facts = [
        (
            "core.story.graduated",
            {
                "kind": "epic",
                "source_kind": "draft",
                "source_id": "epic",
                "source_digest": POLICY,
                "issue": "example/work#478",
                "initial_state": {
                    "workflow_id": "configured",
                    "revision": POLICY,
                    "state_id": "plan",
                    "label": "Plan",
                },
            },
        )
    ]
    for role, path, raw in (("design", DESIGN, design), ("plan", PLAN, plan)):
        content = canonicalize(raw, DocumentSchema())
        facts.append(
            (
                "core.doc.accepted",
                {
                    "role": role,
                    "path": path,
                    "canonical_version": "aitm.authored-content/v1",
                    "canonical_digest": content.canonical_sha256,
                    "raw_digest": content.raw_sha256,
                    "review_refs": ["approved"],
                    "levels": ["xpr"],
                    "policy_digest": POLICY,
                    "source_planning_sha": "a" * 40,
                    "plan_generation": 1,
                },
            )
        )
    records = []
    digest = sha256()
    for sequence, (kind, data) in enumerate(facts, 1):
        row = (
            EventEnvelope(
                v=1,
                id=f"e{sequence}",
                ts=STAMP,
                type=kind,
                story=PARENT,
                actor=EventActor(kind="agent"),
                operation_id=f"op{sequence}",
                sequence=sequence,
                prior_log_digest=digest.hexdigest(),
                data=data,
            )
            .model_dump_json(exclude_none=True)
            .encode()
            + b"\n"
        )
        records.append(row)
        digest.update(row)
    store = MemoryBackend(
        {
            DESIGN: design,
            PLAN: current_plan if current_plan is not None else plan,
            story_event_path(PARENT): b"".join(records),
            **(issuance or {}),
        }
    )
    return store, facts[-1][1]["canonical_digest"]


def load(entries=ENTRIES, **changes):
    store, expected_plan = inputs(entries, **changes)
    return prepare_decomposition(store, store.snapshot(), PARENT, expected_plan, POLICY)


def test_plan_entry_contract_freezes_parents_and_canonical_descriptors():
    parent = load()
    source = prepare_plan_entry(parent, "second")
    assert source.parent == PARENT
    assert source.identity == "478:second"
    assert source.plan_digest == parent.plan_digest
    assert source.design_digest == parent.design_digest
    assert source.descriptor.scope == SECOND["description"]["scope"]
    assert parent.entry("second").dependencies == ("first",)
    assert parent.entry("second").proposal.phase == "decomposition"
    assert {read.path for read in parent.reads} == {
        DESIGN,
        PLAN,
        story_event_path(PARENT),
    }

    changed = load(design_body="Accepted new design")
    updated = prepare_plan_entry(changed, "second")
    assert updated.semantic_key == source.semantic_key
    assert updated.entry_digest == source.entry_digest
    assert updated.design_digest != source.design_digest


def test_plan_entry_contract_rejects_unknown_references_cycles_and_prose():
    with pytest.raises(ValueError, match="depend"):
        load({"second": SECOND})
    with pytest.raises(ValueError, match="cycle"):
        load({"first": FIRST | {"dependencies": ["second"]}, "second": SECOND})
    with pytest.raises(ValueError, match="decomposition"):
        load(None)
    with pytest.raises(ValueError, match="accepted"):
        load(current_plan=authored("plan", "Unreviewed edit", ENTRIES))
    with pytest.raises(ValueError, match="entry"):
        prepare_plan_entry(load(), "unspecified")


def test_reconcile_plan_entry_preserves_permanent_child_and_requires_current_provenance():
    original = load()
    prior = prepare_plan_entry(original, "second")
    changed = load(plan_body="Reviewed plan update")
    assert (
        assess_decomposition(prior, original, design_coverage="own-document").status
        == "current"
    )
    assert (
        assess_decomposition(prior, original, design_coverage=None).status
        == "unavailable"
    )
    assert (
        assess_decomposition(prior, original, design_coverage="parent-only").status
        == "unavailable"
    )
    assert (
        assess_decomposition(prior, changed, design_coverage="own-document").status
        == "stale"
    )
    with pytest.raises(ValueError, match="parent/store"):
        reconcile_plan_entry(75, prior, changed, store=original.snapshot.store)
    result = reconcile_plan_entry(75, prior, changed, store=changed.snapshot.store)
    assert result.identity == (changed.snapshot.store, PARENT, "second")
    assert result.child == 75
    assert result.previous == prior
    assert result.current.identity == prior.identity
    assert result.current.plan_digest == changed.plan_digest
    assert result.current.entry_digest == prior.entry_digest


def test_c26_port_requires_the_issued_child_and_pins_all_current_provenance():
    from functools import partial

    from aitm_core.graduation import GraduatedRecord, graduation_path
    from aitm_core.models.config import BacklogIssuer, DeliveryTarget
    from aitm_core.models.lifecycle import Graduation, WorkflowObservation
    from aitm_core.models.operations import OperationOwner
    from aitm_core.providers.backlog import GraduationIntent, IssueRef
    from aitm_core.reviews.acceptance import DocumentInput, _applicability
    from aitm_core.reviews.turns import ReviewContext

    source = prepare_plan_entry(load(), "second")
    issuer = BacklogIssuer(
        backlog="local",
        backlog_repository="example/work",
        numbering_namespace="example",
    )
    intent = GraduationIntent(
        operation_id="issue-second",
        issuer=issuer,
        shared=False,
        source=source,
        delivery_target=DeliveryTarget(
            repository="example/work", ref="refs/heads/trunk"
        ),
        parent=PARENT,
    )
    record = GraduatedRecord(
        intent=intent,
        issue=IssueRef(issuer=issuer, number=75),
        operation="issue-second",
        workflow_digest=POLICY,
    )
    path = graduation_path(source)
    issuance = {path: record.model_dump_json().encode()}
    child = Graduation(
        kind="story",
        source_kind="plan-entry",
        source_id=source.identity,
        source_digest=source.entry_digest,
        issue="example/work#75",
        parent=PARENT,
        initial_state=WorkflowObservation(
            workflow_id="configured",
            revision=POLICY,
            state_id="design",
            label="Design",
        ),
    )
    doc = DocumentInput(75, ".aitm/stories/000/75/design/design.md", "design", b"")
    port = partial(plan_entry_applicability, design_coverage="own-document")

    def evaluate(**changes):
        store, _ = inputs(**changes)
        context = ReviewContext(
            store,
            store.snapshot(),
            OperationOwner(actor=EventActor(kind="agent")),
            POLICY,
            "observe-child",
            STAMP,
            store.transact,
        )
        return _applicability(context, child, doc, port)

    current = evaluate(issuance=issuance)
    assert current.status == "current"
    assert {read.path for read in current.reads} == {
        PLAN,
        DESIGN,
        story_event_path(PARENT),
        path,
    }
    assert (
        evaluate(issuance=issuance, design_body="Parent design changed").status
        == "stale"
    )
    assert (
        evaluate(issuance=issuance, plan_body="Parent plan changed").status == "stale"
    )
    assert evaluate().status == "unavailable"
