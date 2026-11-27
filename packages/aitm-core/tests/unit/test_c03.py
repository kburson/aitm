"""Freeze the v1 YAML subset and authored-content hash inputs."""

import hashlib

import pytest

from aitm_core.documents import DocumentError, canonicalize, rewrite_metadata
from aitm_core.models.documents import DocumentSchema, Metadata

BASE = b"schema: aitm.doc/v1\nstory: 5\nrole: design\n"
BODY = "\r\nCafe\u0301 ·  \r\n".encode()


def document(header=b"", body=BODY, identity=BASE):
    return b"---\n" + identity + header + b"---\n" + body


def test_canonical_vectors():
    raw = document(
        b'title: "quoted \\"value\\""\n'
        b"decomposition: {z: 1e3, a: [333333333.33333329, 4.50, 2e-3, 1e-27]}\n"
        b'updated: "yesterday"\n'
    )
    expected = (
        '{"body":"\\r\\nCafe\u0301 ·  \\r\\n","document_schema":"aitm.doc/v1",'
        '"header":{"decomposition":{"a":[333333333.3333333,4.5,0.002,1e-27],"z":1000},'
        '"title":"quoted \\"value\\""},"role":"design","schema":"aitm.authored-content/v1","story":5}'
    ).encode()
    result = canonicalize(raw, DocumentSchema())
    assert result.canonical_sha256 == hashlib.sha256(expected).hexdigest()
    assert result.raw_sha256 == hashlib.sha256(raw).hexdigest()


@pytest.mark.parametrize(
    "key",
    [b"created", b"updated", b"last-branch", b"last-worktree", b"status"],
)
def test_generated_key_changes_only_the_raw_digest(key):
    before = canonicalize(document(key + b": before\n"), DocumentSchema())
    after = canonicalize(document(key + b": after\n"), DocumentSchema())
    assert before.canonical_sha256 == after.canonical_sha256
    assert before.raw_sha256 != after.raw_sha256


def test_rewrite_only_updates_metadata_and_preserves_exact_body():
    schema = DocumentSchema(semantic_fields={"score": "number"})
    raw = document(b"title: yes\nscore: 1e3\nupdated: old\nstatus: backlog\n")
    updated = rewrite_metadata(raw, Metadata(updated="new", status=None), schema=schema)
    assert updated.partition(b"---\n")[2].partition(b"---\n")[2] == BODY
    assert b'"updated": "new"' in updated
    assert b'"status"' not in updated
    assert (
        canonicalize(raw, schema).canonical_sha256
        == canonicalize(updated, schema).canonical_sha256
    )
    assert (
        canonicalize(raw, schema).raw_sha256 != canonicalize(updated, schema).raw_sha256
    )


def test_semantic_identity_binds_every_field():
    schema = DocumentSchema(semantic_fields={"note": "string"})
    header = (
        b"title: Example\nsource: input\nnote: memo\ndecomposition: {one: {hours: 2}}\n"
    )
    baseline = canonicalize(document(header), schema).canonical_sha256
    updates = [
        document(header, identity=BASE.replace(b"story: 5", b"story: 6")),
        document(header, identity=BASE.replace(b"role: design", b"role: plan")),
        document(header.replace(b"Example", b"Change")),
        document(header.replace(b"input", b"other")),
        document(header.replace(b"memo", b"changed")),
        document(header.replace(b"one", b"two")),
        document(header.replace(b"hours: 2", b"hours: 3")),
        document(header, body=BODY.replace(b"  ", b" ")),
    ]
    for raw in updates:
        assert canonicalize(raw, schema).canonical_sha256 != baseline


@pytest.mark.parametrize("plain", [b"yes", b"on", b"2026-11-27", b"0o12", b"01"])
def test_plain_non_json_scalars_are_strings(plain):
    schema = DocumentSchema()
    assert canonicalize(
        document(b"title: " + plain + b"\n"), schema
    ).canonical_sha256 == (
        canonicalize(document(b'title: "' + plain + b'"\n'), schema).canonical_sha256
    )


def test_json_resolution_and_integer_boundaries():
    schema = DocumentSchema(
        semantic_fields={"n": "number", "flag": "boolean", "nil": "null"}
    )
    assert canonicalize(
        document(b"n: 1e3\nflag: true\nnil: null\n"), schema
    ).canonical_sha256 == (
        canonicalize(
            document(b"n: 1000\nflag: true\nnil: null\n"), schema
        ).canonical_sha256
    )
    for value in (b"9007199254740991", b"-9007199254740991"):
        canonicalize(document(b"n: " + value + b"\n"), schema)
    for value in (
        b"9007199254740992",
        b"-9007199254740992",
        b"1e999",
        b"1e16",
        b"-1e20",
        b"9007199254740992.0",
        b"9007199254740991.9",
        b'"3"',
        b"01",
        b".inf",
    ):
        with pytest.raises(DocumentError):
            canonicalize(document(b"n: " + value + b"\n"), schema)


@pytest.mark.parametrize(
    "header",
    [
        b"title: hi\ntitle: bye\n",
        b"title: !!str 3\n",
        b"title: &anchor hi\nsource: *anchor\n",
        b"title: &single hi\n",
        b"title: [unfinished\n",
        b"title: false\n",
        b"title: 1e3\n",
        b"true: yes\n",
        b"unsupported: hi\n",
        b"decomposition: {x: {nested: true, nested: false}}\n",
        b"decomposition: {3: value}\n",
    ],
)
def test_rejects_unsupported_yaml(header):
    with pytest.raises(DocumentError):
        canonicalize(document(header), DocumentSchema())


def test_invalid_schema_body_or_metadata_fails_closed():
    with pytest.raises(DocumentError):
        canonicalize(document(identity=BASE.replace(b"v1", b"v2")), DocumentSchema())
    with pytest.raises(DocumentError):
        canonicalize(document(body=b"\xff"), DocumentSchema())
    with pytest.raises(ValueError):
        Metadata(title="outside generation scope")
