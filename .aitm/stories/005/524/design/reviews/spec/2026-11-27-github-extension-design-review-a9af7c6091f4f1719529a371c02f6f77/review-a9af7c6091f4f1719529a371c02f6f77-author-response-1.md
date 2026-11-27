<!-- ai-peer-review-template version="1" digest="sha256:f81da1894a46ceb20866070833b4e99ef536ef633542b418783d29e6a981dbd8" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-a9af7c6091f4f1719529a371c02f6f77"
role: "author"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/005/524/design/github-extension-design.md"
artifact_commit: "8862808e2dd2062df1c0d2e156e6711c2dbaabbb"
artifact_blob: "e4e12d87bab444496df675abf41d410b63eb6fa5"
artifact_digest: "sha256:bce3087c1067ca38c1f25c7c98486c5934b4eb4fff3048fcf5eee75e99cf547b"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6.2-sol"
  model_display: "gpt-6.2-sol"
  session_fingerprint: "sha256:1918137c8506c6a045c17ba1bd9406968a6f9eee76d71a87ad9966b7592223a8"
  identity_source: "runtime"
started_at: "2026-11-27T06:12:53.106Z"
submitted_at: "2026-11-27T06:16:59.226Z"
finding_ids: []
answered_finding_ids: ["R1-F001","R1-F002","R1-F003","R1-F004","R1-F005","R1-F006"]
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Revised the design against round-one findings and aligned the producer and consumer contracts across M2, M7 and M8.

## Finding dispositions

- R1-F001 Accepted. Post-cutoff flags describe observed issue activity or comment updates. They do not assert body edits or historic bytes.
- R1-F002 Accepted. Excluded PRs are counted and covered by a fixture.
- R1-F003 Accepted. Pinned raw Markdown UTF-8 representation, null/empty distinction, record and response-byte digests.
- R1-F004 Accepted. Added required initial issue metadata and covered versus unsupported source categories.
- R1-F005 Accepted. A consumer predicate is a versioned request input. #525 qualifies with a fixture and its own scoped live predicate before M7 pickup.
- R1-F006 Accepted. M2 owns the GitHub reader and M7 owns the parser and normalizer.

## Changes made

Updated the reviewed spec. The other two coordinated spec drafts are visible in this isolated checkout as cross-reference context. Each has its own review and acceptance.

## Declined changes and rationale

None. The M7 timing predicate is a consumer input so #525 stays independent.

## Verification

Verified edited links, exact estimate row sums and design alignment for predicate ownership, cutoff and replay, optional evidence and corpus handoff. Verified the native dependency graph separately. Implementation tests remain part of the planned acceptance.
