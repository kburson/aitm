---
schema: "aitm.story/v0"
id: 86
title: "[Usage U13] Draft aliases, ancestry and direct/inclusive rollups"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/86"
parent: 83
children: []
blocking: [91]
blocked-by: [85]
created: "2026-11-09T14:42:17Z"
updated: "2026-11-09T14:43:23+00:00"
last-branch: "planning"
estimate: {"agent-hours": 2.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 83, "key": "U13", "path": ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md", "publication": "6ee371590ff3ce0cb5a108bdd1e89cfb17bc2300", "raw-sha256": "07919dde4475310b7fe277791206f611ce5cd615eeaed491d3a619e61142daf5", "section-sha256": "266835e43f20043047ae4394ffdb2aa6eb88c119d7a5b71676f37eed1650e2bc"}
---

# [Usage U13] Draft aliases, ancestry and direct/inclusive rollups

[GitHub issue](https://github.com/kburson/aitm/issues/86) · [Parent #83](../83/story.md) · Backlog

**Required predecessors** [#85](../85/story.md)

## Accepted parent decomposition

**Files** `src/aitm_usage/{rollup,cli}.py`, `tests/test_rollup.py`.

**Contract** `rollup(root: ItemKey, view: LedgerView) -> UsageRollup`. Queue alias and parent commands through U02's inbox. Preserve revisions of ancestry and graduation aliases and compute inclusive totals from distinct canonical descendants. Represent known Decimal price and a separate Unknown count.

- [ ] Write `test_graduation_and_inclusive_rollup` with an epic, two children, an alias from draft to issue, epic batch usage and per-child usage. Assert each observation contributes once, previous as-of results remain intact and cycles or contradictory aliases are refused. Exercise real CLI publication of alias and parent commands. Use price fixtures until U06 supplies accounting.
- [ ] Run `test_rollup.py` to show failure, implement the rollup and alias/ancestry commands, then pass leaf verification.
