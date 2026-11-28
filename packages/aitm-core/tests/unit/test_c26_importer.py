"""C26's authored projection respects refreshed content and generated metadata."""

import pytest

from aitm_core.documents import _parse, canonicalize
from aitm_core.models.documents import DocumentSchema
from aitm_core.reviews.importer import _revised_document

PATH = ".aitm/stories/000/16/plan/current.md"


def _document(body, generated=b""):
    return (
        b"---\nschema: aitm.doc/v1\nstory: 16\nrole: plan\ntitle: Plan\n"
        + generated
        + b"---\n"
        + body
    )


def test_import_projects_reviewed_content_without_review_workspace_metadata():
    base = _document(b"Original\n", b'last-worktree: "review-branch"\n')
    final = _document(b"Revised \n", b'last-worktree: "review-branch"\n')
    refreshed = _document(b"Original\n", b'last-worktree: "story-16"\n')
    revised = _revised_document(16, PATH, refreshed, base, final)
    assert revised is not None
    assert _parse(revised).header["last-worktree"] == "story-16"
    assert _parse(revised).body == b"Revised \n"
    assert (
        canonicalize(revised, DocumentSchema()).canonical_sha256
        == canonicalize(final, DocumentSchema()).canonical_sha256
    )


@pytest.mark.parametrize("current", [b"Newer author edit\n", b"Already revised\n"])
def test_import_does_not_replace_newer_or_already_reviewed_content(current):
    base = _document(b"Original\n")
    final = _document(b"Already revised\n")
    refreshed = _document(current, b'updated: "2026-11-27"\n')
    assert _revised_document(16, PATH, refreshed, base, final) is None


@pytest.mark.parametrize(
    ("publication", "shared", "project"),
    [
        ("pending", True, False),
        ("not-applicable", True, False),
        ("verified", True, True),
        ("not-applicable", False, True),
    ],
)
def test_workspace_projection_is_fenced_until_authoritative_publication(
    publication, shared, project
):
    from aitm_core.models.common import PublicationOutcome
    from aitm_core.reviews.importer import _projection_admitted

    assert _projection_admitted(PublicationOutcome(publication), shared) is project
