"""Verify v1 authored byte ownership and metadata update boundaries."""

import pytest

from aitm_core.documents import DocumentError, canonicalize, rewrite_metadata
from aitm_core.models.documents import DocumentSchema, Metadata
from tests.unit.test_c03 import BASE, BODY, document


@pytest.mark.parametrize(
    ("raw", "reason"),
    [
        pytest.param(
            b"\n" + document(), "opening frontmatter", id="preamble-before-header"
        ),
        pytest.param(b"---\n" + BASE, "closing frontmatter", id="unterminated-header"),
        pytest.param(b"---\n- not a mapping\n---\n", "one mapping", id="list-header"),
        pytest.param(
            document(b"title: \xff\n"),
            "invalid document frontmatter",
            id="invalid-header-encoding",
        ),
        pytest.param(
            b"---\n%YAML 1.2\n" + BASE + b"---\n",
            "directives",
            id="yaml-directive",
        ),
    ],
)
def test_frontmatter_has_exact_document_boundary(raw, reason):
    with pytest.raises(DocumentError, match=reason):
        canonicalize(raw, DocumentSchema())


@pytest.mark.parametrize(
    "identity",
    [
        pytest.param(BASE.replace(b"story: 5", b"story: true"), id="boolean-story"),
        pytest.param(BASE.replace(b"story: 5", b"story: 0"), id="zero-story"),
        pytest.param(BASE.replace(b"role: design\n", b""), id="missing-role"),
    ],
)
def test_authored_identity_has_a_real_story_and_role(identity):
    with pytest.raises(DocumentError, match="positive story ID and nonempty role"):
        canonicalize(document(identity=identity), DocumentSchema())


@pytest.mark.parametrize(
    "owned",
    [
        pytest.param("role", id="document-identity"),
        pytest.param("last-worktree", id="generated-metadata"),
        pytest.param("title", id="built-in-authorship"),
    ],
)
def test_custom_schema_cannot_take_over_a_v1_owned_field(owned):
    schema = DocumentSchema(semantic_fields={owned: "string"})
    with pytest.raises(DocumentError, match="cannot override v1 ownership"):
        canonicalize(document(), schema)


def test_noop_generated_update_preserves_even_frontmatter_formatting():
    original = document(b"title: 'quoted'\nupdated: old  # keep comment\n")
    assert rewrite_metadata(original, Metadata(updated="old")) == original


def test_metadata_patch_preserves_unset_fields_and_uses_wire_alias():
    original = document(b"created: original\nlast-branch: old\nstatus: review\n")
    rewrite = rewrite_metadata(original, Metadata(last_branch="codex/work"))
    assert b'"last-branch": "codex/work"' in rewrite and b'"last_branch"' not in rewrite
    assert b'"created": "original"' in rewrite and b'"status": "review"' in rewrite
    assert (
        canonicalize(rewrite, DocumentSchema()).canonical_sha256
        == canonicalize(original, DocumentSchema()).canonical_sha256
    )


def test_metadata_update_preserves_crlf_fences_and_body_bytes():
    original = b"---\r\n" + BASE.replace(b"\n", b"\r\n") + b"---\r\n" + BODY
    result = rewrite_metadata(original, Metadata(updated="now"))
    assert result.startswith(b"---\r\n")
    header, _, body = result[5:].partition(b"---\r\n")
    assert b"\n" not in header.replace(b"\r\n", b"")
    assert body == BODY


def test_authored_text_is_not_unicode_normalized_during_identity_calculation():
    composed = document(body="Café\n".encode())
    decomposed = document(body="Cafe\u0301\n".encode())
    assert (
        canonicalize(composed, DocumentSchema()).canonical_sha256
        != canonicalize(decomposed, DocumentSchema()).canonical_sha256
    )
