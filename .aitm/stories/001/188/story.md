---
schema: "aitm.story/v0"
id: 188
title: "[#181 A03] Compute workflow timing and epic totals"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/188"
parent: 181
children: []
blocking: [190]
blocked-by: [187]
created: "2026-11-10T21:02:16Z"
updated: "2026-11-11T04:22:12Z"
last-branch: "trunk"
estimate: {"agent-hours": 3.75, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": ["plan/jit.md"], "plan": ["plan/jit.md", "plan/delivery-checklist.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 181, "key": "A03", "path": ".aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md", "publication": "fd5b22ff0c33c582dd9a0926435d071f09ac6156", "raw-sha256": "147cbee5740f725c9c65df9c09034912220d179475dc1c707e0844316a6c1c80", "section-sha256": "4eb0bf6e348515dc553a8cc83910821b4aa1f1366b116313e3ddcc89f7254185"}
---

# [#181 A03] Compute workflow timing and epic totals

[GitHub issue #188](https://github.com/kburson/aitm/issues/188) · [Parent #181](../181/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/fd5b22ff0c33c582dd9a0926435d071f09ac6156/.aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md#L70)

Required predecessors #187. The proposed estimate is 3.75 implementation agent-hours. Recheck scope and estimate at the leaf’s own refinement and JIT.

## Accepted plan excerpt

## A03. Compute workflow timing and epic totals

- [ ] Test `test_parallel_wait_and_elapsed_scopes`. The accepted fixture gives 2h45m elapsed, 2h15m working wall time and 3.25 agent-hours. Overlap the same actor's turn and tool interval. Overlap two documented owner waits while another actor works. Exercise pending wait watermark, missing response, missing elapsed start and age. An implementation-only estimate mismatched with all-phase Actual and all partial records stay out of calibration. Verify #111 implementation-delivery elapsed is 774,000 ms with all-phase Unknown.
- [ ] Run red. Implement `project_timing`. Union qualified turn/tool evidence for each actor, subtract evidenced exclusion intervals for that actor, and sum actors. Union owner wait on the calendar and bound pending observations by the positive evidence watermark and as-of. Derive elapsed from the selected boundary pair and use age for supported open intervals. Consume the A01 parent graph and walk distinct descendants once. Treat graph gaps as incomplete coverage. Keep raw integer milliseconds, phase/role evidence and independent watermarks.
- [ ] Run green and verify exact direct plus descendant totals at the historical parity pin `17761cc1928fd916cf32a9c078d4a742bfcb32b8`. The verified seed has no same-actor overlaps, and the graph restricted to measured descendants matches the seed’s counted children. Assert both facts as fixture preconditions. Additional unmeasured children keep coverage partial. A changed graph or new overlap in a later snapshot is reported with scoped provenance. Maintain the distinction between elapsed, Actual, observed work wall time and trip qualification.

## Delivery evidence

[Reviewed pickup](plan/jit.md) · [Independent pickup review](plan/jit-review.md) · [Delivery checklist](plan/delivery-checklist.md)

## Delivered

Verified source `72ca2d2535248844b164014d7817bffec0e9fb7e` landed on trunk. GitHub Closed Completed and AITM-PY Done were verified.

[Source PR](https://github.com/kburson/aitm/pull/213) · [Signed CI](plan/hosted-verification-2.json) · [Source review](plan/post-ci-source-review.md) · [Implementing-agent sign-off](retro/2026-11-10-implementer-signoff.md)
