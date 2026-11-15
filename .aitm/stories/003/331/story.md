---
schema: "aitm.story/v0"
id: 331
title: "[M11e] Enroll new Grok streams under existing capture grants"
kind: "story"
state: "test"
issue: "https://github.com/kburson/aitm/issues/331"
parent: 100
children: []
blocking: [121]
blocked-by: [329]
created: "2026-11-15T20:26:05Z"
updated: "2026-11-15T20:26:19.292544+00:00"
last-branch: "planning"
estimate: {"agent-hours": 2.75, "size": "M", "scope": "provisional"}
priority: null
origin: ".aitm/stories/001/121/plan/2026-11-15-121-grok-prospective-enrollment-amendment.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan-amendment", "source-story": 121, "key": "M11e", "publication": "4b8ab7bb2bc720439c84ce76a18e32c620b580ab", "raw-sha256": "eec5d84ba0e4e76f6412a35bc60dfa200b5af85a312617c7e41b20923411006b"}
---

# [M11e] Enroll new Grok streams under existing capture grants

[Native issue](https://github.com/kburson/aitm/issues/331) · [Accepted parent plan](../../001/121/plan/2026-11-15-121-grok-prospective-enrollment-amendment.md)

Rank 249.5, provisional Estimate 2.75 implementation hours. #329 must close before independent Refine and JIT. #121 owns the coordinator call.

## Refine

Verified #329 Close and the M11e split release this leaf at Rank 249.5. [Independent refinement packet](plan/2026-11-15-331-grok-prospective-enrollment-refine.md).

[First independent Refine](plan/grok-enrollment-independent-refine-r1.md) held the durable gap and proof derivation. [Recovery](plan/2026-11-15-331-grok-prospective-enrollment-refine-r2.md) pins the exact committed command publication and present control APIs.

[Independent Refine recovery passed](plan/grok-enrollment-independent-refine-r2.md) on the exact applied-command proof, durable prospective gap and disjoint three-file ownership.

[Exact JIT](plan/2026-11-15-331-grok-prospective-enrollment-jit.md) is submitted for independent acceptance.

[Independent JIT](plan/grok-enrollment-independent-jit.md) passed with pins J1–J10 for exact trunk. Develop uses the three accepted paths.

## Test

The exact candidate passed 1,484 locked local tests. The focused regressions cover grant reconstruction, empty roots, late discovery and in-flight turns, profile and incarnation changes, the pending-disable fence, and preserved gap readback. [Exact local Test](plan/grok-enrollment-local-test.json) · [PR #334](https://github.com/kburson/aitm/pull/334).

[Signed hosted Test](plan/grok-enrollment-signed-hosted-test.json) verified the same exact candidate and inherited controls. Independent source review is submitted.

[Independent source review](plan/grok-enrollment-independent-source.md) returned **HOLD** on the exact signed candidate. [Receipt](plan/grok-enrollment-independent-source-receipt.json).

## Source review recovery

The exact candidate passed 1,487 locked local tests. The regressions cover quiet and in-flight reissue gaps, and retired gap readback after the source approval set changes. [Exact local Test](plan/grok-enrollment-source-r2-local-test.json) · [PR #334](https://github.com/kburson/aitm/pull/334).
