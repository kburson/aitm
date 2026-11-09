---
schema: "aitm.review-response/v0"
level: "xpr"
story: 2
role: "reviewer"
round: 3
artifact_path: ".aitm/stories/000/2/design/core-design.md"
artifact_base_commit: "bcacb1378ca2cf268bb194cdf80f4fe21f155b2d"
artifact_digest: "sha256:5eaafbc1af04f13d4de25dcf5e9dacb35042ef775e0f230be89e4fba9452f3e7"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  effort: "high"
reviewer_session: "sha256:35a1a3958c703c369c77ad51a58d221a0d89a598752b450dcfc98a8a996b9cb8"
session_identity_kind: "native-fingerprint"
started_at: "2026-11-09T13:07:06.039Z"
submitted_at: "2026-11-09T13:08:46.410Z"
start_basis: "prior-submit"
start_source: "author-response-2.md"
finding_ids: []
answered_finding_ids: []
native_source: "native/spec/2026-11-09-core-design-review-48ae3de9ffa0067249b56573a8a3b1c8/review-48ae3de9ffa0067249b56573a8a3b1c8-reviewer-response-3.md"
native_source_digest: "sha256:a8fc63ffa0939b654a08e4b0d038259d6760ccc00d0d96637c48296b0f7439ae"
---

Mode: `normal`

## Summary

Accepted. This is round 3 of the separate full-file validation of `.aitm/stories/000/2/design/core-design.md`. The reviewer is Anthropic Opus 5.5 at effort high, in the same registered session; the author is gpt-6-astra (Codex). No required finding remains open. Every round-1 and round-2 finding has been verified as resolved against the freshly reread file.

### Fresh full-file reread

- **How it was read:** with the Read tool in chunks of at most 60 contiguous lines, during this round. The file changed in the author's turn, so the read restarted at line 1.
- **Ranges read:** 1–60, 61–120, 121–180, 181–240, 241–300, 301–360, 361–420, 421–480, 481–540, 541–600, 601–660, 661–720, 721–727. The final request (offset 721, limit 60) returned lines 721–726 and an empty display element 727, then stopped. That is EOF.
- **Observed line count:** 726 authored lines plus a terminating newline.
- **Native input artifact identity:** taken from this turn's package-generated response header; I did not recompute it, because shell access is unavailable in this session.
  - `artifact_digest` `sha256:5eaafbc1af04f13d4de25dcf5e9dacb35042ef775e0f230be89e4fba9452f3e7`
  - `artifact_blob` `3b83c1b5858036702f0993bfb7b48b21800d4a2f`
  - `artifact_commit` `013cdf2fd4ea753ae94cbb434d146fe5a284f61e`
- **Truncation:** none. A Grep for `^.{2000,}$` over the file found 0 matches, so no line was silently cut short.

### Preceding responses read

I read the complete `author-response-2.md`. My round-1 and round-2 reviewer responses and `author-response-1.md` were read in earlier rounds of this same session, and their dispositions are re-verified below against the current file.

### Independent checks of the author's factual claims

- **The plan's per-leaf boundary.** `.aitm/stories/000/2/plan/core-implementation-plan.md` line 66, under "Execution and evidence contract for every leaf", says: "Before Develop, create its design/plan/JIT records as required by the explicitly applicable policy. The accepted epic plan is input to those records, not an invented leaf acceptance." This confirms the author's statement that the accepted plan already treats parent decomposition as input to each leaf's own design, not as the leaf's acceptance.
- **Both dependency event directions exist in v0.** A Grep found `"type":"core.link.dependency-added"` 238 times across 69 `events.jsonl` files under `.aitm/stories/000/`, next to the `core.link.dependent-added` shape I cited in round 2. The FUR's pairing rule on line 673 therefore has real inputs on both sides.

### Verification of all dispositions

- **R1-F001, R1-F002, R1-F003: still resolved.** The round-2 fixes are intact in the current file:
  - kind source and split: FUR 268–269, 387–391, 413, 698;
  - the source-review record and its policy: 132–135, 496–502, 709;
  - the reconfiguration, pivot and pre-story editing/discard acceptance rows: 696, 700, 710.

  The round-3 edits did not regress any of them.
- **R2-F001: resolved by the author's alternative, which I accept.**
  - In round 2 I offered two resolutions: (a) a policy-expressible inherited coverage kind, or (b) an explicit statement that each decomposed leaf needs its own design. The author chose (b) and made it concrete.
  - FUR 397 makes `design_coverage = "own-document"` an explicit policy element. Line 127 includes it in the labeled fixture. A `parent-plan-section` or any other unsupported coverage mode is reported as unavailable, never inferred.
  - This is the architecture's Backlog rule ("Design accepted", architecture 115), and it matches the accepted implementation plan (line 66). So it is not a new owner decision, and it does not silently pick the review-depth matrix (397, 469).
  - My round-2 concern that leaves could never reach verified Done is answered: the route is an explicit own-document design plus whatever levels the selected policy requires. Its cost is a matter of review policy, which stays owner-open.
  - The other parts of the finding are also covered:
    - a typed `decompose` source route with a stable entity identity, using the same identity, publication, lost-response and finalization rules, with no synthesized draft (393–395, 642);
    - a separate `decomposition` estimate phase, with Refine requiring its own current record (277, 399);
    - parent design or plan changes making the child's provenance stale until reconciled (399);
    - unresolved dependency entries counting as a readiness condition (395);
    - a dedicated acceptance row (699).
- **R2-F002: resolved.**
  - FUR 671 makes the migration corpus inventory-driven over the pinned tip: every event type, key and header is mapped, kept opaque, or listed as a blocker.
  - Line 673 names the mappings for dependent/dependency pairing, plan-entry graduation, alias issuance without re-issue, and the decomposition estimate. It explicitly avoids claiming that a v1 descriptor or the `decompose` command existed historically.
  - Line 675 maps manual-bootstrap provenance to imported, non-runtime evidence; treats the synthesized draft as historical material only; and replaces absolute `last-worktree` paths with an opaque legacy ID that can never select a live checkout.
  - Line 687 extends the fixture and qualification set beyond #1/#2 to the full-corpus inventory plus representative decomposed leaves. Line 715 updates the Migration acceptance row to match.
- **Round-2 optional suggestions: both adopted.** The expansion paragraph is now split at a sentence boundary (552–554). I accept the author's reason for keeping physical lines bounded instead of joining them. The route for a leaf found oversized at Plan or JIT is now stated (391).

### Overall

The design matches the accepted architecture and the owner decisions, and it keeps every open owner choice open: the expansion-completion boundary, the second-trip cap, the review-depth matrix and the every-push audit (157, 469, 556, 726). Its contracts are internally consistent and specific enough to implement, and each contract now has a matching acceptance row. The implementation plan is downstream and must be reconciled with the round-1 to round-3 contract additions in its own separately authorized validation; as the author notes, this review did not change it.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. **Generalize the Graduation paragraphs to both source kinds (FUR 590, 594, 596).** These paragraphs still say "frozen draft snapshot", "a stable draft ID" and "moves the exact draft snapshot". Lines 393–395 state that `decompose` uses the same protocol, with entity identity `(store UUID, parent ID, entry key)` and frozen design/plan/entry digests, and that wins for a careful reader. Wording these three sentences as "frozen source (draft or plan entry)", and noting that for a plan entry finalization initializes the description from the typed descriptor instead of moving a draft, would stop a builder from implementing the one-intent-per-entity predicate for drafts only. This is not required: the rule is already established at 395 and covered by acceptance row 699.

## Decision

accepted
