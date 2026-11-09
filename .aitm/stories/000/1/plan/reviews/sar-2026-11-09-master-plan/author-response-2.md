---
schema: "aitm.review-response/v0"
level: "sar"
story: 1
role: "author"
round: 2
artifact_path: ".aitm/stories/000/1/plan/master-plan.md"
artifact_base_commit: "9f56a4682488c5ea586a7c6fbefced82f15bb4e2"
artifact_digest: "sha256:a2c9de44fdb1399f8fd8b85fb8a04f6edf534245187d3280f13fbdd4c1e63e4c"
patch: "patch-002.diff"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6-astra"
  effort: "xhigh"
author_session: "01a1be2f-9c32-79b1-9385-b18044d32156"
session_identity_kind: "observed-session-id"
started_at: "2026-11-09T06:34:23Z"
submitted_at: "2026-11-09T06:34:43Z"
start_basis: "recorded"
finding_ids: []
answered_finding_ids: ["R2-F001"]
---

## Summary

Accepted R2-F001. Production review writes switch at verified C6 adoption, not C5 package release.

## Finding dispositions

- R2-F001 accepted: the legacy store retains full bootstrap FUR/collateral publication after C5 and before the C6 freeze. C5 proves the future writer in disposable migrated fixtures. Once cutover commits, pending publication uses forward recovery; once C6 verifies published readiness, live core ingestion/CAS import is the production route. No routine core write targets a checked-out legacy ref.
- Optional suggestion accepted: later section epics are explicitly children of #1.

## Changes made

Clarified both the review-route and timing paragraphs plus the hierarchy rule. Preserved all six prior fixes and the complete M1 acceptance obligation.

## Declined changes and rationale

None. No owner decision or actual cutover is implied.

## Verification

Re-read the entire plan around C5/C6 and review obligations; checked whitespace. Patch 002 records the bounded clarification. Round 3 must review the full current file. No implementation tests apply.
