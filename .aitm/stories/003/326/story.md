---
schema: "aitm.story/v0"
id: 326
title: "[M11b] Authenticate sources through a shared metadata inventory"
kind: "story"
state: "review"
issue: "https://github.com/kburson/aitm/issues/326"
parent: 100
children: []
blocking: [121]
blocked-by: [115, 120, 304]
created: "2026-11-15T18:21:55Z"
updated: "2026-11-15T18:22:18Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "M"}
priority: null
origin: ".aitm/stories/001/121/plan/2026-11-15-121-watch-inventory-coordinator-split-r2.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan-amendment", "source-story": 121, "key": "M11b", "publication": "1c31ecbf2680b3c59e69a8fb06ae02590e593c83", "raw-sha256": "84ede6331b21b6e01347bda1bd9e027279bfc0b7b853da9dbab81e2b7ded747e"}
---

# [M11b] Authenticate sources through a shared metadata inventory

[Native issue #326](https://github.com/kburson/aitm/issues/326) · [Epic #100](../../001/100/story.md) · [Accepted M11 amendment](../../001/121/plan/2026-11-15-121-watch-inventory-coordinator-split-r2.md)

Rank 247.5 and provisional Estimate 3.5 implementation hours. Complete the independent Refine and JIT before Develop. The existing signed Test, independent source review, verified delivery and native Close apply.

## Refine

Verified #115, #120 and #304 Close and the M11b split release this leaf at Rank 247.5. [Independent refinement packet](plan/2026-11-15-326-metadata-inventory-refine.md).

Independent Refine accepted the six-file inventory scope at 3.5 implementation hours. [Refine receipt](plan/metadata-inventory-independent-refine-receipt.json).

[Exact JIT](plan/2026-11-15-326-metadata-inventory-jit.md) is submitted for independent acceptance.

## Develop

Independent JIT passed. Develop starts on the verified compatible watcher delivery. [JIT receipt](plan/metadata-inventory-independent-jit-receipt.json).

## Test

Actual native and Grok selected-read audits found zero opens of unchanged parked siblings. Changed transcripts and a changed Grok origin witness forced reauthentication. The existing journal entry exercised the same explicit cycle. The exact candidate passed 1,424 locked local tests. [Test proof](plan/metadata-inventory-local-test.json) · [PR #328](https://github.com/kburson/aitm/pull/328).

## Independent source

The exact selected-source inventory passed signed Test. Independent source returned **HOLD**. [Signed Test](plan/metadata-inventory-signed-hosted-r1.json) · [Source receipt](plan/metadata-inventory-independent-source-r1-receipt.json).

## Source recovery

Test-only proof now covers root and nested-directory supersession, inventory reuse and current key refusal, and exact Grok descriptor-relative opens. [Exact candidate](plan/metadata-inventory-source-recovery-candidate.json).

## Independent source recovery

The exact selected-source inventory passed signed Test. Independent source returned **PASS**. [Signed Test](plan/metadata-inventory-signed-hosted-r2.json) · [Source receipt](plan/metadata-inventory-independent-source-r2-receipt.json).
