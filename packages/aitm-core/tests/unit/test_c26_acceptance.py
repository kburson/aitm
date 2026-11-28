"""Check exact-content review coverage independently of store publication."""

import tomllib
from dataclasses import replace
from hashlib import sha256
from json import dumps, loads
from pathlib import PurePosixPath

import pytest

from aitm_core.documents import canonicalize, rewrite_metadata
from aitm_core.models.common import LocalOutcome
from aitm_core.models.config import ReviewPolicy
from aitm_core.models.documents import DocumentSchema, Metadata
from aitm_core.models.events import EventActor
from aitm_core.models.operations import (
    AuthorityOrigin,
    OperationOwner,
    WriteAuthorization,
    story_event_path,
)
from aitm_core.reviews.acceptance import (
    ApplicabilityResult,
    DocumentInput,
    ReviewRecord,
    accept_document,
    evaluate_acceptance,
)
from aitm_core.reviews.policy import ValidatedReview
from aitm_core.reviews.portable import Original, PortableManifest, ReconstructedReview
from aitm_core.reviews.turns import ReviewContext
from aitm_core.services import ServicePorts
from aitm_core.store.memory_backend import MemoryBackend
from tests.support.c07 import settings_at
from tests.unit.test_c15 import graduated

DESIGN_PATH = ".aitm/stories/000/16/design/current.md"
PLAN_PATH = ".aitm/stories/000/16/plan/current.md"


def document(content, *, story=16, role="design", path=DESIGN_PATH):
    raw = (
        f"---\nschema: aitm.doc/v1\nstory: {story}\nrole: {role}\n---\n{content}\n"
    ).encode()
    return DocumentInput(story, path, role, raw)


def record(level, content, **coordinates):
    doc = document(content, **coordinates)
    digest = "sha256:" + sha256(doc.raw).hexdigest()
    manifest = PortableManifest.model_validate(
        {
            "schema": "aitm.review-manifest/v0",
            "story": doc.story,
            "level": level,
            "artifact_path": doc.path,
            "base_digest": digest,
            "final_digest": digest,
            "rounds": 1,
            "outcome": "exhausted",
        }
    )
    return ReviewRecord(
        f"{level}-{content}",
        ValidatedReview(
            ReconstructedReview(manifest, doc.raw, doc.raw, (), ()),
            level,
            "declared-manual",
        ),
    )


@pytest.fixture
def policy():
    value = tomllib.loads(settings_at("a" * 40))["review"]
    value["documents"].update(design=["sar", "spr", "xpr"], plan=["sar"])
    return ReviewPolicy.model_validate(value)


def test_each_level_must_review_the_same_final_content(policy):
    historic = (record("sar", "A"), record("spr", "B"), record("xpr", "C"))
    result = evaluate_acceptance(document("C"), policy, historic)
    assert result.outcome is LocalOutcome.REFUSED
    assert result.missing_levels == ("sar", "spr")

    complete = (*historic, record("sar", "C"), record("spr", "C"))
    result = evaluate_acceptance(document("C"), policy, complete)
    assert result.accepted
    assert result.review_refs == ("sar-C", "spr-C", "xpr-C")

    changed = evaluate_acceptance(document("D"), policy, complete)
    assert changed.missing_levels == ("sar", "spr", "xpr")
    assert changed.review_refs == ()
    assert (
        changed.canonical_digest
        == canonicalize(document("D").raw, DocumentSchema()).canonical_sha256
    )


def test_generated_metadata_preserves_the_exact_content_obligations(policy):
    doc = document("C")
    refreshed = rewrite_metadata(doc.raw, Metadata(status="Updated"))
    result = evaluate_acceptance(
        replace(doc, raw=refreshed),
        policy,
        (record("sar", "C"), record("spr", "C"), record("xpr", "C")),
    )
    assert result.accepted
    assert (
        result.canonical_digest
        == canonicalize(doc.raw, DocumentSchema()).canonical_sha256
    )
    assert refreshed != doc.raw


@pytest.mark.parametrize(
    "coordinates",
    [
        {"story": 23, "path": ".aitm/stories/000/23/design/current.md"},
        {"role": "plan", "path": PLAN_PATH},
        {"role": "plan"},
        {"path": ".aitm/stories/000/16/design/different.md"},
    ],
    ids=[
        "another-story",
        "parent-plan-role",
        "different-role-at-same-path",
        "another-path",
    ],
)
def test_design_coverage_requires_the_exact_own_document(policy, coordinates):
    result = evaluate_acceptance(
        document("C"),
        policy,
        (record("sar", "C", **coordinates), record("spr", "C"), record("xpr", "C")),
    )
    assert result.missing_levels == ("sar",)


def test_a_review_with_disallowed_assurance_cannot_cover_its_level(policy):
    sar = record("sar", "C")
    sar = replace(sar, review=replace(sar.review, assurance="independently-attested"))
    result = evaluate_acceptance(
        document("C"), policy, (sar, record("spr", "C"), record("xpr", "C"))
    )
    assert result.missing_levels == ("sar",)


@pytest.mark.parametrize(
    "fields",
    [
        {"design": ()},
        {"binding": "sequence"},
        {"design_coverage": "parent-plan-section"},
    ],
    ids=["empty-required-levels", "unsupported-binding", "unsupported-design-coverage"],
)
def test_policy_must_explicitly_select_supported_coverage(policy, fields):
    policy = policy.model_copy(
        update={"documents": policy.documents.model_copy(update=fields)}
    )
    result = evaluate_acceptance(document("C"), policy, ())
    assert result.outcome is LocalOutcome.UNAVAILABLE
    assert not result.accepted


def test_round_cap_cannot_cover_a_required_level(policy):
    sar = record("sar", "C")
    capped = replace(
        sar.review.record,
        manifest=sar.review.record.manifest.model_copy(update={"outcome": "round-cap"}),
    )
    result = evaluate_acceptance(
        document("C"),
        policy,
        (
            replace(sar, review=replace(sar.review, record=capped)),
            record("spr", "C"),
            record("xpr", "C"),
        ),
    )
    assert result.missing_levels == ("sar",)


def test_committed_authority_does_not_waive_missing_review_without_a_grant(policy):
    definition = policy.model_dump(by_alias=True)
    definition["exceptions"] = {
        "enabled": True,
        "authority": "review-board",
        "scope": "exact-document-digest",
        "waived_requirement": "explicit",
        "rationale": "required",
        "validity": "bounded",
    }
    result = evaluate_acceptance(
        document("C"), ReviewPolicy.model_validate(definition), (record("xpr", "C"),)
    )
    assert result.outcome is LocalOutcome.REFUSED
    assert result.missing_levels == ("sar", "spr")


@pytest.mark.parametrize(
    ("port", "outcome"),
    [
        (None, LocalOutcome.UNAVAILABLE),
        (lambda *_: ApplicabilityResult("stale"), LocalOutcome.REFUSED),
        (lambda *_: ApplicabilityResult("current"), LocalOutcome.UNAVAILABLE),
    ],
    ids=["missing", "stale", "unqualified"],
)
def test_plan_entry_requires_typed_current_applicability_before_acceptance(
    policy, port, outcome
):
    doc = document("C")
    graduation = loads(graduated())
    graduation["data"].update(source_kind="plan-entry", parent=10)
    event_path = story_event_path(doc.story)
    raw = dumps(graduation).encode() + b"\n"
    backend = MemoryBackend({doc.path: doc.raw, event_path: raw})
    before = backend.snapshot()
    context = ReviewContext(
        backend,
        before,
        OperationOwner(actor=EventActor(kind="tool", harness="test")),
        "c" * 64,
        "accept-test",
        "2026-11-27T12:30:00Z",
        backend.transact,
    )
    result = accept_document(
        "design",
        (record("sar", "C"), record("spr", "C"), record("xpr", "C")),
        doc,
        policy,
        context=context,
        proof_paths=(),
        applicability=port,
    )
    assert result.command.local is outcome
    assert backend.snapshot() == before
    assert backend.read(before, (event_path,))[event_path] == raw


@pytest.mark.parametrize("collision", [False, True], ids=["retained", "collision"])
def test_identity_mapping_is_pinned_and_retained_with_acceptance(policy, collision):
    coordinates = {"path": PLAN_PATH, "role": "plan"}
    plan = document("C", **coordinates)
    sar = record("sar", "C", **coordinates)
    initial_log = graduated()
    event_path = story_event_path(plan.story)
    root = PurePosixPath(event_path).parent
    manifest_path = f"{root}/evidence/reviews/{sar.record_id}/review-manifest.md"
    manifest = sar.review.record.manifest.model_dump_json(by_alias=True).encode()
    sar = replace(
        sar,
        review=replace(
            sar.review,
            record=replace(
                sar.review.record,
                originals=(Original("review-manifest.md", manifest),),
            ),
        ),
    )
    digest = canonicalize(plan.raw, DocumentSchema()).canonical_sha256
    stamped = "2026-11-27T12:00:00Z"
    completed = {
        "v": 1,
        "id": "review-completed",
        "operation_id": "complete",
        "ts": stamped,
        "type": "core.doc-review.completed",
        "story": plan.story,
        "actor": {"kind": "tool"},
        "sequence": 2,
        "prior_log_digest": sha256(initial_log).hexdigest(),
        "data": {
            "record_id": sar.record_id,
            "path": plan.path,
            "level": "sar",
            "rounds": 1,
            "outcome": "exhausted",
            "base_digest": digest,
            "final_digest": digest,
            "started_at": None,
            "ended_at": stamped,
            "manifest_path": manifest_path,
        },
    }
    mapping = b'{  "evidence": "fixture" ,  "bindings": [] }\n'
    mapping_digest = sha256(mapping).hexdigest()
    mapping_path = f"{root}/evidence/review-identities/{mapping_digest}.json"
    files = {
        event_path: initial_log + dumps(completed).encode() + b"\n",
        plan.path: plan.raw,
        manifest_path: manifest,
    }
    if collision:
        files[mapping_path] = b"corrupt existing mapping"
    backend = MemoryBackend(
        files,
        ports=ServicePorts(
            write_authorization=lambda *_: WriteAuthorization(
                allowed=True, origin=AuthorityOrigin.FIXTURE
            )
        ),
    )
    memory_snapshot = backend.snapshot()
    snapshot = replace(memory_snapshot, revision="f" * 40)

    class PinnedView:
        def snapshot(self):
            return snapshot

        def read(self, pinned, paths):
            assert pinned == snapshot
            return backend.read(memory_snapshot, paths)

    def publish(operation, pinned):
        assert pinned == snapshot
        assert mapping_path in {
            item.path for item in operation.change.read_set if item.digest is None
        }
        assert loads(operation.intent.payload)["identity_mapping"] == {
            "path": mapping_path,
            "sha256": mapping_digest,
            "legacy_session_namespace": "terminal / Codex",
        }
        return backend.transact(operation, memory_snapshot)

    context = ReviewContext(
        PinnedView(),
        snapshot,
        OperationOwner(actor=EventActor(kind="tool", harness="test")),
        "c" * 64,
        "accept-test",
        "2026-11-27T12:30:00Z",
        publish,
    )

    def accept(pinned):
        return accept_document(
            "plan",
            (sar,),
            plan,
            policy,
            context=pinned,
            proof_paths=(manifest_path,),
            identity_mapping=mapping,
            legacy_session_namespace="terminal / Codex",
        )

    result = accept(context)
    if collision:
        assert result.command.local is LocalOutcome.CONFLICT
        assert backend.read(memory_snapshot, (event_path, mapping_path)) == {
            path: files[path] for path in (event_path, mapping_path)
        }
        return
    assert result.command.local is LocalOutcome.COMPLETED
    saved = backend.read(result.snapshot, (event_path, mapping_path))
    assert saved[mapping_path] == mapping
    acceptance = loads(saved[event_path].splitlines()[-1])
    assert acceptance["type"] == "core.doc.accepted"
    assert acceptance["data"]["review_refs"] == [
        manifest_path,
        f"{mapping_path}#legacy_session_namespace=terminal+%2F+Codex",
    ]

    missing = MemoryBackend({**files, event_path: saved[event_path]})
    backend = missing
    memory_snapshot = missing.snapshot()
    snapshot = replace(memory_snapshot, revision="1" * 40)
    result = accept(replace(context, snapshot=snapshot, operation_id="retry"))
    assert result.command.local is LocalOutcome.CONFLICT
