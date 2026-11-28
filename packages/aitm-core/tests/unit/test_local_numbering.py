"""The allocator reserves every valid numbered path at its pinned frontier."""

import pytest

from aitm_core.providers.local import next_number


@pytest.mark.parametrize(
    ("paths", "expected"),
    [
        ((), 1),
        ((".aitm/stories/000/1/events.jsonl",), 2),
        ((".aitm/stories/000/99/story.md",), 100),
        ((".aitm/stories/001/100/story.md",), 101),
        ((".aitm/stories/123/12345/story.md",), 12346),
        ((".aitm/stories/000/9/story.md", ".aitm/stories/000/2/events.jsonl"), 10),
        ((".aitm/stories/000/9/story.md", ".aitm/stories/000/9/events.jsonl"), 10),
        ((".aitm/stories/009/900/attachments/blob",), 901),
        ((".aitm/drafts/000/99/story.md", "docs/stories/009/900/story.md"), 1),
    ],
)
def test_number_follows_every_reserved_story(paths, expected):
    assert next_number(iter(paths)) == expected


@pytest.mark.parametrize(
    "path",
    [
        ".aitm/stories/000/0/story.md",
        ".aitm/stories/001/99/story.md",
        ".aitm/stories/000/001/story.md",
        ".aitm/stories/000/one/story.md",
        ".aitm/stories/000/٢/story.md",
        ".aitm/stories/000/12",
    ],
)
def test_invalid_story_path_refuses_allocation(path):
    with pytest.raises(ValueError, match="story path"):
        next_number([path])
