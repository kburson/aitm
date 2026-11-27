---
schema: "aitm.story/v0"
id: 242
title: "[Core C89] Installed managed PR and evidence commands"
kind: "story"
state: ready-for-plan
issue: "https://github.com/kburson/aitm/issues/242"
parent: 490
children: []
blocking: [513, 514]
blocked-by: [240, 241, 499]
created: "2026-11-11T15:58:21Z"
updated: "2026-11-27T06:32:11.294Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c89"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C89", "parent": 490}
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":490,"design_sources":[2],"scope_entry":"C89","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
---

# [Core C89] Installed managed PR and evidence commands

## Accepted workflow reconciliation

[Core plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md) · [Native reconciliation receipt](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-26-core-native-reconciliation-receipt.json).

Current parent: [#490](https://github.com/kburson/aitm/issues/490). Key: C89. Estimate: **3.5 h**. Blocked by: #240, #241, #499.

Register composed source for Dev, mount pickup and governed PR operations through the shared catalog, and require local proof before push and current hosted CI/XPR for merge. Retirement happens after verified closeout under its retained dependent fence. C100/C101 prove the mounted order and parity.

The earlier decomposition below is retained as historical provenance. Current behavior and tests follow the accepted replan.

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

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **20** · **P1/S** · **3.5 agent-hours**. Design accepted for this manual workflow through issue #490 with scope entry **C89**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).
