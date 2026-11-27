"""Validate explicit selection and immutable typed document authority."""

from types import SimpleNamespace

import pytest

from aitm_core.models.attempts import BindingPurpose
from aitm_core.models.binding import StoryRef
from aitm_core.store.sync import PathSelection, _select, _validate_authored

BASE = ".aitm/stories/000/16/"
PLAN = BASE + "plan/current.md"
ATTACHMENT = BASE + "attachments/output.txt"


@pytest.fixture
def binding():
    return SimpleNamespace(
        purpose=BindingPurpose.PLANNING,
        paths=tuple(SimpleNamespace(path=path) for path in (PLAN, ATTACHMENT)),
        scope=StoryRef(story=16),
    )


@pytest.mark.parametrize(
    "path",
    [
        BASE + "events.jsonl",
        BASE + "story.md",
        BASE + "description.md",
        BASE + "evidence/receipt.md",
        BASE + "plan/scratch.md",
        ".aitm/stories/000/17/plan/current.md",
        "/tmp/unbound.md",
        BASE + "plan/../draft.md",
    ],
)
def test_sync_refuses_explicit_foreign_selection(binding, path):
    with pytest.raises(ValueError):
        _select(binding, PathSelection((path,)))


def test_deletion_is_an_explicit_part_of_selected_scope(binding):
    assert _select(binding, PathSelection((PLAN,), (ATTACHMENT,))) == (PLAN, ATTACHMENT)


def test_evidence_binding_has_no_authored_selection(binding):
    binding.purpose = BindingPurpose.EVIDENCE
    with pytest.raises(ValueError, match="no authored sync"):
        _select(binding, PathSelection((PLAN,)))


def typed(header, body="Plan"):
    return f"---\n{header}\n---\n{body}\n".encode()


HEADER = 'schema: aitm.doc/v1\nstory: 16\nrole: plan\nupdated: "2026-11-27"'


@pytest.mark.parametrize(
    "candidate",
    [
        b"Missing identity\n",
        typed(HEADER.replace("story: 16", "story: 17")),
        typed(HEADER.replace("role: plan", "role: design")),
        typed(HEADER.replace("2026-11-27", "2026-11-28")),
        typed(HEADER.replace("schema: aitm.doc/v1", "schema: aitm.doc/v9")),
    ],
)
def test_typed_documents_reject_identity_or_generated_edits(binding, candidate):
    with pytest.raises(ValueError):
        _validate_authored(binding, PLAN, typed(HEADER), candidate)


def test_typed_body_remains_authored(binding):
    _validate_authored(binding, PLAN, typed(HEADER), typed(HEADER, "Revised scope"))
