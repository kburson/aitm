---
schema: "aitm.story/v0"
id: 478
title: "[Epic] Core — Planning and pickup evidence"
kind: "epic"
state: done
issue: "https://github.com/kburson/aitm/issues/478"
parent: 1
children: [36, 75, 501, 502]
blocking: []
blocked-by: [8, 13, 15, 27, 35, 500]
created: "2026-11-27T04:48:45Z"
updated: "2026-11-28T07:33:59.204125+00:00"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 15.0, "size": "Feature"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "EP09"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-28-pickup.md", "plan/2026-11-28-pr-579-verification.md", "plan/2026-11-28-pr-579-source-sar.md", "plan/2026-11-28-pr-579-hosted.json", "plan/2026-11-28-pr-579-verifier.json", "plan/2026-11-28-pr-579-premerge-verifier.json", "plan/2026-11-28-pr-579-source-sar.json", "plan/2026-11-28-pr-579-branch-gates.json", "plan/2026-11-28-pr-579-delivery.json", "plan/2026-11-28-pr-579-ep09-composition.json", "plan/2026-11-28-pr-579-postmerge-verifier.json", "plan/2026-11-28-pr-579-native-link.json", "plan/2026-11-28-pr-579-readiness.json", "plan/2026-11-28-pr-579-composed-proof.json"], "attachments": []}
expansions: []
trips: []
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":1,"design_sources":[1,2],"scope_entry":"EP09","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
linked-pr: "https://github.com/kburson/aitm/pull/579"
---

# [Epic] Core — Planning and pickup evidence

**GitHub issue:** [#478](https://github.com/kburson/aitm/issues/478)

## Scope

Verify all three planning bases and the peer-review boundary for material child-JIT changes.

Parent: #1. Core coordination: #2. State: Ready for Planning.

## Delivery

Integration owner: #502. Require verified sibling deliveries #36, #75, #501, the exact composed-tree proof, and the applicable CI and review gates before trunk admission. Resource-only preparation may precede sibling delivery.

Required upstream trunk receipts: #8, #13, #15, #27, #35, #500.

## Children

- #36 · C27 · 3.5 h
- #75 · C72 · 4 h
- #501 · C93 · 3.5 h
- #502 · C94 · 4 h

Estimate: **15 implementation agent-hours**, including verification and review. [Reviewed implementation plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Accepted delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md).

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **90** · **P1/Feature** · **15 agent-hours**. Design accepted for this manual workflow through issue #1 with scope entry **EP09**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).


## Verified delivery

[Scoped JIT](plan/2026-11-28-pickup.md) · [Coordinator sign-off and Agent Cost](retro/2026-11-28-delivery.md) · [Native Linked PR #579](https://github.com/kburson/aitm/pull/579).
