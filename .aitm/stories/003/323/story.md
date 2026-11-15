---
schema: "aitm.story/v0"
id: 323
title: "[#133] Qualify explicit recovery after a missed full-suite slot"
kind: "story"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/323"
parent: 133
children: []
blocking: []
blocked-by: [294]
created: "2026-11-15T17:24:59Z"
updated: "2026-11-15T17:25:50Z"
last-branch: "planning"
estimate: {"agent-hours": 4, "size": "M"}
priority: "P2"
origin: ".aitm/stories/002/294/plan/2026-11-15-294-cutover-and-rollback-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/start.json", "plan/2026-11-15-323-missed-slot-recovery-plan.md"], "attachments": []}
expansions: []
trips: []
---

# [#133] Qualify explicit recovery after a missed full-suite slot

Parent #133. Required predecessor #294, delivered. Rank 150, 4 implementation agent-hours, M, P2.

Authenticate the missed current production 03:47 UTC full-suite slot with a read-only protected-source and GitHub provider capture. On a disposable native GitHub protected default target, intentionally miss a separate rehearsal window and qualify a separately authorized operator dispatch. Run the exact full production scheduled-suite scope at a pinned protected production SHA. Reconcile run/attempt, workflow, target, issuance, ordered inventories and full report phases, native child witnesses, timing, and published evidence against independent GitHub reads and collected test outcomes. Fail closed for absent or late slots, a pending or red result, missing or foreign evidence, stale/moved targets, wrong events and supersession/replay.

Keep the simulated incident hold active until the operator explicitly acknowledges still-current verified evidence. Retain live records, clearly labeled replay controls, reproducibility instructions and an independently signed exact-evidence review. Production stays read-only apart from issue, board and planning records. The production diagnostic dispatch provides no recovery eligibility. #103 remains authoritative and production cutover requires separate explicit owner approval.

[Independently accepted #294 decision](https://github.com/kburson/aitm/blob/6d2a29fdfcef865c6769bfefe1cc07ddc628302f/.aitm/stories/002/294/plan/2026-11-15-294-cutover-and-rollback-plan.md).

## Pickup

[Verified native Dev state, rank and dependencies](plan/start.json).

## Rehearsal plan

[Scope and acceptance cases](plan/2026-11-15-323-missed-slot-recovery-plan.md).
