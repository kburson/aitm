"""Validate story and stable-entity authored ownership."""

import pytest

from aitm_core.models.binding import EntityRef, StoryRef, allows_authored

STORY = ".aitm/stories/000/16"


@pytest.mark.parametrize(
    ("path", "allowed"),
    [
        ("draft.md", True),
        ("design/accepted.md", True),
        ("plan/deep/plan.md", True),
        ("attachments/drawing.txt", True),
        ("story.md", False),
        ("description.md", False),
        ("events.jsonl", False),
        ("operations/write.json", False),
        ("evidence/review.md", False),
        ("extension-owner/a.md", False),
        ("plan/reviews/original.md", False),
        ("plan/../draft.md", False),
    ],
)
def test_exact_story_authorship(path, allowed):
    assert allows_authored(StoryRef(story=16), f"{STORY}/{path}") is allowed


def test_entity_uses_stable_identity_and_exact_owned_paths():
    directory = ".aitm/drafts/2026-11/some-draft"
    entity = EntityRef(identity="draft-id-14", document=f"{directory}/draft.md")
    assert allows_authored(entity, entity.document)
    assert allows_authored(entity, f"{directory}/attachments/map.txt")
    assert not allows_authored(entity, ".aitm/drafts/2026-11/neighbor/draft.md")
    assert not allows_authored(entity, ".aitm/drafts/discarded/14.json")
    assert not allows_authored(entity, f"{STORY}/draft.md")
