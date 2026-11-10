---
schema: "aitm.story/v0"
id: 152
title: "[#133 T15] Schedule full trunk validation and ingest evidence"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/152"
parent: 133
children: []
blocking: [153, 160]
blocked-by: [150]
created: "2026-11-10T16:51:31Z"
updated: "2026-11-10T16:56:26Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T15", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "aff13a45e1be82f0ad543478da1006c60c3b4fda82cd8f8a3a75d5fb57f588ef"}
---

# [#133 T15] Schedule full trunk validation and ingest evidence

[GitHub issue #152](https://github.com/kburson/aitm/issues/152) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L396)

**Required predecessors** [T13 #150](../150/story.md).

The planning estimate is 3.5 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T15. Schedule full trunk validation and ingest evidence — 3.5h, P1, T13

**Owns** `.github/workflows/tia-full.yml`,
`tools/ci/tia/scheduled.py`, `test_tia_scheduled.py`.
**Interface** `ingest(run, trusted_expectation, now) -> HealthEvent`.

- [ ] `test_failed_test_precedes_incomplete_run` and
  `test_overdue_schedule_holds_merges` authenticate negative evidence
  independently of final success. Unknown is never healthy.
- [ ] Use nightly full validation in the isolated target, with an
  immediate incident-bound dispatch for recovery. Proposed default
  freshness is 30 hours since the last qualifying completion,
  with missed-dispatch detection independent of that workflow.
  Reconcile all outcomes against the last trusted full trunk baseline
  using T10's ordered intervening inventory dispositions.
  V(scheduled) and a hosted skipped/missing shard drill pass.
