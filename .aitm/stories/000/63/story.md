---
schema: "aitm.story/v0"
id: 63
title: "[Core C62] Epic aggregation and scope-resolution checkpoint"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/63"
parent: 2
children: []
blocking: [65]
blocked-by: [26, 38, 45, 49]
created: "2026-11-09T08:03:57Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 2.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c62-epic-aggregation-and-scope-resolution-checkpoint"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C62", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "21a4bfc15642d00f1432f0c4337cd2aeed254751c64116c2d1bba7eeeabd2825"}
---

# [Core C62] Epic aggregation and scope-resolution checkpoint

**GitHub issue:** [kburson/aitm#63](https://github.com/kburson/aitm/issues/63) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C62 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 2.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c62-epic-aggregation-and-scope-resolution-checkpoint), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C22 / #26](../26/story.md), [C29 / #38](../38/story.md), [C38 / #45](../45/story.md), [C42 / #49](../49/story.md).

**Blocking:** [C49 / #65](../65/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 2.5 h · **Depends on:** C22, C29, C38, C42 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/aggregation.py; src/aitm_core/machine/kinds.py; packages/aitm-core/tests/integration/test_c62.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `aggregate_children(snapshot, epic) -> AggregateEvidence`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_epic_aggregate: real epic transitions start with accepted plan/child set despite mixed child states; later Test/Review rechecks required verification and delivered or explicitly scope-resolved children. Changed child scope invalidates assessment; abandoned/replaced dependency needs explicit dependent resolution. No epic clock/JIT/PR/test subprocess.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c62.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Use one pinned related-story snapshot and CAS read-set; scope resolution is retained evidence, not blanket acceptance of abandoned work.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Use one pinned related-story snapshot and CAS read-set; scope resolution is retained evidence, not blanket acceptance of abandoned work.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:03:57Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
