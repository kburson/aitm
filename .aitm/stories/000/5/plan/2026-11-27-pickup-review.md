# #5 Pickup review

Grok 4.7 Build Fast. The revised pickup resolved the round-one findings about exact canonical identity coverage, scalar resolution and the revalidated generated-only rewrite.

**PASS**

No remaining blocker. The exact acceptance vectors close the prior admission gaps.

- An unsupported version fails with no migration path, while a different supported schema identity changes the canonical digest.
- The canonical object binds `schema: aitm.authored-content/v1`, `document_schema`, `story`, `role`, the full typed semantic `header`, and the exact `body`, hashed as UTF-8 RFC 8785. The raw SHA-256 is a separate digest of the complete file bytes.
- An external RFC 8785 number, string-escaping, and key-order vector is required on the pinned serializer. Story, role, title, source, nested decomposition, schema-declared semantic fields, and exact body bytes each move the canonical digest.
- Each generated key (`created`, `updated`, `last-branch`, `last-worktree`, `status`) keeps the canonical digest stable and changes the raw digest. Typed Metadata writes only those keys, preserves the semantic header and the exact UTF-8 body after the closing fence (blank lines and original line endings), revalidates, recomputes both digests, and refuses a rewrite that changes canonical identity.
- Aliases, anchors, and explicit tags are rejected. Parsing stays on the base scanner/composer, with scalar resolution in Core and no YAML constructors or default scalar inference. Duplicate and non-string keys, malformed values, unsupported keys, and type mismatches fail. Quoted values and plain scalars such as dates, `yes`, `on`, `0o12`, and `01` stay strings. Only JSON booleans, null, and number grammar resolve, with integers inclusive of ±(2^53−1), nonfinite and out-of-range values rejected, and `1e3` covered. The full decomposition map is semantic hash input; C72 keeps descriptor interpretation.
- `rfc8785` and `ruamel.yaml` stay the installed #3 pins. The manifest and lock stay unchanged. Import, bind/recover, and document acceptance stay outside this leaf. The #470 pin remains `3ee8b2cbd0aedc0bb9b2fce0f01631ae9730c644` on the stated C03 paths.

Reviewed plan SHA-256 8e4e78633e4c5a5ec6782c83695055f8fdfbe5e9b7f81abbb2baddaaa48ada50.
