---
schema: "aitm.story/v0"
id: 157
title: "[#133 T20] Authenticate workspace and incident authority"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/157"
parent: 133
children: []
blocking: [159, 160, 165]
blocked-by: [156]
created: "2026-11-10T16:51:42Z"
updated: "2026-11-10T16:56:26Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T20", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "692d9d89dad4a4cbfec1f08d7941c4db151352567604742b319bdbecb6199fec"}
---

# [#133 T20] Authenticate workspace and incident authority

[GitHub issue #157](https://github.com/kburson/aitm/issues/157) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L485)

**Required predecessors** [T19 #156](../156/story.md).

The planning estimate is 3.5 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T20. Authenticate workspace and incident authority — 3.5h, P1, T19

**Owns** `tools/ci/tia/authority_io.py`, `test_tia_authority_io.py`,
and disposable host transport configuration.
**Interface** `handle(actor, request, store) -> Decision` and
`require_current_authority(repository, expected_version) -> Current | Hold`.

- [ ] `test_candidate_cannot_request_repair_or_bypass_continuity`
  checks impersonation, authorized appointment and singular repair
  binding, stale version, and unavailable or inconsistent witness.
- [ ] Qualify a restricted authenticated workspace command endpoint,
  initially SSH forced-command on the disposable host, binding
  identity and generation to credentials and operation allowlists.
  Keep workspace, health-read, candidate and merge roles separate.
  Authenticate the appointing operator and verify the appointed
  owner's exact repair binding or external-interruption diagnosis.
  Pin T18 continuity and require it on all live grants and dispatch.
  Return delivery deferral for ordinary validation against stopped
  trunk. V(authority_io) and a cross-clone request pass. Prove the
  normal entry point issues no grant and dispatches nothing with only
  T17 storage or an inconsistent witness.
