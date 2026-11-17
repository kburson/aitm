<!-- ai-peer-review-template version="1" digest="sha256:f81da1894a46ceb20866070833b4e99ef536ef633542b418783d29e6a981dbd8" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-9e6f1dfbab13cc5d8c17d1c53bd75978"
role: "author"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-16-368-hosted-restore-retry-packet.md"
artifact_commit: "41c129a1c5a10da34ead7afd74086d161cdcb411"
artifact_blob: "7352a3b8ab8f6e924078dd162459a1550e01da4c"
artifact_digest: "sha256:ba5f792ba3f84190926061c808a2e2c26b5d01d4f4cf79c555732d80fc22f00d"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6.1-sol"
  model_display: "gpt-6.1-sol"
  session_fingerprint: "sha256:76db90c482a2d4b62a9e997e0578af0ecf27a2a2853532bf57af0df506c86756"
  identity_source: "runtime"
started_at: "2026-11-17T05:22:30.515Z"
submitted_at: "2026-11-17T05:28:59.731Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

The revision records the authenticated manifest access scan, improves failure diagnostics and adds offline restore coverage.

## Finding dispositions

1. The authenticated 8,973-entry manifest has 8,570 files and 393 directories. Mode bit checks found zero files missing other-read and zero directories missing other-read or traversal. The hosted retry exercises the remaining known symlink-mode hypothesis.
2. Record both the innermost spike frame and the leaf frame. Include only controlled-runtime or private-evidence relative filenames.
3. Added synthetic tar and traceback tests. Eleven tests passed.
4. Quoted original receipt fields, present and absent raw streams, and recorded the durable dry-restore receipt with exact scope and digests.

## Changes made

Separated extraction from privileged install. Rebound the exact ten-path workflow, tree and two changed blobs.

## Declined changes and rationale

The optional privileged restore belongs in the disposable hosted job. The ordinary-account dry restore used real ditto and stopped before interpreter execution.

## Verification

Eleven focused unit tests, independent manifest permission scan, dry restored bytes and modes, and Mach-O probe table comparison passed.
