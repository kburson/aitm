<!-- ai-peer-review-template version="1" digest="sha256:f81da1894a46ceb20866070833b4e99ef536ef633542b418783d29e6a981dbd8" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-4971bb10bf0cd947510cc8f5c48ebbf4"
role: "author"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/001/181/design/story-timing-dashboard-design.md"
artifact_commit: "307c2577e2848331f29bbd16402d82e5d95a3403"
artifact_blob: "9da51a9bfa253bbbd107bf712e7c581d737d49af"
artifact_digest: "sha256:3edf5b36d09c7832c31d69fdbce42391d28aecdaccf21d8bed3fbc25b84b6ccb"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6.1-sol"
  model_display: "gpt-6.1-sol"
  session_fingerprint: "sha256:c1cbcb4fcd7a783ae196e3c00bcb80a1c4c8df5c4a0a48d8a37423b000b5533c"
  identity_source: "runtime"
started_at: "2026-11-10T20:41:07.560Z"
submitted_at: "2026-11-10T20:43:55.857Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
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
