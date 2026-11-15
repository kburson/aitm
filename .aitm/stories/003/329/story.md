---
schema: "aitm.story/v0"
id: 329
title: "[M11c] Prove positive Grok capture and scope authority"
kind: "story"
state: "review"
issue: "https://github.com/kburson/aitm/issues/329"
parent: 100
children: []
blocking: [330, 331]
blocked-by: [115, 117, 304, 326]
created: "2026-11-15T19:50:35Z"
updated: "2026-11-15T19:51:14Z"
last-branch: "codex/aitm-329-grok-capture"
estimate: {"agent-hours": 3.75, "size": "M", "scope": "provisional"}
priority: null
origin: ".aitm/stories/001/121/plan/2026-11-15-121-grok-guarded-delivery-amendment.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan-amendment", "source-story": 121, "key": "M11c", "publication": "121f47b5588dcd351de191cd07a24da0c4cb5e0b", "raw-sha256": "9ff468c70ce7c9ddec99858bbaaa4eb35761754fe282109b09a03bd8eb731732"}
---

# [M11c] Prove positive Grok capture and scope authority

[Native issue #329](https://github.com/kburson/aitm/issues/329) · [Epic #100](../../001/100/story.md) · [Accepted M11 amendment](../../001/121/plan/2026-11-15-121-grok-guarded-delivery-amendment.md)

Rank 248 and provisional Estimate 3.5 implementation hours. Complete the independent Refine and JIT before Develop. The existing signed Test, independent source review, verified delivery and native Close apply.

## Refine

Verified #115, #117, #304 and #326 Close and the M11c split release this leaf at Rank 248. [Independent refinement packet](plan/2026-11-15-329-positive-grok-capture-refine.md).

[Independent Refine passed](plan/grok-capture-independent-refine.md), with 14 conditions for exact JIT.

[Exact JIT](plan/2026-11-15-329-positive-grok-capture-jit.md) is submitted for independent acceptance.

[First JIT held](plan/grok-capture-independent-jit-r1.md) on the exact cut, codec and authority boundaries. [Recovery JIT](plan/2026-11-15-329-positive-grok-capture-jit-r2.md) is submitted on literal trunk.

[Independent JIT recovery passed](plan/grok-capture-independent-jit-r2.md). [Develop entry evidence](plan/grok-capture-develop-entry.json) binds the actual #326 merge and exact legacy goldens.

## Test

The exact candidate passed 1,450 locked local tests. The earlier run identified an extra exclusion decision consumer. The correction passed the existing invariant and the same locked suite. The strict cursor and original-route proofs used retained bytes and the isolated issuer. [Exact local Test](plan/grok-capture-local-test.json) · [PR #332](https://github.com/kburson/aitm/pull/332).

[Signed hosted Test](plan/grok-capture-signed-hosted-test.json) verified the same exact candidate and inherited controls. Independent source review is submitted.

[Independent source review](plan/grok-capture-independent-source.md) returned **HOLD** on the exact signed candidate. [Receipt](plan/grok-capture-independent-source-receipt.json).

The [exact recovery candidate](plan/grok-capture-local-recovery-test.json) passed 1,459 locked local tests and 111 focused tests. The source findings on mixed cuts, held terminal handling and the receipt matrix are reproduced and corrected in the accepted four paths.

[Signed hosted recovery](plan/grok-capture-signed-hosted-recovery.json) verified the exact corrected tree and unchanged controls. The ordinary source recovery is submitted.
