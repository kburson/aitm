<!-- ai-peer-review-template version="1" digest="sha256:f81da1894a46ceb20866070833b4e99ef536ef633542b418783d29e6a981dbd8" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-da800297e0b0c147b91cbdf5f1aad338"
role: "author"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/005/522/design/history-import-design.md"
artifact_commit: "8862808e2dd2062df1c0d2e156e6711c2dbaabbb"
artifact_blob: "7eaa5a2ebba5e647ff6fe4651a89efd5cf4f3842"
artifact_digest: "sha256:d44646dd8a917a4ff7588d3582503604514bc869db24e219c43a5aba455a7556"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6.2-sol"
  model_display: "gpt-6.2-sol"
  session_fingerprint: "sha256:1918137c8506c6a045c17ba1bd9406968a6f9eee76d71a87ad9966b7592223a8"
  identity_source: "runtime"
started_at: "2026-11-27T06:12:53.107Z"
submitted_at: "2026-11-27T06:16:59.249Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Revised the design against round-one findings and aligned the producer and consumer contracts across M2, M7 and M8.

## Finding dispositions

1. Accepted. Pinned replay now reuses captured bytes and reports a separate live acquisition as possible drift. An authorized second reader re-normalizes the restricted replay bundle.
2. Accepted. Define acquired revision using the update timestamp and acquired-record digest. An unproved pre-work revision cannot qualify as an estimate label.
3. Accepted. Commit, unselected comments, and outside approval evidence are optional unsupported sources pending a distinct contract.
4. Accepted concern. The coordinated M2 revision implements the alternate consumer-input resolution. #525 qualifies the selection mechanism using its own bounded fixture and approved live predicate. M7 then pins its own versioned predicate at capture. This preserves #525’s independent delivery and removes the proposed reverse prerequisite.

## Changes made

Updated the reviewed spec. The other two coordinated spec drafts are visible in this isolated checkout as cross-reference context. Each has its own review and acceptance.

## Declined changes and rationale

None. The M7 timing predicate is a consumer input so #525 stays independent.

## Verification

Verified edited links, exact estimate row sums and design alignment for predicate ownership, cutoff and replay, optional evidence and corpus handoff. Verified the native dependency graph separately. Implementation tests remain part of the planned acceptance.
