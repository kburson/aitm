---
schema: "aitm.review-response/v0"
level: "xpr"
story: 181
role: "author"
round: 1
artifact_path: ".aitm/stories/001/181/design/story-timing-dashboard-design.md"
artifact_base_commit: "307c2577e2848331f29bbd16402d82e5d95a3403"
artifact_digest: "sha256:ed54c65d42aad04bde7a4f942894beb6a2280016d5fc2ff0b6411297ce5f46a5"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6.1-sol"
  effort: "high"
author_session: "sha256:c1cbcb4fcd7a783ae196e3c00bcb80a1c4c8df5c4a0a48d8a37423b000b5533c"
session_identity_kind: "native-fingerprint"
started_at: "2026-11-10T20:42:36.976Z"
submitted_at: "2026-11-10T20:43:55.857Z"
start_basis: "claim"
start_source: "native/spec/2026-11-10-story-timing-dashboard-design-review-4971bb10bf0cd947510cc8f5c48ebbf4/review-4971bb10bf0cd947510cc8f5c48ebbf4-review-manifest.md#claim-claim-fc6049e8-3c20-4353-83cc-3544ee5e41cb"
finding_ids: []
answered_finding_ids: []
patch: "patch-001.diff"
native_source: "native/spec/2026-11-10-story-timing-dashboard-design-review-4971bb10bf0cd947510cc8f5c48ebbf4/review-4971bb10bf0cd947510cc8f5c48ebbf4-author-response-1.md"
native_source_digest: "sha256:0f00ed8b162f12da4a8bddd527846b5e5c9f7a84321ced84804ca45b38cb685e"
---

Mode: `normal`

## Summary

A usage input now selects one pinned report and resolves its registered per-story receipts. The canonical snapshot records exactly which receipts it consumed.

## Finding dispositions

Accepted the required change in Finding 1. The project, report or sequence, window, cutoff and pricing basis define the selector. Receipt resolution is scoped to that selection, with explicit rules for missing rows, supersession and conflicts.

## Changes made

Aligned display, capture and acceptance on the report selector. Added a replay case with two reports in one planning tree, distinguished the fixture actors, clarified future-dated evidence, and scoped byte determinism to the JSON.

## Declined changes and rationale

None.

## Verification

Checked the revised text across the snapshot, capture and acceptance sections. The two-report fixture now asserts one cutoff per view. Revised raw SHA-256 `ed54c65d42aad04bde7a4f942894beb6a2280016d5fc2ff0b6411297ce5f46a5`.
