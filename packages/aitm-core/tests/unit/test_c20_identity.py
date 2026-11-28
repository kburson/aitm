"""The prepared identity has stable source-specific keys and typed coordinates."""

import pytest
from pydantic import ValidationError

from aitm_core.models.attempts import SourceSnapshot
from aitm_core.models.binding import EntityRef
from aitm_core.models.config import BacklogIssuer
from aitm_core.models.identity import (
    DeliveryTarget,
    DraftSource,
    PlanEntrySource,
    SourceDescription,
)
from aitm_core.providers.backlog import GraduationIntent

ISSUER = BacklogIssuer(
    backlog="provider", backlog_repository="owner/issues", numbering_namespace="issues"
)
DRAFT = DraftSource(
    entity=EntityRef(
        identity="1:entry", document=".aitm/drafts/2026-11/20261127-1200-title/draft.md"
    ),
    snapshot=SourceSnapshot(commit="a" * 40, tree="b" * 40),
    draft_tree="c" * 40,
    document_digest="d" * 64,
)
ENTRY = PlanEntrySource(
    parent=1,
    entry_key="entry",
    design_digest="a" * 64,
    plan_digest="b" * 64,
    entry_digest="c" * 64,
    descriptor=SourceDescription(title="Title", scope="Scope"),
)


@pytest.mark.parametrize(
    "field", ["design_digest", "plan_digest", "entry_digest", "descriptor"]
)
def test_plan_entry_semantic_key_excludes_mutable_content(field):
    change = (
        SourceDescription(title="Another title", scope="Scope")
        if field == "descriptor"
        else "d" * 64
    )
    assert ENTRY.model_copy(update={field: change}).semantic_key == ENTRY.semantic_key


@pytest.mark.parametrize("field,value", [("parent", 2), ("entry_key", "other")])
def test_plan_entry_key_is_parent_scoped(field, value):
    assert ENTRY.model_copy(update={field: value}).semantic_key != ENTRY.semantic_key


def test_tag_disambiguates_equal_display_identities():
    assert ENTRY.identity == DRAFT.identity
    assert ENTRY.semantic_key != DRAFT.semantic_key


def test_draft_semantic_key_excludes_snapshot_and_content():
    current = DRAFT.model_copy(
        update={
            "snapshot": SourceSnapshot(commit="e" * 40, tree="f" * 40),
            "draft_tree": "e" * 40,
            "document_digest": "f" * 64,
        }
    )
    assert current.semantic_key == DRAFT.semantic_key


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_kind", "draft"),
        ("source_id", "unrelated"),
        ("source_digest", "d" * 64),
    ],
)
def test_graduation_refuses_inconsistent_prepared_coordinates(field, value):
    with pytest.raises(ValidationError, match="disagree"):
        GraduationIntent(
            operation_id="op",
            issuer=ISSUER,
            shared=True,
            source=ENTRY,
            **{field: value},
        )


def test_graduation_projects_legacy_coordinates_from_the_typed_source():
    intent = GraduationIntent(
        operation_id="op", issuer=ISSUER, shared=True, source=ENTRY
    )
    assert (intent.source_kind, intent.source_id, intent.source_digest) == (
        ENTRY.kind,
        ENTRY.identity,
        ENTRY.digest,
    )


@pytest.mark.parametrize("ref", ["trunk", "refs/tags/x", "refs/heads/"])
def test_declared_delivery_target_requires_a_branch_ref(ref):
    with pytest.raises(ValidationError):
        DeliveryTarget(repository="owner/code", ref=ref)


def test_an_idea_is_not_a_prepared_draft():
    idea = EntityRef(
        identity="1:entry", document=".aitm/ideas/2026-11/20261127-1200-title.md"
    )
    with pytest.raises(ValidationError, match="draft document"):
        DraftSource(
            entity=idea,
            snapshot=DRAFT.snapshot,
            draft_tree=DRAFT.draft_tree,
            document_digest=DRAFT.document_digest,
        )
