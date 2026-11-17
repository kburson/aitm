<!-- ai-peer-review-template version="1" digest="sha256:f81da1894a46ceb20866070833b4e99ef536ef633542b418783d29e6a981dbd8" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-a4a8291ce43671588b36a83b461ad7fa"
role: "author"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-17-368-hosted-ancestry-run-findings.md"
artifact_commit: "6aebc0300ac50d07d34fa74516a78ab5264314c4"
artifact_blob: "0219a6254b6da55ddf2de71464158d5ad2684a59"
artifact_digest: "sha256:e3b27b2243efc1afcbf893eee8f8e36e5ccaf4ea8c9d99bc4238e77638ddf3a3"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6.1-sol"
  model_display: "gpt-6.1-sol"
  session_fingerprint: "sha256:76db90c482a2d4b62a9e997e0578af0ecf27a2a2853532bf57af0df506c86756"
  identity_source: "runtime"
started_at: "2026-11-17T12:53:49.769Z"
submitted_at: "2026-11-17T12:58:10.901Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Bound exact queue and cancellation evidence and recorded the exhausted phase budget.

## Finding dispositions

1. Stated that 2.152 plus 0.348 exhausted the approved 2.5 hours. Recorded cumulative overall/packet charges and balances at HOLD, plus the authorization and exact packet needed for a future attempt.
2. Added individual authenticated API response hashes with selected fields and capture-completion times. Named the final job with runner ID zero and no steps as controlling evidence.

## Changes made

Used the same product dispatch deadline term and included the 701-second observed queue interval through the deadline.

## Declined changes and rationale

None.

## Verification

Matched the active run head and original deadline, checked raw file hashes, capture times, terminal job and artifact counts, and recalculated the two cumulative limits.
