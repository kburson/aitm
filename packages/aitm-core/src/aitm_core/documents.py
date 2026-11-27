"""Validate the strict v1 frontmatter subset and identify authored content."""

import json
import math
import re
from dataclasses import dataclass
from hashlib import sha256

import rfc8785
from pydantic import JsonValue
from ruamel.yaml import YAML, YAMLError
from ruamel.yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode
from ruamel.yaml.tokens import AliasToken, AnchorToken, DirectiveToken, TagToken

from aitm_core.models.documents import (
    CANONICAL_SCHEMA,
    ContentIdentity,
    DocumentSchema,
    Metadata,
)

_IDENTITY_KEYS = {"schema", "story", "role"}
_GENERATED_KEYS = {"created", "updated", "last-branch", "last-worktree", "status"}
_DEFAULT_SEMANTIC_TYPES = {
    "title": "string",
    "source": "string",
    "decomposition": "object",
}
_STRICT_TYPES = {
    "array": (list,),
    "boolean": (bool,),
    "integer": (int,),
    "null": (type(None),),
    "number": (int, float),
    "object": (dict,),
    "string": (str,),
}
_JSON_LITERALS = {"true": True, "false": False, "null": None}
_JSON_NUMBER = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?")
_MAX_INTEGER = 2**53 - 1
_NON_SUBSET = (AliasToken, AnchorToken, DirectiveToken, TagToken)
_OPEN_FENCE = (b"---\n", b"---\r\n")
_CLOSE_FENCE = (*_OPEN_FENCE, b"---")


class DocumentError(ValueError):
    """Input does not match the supported document contract."""


@dataclass(frozen=True, slots=True)
class _Document:
    opening: bytes
    closing: bytes
    body: bytes
    header: dict[str, JsonValue]


def _scalar(node: ScalarNode) -> JsonValue:
    value = node.value
    if node.style is not None:
        return value
    if value in _JSON_LITERALS:
        return _JSON_LITERALS[value]
    if not _JSON_NUMBER.fullmatch(value):
        return value
    if any(marker in value for marker in ".eE"):
        number = float(value)
        if not math.isfinite(number):
            raise DocumentError("nonfinite frontmatter number")
        # Binary64 values beyond this bound are integral even when the token
        # used decimal or exponent syntax. Refuse them before hashing.
        if abs(number) > _MAX_INTEGER:
            raise DocumentError(
                "frontmatter integer is outside the interoperable range"
            )
        return number
    try:
        integer = int(value)
    except ValueError as error:
        raise DocumentError(
            "frontmatter integer is outside the interoperable range"
        ) from error
    if abs(integer) > _MAX_INTEGER:
        raise DocumentError("frontmatter integer is outside the interoperable range")
    return integer


def _resolve(node: Node) -> JsonValue:
    if isinstance(node, ScalarNode):
        return _scalar(node)
    if isinstance(node, SequenceNode):
        return [_resolve(item) for item in node.value]
    if isinstance(node, MappingNode):
        result: dict[str, JsonValue] = {}
        for key_node, value_node in node.value:
            key = _scalar(key_node) if isinstance(key_node, ScalarNode) else None
            if not isinstance(key, str):
                raise DocumentError("frontmatter mapping keys must be strings")
            if key in result:
                raise DocumentError(f"duplicate frontmatter key: {key}")
            result[key] = _resolve(value_node)
        return result
    raise DocumentError("unsupported frontmatter value")


def _parse(raw: bytes) -> _Document:
    lines = raw.splitlines(keepends=True)
    if not lines or lines[0] not in _OPEN_FENCE:
        raise DocumentError("document requires opening frontmatter")
    close = next(
        (index for index in range(1, len(lines)) if lines[index] in _CLOSE_FENCE), None
    )
    if close is None:
        raise DocumentError("document requires a closing frontmatter fence")
    try:
        raw_header = b"".join(lines[1:close]).decode("utf-8")
        scanner = YAML(typ="base", pure=True)
        if any(isinstance(token, _NON_SUBSET) for token in scanner.scan(raw_header)):
            raise DocumentError(
                "YAML anchors, aliases, directives and explicit tags are unsupported"
            )
        parsed = YAML(typ="base", pure=True).compose(raw_header)
        if not isinstance(parsed, MappingNode):
            raise DocumentError("frontmatter must contain one mapping")
        header = _resolve(parsed)
        assert isinstance(header, dict)
    except (UnicodeError, YAMLError, RecursionError) as error:
        raise DocumentError("invalid document frontmatter") from error
    return _Document(lines[0], lines[close], b"".join(lines[close + 1 :]), header)


def _identity(raw: bytes, doc: _Document, schema: DocumentSchema) -> ContentIdentity:
    header = doc.header
    story, role = header.get("story"), header.get("role")
    if header.get("schema") != schema.name:
        raise DocumentError("unsupported document schema")
    if type(story) is not int or story < 1 or not isinstance(role, str) or not role:
        raise DocumentError("document requires a positive story ID and nonempty role")

    protected = _IDENTITY_KEYS | _GENERATED_KEYS | _DEFAULT_SEMANTIC_TYPES.keys()
    if protected.intersection(schema.semantic_fields):
        raise DocumentError("additional semantic fields cannot override v1 ownership")
    semantic_types = _DEFAULT_SEMANTIC_TYPES | schema.semantic_fields
    semantic: dict[str, JsonValue] = {}
    for key, value in header.items():
        if key in _IDENTITY_KEYS:
            continue
        if key in _GENERATED_KEYS:
            if type(value) not in (str, type(None)):
                raise DocumentError(f"invalid generated value: {key}")
            continue
        kind = semantic_types.get(key)
        if kind is None or type(value) not in _STRICT_TYPES[kind]:
            raise DocumentError(
                f"unsupported or incorrectly typed semantic field: {key}"
            )
        semantic[key] = value
    try:
        canonical = rfc8785.dumps(
            {
                "schema": CANONICAL_SCHEMA,
                "document_schema": schema.name,
                "story": story,
                "role": role,
                "header": semantic,
                "body": doc.body.decode("utf-8"),
            }
        )
    except (UnicodeError, rfc8785.CanonicalizationError, RecursionError) as error:
        raise DocumentError("invalid canonical authored content") from error
    return ContentIdentity(
        canonical_sha256=sha256(canonical).hexdigest(),
        raw_sha256=sha256(raw).hexdigest(),
    )


def canonicalize(raw: bytes, schema: DocumentSchema) -> ContentIdentity:
    """Hash the authored meaning and the full raw bytes independently."""
    return _identity(raw, _parse(raw), schema)


def rewrite_metadata(
    raw: bytes, generated: Metadata, *, schema: DocumentSchema | None = None
) -> bytes:
    """Update only generated metadata and confirm that authorship is unchanged."""
    schema = DocumentSchema() if schema is None else schema
    original = _parse(raw)
    before = _identity(raw, original, schema)
    header = original.header.copy()
    for key, value in generated.model_dump(by_alias=True, exclude_unset=True).items():
        if value is None:
            header.pop(key, None)
        else:
            header[key] = value

    if header == original.header:
        return raw
    separator = original.opening[3:]
    encoded = json.dumps(header, ensure_ascii=False, allow_nan=False, indent=2).encode(
        "utf-8"
    )
    rewritten = original.opening + encoded.replace(b"\n", separator) + separator
    rewritten += original.closing + original.body
    after = canonicalize(rewritten, schema)
    if before.canonical_sha256 != after.canonical_sha256:
        raise DocumentError("generated metadata update changed authored content")
    return rewritten
