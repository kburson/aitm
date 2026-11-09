---
schema: "aitm.story/v0"
id: 92
title: "[Usage U08] Collector service, live commands and status"
kind: "story"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/92"
parent: 83
children: []
blocking: [93]
blocked-by: [91]
created: "2026-11-09T14:42:21Z"
updated: "2026-11-09T20:52:23+00:00"
last-branch: "codex/aitm-usage-u08"
estimate: {"agent-hours": 4, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md"
files: {"draft": "draft.md", "events": "events.jsonl", "design": ["design/design.md"], "plan": ["plan/implementation-plan.md", "plan/jit.md", "plan/pickup-review.md", "plan/source-review.md", "plan/launch-health-jit.md", "plan/launch-health-pickup-review.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 83, "key": "U08", "path": ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md", "publication": "6ee371590ff3ce0cb5a108bdd1e89cfb17bc2300", "raw-sha256": "07919dde4475310b7fe277791206f611ce5cd615eeaed491d3a619e61142daf5", "section-sha256": "6bdc895734ef1dbc8d838cc8e8b4486b6eb2c26f6b9adf3dbfe7c24d5674c11e"}
---

# [Usage U08] Collector service, live commands and status

[GitHub issue](https://github.com/kburson/aitm/issues/92) · [Parent #83](../83/story.md) · Develop

**Required predecessors** [#91](../91/story.md)

## Accepted parent decomposition

**Files** `src/aitm_usage/{service,cli}.py`, `tests/test_service.py`.

**Contract** `collect_once(registration: Registration, ledger: Ledger) -> CollectionReport` and `run_service(registration: Registration, interval_seconds: int = 15) -> int`. Wire actual providers, cursors, inbox and heartbeat in the same process. An explicit register command pins approved roots, permitted checkout/worktree anchors, and the activation cut-off before scanning. Apply U06 accounting to each committed adapter batch and expose U02 task and feature rollups with tokens, known price and Unknown coverage. A restart reloads the registration without resetting the cut-off. `status --json` reports version, heartbeat, interpreter version, per-source watermarks, observed-through time, lag, known retention limits and coverage. Poll local sources without model calls. Restart from durable state.

- [ ] Write `test_service_commands_and_coverage` through the actual service entry point with temporary project roots and both providers. Verify the command table, confirmed registration, `collect-once` lease refusal, and that a bind, correction and anchor addition are queued and acknowledged while the same service keeps its writer lock. Test permission loss, incomplete rows, and separate heartbeat, watermarks and source lag. Verify known price reaches direct and inclusive rollups, Unknown price preserves tokens, and quota and spend remain separate.
- [ ] Run `test_service.py` to show failure, implement the loop and commands, then pass leaf verification.

## Accepted amendment

[Revised implementation plan](../83/plan/usage-capture-replan.md). Extend types.py with typed registration and source anchor records and their static codecs. Edit only the source-anchor dispatch case in scopes.py. Keep approved raw roots in private configuration and store only pseudonymous anchor records and configuration identity in the ledger. Prove restart and acknowledgment of an added anchor without resetting the activation boundary.

## Current pickup

[Design](design/design.md) · [Plan](plan/implementation-plan.md) · [JIT](plan/jit.md) · [Scoped review](plan/pickup-review.md). This is a manual Develop admission for the dedicated worktree at the pinned base.

[Source verification and independent review](plan/source-review.md). Staged for the reviewed #83 integration. Delivery evidence is recorded when the package lands.

[Launch health supplemental JIT](plan/launch-health-jit.md) · [Independent pickup review](plan/launch-health-pickup-review.md). The original collector source receipt is preserved.
