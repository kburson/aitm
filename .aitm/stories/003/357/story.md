---
schema: "aitm.story/v0"
id: 357
title: "[Spike] Classify tests into execution categories"
kind: "spike"
state: "done"
issue: "https://github.com/kburson/aitm/issues/357"
parent: 356
children: []
blocking: [358, 359]
blocked-by: []
created: "2026-11-16T19:41:49Z"
updated: "2026-11-20T14:59:53Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": "S"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-20-357-delivery-plan.md", "plan/2026-11-20-357-collection-checkpoint.md", "plan/2026-11-20-357-classification-findings.md", "plan/reviews/2026-11-20-357-independent-findings-review.md", "plan/2026-11-20-357-delivery.json", "plan/2026-11-20-357-closure-receipt.json"], "attachments": ["attachments/2026-11-20-357-category-register.tsv", "attachments/2026-11-20-357-classification-evidence.json", "attachments/2026-11-20-357-collected-nodeids.tsv", "attachments/2026-11-20-357-source-witnesses.tsv", "attachments/2026-11-20-357-ubuntu-nodeids.tsv", "attachments/2026-11-20-357-unit-timing.tsv", "attachments/phase_timing.py"]}
expansions: []
trips: []
---

# [Spike] Classify tests into execution categories

[GitHub issue #357](https://github.com/kburson/aitm/issues/357) · [Parent #356](../356/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 570. Priority P2. Size S.

Question: which collected tests belong in fast unit, slow unit, local integration, and systems integration, and which collected tests fit none of those four?

Use the #285 family inventory and the current collected tests. Publish a written classification with a witness for each placement and an explicit list of the tests that fit none.

## Bound

This is research for #356. Write the classification. The suite, the hosted path map, and CI stay unchanged.

## Handoff

#358 and #359 stay blocked until this receipt is accepted.

## Acceptance criteria

- Pin source commit and tree, locked tooling, platform and all pytest collection roots. Preserve exact parameterized IDs and two agreeing clean collections. Document optional native profiles, source discovery and profile differences.
- Give every collected ID one category or an explicit exception, with a source or fixture witness and reason. Use timing to distinguish fast unit from slow unit. Cite the timing profile and keep unmeasured or ambiguous placement visible.
- Reconcile the register against the collection and the #285 family audit. Publish categorized and exception counts, exact set differences and any collection caveats. Obtain independent acceptance of the dated findings before releasing #358 or #359.

[Delivery plan](plan/2026-11-20-357-delivery-plan.md).

[First collection checkpoint](plan/2026-11-20-357-collection-checkpoint.md).

[Classification findings](plan/2026-11-20-357-classification-findings.md) and [reconciled evidence](attachments/2026-11-20-357-classification-evidence.json).

[Independent acceptance](plan/reviews/2026-11-20-357-independent-findings-review.md) · [Delivery receipt](plan/2026-11-20-357-delivery.json) · [Sign-off](retro/2026-11-20-357-sign-off.md).

[Verified closure](plan/2026-11-20-357-closure-receipt.json).
