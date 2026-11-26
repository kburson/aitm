<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-267e823be939722787b850589663a74b"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/004/459/plan/2026-11-26-core-cost-fixture-plan.md"
artifact_commit: "135ce9e82cac8c541392e17be40319e4d7e5f286"
artifact_blob: "9f270fcfca20855ceb1c8cdd15426d9b03a7a14f"
artifact_digest: "sha256:b748c161e67f3428c5ee3e3114d4786b3739ef77584e2147409ab27ffa69b8d3"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-sonnet-5-5"
  model_display: "claude-sonnet-5-5"
  session_fingerprint: "sha256:8e19e746d2e8dc2d737de00b9261687ead9ba6ce7c9e35a8f69cd092ef9722cf"
  identity_source: "runtime"
started_at: "2026-11-26T13:10:04.059Z"
submitted_at: "2026-11-26T13:11:52.969Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Re-review of the revised plan (artifact commit `135ce9e8`) against my turn-1 findings and the author's dispositions. All three required changes and all optional suggestions are resolved in the plan text. As before, no `packages/aitm-usage` source exists in this worktree, so the author's claims about fixture behaviour (same-cutoff projection conflict, reconciliation items) are taken from their stated reading of the pinned receiver, not verified by me.

## Findings

None. Disposition check against turn 1:

1. Rate-only outcome: resolved. Task 1 now says price is in the v1 row only when available, the subtotal is separate in provenance, and a same-cutoff rate-only change is accepted under a different rate basis. Original row bytes are kept, one reconciliation item is recorded per changed accepted source, and replay of either snapshot is duplicate.
2. Changed scope key: resolved. A Task 2 case rebuilds the same pin with a different key and expects a same-cutoff projection conflict, preserved original bytes and no new acceptance.
3. Exact commands: resolved. Task 2 names a `uv run --locked pytest` command covering `tests/test_export.py` and `tests/test_monitor_recovery_fence.py`.
4. Over-limit bundle: resolved. It is refused before stdout with exit 2 and a fixed message, and a test checks for zero bytes on stdout.
5. Key bytes: resolved. Exactly 32 bytes with no trimming, so a key plus newline is invalid, with a test.
6. Task structure: resolved. Red runs precede implementation, and local, CI and merge gates are separate checkboxes.

## Required changes

None.

## Optional suggestions

None.

## Decision

accepted
