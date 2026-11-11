---
schema: "aitm.story/v0"
id: 189
title: "[#181 A04] Resolve a pinned usage report"
kind: "story"
state: "review"
issue: "https://github.com/kburson/aitm/issues/189"
parent: 181
children: []
blocking: [190]
blocked-by: [186]
created: "2026-11-10T21:02:17Z"
updated: "2026-11-11T04:02:28Z"
last-branch: "codex/aitm-189-usage-view"
estimate: {"agent-hours": 3.0, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": ["plan/jit.md"], "plan": ["plan/jit.md", "plan/delivery-checklist.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 181, "key": "A04", "path": ".aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md", "publication": "fd5b22ff0c33c582dd9a0926435d071f09ac6156", "raw-sha256": "147cbee5740f725c9c65df9c09034912220d179475dc1c707e0844316a6c1c80", "section-sha256": "9650893a5b5b7b09cec23b683bd6d07f6dfa80ba2529b14102fbef98c95173f7"}
---

# [#181 A04] Resolve a pinned usage report

[GitHub issue #189](https://github.com/kburson/aitm/issues/189) · [Parent #181](../181/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/fd5b22ff0c33c582dd9a0926435d071f09ac6156/.aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md#L76)

Required predecessors #186. The proposed estimate is 3 implementation agent-hours. Recheck scope and estimate at the leaf’s own refinement and JIT.

## Accepted plan excerpt

## A04. Resolve a pinned usage report

- [ ] Test `test_select_one_registered_usage_report` with two reports for one story at different cutoff and rate identities, one missing story, one partial price and one conflicting candidate. Exercise an operator-verified monitor export identity, then a self-asserted assurance claim, mismatched export digest, mismatched selector and wrong story scope. Only the verified evidence contributes. Assert only the selected report is visible, that an evidenced supersession within it is deterministic, and that an absent or conflicted row is Unknown. Replayed identities and overlapping descendant rows cannot inflate cost.
- [ ] Run red. Implement `select_usage` over A01's registrations. Select the project, original report/sequence, UTC window and cutoff, rate card and pricing basis together. Require one effective direct receipt per story. Bind Cost admission to A01’s embedded verification record and evidence registration. Match its report identity and source digest to the verified fixed source binding, subject and selector to the direct usage receipt, and rate basis, coverage and sanitized data digest to the selected evidence. Check that binding, including the sanitized data digest in the committed evidence. Reject a receipt self-assertion or mismatch as Unknown. Preserve resolved digests and exact decimal subtotals. Compute inclusive totals using the A01 parent graph, which is the same graph used for timing. Mark incomplete price or attribution independently. A manually asserted timing record carries no token amount or rate.
- [ ] Run green with a sanitized fixture. Verify stable selection and separate cost coverage when timing evidence changes. Keep monitor report/export and C44 import authority with #100 and #2.

## Delivery evidence

[Reviewed pickup](plan/jit.md) · [Independent pickup review](plan/jit-review.md) · [Delivery checklist](plan/delivery-checklist.md)
