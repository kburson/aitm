---
schema: "aitm.story/v0"
id: 285
title: "[#133] Audit existing tests for behavioral value and execution cost"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/285"
parent: 133
children: []
blocking: [287, 288, 290]
blocked-by: [267]
created: "2026-11-14T13:09:48Z"
updated: "2026-11-15T02:13:27Z"
last-branch: "planning"
estimate: {"agent-hours": 4, "size": "M"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-14-133-behavior-driven-validation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-14-285-behavior-audit-checkpoint.md", "plan/audit-inventory.json", "plan/audit_inventory.py", "plan/start-audit.sh", "plan/2026-11-14-285-behavior-audit.md", "plan/audit-families.tsv", "plan/reviews/2026-11-14-285-behavior-audit-review.md", "plan/collection-inputs/product-collection.log", "plan/collection-inputs/helper-collection.log", "plan/collection-inputs/all-helper-collection.log", "plan/collection-inputs/hosted-python.log", "plan/delivery.json", "plan/closure-receipt.json"], "attachments": []}
expansions: []
trips: []
---

# [#133] Audit existing tests for behavioral value and execution cost

Parent #133. Rank 100.

Inventory the pinned collected tests by family, timing, behavior and protective boundary. Review every family, prioritizing the slowest and largest. Record candidates to keep, consolidate, replace or investigate with exact witnesses and unknowns. Publish a repeatable inventory and reviewable findings.

[Reviewed epic plan](../../001/133/plan/2026-11-14-133-behavior-driven-validation-plan.md). #103 governs production.

## Audit kickoff

[Checkpoint](plan/2026-11-14-285-behavior-audit-checkpoint.md) and [exact inventory](plan/audit-inventory.json).

## Completed behavior audit

[Audit](plan/2026-11-14-285-behavior-audit.md) · [All 42 families](plan/audit-families.tsv) · [Independent review](plan/reviews/2026-11-14-285-behavior-audit-review.md). The published inventory can be regenerated using the retained inputs.

## Closure

[Verified closure receipt](plan/closure-receipt.json).
