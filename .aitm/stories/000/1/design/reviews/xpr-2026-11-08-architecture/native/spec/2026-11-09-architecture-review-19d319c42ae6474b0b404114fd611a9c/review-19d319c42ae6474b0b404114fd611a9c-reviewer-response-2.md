<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-19d319c42ae6474b0b404114fd611a9c"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/1/design/architecture.md"
artifact_commit: "572a1772005290bcfcee8531bf5955f7b7d7bbed"
artifact_blob: "74dfc233067be07a20d73623c50e7587fbd5104c"
artifact_digest: "sha256:cf16a5b22f6eaf643885f6694f35d82181a684c36e1b4f2595fb4c8016138b93"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:767689f69b20228949123d8faba84671fb404a4027e939125a5f4ad422c4d3a4"
  identity_source: "runtime"
started_at: "2026-11-09T03:53:44.261Z"
submitted_at: "2026-11-09T04:01:23.491Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Accepted. This is round 2 of the XPR review, run by the same registered reviewer session. I read author-response-1 in full and re-read the complete revised FUR at the digest in the frontmatter above. I checked each disposition against the round-1 finding, the decision record (`../draft.md`), the context-only core design and the master plan. Then I re-read the whole FUR for regressions and new contradictions introduced by the additions. I made no network calls this round. The author reports checking the GitHub Pages publishing-source constraint (root or `/docs` for branch publishing; custom Actions as a separate route) against primary documentation, which closes the gap I flagged as unverified in R1-F005.

All five round-1 findings are resolved:

- **R1-F001 (content-bound acceptance vs machine-owned frontmatter): resolved.** FUR line 136 binds acceptance to a versioned canonical authored-content digest that excludes only schema-defined generated metadata. It states that regenerating metadata never invalidates acceptance and any authored-content change does, and keeps full-file digests and patches as separate reconstruction evidence. This keeps the owner's `[user]` per-file frontmatter requirement (draft line 96) instead of removing it, which is the better of the two options I offered. Line 140 deals with migrating existing v0 byte-bound records without retroactively labelling later bytes accepted, and line 226 adds canonicalisation and migration to the core-reconciliation obligations.
- **R1-F002 (interim procedure vs M1 guards): resolved.** Line 140 limits the planning checkout to pre-M1, requires an M1 import of the revised FUR and review folder through the compare-and-swap writer, restricted to the story's paths, before the checkout is retired, and states that a review branch derived from planning is a distinct ref that git, harness and core guards must permit while still protecting the planning ref. Line 226 adds the M1 import to the core obligations. This matches the master plan's M1 retirement and does not change any milestone.
- **R1-F003 (delivery evidence): resolved.** Line 167 adds verified delivery/merge status to the git-host role. Line 130 defines the delivered version as the reviewed source head or deliverable that the delivery mechanism verifies as landed, with no SHA equality required after squash or rebase merges. It rules out "issue closed" as proof, requires core-only and offline delivery evidence, and keeps an unverifiable remote target pending. These are consistent with Goal 1: a pending verification is a substantive, retryable condition, not fabricated evidence. The clock still stops at passing PR review (line 128).
- **R1-F004 (config authority): resolved.** Line 85 names the default branch's committed `.aitm.toml`, read from its fetched ref, as the policy authority. Story-branch policy edits take effect only after delivery, and each transition records the effective policy revision. The closing clause ("must not silently substitute an agent-edited policy for the authoritative one") also covers the case I checked for regression: a story branch editing the ref-selection setting itself (`[store] trunk`) to point the policy lookup at its own branch.
- **R1-F005 (Pages workflow-ref constraint): resolved.** Line 209 applies the workflow-ref constraint to the Pages build, permits a non-push trigger with disclosed freshness, and keeps the every-push audit requirement (lines 93–95, 222) unweakened.

All three optional suggestions were handled appropriately. The event-union wording (line 106) is now unambiguous. The root `README.md` allowance is routed to core reconciliation without approving an exception (line 226). The response-schema normalisation is handled as export collateral rather than FUR policy, and native protected records are not edited.

Regression check: the additions introduce no conflict with any `[user]` or `[agreed]` decision. They resolve none of the open owner choices (expansion interpretation, second-trip cap, audit mechanism, distribution name, refactor location, review depth), and no new owner decision is needed. Section-level mechanics are assigned to the core, provider and viewer designs rather than decided here. Only the frontmatter `updated` and `last-branch` fields changed outside the body, and those are now generated metadata under the new canonicalisation contract.

Acceptance applies to the FUR digest in this response's frontmatter. It does not accept or revise the core design or the master plan.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. Collateral only, not a FUR change: the SAR and SPR acceptances cover the earlier digest (`sha256:faa18da7…`). The five XPR additions were reviewed only at the XPR level. When the final record is exported, the manifest should say this explicitly: which digest each level accepted, and that the final architecture acceptance is this XPR round's digest. That way nobody reads the SAR/SPR records as covering the XPR-added text. Whether a delta SAR is wanted over those additions belongs to the open review-depth question (FUR line 224); I do not require one.

## Decision

accepted
