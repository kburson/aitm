<!-- ai-peer-review-template version="1" digest="sha256:f81da1894a46ceb20866070833b4e99ef536ef633542b418783d29e6a981dbd8" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-2001d40a8de8ac60b2d33b424e958263"
role: "author"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/001/103/design/github-ci-quality-gates-design.md"
artifact_commit: "dc507c8017ed6fb01cb39c561cec77a6959fb206"
artifact_blob: "0fe509aa14e59d00553fe94170bdb30188b624a4"
artifact_digest: "sha256:96ef0fb0019e82c3ed43387c6e9efedc83bfeeae6a9094ac4de42980009d120b"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6.1-sol"
  model_display: "gpt-6.1-sol"
  session_fingerprint: "sha256:664318926dfdb04419486df4dc11e2de5f5ae3b5fa76b098a3d841a6e3c93bef"
  identity_source: "runtime"
started_at: "2026-11-10T02:45:20.325Z"
submitted_at: "2026-11-10T02:52:34.032Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

The revision defines authoritative live candidate inputs and separate delivery gates for the workflow and its verifier.

## Finding dispositions

- **F1 addressed.** The live base comes directly from the declared target branch ref. Authenticated GitHub PR, workflow, run, check suite and attempt metadata bind the raw test merge, both parents and the exact attempt. Candidate output supplies lane data and cannot supply trusted identity. Missing fork linkage or any mismatch refuses. Added explicit stale-base refusal.
- **F2 addressed.** Acceptance is mapped to ordered, independently closable leaves. If needed, scoped behavioral coverage work comes first under its own viable route. The bootstrap leaf uses manual exact readback through its own source merge and route proof. The verifier uses established CI, with manual readback before it is delivered. File-quality work follows. Manual versus trusted verifier parity belongs to parent acceptance, outside the bootstrap leaf closure. This also resolves manual SPR-CI04.

## Changes made

Explicitly exclude the editable project from the locked wheel-smoke runtime. Carry runner and hosted runtime evidence to refinement.

## Declined changes and rationale

No required changes declined. Actual hosted proof and enforcement remain delivery scope.

## Verification

Reviewed the exact draft against both current required findings, the independent SPR finding and owner constraints. The 90% line floor, behavioral-test intent, exact required evidence, individual story closure and Core exclusion remain explicit.
