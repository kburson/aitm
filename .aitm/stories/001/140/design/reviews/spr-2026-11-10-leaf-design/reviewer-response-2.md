---
schema: "aitm.review-response/v0"
level: "spr"
story: 140
role: "reviewer"
round: 2
artifact_path: ".aitm/stories/001/140/design/resolve-exact-git-changes-design.md"
artifact_base_commit: "e2411e2082f566c61a3943d293cd6881392c49a4"
artifact_digest: "sha256:f20d48b0ad669f29378901b275ad8b22f1e0f364503c19460e37da41367fe029"
agent: {"host": "codex", "provider": "openai", "model_id": "gpt-6.1-sol", "effort": "high"}
role_session: "codex-collaboration:/root/refine_138"
session_identity_kind: "distinct-collaboration-participant"
started_at: "2026-11-10T18:46:46Z"
submitted_at: "2026-11-10T18:47:16Z"
start_basis: "recorded UTC bound"
finding_ids: []
answered_finding_ids: []
---

## Summary

I independently read all 57 lines of the revised candidate in fresh,
contiguous numbered ranges 1–50 and 51–57. The raw SHA-256 matched before
and after retrieval. I checked the author response against the revised
artifact in the same distinct reviewer session.

## Findings

- **SPR-01 resolved.** Lines 27–30 disable Git replacement refs for
  every pinned commit, tree, diff and blob read. They apply the same
  invariant to the local story-base and deferred endpoint reads. Line
  53 requires a fixture in which a replacement ref exists on a pinned
  base or blob. The comparison and endpoint read must use original
  bytes or return uncertainty. This covers the round-one substitution
  route. The three-hour estimate and T03 source ownership still apply.

## Required changes

None.

## Optional suggestions

None.

## Decision

Accepted.
