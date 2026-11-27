"""Exercise planning decisions on in-memory paths, trees and history."""

import json
from hashlib import sha256

import pytest

from aitm_core.models.common import LocalOutcome
from aitm_core.store.validation import (
    PlanningPath,
    classify_planning_path,
    validate_history,
)
from tests.support.c06 import planning_history


@pytest.fixture
def store():
    return planning_history()


@pytest.mark.parametrize(
    ("path", "kind"),
    [
        pytest.param(".aitm/README.md", PlanningPath.DATA, id="store-readme"),
        pytest.param(".aitm/store.json", PlanningPath.STORE, id="store-anchor"),
        pytest.param(
            ".aitm/operations/create.json",
            PlanningPath.OPERATION,
            id="pre-story-operation",
        ),
        pytest.param(
            ".aitm/repairs/restore.json", PlanningPath.REPAIR, id="repair-receipt"
        ),
        pytest.param(
            ".aitm/stories/001/109/events.jsonl", PlanningPath.EVENTS, id="story-events"
        ),
        pytest.param(
            ".aitm/stories/001/109/description.md",
            PlanningPath.DATA,
            id="story-description",
        ),
        pytest.param(
            ".aitm/stories/001/109/plan/pickup.md", PlanningPath.DATA, id="story-plan"
        ),
        pytest.param(
            ".aitm/stories/001/109/attachments/quotes/quote.PDF",
            PlanningPath.DATA,
            id="story-attachment",
        ),
        pytest.param(
            ".aitm/stories/001/109/operations/change.json",
            PlanningPath.OPERATION,
            id="story-operation",
        ),
        pytest.param(".aitm/ideas/2026-11/proposal.md", PlanningPath.DATA, id="idea"),
        pytest.param(
            ".aitm/drafts/discarded/proposal.json",
            PlanningPath.DATA,
            id="discarded-draft",
        ),
        pytest.param(
            ".aitm/drafts/2026-11/proposal/draft.md",
            PlanningPath.DATA,
            id="active-draft",
        ),
        pytest.param(
            ".aitm/drafts/2026-11/proposal/attachments/reference.png",
            PlanningPath.DATA,
            id="draft-attachment",
        ),
    ],
)
def test_classifies_declared_planning_paths(path, kind):
    assert classify_planning_path(path) == kind


@pytest.mark.parametrize(
    ("path", "reason"),
    [
        pytest.param(
            "../outside", "normalized repository-relative", id="parent-traversal"
        ),
        pytest.param(
            ".aitm/../outside", "normalized repository-relative", id="nested-traversal"
        ),
        pytest.param(
            ".aitm//README.md",
            "normalized repository-relative",
            id="noncanonical-separator",
        ),
        pytest.param(
            ".aitm/unknown.py", "unauthorized planning data path", id="undeclared-code"
        ),
        pytest.param("README.md", "outside planning data paths", id="outside-store"),
        pytest.param(
            ".aitm/stories/001/109/attachments/.GiT/config.txt",
            "outside planning data paths",
            id="git-directory",
        ),
        pytest.param(
            ".aitm/ideas/2026-13/proposal.md",
            "unauthorized planning data path",
            id="invalid-idea-month",
        ),
        pytest.param(
            ".aitm/ideas/2026-11/archive/proposal.md",
            "unauthorized planning data path",
            id="nested-idea",
        ),
        pytest.param(
            ".aitm/drafts/2026-11/proposal/notes.txt",
            "unauthorized planning data path",
            id="undeclared-draft-content",
        ),
        pytest.param(
            ".aitm/stories/000/109/events.jsonl",
            "invalid story path identity",
            id="wrong-story-bucket",
        ),
        pytest.param(
            ".aitm/stories/001/0109/events.jsonl",
            "invalid story path identity",
            id="noncanonical-story-number",
        ),
        pytest.param(
            ".aitm/stories/001/109/events.txt",
            "unauthorized planning data path",
            id="wrong-event-extension",
        ),
        pytest.param(
            ".aitm/stories/001/109/operations/change.md",
            "unauthorized planning data path",
            id="untyped-operation",
        ),
    ],
)
def test_layout_rejects_unnormalized_and_undeclared_paths(path, reason):
    with pytest.raises(ValueError, match=reason):
        classify_planning_path(path)


def test_history_rejects_regular_blob_outside_data_policy(store):
    repo, anchor = store
    path = ".aitm/attachments/tool.py"
    candidate = repo.create_commit(repo.tip(), {path: b"text fixture"}, "invalid path")
    result = validate_history(anchor, candidate.revision, repository=repo)
    assert result.outcome == LocalOutcome.INTEGRITY_ERROR
    assert path in result.reason


def test_core_transaction_record_is_bound_to_its_operation_and_parent(store):
    repo, anchor = store
    start = repo.tip()
    path = ".aitm/operations/unbound.json"
    content = json.dumps(
        {
            "schema_version": "aitm.operation-record/v1",
            "base": start.revision,
            "request_digest": "a" * 64,
            "command": {"operation_id": "fixture", "local": "completed"},
        }
    ).encode()
    candidate = repo.create_commit(start, {path: content}, "record")
    result = validate_history(anchor, candidate.revision, repository=repo)
    assert result.outcome == LocalOutcome.INTEGRITY_ERROR
    assert path in result.reason
    assert result.valid_prefix == start.revision


@pytest.mark.parametrize(
    ("schema", "record_story", "expected"),
    [
        ("aitm.operation-record/v1", 9, LocalOutcome.COMPLETED),
        ("aitm.operation-record/v1", 10, LocalOutcome.INTEGRITY_ERROR),
        ("aitm.unregistered/v1", 9, LocalOutcome.INTEGRITY_ERROR),
    ],
)
def test_story_owned_operation_requires_a_bound_record(
    store, schema, record_story, expected
):
    repo, anchor = store
    start = repo.tip()
    operation_id = "story-fixture"
    identity = sha256(operation_id.encode()).hexdigest()
    path = f".aitm/stories/000/9/operations/{identity}.json"
    content = json.dumps(
        {
            "schema_version": schema,
            "story": record_story,
            "base": start.revision,
            "request_digest": "a" * 64,
            "command": {"operation_id": operation_id, "local": "completed"},
        }
    ).encode()
    candidate = repo.create_commit(start, {path: content}, "story record")

    result = validate_history(anchor, candidate.revision, repository=repo)

    assert result.outcome == expected
    if expected == LocalOutcome.INTEGRITY_ERROR:
        assert path in result.reason
        assert result.valid_prefix == start.revision
