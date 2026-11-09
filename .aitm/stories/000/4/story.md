---
schema: "aitm.story/v0"
id: 4
title: "[Core C02] Event envelopes and reducer dispatch invariants"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/4"
parent: 2
children: []
blocking: [6, 7, 8, 9, 14, 16, 23, 28, 29]
blocked-by: [3]
created: "2026-11-09T07:59:41Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 2.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c02-event-envelopes-and-reducer-dispatch-invariants"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C02", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "cdd36ebf320b31ebf8b8fe0918f8321709b2cf33811847ff83f91509a2a3078b"}
---

# [Core C02] Event envelopes and reducer dispatch invariants

**GitHub issue:** [kburson/aitm#4](https://github.com/kburson/aitm/issues/4) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C02 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 2.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c02-event-envelopes-and-reducer-dispatch-invariants), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C01 / #3](../3/story.md).

**Blocking:** [C54 / #6](../6/story.md), [C55 / #7](../7/story.md), [C56 / #8](../8/story.md), [C04 / #9](../9/story.md), [C13 / #14](../14/story.md), [C15 / #16](../16/story.md), [C18 / #23](../23/story.md), [C23 / #28](../28/story.md), [C24 / #29](../29/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 2.5 h · **Depends on:** C01 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/models/events.py; src/aitm_core/events.py; packages/aitm-core/tests/unit/test_c02.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `validate_envelope(raw) -> EventEnvelope; fold(events, reducers: ReducerRegistry) -> StoryState`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_causal_envelope: same-timestamp/late occurrence preserves append order; sequence/prior digest and duplicate-ID/different payload fail. Reducer registry rejects missing required core reducer and retains unknown optional extension bytes. C54–C56 supply domain payload schemas and reducers before production fold is complete.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c02.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** This leaf owns only envelope/dispatch/causal identity, not every domain schema or clock algorithm. Unsupported required domains are unavailable, never folded as success.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: This leaf owns only envelope/dispatch/causal identity, not every domain schema or clock algorithm. Unsupported required domains are unavailable, never folded as success.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T07:59:41Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
