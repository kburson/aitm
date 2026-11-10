---
schema: "aitm.review-response/v0"
level: "xpr"
story: 181
role: "reviewer"
round: 2
artifact_path: ".aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md"
artifact_base_commit: "3c4815fb6e42a5372f9f99fad5453c4a535e0169"
artifact_digest: "sha256:147cbee5740f725c9c65df9c09034912220d179475dc1c707e0844316a6c1c80"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  effort: "high"
reviewer_session: "sha256:ff8a11f512bd9ed26aac55367574791ae964359ddeb6d2365a98f8fe2916149f"
session_identity_kind: "native-fingerprint"
started_at: "2026-11-10T21:00:55.597Z"
submitted_at: "2026-11-10T21:01:35.989Z"
start_basis: "prior-submit"
start_source: "author-response-1.md"
finding_ids: []
answered_finding_ids: []
native_source: "native/plan/2026-11-10-story-timing-dashboard-implementation-plan-review-f5ba57dde8773c6e0ff6937ff556822e/review-f5ba57dde8773c6e0ff6937ff556822e-reviewer-response-2.md"
native_source_digest: "sha256:10ff9f23fcd1d32f45186cfc296df59c8b4952b8b31047685bc52774441aab15"
---

Mode: `normal`

## Summary

I re-reviewed the revised plan at commit `aa2ae50` (blob `04540fa`, raw SHA-256 `147cbee5…1c80`). I checked it against my turn-1 required changes, author response 1, the accepted design and the #181 seed registration in `events.jsonl` line 3. All five required changes are resolved, and the five optional suggestions were adopted. The revised estimates add up: A01 is 3.75 h, A totals 20.0 h, B totals 6.0 h, and the overall total is 26.0 h. The dependency table is unchanged and still acyclic.

How each turn-1 required change was resolved:

1. **Seed admission.** A01 now admits only #181's existing `historical-actual-backfill` event. It binds `data.receipt_sha256` to the exact JSON path in `data.evidence` and to the design digest `8d619b60…b139`. It ignores the Markdown companions and rejects a wrong story, path or digest, or a second purported seed. Missing typed dimensions stay Unknown. Line 47 states that new registrations use the v1 shape and that the legacy event is read without being rewritten. This matches the actual registration shape.
2. **Verification ownership.** A01 now owns an embedded `verification` record in the usage receipt, with named fields. A04 binds the report identity, source digest, subject, selector, rate basis, coverage and sanitized data digest to that record and to an attributable registration. A missing or mismatched record leaves Cost Unknown. A04 no longer needs to change A01's files.
3. **Seed parity.** A03 and A05 now assert parity at a fixed historical pin, `17761cc1…2b8`. Two preconditions are asserted in the fixture: no same-actor overlaps across stories, and measured descendants equal to the seed's `counted_children`. A later graph change or overlap is reported with scoped provenance instead of breaking parity. The author says the pinned tree was checked independently (author response 1, Verification). Because the fixture asserts both preconditions, a wrong claim would fail red instead of passing silently.
4. **Registration conflicts.** A01's test now covers an identical duplicate registration (one receipt), conflicting digests or a rewritten payload at the same path (held), and a subject or scope mismatch (held).
5. **Watermarks and provenance.** B01's test now asserts the commit with its committer time, the as-of, the usage selector, cutoff and rate basis, and the per-measure evidence-through UTC and basis, including an Unknown-watermark row. The B01 browser check and B02 both observe watermarks and evidence basis.

The optional items adopted:
- An estimate scope fixture in A01.
- An explicitly no-op identical retry in A06.
- A full lowercase 40-hex commit pin, with refs and abbreviations rejected.
- Checks that outputs resolve physically outside any worktree, in both CLIs.
- Named canonical JSON serialization rules in A05.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. A05 and B01 each implement the check that the output path resolves physically outside any worktree. B01 already depends on A05, so it could import A05's helper instead of keeping a second copy. That keeps the symlink and alias handling identical in both CLIs.
2. Name what `sanitized_data_sha256` covers in the embedded verification record, for example a canonical serialization of the receipt's usage rows without the `verification` object. A receipt cannot contain its own whole-file digest. Without a named basis, the A01 validator and the A04 binding could compute different digests.
3. The full lowercase 40-hex commit pin assumes a SHA-1 repository. Note in `capture.md` that a SHA-256 object-format repository is unsupported and fails closed until the pin rule changes.

## Decision

accepted
