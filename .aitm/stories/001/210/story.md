---
schema: "aitm.story/v0"
id: 210
title: "[M08b4c] Verified paired disposition settlement"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/210"
parent: 100
children: []
blocking: [119, 204]
blocked-by: [209]
created: "2026-11-11T02:38:35Z"
updated: "2026-11-11T02:41:48+00:00"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan-split", "story": 100, "key": "M08b4c", "source-leaf": 199, "raw-sha256": "8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21", "split-sha256": "1c97ab7d36b9fe162e59472e89da03a36b2ddbcf83717f6fb70a89eeba85000f", "path": ".aitm/stories/001/199/plan/2026-11-10-199-m08b-proof-split.md", "refinement": {"source-leaf": 203, "sha256": "0158b267bcfcee8989639d7aa89a84bdf4e1687849ec449abfab07fe198a6cbf", "path": ".aitm/stories/001/203/plan/2026-11-10-203-disposition-proof-split.md"}}
---

# [M08b4c] Verified paired disposition settlement

[GitHub issue #210](https://github.com/kburson/aitm/issues/210) · [Epic #100](../100/story.md) · [Accepted split](../203/plan/2026-11-10-203-disposition-proof-split.md)

Direct child of Epic #100. Requires #209 and directly gates #119 and #204.

Qualify a genuinely settled native terminal with no later usage under chronological public-reader evidence. A proof-only EOF receipt with an unresolved boundary or absent cursor cannot settle it. Independently verify both owner and rival source/span/frontier authorities before any paired release. Derive the admitted routing ScopeView's effective hold from the one committed journal change under the existing writer and publication fence. Keep earlier evidence, first ownership, unsupported coverage, and all unresolved frontiers. M09 retains publication and project ACK.

Project 24 Rank 228.2. Size and Estimate follow independent Refine and JIT. Start Date follows Develop.

## Independent Refine checkpoint

[Refine](plan/2026-11-11-210-native-terminal-refine.md) held because no chronological public-reader control qualified a genuinely settled no-later-usage terminal. [Independent verdict](plan/2026-11-11-210-native-terminal-refine-review.md) · [Native qualification evidence](plan/native-terminal-qualification.json).
