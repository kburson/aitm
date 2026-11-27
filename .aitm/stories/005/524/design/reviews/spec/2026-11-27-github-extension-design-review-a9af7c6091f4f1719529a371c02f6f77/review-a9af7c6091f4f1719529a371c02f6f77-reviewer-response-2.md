<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-a9af7c6091f4f1719529a371c02f6f77"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/005/524/design/github-extension-design.md"
artifact_commit: "ec9d4443c6644d3c12b1ff9a3af81b6924257ade"
artifact_blob: "af55b56f14fc648e3a087c403cc3f662beeb8c7d"
artifact_digest: "sha256:4f609ef4c63fec821bae5417f6299068a170fea508db4e787af5750ed465288b"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:0c13cad915596f8573c341829b1f37504efbaedb00fd577eb7fafa121ffe23b5"
  identity_source: "runtime"
started_at: "2026-11-27T06:13:28.603Z"
submitted_at: "2026-11-27T06:17:52.525Z"
finding_ids: ["R2-F001"]
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I re-reviewed the revised artifact (blob `af55b56f`) against each round-one finding and the author's dispositions. Five of the six findings are fully resolved. One new gap comes directly from the R1-F005 fix.

- **R1-F001 — resolved.** A post-cutoff `updated_at` is now described as observed activity: the acquired bytes "may postdate" the cutoff. Issue and comment flags are distinguished. The text states explicitly that neither flag proves a content edit or the bytes present at the cutoff.
- **R1-F002 — resolved.** Pull-request entries are identified by the `pull_request` member and excluded. The exclusion is counted in the receipt, and the fixture includes an excluded PR.
- **R1-F003 — resolved.** The design pins:
  - the raw Markdown JSON representation;
  - exact UTF-8 bytes without normalization;
  - lowercase SHA-256;
  - null encoded as absent with a null digest, and an empty string encoded as present with the zero-byte digest;
  - a record digest over canonical JSON with sorted keys and schema-defined array order;
  - page digests over the entity bytes fed to the parser.

  The fixture covers null and empty bodies.
- **R1-F004 — resolved.** The title, labels, state and state reason are in the initial payload. Actor IDs are opt-in under authorized field selection. Covered versus unsupported source kinds are enumerated: PRs, other comments, commit history, approval records and edit history are unsupported. Those kinds are reported in the handoff, so M7's sufficiency check is mechanical.
- **R1-F005 — partially resolved; see R2-F001.** Making comment selection a versioned request input removes the M2→M7 scheduling cycle, and the receipt records the predicate ID and version. However, the predicate's form and the evidence of its evaluation are not yet defined. As a result, "M7 chooses its own supported predicate at capture" may still be unsatisfiable without a new #525 change.
- **R1-F006 — resolved.** The "M2-owned GitHub legacy-source read adapter" is named. M7 owns parsing and normalization.

Two of my optional suggestions were also picked up:

- The children-count wording now applies per capability slice. This matches the roughly 12-child estimate table.
- Retry-After and rate-reset handling are now part of the handoff proof.

The cross-references and estimate sums are unchanged and still correct (44.5 h; PR row 19.5 h).

## Findings

### R2-F001 — The comment-selection predicate has no defined form, expressiveness or evaluation evidence

The revision makes comment selection "an explicit, versioned request input". #525 qualifies "the mechanism using a scoped fixture predicate and independently approved bounded live qualification predicate", and "M7 chooses its own supported predicate at capture." The independence claim, "This requires no M7 implementation or M7 policy approval for #525 to land", only holds if M7's eventual Timing Log predicate is expressible in the mechanism #525 ships and qualifies. The artifact does not say what that mechanism is. Three things are unspecified:

1. **Form and expressiveness.** It is unclear whether the predicate is a declarative, schema-versioned structure or something else. A declarative structure could include, for example, an author or actor allow-list, a leading-marker or heading match on the raw body, a bounded regular expression of a pinned dialect, and created-at bounds. An unbounded expression would conflict with the read-only, bounded adapter surface. Without a defined grammar, M7's trusted-formats decision (`history-import-design.md` line 44) could require a predicate the shipped adapter cannot evaluate. That would reintroduce the dependency R1-F005 aimed to remove, only discovered later at M7 intake.
2. **Where it is evaluated and what is retained.** To evaluate a body-content predicate, the adapter must read non-selected comments. "Other comments" are outside the contract and the consented field set. The design should say that non-matching comments are evaluated in memory only: their bodies are neither returned nor persisted, and logs and receipts carry at most counts or IDs, as the schema permits.
3. **Completeness evidence.** A `complete` result must prove that every comment within the requested bounds was evaluated against the predicate, not merely that every returned comment matched. M7 must "reproduce its capture decisions". For that, the receipt or result needs at least the count of comments evaluated versus selected for each issue or page. It also needs the predicate ID, version and digest. Without the evaluated count, an under-read comment page and a correctly filtered page look identical.

## Required changes

1. Define the comment-selection predicate as a declarative, schema-versioned structure with an explicitly bounded grammar. Its supported operators must be pinned in the versioned source schema. Qualification should exercise each operator with the fixture predicate (R2-F001.1).
2. State that the predicate is evaluated inside the adapter, and that non-matching comment bodies are not returned, persisted or logged. Only the permitted counts or IDs are retained (R2-F001.2).
3. Require the result and receipt to carry evaluated versus selected comment counts per bound, plus the predicate ID, version and digest. A `complete` result must assert that every in-bound comment was evaluated (R2-F001.3).

## Optional suggestions

1. "UTF-8 canonical JSON … with sorted keys" leaves number formatting and string escaping open. Citing RFC 8785 (JSON Canonicalization Scheme), or an equivalent pinned rule, would make record digests byte-reproducible across implementations.
2. "Page digests cover the exact response entity bytes fed to the JSON parser" could state explicitly that this means the bytes after content-decoding (for example, after gzip). It could also state that page digests are acquisition evidence and are not expected to reproduce on a live reread.
3. If comments are ever listed through the repository-wide `GET /repos/{owner}/{repo}/issues/comments` endpoint instead of per issue, those comments include PR comments. Note that the PR exclusion also applies to comments whose parent is an excluded PR entry.
4. Unchanged from round one and still optional: the reference link line sits between "Acceptance and open decisions" and "Delivery handoff and sequencing".

## Decision

revisions-requested
