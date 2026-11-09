---
schema: "aitm.review-response/v0"
level: "sar"
story: 2
role: "author"
round: 2
artifact_path: ".aitm/stories/000/2/design/core-design.md"
artifact_base_commit: "981b8d77e2e988e9ec3f79768c7c9728cb66c11a"
artifact_digest: "sha256:d28699369045b9c54451bdb460d70158053e419bd9cfe72ca62bcc3b47183cd9"
patch: "patch-002.diff"
agent: {"host":"codex","provider":"openai","model_id":"gpt-6-astra","effort":"xhigh"}
author_session: "01a1be2f-9c32-79b1-9385-b18044d32156"
started_at: "2026-11-09T04:46:14.339Z"
submitted_at: "2026-11-09T04:50:25Z"
start_basis: "recorded"
finding_ids: []
answered_finding_ids: ["R2-F001","R2-F002","R2-F003","R2-F004","R2-F005","R2-F006","R2-F007"]
---

## Summary

Accepted all seven round 2 findings after reading the complete response and checking the current design and owner decisions. The changes close the remaining interface gaps without choosing the existing open trip, cap, review-depth or hosted audit policy. The upstream additions remain integrated; their original attribution and two-base provenance in author-response-1 are unchanged.

## Finding dispositions

- **R2-F001:** Accepted. Added a separately published dispatch claim for non-idempotent creation, observation-only handling of uncertain/in-flight senders, positive fencing and absence before redispatch, and shared publication of the current local allocator generation before an ID is exposed. Single-clone/no-remote allocation remains local. Acceptance now covers two clones resuming one intent and stale authority handoff.

- **R2-F002:** Accepted. Added review open and a stable level-record identity, provisional live turn import before a final manifest, immutable response/basis sources, normalized turn deduplication apart from recording envelopes, and versioned timing corrections. Prior-submit/claim anchors are independently reproducible. Proxy spans containing unknown excluded work stay bounded/Unknown instead of becoming response-writing duration. Per-state intersection and same-session versus distinct-agent accounting are explicit. Migration and acceptance cover live-plus-import/backfill equivalence including the actual native XPR provenance. This further reviews the upstream timing additions without crediting their introduction to SAR.

- **R2-F003:** Accepted. Added SAR/SPR/XPR participant topology, continuity, comparable identity mapping, permitted assurance and retained-but-unaccepted provenance rules. Manual M1 records remain usable under explicit declared-assurance policy; native v0 unavailable authority is preserved. Wrong-provider and same-session cases are acceptance scenarios.

- **R2-F004:** Accepted. Local delivery now verifies positive content mapping/expected integration, not ancestry alone; ours merges and unreviewed conflict resolutions cannot pass. Authorized mutations retain an intent and expected result before target CAS, and reconcile exact results after crashes instead of repeating a merge. Verified the Git merge-strategy behavior against primary documentation.

- **R2-F005:** Accepted. Init writes store UUID/authority and proposed genesis anchors into committed code-default policy, with its bootstrap journal only for pre-policy resume. Fresh clones verify against code-policy anchors. Legacy adoption pins the exact bounded baseline independently of the receipt. Receipt result hashes omit the receipt path itself, avoiding circularity.

- **R2-F006:** Accepted. Added the command-boundary ordering before ordinary sync/implementation/verification or effective review pass, repeated on CAS retry and after subprocess completion. Retained observation/proof and fenced analysis/recovery commands remain available without authorizing further implementation.

- **R2-F007:** Accepted. Defined minimum integrity inputs versus advisory workflow waivers, provisional attempts with missing plan/binding, normal bind/attempt reconciliation without budget reset, and reopening Done/unverified for same-source evidence or same-attempt rework. Original waived results remain historical facts.

## Changes made

Added narrowly scoped contracts for identity dispatch ownership, live review-turn evidence and timing anchors, review topology/assurance, delivery content proof and recovery, independently anchored store/migration identity, command-boundary trip ordering and provisional advisory recovery. Added the corresponding acceptance cases. Adopted the optional suggestion to mark the event JSON example as abbreviated rather than implying it includes every required field.

## Declined changes and rationale

None. All seven findings are addressed; no new owner decision is requested and no required finding is deferred. No decision/context document, prior review record, event log or implementation file changed. Existing owner choices remain open, with original numeric limits unchanged.

## Verification

- Verified the FUR is the only changed tracked file, all its relative links resolve and Git whitespace checks pass.
- Checked the local-delivery failure case against [Git's merge-strategy documentation](https://git-scm.com/docs/merge-strategies): ancestry can exist while the reviewed content is discarded, so the design now requires positive content mapping.
- The current raw output digest is recorded above. Round 3 must read the full document, including upstream timing/provenance and these revisions.
- No implementation tests apply. Portable response validation and complete per-turn patch replay will run before publication. This author-turn span is recorded elapsed provenance, not proof of uninterrupted engaged time.
