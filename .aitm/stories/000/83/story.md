---
schema: "aitm.story/v0"
id: 83
title: "[Epic] Continuous agent usage capture"
kind: "epic"
state: "plan"
issue: "https://github.com/kburson/aitm/issues/83"
parent: null
children: [84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96]
blocking: [3]
blocked-by: []
created: "2026-11-09T13:53:47Z"
updated: "2026-11-09T22:39:52+00:00"
last-branch: "planning"
estimate: {"agent-hours": 48.5, "size": "L"}
priority: "P1"
origin: "Owner brainstorming and lifetime usage planning, 2026-11-09"
files: {"draft": "draft.md", "events": "events.jsonl", "design": ["design/usage-capture-design.md"], "plan": ["plan/usage-capture-implementation-plan.md", "plan/leaf-stories.md", "plan/usage-capture-replan.md", "plan/usage-capture-relationship-replan.md", "plan/usage-capture-accounting-integration-supplement.md", "plan/usage-capture-accounting-integration-supplement-review.md", "plan/usage-capture-launch-health-replan.md", "plan/usage-capture-desktop-marker-replan.md", "plan/usage-capture-claude-startup-replan.md"], "attachments": ["attachments/agent-usage.md", "attachments/source-delivery.md"]}
expansions: []
trips: []
---

# [Epic] Continuous agent usage capture

[GitHub issue #83](https://github.com/kburson/aitm/issues/83) · [Core #2](../2/story.md) · [C44 / #51](../51/story.md) · [Measurement spike #73](../73/attachments/report.md)

As an AITM maintainer, I want the same continuous usage collector and durable ledger throughout the project's life. Start collection before Core delivery and keep it running through Core adoption and subsequent work.

## Reviewed design and plan

- [Accepted lifetime design](design/usage-capture-design.md) and [native design XPR](design/reviews/xpr-2026-11-09-usage-capture-design/review-manifest.md).
- [Accepted implementation plan](plan/usage-capture-implementation-plan.md) and [native plan XPR](plan/reviews/xpr-2026-11-09-usage-capture-plan/review-manifest.md).
- [Delivery order and 13 leaf issues](plan/leaf-stories.md), totaling **48.5 implementation agent-hours**. Each leaf stays within four hours.

## First delivery priority

Qualify the installed collector and record its live activation before [Core C01 / #3](../3/story.md) enters Develop. The reviewed Core #2 decomposition remains the baseline for the Core work itself. C44 later imports compatible observations while the collector and ledger continue in service.

Implementation resumed with #84 on the [accepted planning amendment](plan/usage-capture-replan.md). The original pickup and pause remain in the event history. [Agent usage evidence](attachments/agent-usage.md). Each leaf's own design, plan, JIT and execution follow applicable authority.

Implementation resumed with #86 after the [relationship admission amendment](plan/usage-capture-relationship-replan.md) passed review. The 48.5-hour epic estimate stays in force.

[Accounting integration follow-up](plan/usage-capture-accounting-integration-supplement.md) and [independent review](plan/usage-capture-accounting-integration-supplement-review.md) record the scoped Claude tier, Codex quota coverage and exact rollup corrections. [#93](../93/story.md) records the accepted real process crash and privacy verification.

[Launch health producer amendment under review](plan/usage-capture-launch-health-replan.md). The #94 source candidate is preserved pending exact process-attribution proof.

Implementation resumed on the accepted [launch health producer amendment](plan/usage-capture-launch-health-replan.md). #94 remains in Planning until the U08 producer witness and U12 exact rerun pass.

[Exact protected-trunk source delivery](attachments/source-delivery.md) is recorded. [#96](../96/story.md) verifies live installation and provider evidence before #83 closes.

[Codex Desktop carrier amendment under review](plan/usage-capture-desktop-marker-replan.md). Live qualification paused at the exact released source. Protected source delivery remains recorded.

The exact [Desktop marker carrier amendment](plan/usage-capture-desktop-marker-replan.md) passed SAR, SPR and native XPR. The accepted repair is on protected trunk. [#96 resumed](../96/plan/desktop-marker-recovery-jit.md) on that release for fresh live activation evidence.

[Claude startup prefix amendment under review](plan/usage-capture-claude-startup-replan.md). The live qualification paused after both Codex order cases passed and the Claude scanner held the target behind timed startup bookkeeping.
