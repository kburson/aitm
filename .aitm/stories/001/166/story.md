---
schema: "aitm.story/v0"
id: 166
title: "[#133 T29] Bridge governed Codex operations"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/166"
parent: 133
children: []
blocking: [167]
blocked-by: [165]
created: "2026-11-10T16:52:04Z"
updated: "2026-11-10T16:56:26Z"
last-branch: "planning"
estimate: {"agent-hours": 4.0, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T29", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "e252b7e63bbc892308fe00ec2d3d34277ec287a25ed69b075b70e152ca26e460"}
---

# [#133 T29] Bridge governed Codex operations

[GitHub issue #166](https://github.com/kburson/aitm/issues/166) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L647)

**Required predecessors** [T28 #165](../165/story.md).

The planning estimate is 4 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T29. Bridge governed Codex operations — 4h, P1, T28

**Owns** `tools/ci/tia/harness.py`, `test_tia_harness.py`, and the
isolated Codex qualification carrier.
**Interface** `guard(request, authority_client) -> Permit | Hold`.

- [ ] `test_running_agent_loses_authority_before_notification` and
  `test_read_only_and_incident_roles` cover pickup, resume and
  bounded mutation. Preserve local changes and locks.
- [ ] Wire the T28-qualified Codex Desktop entry points and trusted
  stop-notification path to the authenticated enrollment. Prove a
  connected stop, missed notification, and fresh denial on
  disconnected mutation. V(harness) plus native Codex evidence pass.
