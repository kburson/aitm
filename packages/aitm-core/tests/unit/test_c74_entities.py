"""Protect Core's generated entity metadata while allowing authored edits."""

from json import dumps

import pytest

from aitm_core.entities import validate_entity_authorship
from aitm_core.models.binding import EntityRef

SOURCE = EntityRef(
    identity="stable", document=".aitm/drafts/2026-11/20261127-1200-test/draft.md"
)
HEADER = {
    "schema": "aitm.intake/v1",
    "identity": "stable",
    "created": "utc",
    "slug": "test",
    "title": "Before",
    "tags": [],
}


def document(header):
    return f"---\n{dumps(header)}\n---\nBody\n".encode()


@pytest.mark.parametrize(
    "change",
    [{"identity": "stolen"}, {"created": "changed"}, {"state": "done"}, {"tags": 5}],
)
def test_entity_authorship_refuses_generated_or_invalid_fields(change):
    with pytest.raises(ValueError):
        validate_entity_authorship(SOURCE, document(HEADER), document(HEADER | change))


def test_title_and_tags_can_change_without_reassigning_the_entity():
    validate_entity_authorship(
        SOURCE, document(HEADER), document(HEADER | {"title": "After", "tags": ["new"]})
    )
