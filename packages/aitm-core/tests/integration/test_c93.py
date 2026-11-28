"""Read exact accepted pickup inputs from a real Git planning tree."""

import json
from dataclasses import replace
from hashlib import sha256

from aitm_core.decomposition import prepare_decomposition, prepare_plan_entry
from aitm_core.documents import canonicalize
from aitm_core.graduation import GraduatedRecord, graduation_path
from aitm_core.jit import Baseline, Coverage
from aitm_core.machine.pickup_basis import (
    ChildJitBasis,
    EpicBasis,
    PickupBasisRequest,
    SourceObservation,
    StandaloneBasis,
    evaluate_pickup_basis,
)
from aitm_core.models.attempts import SourceSnapshot
from aitm_core.models.config import BacklogIssuer, DeliveryTarget
from aitm_core.models.documents import DocumentSchema
from aitm_core.models.events import EventActor, EventEnvelope
from aitm_core.models.operations import story_event_path
from aitm_core.providers.backlog import GraduationIntent, IssueRef
from tests.integration.test_c05 import make_backend as make_backend
from tests.unit.test_c72 import DESIGN, PARENT, PLAN, POLICY, STAMP, inputs


def story_log(story, source_id, *, parent=None, source_digest=POLICY, plan=None):
    data = {
        "kind": "story",
        "source_kind": "plan-entry" if parent else "draft",
        "source_id": source_id,
        "source_digest": source_digest,
        "issue": f"example/work#{story}",
        "parent": parent,
        "initial_state": {
            "workflow_id": "configured",
            "revision": POLICY,
            "state_id": "plan",
            "label": "Plan",
        },
    }
    rows = [("core.story.graduated", data)]
    if plan is not None:
        path, identity = plan
        rows.append(
            (
                "core.doc.accepted",
                {
                    "role": "plan",
                    "path": path,
                    "canonical_version": "aitm.authored-content/v1",
                    "canonical_digest": identity.canonical_sha256,
                    "raw_digest": identity.raw_sha256,
                    "review_refs": ["approved"],
                    "levels": ["xpr"],
                    "policy_digest": POLICY,
                    "source_planning_sha": "a" * 40,
                    "plan_generation": 1,
                },
            )
        )
    digest = sha256()
    records = []
    for index, (kind, fact) in enumerate(rows, 1):
        line = (
            EventEnvelope(
                v=1,
                id=f"c93-{story}-{index}",
                ts=STAMP,
                type=kind,
                story=story,
                actor=EventActor(kind="agent"),
                operation_id=f"op-{story}-{index}",
                sequence=index,
                prior_log_digest=digest.hexdigest(),
                data=fact,
            )
            .model_dump_json(exclude_none=True)
            .encode()
            + b"\n"
        )
        records.append(line)
        digest.update(line)
    return b"".join(records)


def test_git_store_resolves_all_pickup_bases_and_refuses_stale_or_foreign_proof(
    make_backend,
):
    code = make_backend({"src/core.py": b"pass\n"}).snapshot()
    source = SourceSnapshot(commit=code.revision, tree=code.tree)
    baseline = Baseline(kind="source", snapshot=source)
    observed = SourceObservation(baseline)
    parent_store, parent_digest = inputs()
    frozen = prepare_decomposition(
        parent_store, parent_store.snapshot(), PARENT, parent_digest, POLICY
    )
    child_source = prepare_plan_entry(frozen, "second")
    wrong_entry = prepare_plan_entry(frozen, "first")
    issuer = BacklogIssuer(
        backlog="local",
        backlog_repository="example/work",
        numbering_namespace="example",
    )
    issuance = GraduatedRecord(
        intent=GraduationIntent(
            operation_id="issue-501",
            issuer=issuer,
            shared=False,
            source=child_source,
            parent=PARENT,
            delivery_target=DeliveryTarget(
                repository="example/work", ref="refs/heads/trunk"
            ),
        ),
        issue=IssueRef(issuer=issuer, number=501),
        operation="issue-501",
        workflow_digest=POLICY,
    )
    standalone_plan = ".aitm/stories/005/510/plan/pickup.md"
    header = {
        "schema": "aitm.doc/v1",
        "story": 510,
        "role": "plan",
        "source": f"source:{source.commit}:{source.tree}",
    }
    raw_plan = (
        "---\n"
        + "".join(f"{key}: {json.dumps(value)}\n" for key, value in header.items())
        + "---\n# Standalone plan\n"
    ).encode()
    acceptance = canonicalize(raw_plan, DocumentSchema())
    files = parent_store.read(
        parent_store.snapshot(), (DESIGN, PLAN, story_event_path(PARENT))
    )
    planning = make_backend(
        {
            **files,
            standalone_plan: raw_plan,
            story_event_path(510): story_log(
                510, "draft-510", plan=(standalone_plan, acceptance)
            ),
            story_event_path(501): story_log(
                501,
                child_source.identity,
                parent=PARENT,
                source_digest=child_source.entry_digest,
            ),
            graduation_path(child_source): issuance.model_dump_json().encode(),
        }
    )
    snapshot = planning.snapshot()

    standalone = StandaloneBasis(acceptance.canonical_sha256, observed)
    epic = EpicBasis(parent_digest)
    coverage = Coverage(
        baseline=baseline,
        plan_digest=parent_digest,
        plan_generation=1,
        attempt="a501",
        attempt_generation=1,
        paths=("src/core.py",),
    )
    child = ChildJitBasis(
        entry=child_source,
        coverage=coverage,
        source=observed,
        attempt="a501",
        attempt_generation=1,
        checklist="Verify the pinned source contract.",
    )

    def evaluate(story, basis, revision=snapshot):
        request = PickupBasisRequest(story, POLICY, basis)
        return evaluate_pickup_basis(planning, revision, request)

    standalone_result = evaluate(510, standalone)
    assert (standalone_result.kind, standalone_result.status) == (
        "standalone",
        "current",
    )
    assert standalone_result.source == source
    epic_result = evaluate(PARENT, epic)
    assert (epic_result.kind, epic_result.status) == ("epic", "current")
    assert epic_result.source is None
    accepted = evaluate(501, child)
    assert accepted.kind == "child-jit" and accepted.status == "current"
    assert accepted.entry == frozen.entry("second")
    assert accepted.source == source
    assert accepted.scope_required
    assert evaluate(501, replace(child, entry=wrong_entry)).status == "hold"
    assert evaluate(501, replace(child, attempt_generation=2)).status == "hold"
    assert evaluate(501, standalone).status == "hold"

    other = make_backend({"src/core.py": b"raise RuntimeError\n"}).snapshot()
    stale_source = SourceObservation(
        Baseline(
            kind="source",
            snapshot=SourceSnapshot(commit=other.revision, tree=other.tree),
        )
    )
    assert evaluate(510, replace(standalone, source=stale_source)).status == "hold"
    assert evaluate(501, replace(child, source=stale_source)).status == "hold"

    newer_parent, _ = inputs(plan_body="A later accepted parent plan")
    changes = newer_parent.read(
        newer_parent.snapshot(), (PLAN, story_event_path(PARENT))
    )
    newer = planning.repository.create_commit(snapshot, changes, "review-new-parent")
    assert evaluate(501, child, newer).status == "hold"
    assert evaluate(501, child, snapshot).status == "current"
    assert planning.snapshot() == snapshot
