---
schema: "aitm.story/v0"
id: 201
title: "[M08b2] Durable causal revision succession"
kind: "story"
state: "test"
issue: "https://github.com/kburson/aitm/issues/201"
parent: 100
children: []
blocking: [119, 202]
blocked-by: [199]
created: "2026-11-10T23:49:52Z"
updated: "2026-11-11T01:12:29+00:00"
last-branch: "codex/aitm-201-durable-revision-succession"
estimate: {"agent-hours": 3.75, "size": "M"}
priority: null
origin: ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-10-201-durable-revision-succession-plan.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan-split", "story": 100, "key": "M08b2", "source-leaf": 199, "raw-sha256": "8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21", "split-sha256": "1c97ab7d36b9fe162e59472e89da03a36b2ddbcf83717f6fb70a89eeba85000f", "path": ".aitm/stories/001/199/plan/2026-11-10-199-m08b-proof-split.md"}
---

# [M08b2] Durable causal revision succession

[GitHub issue #201](https://github.com/kburson/aitm/issues/201) · [Epic #100](../100/story.md) · [Exact split](../199/plan/2026-11-10-199-m08b-proof-split.md)

Use #199 writer-issued proof to reserve exact successors whose predecessor material equals the durable head, retain verified older no-op and historic views across restart, and migrate the dormant v1 store only through reviewed exact schema compatibility. Keep every unresolved source, quota and scope replay obligation. No destination write or ACK.

Project 24 Rank 226. Size and Estimate follow its own independent Refine and JIT. Start Date follows Develop.

## Accepted pickup

[Exact #201 JIT](plan/2026-11-10-201-durable-revision-succession-plan.md) passed its [second independent review](plan/2026-11-10-201-pickup-review-r2.md). #199 is Closed Completed and Project Done. #201 stays a direct #119 and #202 prerequisite. The earlier-cursor cold-read fixture is a hard gate.
