---
schema: "aitm.story/v0"
id: 209
title: "[M08b4b] Atomic journal disposition and coverage projection"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/209"
parent: 100
children: []
blocking: [119, 210]
blocked-by: [203]
created: "2026-11-11T02:38:34Z"
updated: "2026-11-12T02:01:18+00:00"
last-branch: "codex/aitm-209-journal-disposition"
estimate: {"agent-hours": 3.9, "size": "M"}
priority: null
origin: ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-11-209-journal-disposition-refine.md", "plan/2026-11-11-209-journal-disposition-jit.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan-split", "story": 100, "key": "M08b4b", "source-leaf": 199, "raw-sha256": "8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21", "split-sha256": "1c97ab7d36b9fe162e59472e89da03a36b2ddbcf83717f6fb70a89eeba85000f", "path": ".aitm/stories/001/199/plan/2026-11-10-199-m08b-proof-split.md", "refinement": {"source-leaf": 203, "sha256": "0158b267bcfcee8989639d7aa89a84bdf4e1687849ec449abfab07fe198a6cbf", "path": ".aitm/stories/001/203/plan/2026-11-10-203-disposition-proof-split.md"}}
---

# [M08b4b] Atomic journal disposition and coverage projection

[GitHub issue #209](https://github.com/kburson/aitm/issues/209) · [Epic #100](../100/story.md) · [Accepted split](../203/plan/2026-11-10-203-disposition-proof-split.md)

Direct child of Epic #100. Requires #203 and directly gates #119 and #210.

Record writer-verified disposition evidence in the private routing journal under independently reviewed v4 compatibility. Determine existing and late affected claims by their exact native half-open span. Write one atomic local JournalChange and retain historical views. Keep cursors, holds and disputes pending until M08b4c.

Exercise the #115 keyed Grok contradiction with the actual approved reader against existing durable claims. Record the missing Grok scope admission. Preserve unresolved quota-only, generic, mixed and aggregate diagnostics and copied-scope causal refusal. M09 owns publication and project ACK.

Project 24 Rank 228.1. Size and Estimate follow independent Refine and JIT. Start Date follows Develop.

## Independent Refine

[Round one](plan/2026-11-11-209-refine-review-r1.md) held on migration detail and misread the #119 dependency list. Both native reads included #202 and all eight dependencies. [Round two](plan/2026-11-11-209-refine-review-r2.md) passed the [amended Refine](plan/2026-11-11-209-journal-disposition-refine.md). Separate exact JIT is pending. [Measured Refine Actual](attachments/timing/refine-actual-readback-input.json) is a partial coordinator total from bounded progress intervals.

## Independent JIT acceptance

[Exact JIT](plan/2026-11-11-209-journal-disposition-jit.md), SHA-256 `ebf4dd8c2152e860a54b3dd3833715c07d69c198b58f9d545b8611392109128a`, passed [independent review](plan/2026-11-11-209-jit-review.md). The accepted implementation estimate is 3.90 agent-hours, Size M. The clean detached baseline passed 1,071 product and CLI tests and 182 helpers on literal trunk. Two earlier full attempts each had one inherited native capture setup refusal. Exact targeted repeats passed, and the final run used isolated fixture storage. The precise trigger was unverified.

The JIT's nonblocking notes guide implementation. A threatened four-hour cap, including recording still not green at 2.25 implementation agent-hours, requires an independent scope split before further Develop. The estimate covers implementation and focused verification, with delivery wait and review tracked separately. [Cumulative planning Actual evidence](attachments/timing/jit-actual-readback-input.json).
