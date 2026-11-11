---
schema: "aitm.story/v0"
id: 203
title: "[M08b4a] Verified native disposition proof"
kind: "story"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/203"
parent: 100
children: []
blocking: [119, 204, 209]
blocked-by: [202]
created: "2026-11-10T23:50:13Z"
updated: "2026-11-11T02:54:42+00:00"
last-branch: "codex/aitm-203-native-disposition-proof"
estimate: {"agent-hours": 3.85, "size": "M"}
priority: null
origin: ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-10-203-disposition-proof-split.md", "plan/2026-11-10-203-native-disposition-proof-plan.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan-split", "story": 100, "key": "M08b4a", "source-leaf": 199, "raw-sha256": "8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21", "split-sha256": "1c97ab7d36b9fe162e59472e89da03a36b2ddbcf83717f6fb70a89eeba85000f", "path": ".aitm/stories/001/199/plan/2026-11-10-199-m08b-proof-split.md", "refinement": {"source-leaf": 203, "sha256": "0158b267bcfcee8989639d7aa89a84bdf4e1687849ec449abfab07fe198a6cbf", "path": ".aitm/stories/001/203/plan/2026-11-10-203-disposition-proof-split.md"}}
---

# [M08b4a] Verified native disposition proof

[GitHub issue #203](https://github.com/kburson/aitm/issues/203) · [Epic #100](../100/story.md) · [Accepted Refine split](plan/2026-11-10-203-disposition-proof-split.md) · [Native graph and Project receipt](plan/native-split-receipt.json)

Require the exact current writer and an append-only native terminal receipt bound to the authenticated older owned span. Preserve strict v1 history, record the separate proof under the exact reviewed private format, and leave the effective hold and journal frontier in place. The independent ordered EOF probe verifies the receipt with an unresolved boundary and no cursor.

[#209](../209/story.md) owns atomic journal recording and coverage projection. [#210](../210/story.md) owns the effective hold and independently qualified paired settlement. [#204](../204/story.md) retains folded proof. Every disposition leaf directly gates #119.

Project 24 Rank 228. Size M, Estimate 3.85 implementation agent-hours, November 10 Start Date. [Exact JIT and delivery checkpoints](plan/delivery-checklist.md).
