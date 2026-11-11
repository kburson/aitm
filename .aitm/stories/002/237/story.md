---
schema: "aitm.story/v0"
id: 237
title: "[Core C83] Published branch and draft provisioning"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/237"
parent: 2
children: []
blocking: [238, 239]
blocked-by: [235, 236]
created: "2026-11-11T15:58:16Z"
updated: "2026-11-11T16:02:43Z"
last-branch: "planning"
estimate: {"agent-hours": 3.75, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c83"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan-amendment", "story": 2, "key": "C83", "path": ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md", "publication": "8939d9fff17599fe644604b5b267625b4bc5621f", "raw-sha256": "e4245997416a6e39188aacbab246a1fbb41d9ccc8c50e1a2971d85f52b033db3"}
---

# [Core C83] Published branch and draft provisioning

[GitHub issue #237](https://github.com/kburson/aitm/issues/237) · [Parent #2](../../000/2/story.md) · Backlog.

## Scope

Resumable pre-pickup provisioning, branch/draft receipts and typed content-free bootstrap provenance.

**Estimate** 3.75 implementation agent-hours, P1/S, including fixture verification and independent source review. Recheck the four-hour bound at leaf JIT.

**Blocked by** [C82 / #235](../235/story.md), [C84 / #236](../236/story.md).

**Blocking** [C85 / #238](../238/story.md), [C86 / #239](../239/story.md).

**Owned areas** src/aitm_core/managed/provision.py; packages/aitm-core/tests/integration/test_c83.py.

## Acceptance criteria

- [ ] With deterministic doubles, publish before effects. Resume separate ref and draft claims after each lost response. Verify exactly one draft and explicit default/non-default target, record exact bootstrap OID, parent and unchanged tree when required, and block pickup before the draft is verified. Bootstrap CI supplies provisioning evidence only.
- [ ] Run the named Core test module and affected contracts, then retain exact review and delivery evidence under the leaf's applicable plan.

[Accepted parent amendment](../../000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md) · [Child reconciliation](../../000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c83).

The leaf's own applicable Design, Plan, JIT and pickup authority are separate.
