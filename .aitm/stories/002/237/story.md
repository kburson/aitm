---
schema: "aitm.story/v0"
id: 237
title: "[Core C83] Published branch and draft provisioning"
kind: "story"
state: ready-for-plan
issue: "https://github.com/kburson/aitm/issues/237"
parent: 485
children: []
blocking: [238, 239, 508, 510]
blocked-by: [235, 236, 502, 509]
created: "2026-11-11T15:58:16Z"
updated: "2026-11-27T06:32:11.294Z"
last-branch: "planning"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c83"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C83", "parent": 485}
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":485,"design_sources":[2],"scope_entry":"C83","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
---

# [Core C83] Published branch and draft provisioning

## Accepted workflow reconciliation

[Core plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md) · [Native reconciliation receipt](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-26-core-native-reconciliation-receipt.json).

Current parent: [#485](https://github.com/kburson/aitm/issues/485). Key: C83. Estimate: **4 h**. Blocked by: #235, #236, #502, #509.

Reserve or backfill exact target and incarnation at pickup. Separate published branch and draft effect claims and their ambiguity recovery. Do not accept provisioning CI as candidate proof. Verify a supported bootstrap commit has the same tree.

The earlier decomposition below is retained as historical provenance. Current behavior and tests follow the accepted replan.

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

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **50** · **P1/S** · **4 agent-hours**. Design accepted for this manual workflow through issue #485 with scope entry **C83**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).
