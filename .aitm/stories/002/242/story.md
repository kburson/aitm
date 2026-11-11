---
schema: "aitm.story/v0"
id: 242
title: "[Core C89] Installed managed PR and evidence commands"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/242"
parent: 2
children: []
blocking: []
blocked-by: [240, 241]
created: "2026-11-11T15:58:21Z"
updated: "2026-11-11T16:02:43Z"
last-branch: "planning"
estimate: {"agent-hours": 3, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c89"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan-amendment", "story": 2, "key": "C89", "path": ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md", "publication": "8939d9fff17599fe644604b5b267625b4bc5621f", "raw-sha256": "e4245997416a6e39188aacbab246a1fbb41d9ccc8c50e1a2971d85f52b033db3"}
---

# [Core C89] Installed managed PR and evidence commands

[GitHub issue #242](https://github.com/kburson/aitm/issues/242) · [Parent #2](../../000/2/story.md) · Backlog.

## Scope

Thin installed command handlers and a catalog/dispatch contract for aitm-github and aitm-harness.

**Estimate** 3 implementation agent-hours, P1/S, including fixture verification and independent source review. Recheck the four-hour bound at leaf JIT.

**Blocked by** [C87 / #240](../240/story.md), [C88 / #241](../241/story.md).

**Blocking** none.

**Owned areas** src/aitm_core/cli/managed_pr.py; packages/aitm-core/tests/integration/test_c89.py.

## Acceptance criteria

- [ ] Through the installed entrypoint, invoke authorized push/refresh, ready/retarget, merge and scoped PR, review and CI evidence reads through the same Core dispatcher. Compare help, catalog, typed results and denied routes. Keep unavailable host operations visible as unavailable. Skill/MCP parity and real hosted controls are the receiving packages' fixtures.
- [ ] Run the named Core test module and affected contracts, then retain exact review and delivery evidence under the leaf's applicable plan.

[Accepted parent amendment](../../000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md) · [Child reconciliation](../../000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c89).

The leaf's own applicable Design, Plan, JIT and pickup authority are separate.
