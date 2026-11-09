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
updated: "2026-11-09T15:05:15+00:00"
last-branch: "planning"
estimate: {"agent-hours": 46.0, "size": "L"}
priority: "P1"
origin: "Owner brainstorming and lifetime usage planning, 2026-11-09"
files: {"draft": "draft.md", "events": "events.jsonl", "design": ["design/usage-capture-design.md"], "plan": ["plan/usage-capture-implementation-plan.md", "plan/leaf-stories.md", "plan/usage-capture-replan.md"], "attachments": ["attachments/agent-usage.md"]}
expansions: []
trips: []
---

# [Epic] Continuous agent usage capture

[GitHub issue #83](https://github.com/kburson/aitm/issues/83) · [Core #2](../2/story.md) · [C44 / #51](../51/story.md) · [Measurement spike #73](../73/attachments/report.md)

As an AITM maintainer, I want the same continuous usage collector and durable ledger throughout the project's life. Start collection before Core delivery and keep it running through Core adoption and subsequent work.

## Reviewed design and plan

- [Accepted lifetime design](design/usage-capture-design.md) and [native design XPR](design/reviews/xpr-2026-11-09-usage-capture-design/review-manifest.md).
- [Accepted implementation plan](plan/usage-capture-implementation-plan.md) and [native plan XPR](plan/reviews/xpr-2026-11-09-usage-capture-plan/review-manifest.md).
- [Delivery order and 13 leaf issues](plan/leaf-stories.md), totaling **46 implementation agent-hours**. Each leaf stays within four hours.

## First delivery priority

Qualify the installed collector and record its live activation before [Core C01 / #3](../3/story.md) enters Develop. The reviewed Core #2 decomposition remains the baseline for the Core work itself. C44 later imports compatible observations while the collector and ledger continue in service.

Implementation paused at #84 source review. [Planning amendment under review](plan/usage-capture-replan.md). The accepted baseline and prior development history are retained. [Agent usage evidence](attachments/agent-usage.md). Each leaf's own design, plan, JIT and execution follow applicable authority.
