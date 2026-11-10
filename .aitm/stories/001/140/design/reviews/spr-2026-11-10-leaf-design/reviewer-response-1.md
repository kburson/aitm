---
schema: "aitm.review-response/v0"
level: "spr"
story: 140
role: "reviewer"
round: 1
artifact_path: ".aitm/stories/001/140/design/resolve-exact-git-changes-design.md"
artifact_base_commit: "e2411e2082f566c61a3943d293cd6881392c49a4"
artifact_digest: "sha256:edbf6cae0ba425d140b57bd881de42ed9c1f27e81398f655ead1e4e2c5014e55"
agent: {"host": "codex", "provider": "openai", "model_id": "gpt-6.1-sol", "effort": "high"}
role_session: "codex-collaboration:/root/refine_138"
session_identity_kind: "distinct-collaboration-participant"
started_at: "2026-11-10T18:44:43Z"
submitted_at: "2026-11-10T18:45:55Z"
start_basis: "recorded UTC bound"
finding_ids: ["SPR-01"]
answered_finding_ids: []
---

## Summary

I independently read lines 1–50 of 50 in one fresh, numbered range. The
raw SHA-256 matched before and after the read. I reviewed the distinct
#140 artifact against the accepted #133 design, T03 plan and #140 story.
I authored the neighboring T01 draft and had no role in authoring this
candidate. The three-hour estimate, P1, exact two owned paths, two direct
consumers and independence from #138 match the accepted leaf.

The hosted path binds the ordered PR parents, exact tested tree and
base-to-tested comparison. The local path distinguishes the index from
effective bytes, preserves rename and deletion endpoints, and invalidates
a read when identity, membership or content changes. Its refusal result
stays distinct from a verified empty change set. One hosted identity
detail still needs to be explicit.

## Findings

- **SPR-01 [P1] Git replacement refs can change the bytes behind a pinned object ID.**
  Lines 21–25 require exact hosted IDs and read source by identity. Lines
  35–39 constrain the Git calls to read-only access and forbid lazy
  fetching. Git normally honors local replacement refs even when a caller
  gives an exact object ID. A replacement for the base commit can supply
  a different before tree while the tested commit's ordered parents and
  tree still match. A replaced blob can supply different content through
  an otherwise correct tree path. Either case could omit a former test
  consumer without making the stated checks fail. The local story-base
  endpoint uses the same object-read boundary.
  [Git replacement reference behavior](https://git-scm.com/docs/git-replace#_description)

## Required changes

- **SPR-01** Require original object semantics for all bound commit, tree,
  diff and blob reads, including the local story-base tree and deferred
  endpoint content reads. Disable replacement refs with
  `git --no-replace-objects` or an equivalent invariant. Add a fixture
  with a replacement ref on a pinned base commit or blob and verify that
  the resolver uses the original content or refuses. The existing scope
  and estimate can absorb this change.

## Optional suggestions

None.

## Decision

Revisions requested.
