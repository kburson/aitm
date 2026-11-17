<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-c67668584e194f580a3052e8f2cef4de"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/355/plan/2026-11-16-355-pre-commit-execution-plan.md"
artifact_commit: "8e0d41582cb3b61c10d1f63bd1280c3b9a321d3a"
artifact_blob: "69d3a275f37e103e75208c93b12d99c6b356c2f0"
artifact_digest: "sha256:c9dab6ea4fb421f46dae71e31db4d8dc772528704aea31c451880cc442de56c9"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:0135f0bf409b44d81249f9ed0ca7917c5525cab72e6b3d74ac0b3c6a2f8231f0"
  identity_source: "runtime"
started_at: "2026-11-17T00:22:18.541Z"
submitted_at: "2026-11-17T00:27:47.352Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is a round-2 independent review of the revised plan at blob `69d3a275f37e103e75208c93b12d99c6b356c2f0`, commit `8e0d4158`, digest `sha256:c9dab6ea…de56c9`. I read the whole plan (lines 1–51) and author response 1. I checked each disposition against the changed text. I ran no command other than the required submit, and I used no Git.

**R1-F001 is resolved.** Line 11 now gives two sources for the strict tier. It links the #351 epic's "Research, then development" section; epic line 38 there says "a trusted pre-commit run". It also cites #353, whose title is "Find the process boundary for trusted local test observation". Line 11 also acknowledges that the accepted #353 finding allows a cooperative advisory result when it is explicitly scoped that way. Line 21 requires the signed HOLD receipt to name both owner routes and to choose neither:

- provision and qualify a protected boundary and the scoped assignment authority under a separate estimate;
- re-scope #355, or use a sibling story, for the #353 advisory result, with advisory provenance.

That is the change I requested.

**R1-F002 is resolved.** Lines 24–32 add a five-row mechanism register. It covers the stock `local.py`, the #146 hosted/DTrace route, an existing distinct principal, an approved installed sandbox/container/VM, and native tracing. Each row has a read-only deciding fact. Each row also says that availability alone is not eligibility, and forbids privilege, account, configuration and SIP changes. Line 18 requires PASS or HOLD for every row. It sends unlisted mechanisms to a separate scope decision and bars callers and candidates from appointing the provider. Line 21 bounds a HOLD to the mechanisms examined. The search can now be checked for completeness, and the executor knows when it is finished.

**Optional suggestions**

- **Accepted.** Line 17 now binds the tooling checkout to the exact commit and tree. It also compares the full sorted node set, pins content SHA-256 `d71cd585…101647`, and pins the `unsupported-change` reason.
- **Accepted.** Line 21 names the HOLD state: planning `blocked`, Project 24 `Dev` with `Disposition_v0 = BLOCKED`, and the issue left open. `BLOCKED` already appears as a disposition value in `002/268/plan/closure-receipt.json`.
- **Accepted.** Line 41 replaces "strong authority" with "the protected observation source established in the mechanism register". Line 34 defines that source.
- **Reasonably declined: pinning the historical snapshot digest.** The author binds candidate bytes, IDs and inventory to the historical probe instead. The live snapshot must repeat on identical fresh reads and is recorded separately. That is sound, because the snapshot's canonical bytes include observation and profile fields that can legitimately differ between checkouts.
- **Reasonably declined: an independent readback of a HOLD.** A HOLD fails closed and comes with a per-mechanism receipt.

**Link check.** The new links resolve: `351/story.md` has the anchored heading, `353/story.md` exists, and `001/146/plan/2026-11-12-146-full-suite-observation-findings.md` exists.

The revisions introduce no new defects.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. In the mechanism register row for a distinct local principal (line 30), "AITM-related loaded service identities" could name the read-only command used, such as a launchd list readback. That way the receipt records a reproducible fact.

## Decision

accepted
