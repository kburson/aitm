---
schema: "aitm.review-response/v0"
level: "sar"
story: 2
role: "reviewer"
round: 3
artifact_path: ".aitm/stories/000/2/design/core-design.md"
artifact_base_commit: "981b8d77e2e988e9ec3f79768c7c9728cb66c11a"
artifact_digest: "sha256:d28699369045b9c54451bdb460d70158053e419bd9cfe72ca62bcc3b47183cd9"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6.1-sol"
  effort: "high"
reviewer_session: "01a1be88-ab35-75f0-aa41-1f21e6062d95"
started_at: "2026-11-09T04:50:47Z"
submitted_at: "2026-11-09T04:51:43Z"
start_basis: "recorded"
finding_ids: []
answered_finding_ids: []
---

## Summary

**Accepted.** I read author-response-2 and the full FUR at the digest above, including the integrated `7e829d5` review-timing and backfill changes. I checked each round-two finding against its revised contract and acceptance scenario, then checked the whole design against the accepted architecture and the latest master decision record. The same reviewer thread conducted all three rounds.

- **R2-F001 resolved.** Lines 458–466 require a published dispatch claim for non-idempotent create, observation-only handling while a sender/request remains uncertain, positive fencing and proof of absence before redispatch, and published current-generation allocation before exposing a shared local-provider ID. This closes the same-intent and stale allocator races.
- **R2-F002 resolved.** Lines 408–420 specify live, provisional turns before final manifest validation, immutable response and timing-anchor evidence, normalized deduplication independent of the recording envelope, legacy identity aliases and appended timing corrections. The actual XPR backfill remains historically distinct from its derived claim/prior-submit evidence. The acceptance case at line 552 checks live-plus-import and backfill of the same level, including coverage, source reproduction and overlap. The response-only boundary is preserved through explicit exclusions and Unknown reporting.
- **R2-F003 resolved.** Lines 370–374 distinguish review topology, participant continuity, comparable identities, content binding and assurance. The actual native v0 record retains unavailable authority and declared participant/model provenance. Inconsistent or insufficient evidence can still be imported for historical reporting without satisfying an acceptance level. The review-depth decision remains open.
- **R2-F004 resolved.** Lines 384–390 verify positive reviewed-content mapping and distinguish unverified transformations from delivery. For an authorized local mutation, durable intent and expected result precede the target CAS. Retry observes the exact result instead of repeating the merge. The acceptance case rejects an ancestry-only merge and exercises the crash after target mutation.
- **R2-F005 resolved.** Lines 121, 129–130 and 147–153 establish a committed code-policy trust anchor independent of planning history, durable bootstrap identity, and a bounded legacy declaration. The migration receipt binds the payload tree excluding itself. The fresh-clone and cutover scenarios test the independent anchor and the verifiable final tree.
- **R2-F006 resolved.** Lines 296–298 and 332–334 put the confirmed-trip check before ordinary sync/work, verification or an effective passing review, and repeat it on CAS retry and after a subprocess returns. Retained evidence and analysis have explicit fenced routes. Advisory behavior remains report-only.
- **R2-F007 resolved.** Lines 353–355 define provisional advisory attempts, later binding/evidence reconciliation without a fresh budget, and a recorded reopening route from Done/unverified. Original waived conditions and dispositions remain historical facts.

The rest of the FUR retains causal operation ordering, story-local write ownership, current-content acceptance and JIT, delivery-before-sign-off, distinct kind and disposition rules, and the core-only path. I found no new substantive conflict from the revisions or upstream additions. The owner choices on expansion completion, second-trip cap and review depth remain open. GitHub's every-push audit mechanism remains an open provider-design obligation. No new owner decision is required for this SAR.

## Findings

None.

## Required changes

None.

## Optional suggestions

- When turning the design into a build plan, carry the advisory provisional-attempt exception into the event-table and clock test cases. Lines 353–355 already define its behavior, while the short summaries at lines 229 and 402 describe the ordinary accepted-plan path.

## Decision

**accepted**

SAR is exhausted. Acceptance applies to the core-design bytes identified above and to this review level.
