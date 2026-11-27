<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-da800297e0b0c147b91cbdf5f1aad338"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/005/522/design/history-import-design.md"
artifact_commit: "8862808e2dd2062df1c0d2e156e6711c2dbaabbb"
artifact_blob: "7eaa5a2ebba5e647ff6fe4651a89efd5cf4f3842"
artifact_digest: "sha256:d44646dd8a917a4ff7588d3582503604514bc869db24e219c43a5aba455a7556"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:95893d0f86ac4fe1742705c376e1ca0f6d6c9a5fed1c21c230c0310a96695d6b"
  identity_source: "runtime"
started_at: "2026-11-27T06:13:32.030Z"
submitted_at: "2026-11-27T06:14:36.517Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Reviewed `history-import-design.md` at the pinned blob against its two linked handoffs: M2 `github-extension-design.md` (§ Read-only source access for M7, § Delivery handoff and sequencing) and M8 `rubric-design.md` (§ Validated history handoff, § Corpus and label admission).

The draft has sound scope and ownership boundaries. M7 owns capture, normalization, provenance and reproducibility. M8 owns comparability and sufficiency. #525 owns the adapter. The M7 → M8 handoff field list matches what M8 pins: manifest location/digest, schema version, scope/cutoff, dispositions, source digests, validation receipt and read fixture. The estimate table sums to 18.5, every row is ≤ 4 h, and rank 260 sits correctly between M2 (250) and M8 (270). Missing-Actual handling and quarantine rules line up with M8's admission rules.

Four places don't line up with the M2 source contract M7 consumes. Each would cause ambiguity or a false failure during implementation or qualification:

- replay determinism versus live drift;
- the identity key's "revision" component;
- commit/approval evidence that has no source contract yet;
- the order of the Timing Log predicate decision relative to #525.

One smaller issue concerns replay access to restricted raw evidence.

## Findings

1. **Exact-hash replay on "repeated extraction" conflicts with M2's live-drift semantics.** Import step 2 says "Match exact hashes and counts on repeated extraction and fresh checkout." M2 § Read-only source access says "Exact replay reads the captured manifest and bytes. A live reread has its own acquisition time and may drift," and "Do not infer a repository-wide snapshot guarantee from a live list response." If "repeated extraction" means a second live crawl, an ordinary edit to a legacy issue or comment makes the acceptance check fail. Determinism has to be defined over the captured snapshot. A live reread should give a reported diff against that snapshot, such as later-edited, added or removed items, and not a pass/fail hash match. The § Acceptance bullet "A second reader reproduces import identity, counts, digests…" has the same ambiguity.

2. **The identity key's "revision" has no defined source.** § Source inventory says identity keys bind "source repository, original issue, evidence kind, and revision," and each item is bound to "revision and content digest." The M2 payload returns IDs, created/updated/closed timestamps, body bytes and a digest. It returns no revision identifier, and GitHub REST issue and comment bodies have no native revision number. M2 also says an item updated after the cutoff is flagged *later-edited*, and its bytes "cannot claim those bytes reflect the past cutoff." The design doesn't say:
   - what "revision" means (for example `updated_at` plus content digest at acquisition);
   - how the M2 *later-edited* flag maps to an M7 disposition.

   This matters for M8, which requires a *pre-execution* estimate revision. An issue body with phase estimates that was edited after work began, or after the cutoff, can't prove estimate chronology from its current bytes. Corpus contract line 29 ("unproved estimate chronology stay visible without creating numeric labels") covers the outcome, but the link from *later-edited* to that disposition should be stated explicitly.

3. **Commit and approval evidence is listed as captured, but M2 gives it no source contract.** § Source inventory says to capture "supported commit or approval evidence." M2 limits the initial #525 surface to issue bodies, approved Timing Log comments and minimal metadata, and says "Commit or adjacent evidence needs its own contract before becoming a required source." § Handoff receipts also requires refusal when the handoff's "allowed evidence … [doesn't] cover the requested corpus." As written, M7 could refuse its own #525 handoff, or it could silently depend on an unspecified second adapter. Either mark commit/approval evidence as an optional later source with an explicit *source-unsupported* disposition, or name the contract and owner that provide it. The § Refinement estimate exclusion ("It excludes the #525 adapter") also leaves no budget for a commit-evidence reader if one is needed.

4. **The Timing Log predicate decision is scheduled after a step that needs it.** § Acceptance lists "trusted Timing Log formats" among decisions to resolve "before implementation pickup" of M7. M2 § Read-only source access says "Pin M7's approved Timing Log selection predicate and its version in the qualification configuration," and #525's handoff proof pins "expected evidence markers" at JIT. That makes the M7-owned predicate (selection rule plus version) an input to #525 qualification, which comes before M7 pickup. The design should say M7 delivers a versioned Timing Log selection predicate to #525 before #525's live qualification. Full format trust and parsing rules can stay a later M7 decision. Otherwise #525 either invents the predicate or qualifies against an unpinned one.

5. **Second-reader replay versus restricted raw evidence (minor).** § Corpus contract keeps "bulk raw logs and excluded sensitive material outside the default publishable view," and raw storage "requires an authorized retention boundary." § Acceptance requires a second reader to reproduce identity, counts, digests and dispositions "from the manifest and permitted evidence." If normalization inputs are withheld, the second reader can't re-run normalization. They can only confirm digests. The design should state which replay is required: full re-normalization from a restricted replay bundle inside the retention boundary, or digest-only verification of the publishable view. The M8 handoff's "receipt must show independent replay" depends on the answer.

## Required changes

1. Findings 1 and 5 (mostly 1). Reword Import step 2 and the first Acceptance bullet so that exact hash and count equality is required for replay from the captured snapshot and on a fresh checkout. A live re-extraction should produce a drift report (later-edited, added or removed) against the pinned snapshot and should not be a hash-equality check.
2. Finding 2. Define the "revision" component of the identity key in terms of fields M2 actually returns, for example `updated_at` plus the content digest at acquisition. Map M2's *later-edited* result to an explicit M7 disposition that blocks estimate-chronology qualification unless it is proven separately.
3. Finding 3. Reclassify commit/approval evidence as optional, with a *source-unsupported* disposition until a separate source contract exists, or name that contract and owner. Make sure the Handoff receipts coverage check doesn't refuse #525 for lacking commit evidence.
4. Finding 4. Add to Handoff receipts or Acceptance that M7 supplies a versioned Timing Log selection predicate to #525 before #525's live qualification. Keep full format trust and parsing as an M7 pre-pickup decision.

## Optional suggestions

1. Finding 5. State which replay the second reader performs (re-normalization from a restricted replay bundle, or digest-only verification of the publishable view) and who may hold the restricted bundle.
2. Align the decomposition labels in § Acceptance ("source access and inventory … publication") with the estimate table rows. "Source access" suggests the #525 adapter, which the estimate explicitly excludes. "Pinned intake and bounded source inventory" is the clearer label.
3. "Exercise a complete pair if supported" could name what makes a pair complete in M7's terms: estimate revision, completed attempt/outcome and qualified Actual. That would make it checkable against M8's admission rule.

## Decision

revisions-requested
