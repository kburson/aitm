<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-d69706914b83ab63954983955c19e200"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
artifact_commit: "06952ccabe243e28caaa34afcda8fd92528cee5d"
artifact_blob: "55b2cc07cf11415bd37380294f68d6c5635a4508"
artifact_digest: "sha256:de790e294f141858ce526df6535c3de8c368ef7f466de79645622a556c68913d"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:0ffb2736ba16f3bda0f21bcb2b01de963d25567b5e97b12aa7409ba76d021bcf"
  identity_source: "runtime"
started_at: "2026-11-27T03:57:28.963Z"
submitted_at: "2026-11-27T04:03:16.733Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Re-reviewed the revised plan (blob `55b2cc07`) against author response 1 and the revised ledger. The crosswalk is unchanged. I did not recompute the SHA-256 digests of the supporting artifacts, because this review had shell access only for the submit command. The plan now requires digest re-verification during reconciliation readback, which covers this.

Turn-1 findings, re-verified:

1. **Integration-owner readiness — resolved.**
   - The trunk-sequence table now has a "Required sibling deliveries for trunk admission" column. For all 22 epics I checked that it lists every non-owner sibling exactly. The one exception is C60, which is deliberately excluded under the documented post-release exception.
   - Both the plan (Delivery bullet 3) and the ledger now state that these lists are mandatory admission relations, equivalent to directed sibling-to-merge edges. Readback verifies them and they are included in the topological proof. Resource-only Plan provisioning is explicitly not delayed.
   - No sibling depends on its own owner, apart from the declared C60 → C69 exception. Adding the relations therefore creates no cycle.
   - The earlier C34 / epic 11 mismatch is gone: C34 now waits on C30–C33, which matches its slice proof.
2. **Owner budget for new keys — resolved.** C94, C95, C96 and C101 are each stated as 3.5 h of contract work, tests and review plus 0.5 h of integration. C110 is stated as 3 h + 0.5 h and is listed at 3.5 h.
3. **Legacy-parity ownership and gates — resolved.**
   - A new epic 2 adds sized children C107–C110 (15 h).
   - The policy table covers the six undecided registrations and the recurring open questions from Changed/Mapped rows. Each entry has an evidence owner and the earliest JIT consumers.
   - The ledger adds hard C110 edges on C07, C28, C79 and C88.
   - Moving a decision to project policy is allowed while still recording it. C110's own proof only requires an explicit disposition or recorded uncertainty, so the hard edges don't contradict the project-policy option.
4. **Optional-package structure — resolved.** Both package epics name an integration owner. #228/#229 are moved out as standalone post-release follow-ups (7.5 h = 2 × 3.75 h). The Cost track is four children at 13.75 h, and #230 is explicitly placed after the wheel.

Recomputed arithmetic:

- **Children:** the 22 epic counts add up to 110, which is 89 retained plus 21 new (C90–C110).
- **Hours:** the epic hours add up to 386.5. Epic 2 is 4 + 3.5 + 4 + 3.5 = 15.
- **Epic and child bounds:** every Core epic has 4–6 children, and every child is ≤ 4 h.
- **Renumbering:** I mapped every epic's "Trunk prerequisites" column under the +1 renumbering. Each one matches the turn-1 graph. Where a child now has the C110 edge, its epic correctly lists epic 2: epics 3, 10, 15 and 20. Every entry points to a lower sequence number, so the order is still a valid topological order.

## Findings

1. Minor: the general instruction for new-child rows still says "add the named test first … implement the named port … run … Ruff". That doesn't fit C107–C110, which are `docs/architecture/legacy-sdlc/*.md` deliverables with no named test or port. The plan also refers to a C110 "trunk decision fixture" and "representative acceptance/refusal vectors" that C07, C28, C79 and C88 consume. But C110's only named path is a Markdown file, and the location and format of the consumable fixture aren't specified. JIT for C110 can settle this, and it doesn't block acceptance.

## Required changes

None.

## Optional suggestions

1. In the "New child contracts" preamble, exempt C107–C110 from the test-first/Ruff steps, or name the verification they use instead. Also name where C110's typed decision fixture or proof vectors live (for example, a machine-readable file beside `policy-decisions.md`), so the four gated consumers can point to an exact path at JIT.

## Decision

accepted
