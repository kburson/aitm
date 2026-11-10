---
schema: "aitm.review-response/v0"
level: "spr"
story: 140
role: "author"
round: 1
artifact_path: ".aitm/stories/001/140/design/resolve-exact-git-changes-design.md"
artifact_base_commit: "e2411e2082f566c61a3943d293cd6881392c49a4"
artifact_digest: "sha256:f20d48b0ad669f29378901b275ad8b22f1e0f364503c19460e37da41367fe029"
agent: {"host": "codex", "provider": "openai", "model_id": "gpt-6.1-sol", "effort": "high"}
role_session: "codex:sha256:97325cc8fb55f4eb160fc8e7bb916436cbc2816c1b8b7ad52566c0039feaf0c1"
session_identity_kind: "observed-session-fingerprint"
started_at: null
submitted_at: "2026-11-10T18:46:36Z"
start_basis: "unknown"
finding_ids: []
answered_finding_ids: ["SPR-01"]
patch: "patch-001.diff"
---

## Summary

Verified the review finding with Git's documented behavior and a
disposable repository that returned the replacement blob by default
and the original with replacement refs disabled.

## Finding dispositions

- **SPR-01 accepted.** Require original-object semantics for the
  before/after graph inputs, deferred object reads and local base.
  Include a replacement-ref fixture as acceptance evidence.

## Changes made

Added the shared Git read invariant and its verification case.
The existing three-hour bound and owned paths still apply.

## Declined changes and rationale

None.

## Verification

Checked the exact delta and reproduced the Git behavior. The
reviewer will freshly read the complete revised leaf design.
