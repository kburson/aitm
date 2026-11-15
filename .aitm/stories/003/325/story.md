---
schema: "aitm.story/v0"
id: 325
title: "[M11a] Own native root watch resources and overflow hints"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/325"
parent: 100
children: []
blocking: [121]
blocked-by: [120]
created: "2026-11-15T18:21:42Z"
updated: "2026-11-15T18:22:18Z"
last-branch: "planning"
estimate: {"agent-hours": 3.0, "size": "M"}
priority: null
origin: ".aitm/stories/001/121/plan/2026-11-15-121-watch-inventory-coordinator-split-r2.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan-amendment", "source-story": 121, "key": "M11a", "publication": "1c31ecbf2680b3c59e69a8fb06ae02590e593c83", "raw-sha256": "84ede6331b21b6e01347bda1bd9e027279bfc0b7b853da9dbab81e2b7ded747e"}
---

# [M11a] Own native root watch resources and overflow hints

[Native issue #325](https://github.com/kburson/aitm/issues/325) · [Epic #100](../../001/100/story.md) · [Accepted M11 amendment](../../001/121/plan/2026-11-15-121-watch-inventory-coordinator-split-r2.md)

Rank 245 and provisional Estimate 3 implementation hours. Complete the independent Refine and JIT before Develop. The existing signed Test, independent source review, verified delivery and native Close apply.

## Refine

Verified #120 Close and the M11a split release this leaf at Rank 245. [Independent refinement packet](plan/2026-11-15-325-native-watch-refine.md).

Independent Refine passed at 3.0 implementation hours. [Refine receipt](plan/native-watch-independent-refine-receipt.json) · [Exact JIT packet](plan/2026-11-15-325-native-watch-jit.md).

## Develop

Independent JIT passed. [Signed-off plan boundary](plan/native-watch-independent-jit-receipt.json).

## Test

Both native watchers delivered events and retired their resources. Linux proved actual overflow and recovery. Both host groups proved zero transcript payload opens. The exact candidate passed 1,409 locked local tests. [Test proof](plan/native-watch-local-test.json) · [PR #327](https://github.com/kburson/aitm/pull/327).

The Darwin watcher now retires its native owner after the last authorized root is lost. The corrected exact candidate passed 1,410 locked local tests. [Corrected Test proof](plan/native-watch-owner-retirement-local-test.json).

## Independent source

The exact dormant native watcher passed signed Test. Independent source returned **PASS**. [Signed Test](plan/native-watch-signed-hosted-r1.json) · [Source receipt](plan/native-watch-independent-source-r1-receipt.json).

## Close

PR #327 merged to trunk after signed hosted Test and independent source review. Native state is Closed Completed and the Project is Done. [Delivery](plan/native-watch-verified-delivery.json) · [Native Close](plan/native-watch-native-close.json).
