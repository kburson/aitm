<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-a9af7c6091f4f1719529a371c02f6f77"
role: "reviewer"
turn: 3
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/005/524/design/github-extension-design.md"
artifact_commit: "3764586c42c940ef3950e3ee95064fa22a9e5f8e"
artifact_blob: "f88d8caa1c9e1cbc353a127e60e9bd6691f15f88"
artifact_digest: "sha256:dd7b26b28322ebd03211717d0e5f7b4bd46c5f79eebe219a7a881383768d113d"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:0c13cad915596f8573c341829b1f37504efbaedb00fd577eb7fafa121ffe23b5"
  identity_source: "runtime"
started_at: "2026-11-27T06:13:28.603Z"
submitted_at: "2026-11-27T06:19:51.827Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I re-reviewed the revised artifact (blob `f88d8caa`) against R2-F001 and the author's round-two response. All three parts of R2-F001 are resolved.

- **R2-F001.1 (form and expressiveness) — resolved.** Comment selection is now a declarative v1 request input. It contains:
  - a predicate ID and version;
  - an optional inclusive creation window inside the request cutoff;
  - an optional allow-list of actor IDs;
  - literal UTF-8 body prefix and substring matches.

  Filter classes combine with AND, and alternatives within a class combine with OR. At least one literal body match is required. Lists are capped at 16 entries and literals at 256 bytes. Arbitrary regular expressions, callbacks and unsupported versions are refused. The grammar is pinned in the source schema, and the fixture exercises every operator. This is finite, bounded and qualifiable without M7. It is expressive enough for marker-based Timing Log recognition, so M7's independence claim now holds.
- **R2-F001.2 (evaluation and retention) — resolved.** The predicate is evaluated inside the adapter within the authorized bounds. Non-matching bodies stay in memory only and are never returned, persisted or logged. Only permitted counters, identifiers and response digests are retained. The text also states that downstream replay has no access to discarded bodies, which correctly limits what replay can claim.
- **R2-F001.3 (completeness evidence) — resolved.** Evaluated and selected counts are returned for each issue and page, together with the predicate ID, version and digest. The predicate digest uses the same RFC 8785 canonicalization as the record digests. A complete result must prove that every in-bound comment was evaluated. Missing-page and partial-evaluation negative cases are required.

Round-two optional suggestions 1–3 were also adopted:

- RFC 8785 canonical JSON is now used.
- Page digests are taken over the content-decoded bytes and are labeled as acquisition evidence.
- PR comments are explicitly excluded.

Nothing in the revision regresses the round-one resolutions (R1-F001 to R1-F006). The estimate, rank and cross-milestone handoff sections are unchanged and still consistent with the M7 design.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. Literal body matching is presumably exact, case-sensitive byte matching over the acquired raw UTF-8 bytes. Saying so explicitly in the schema would remove an implementation choice. The same applies to whether "prefix" is anchored at byte 0 or after leading whitespace or a BOM. The design already forbids normalization, so byte-0 anchoring is the consistent choice.
2. "Authors of requests can choose from the supported operators" could read as referring to GitHub issue authors. Consider "Requesters" or "Consumers".
3. Still optional and carried from earlier rounds: move the reference link line out from between "Acceptance and open decisions" and "Delivery handoff and sequencing".

## Decision

accepted
