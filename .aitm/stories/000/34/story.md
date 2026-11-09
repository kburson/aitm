---
schema: "aitm.story/v0"
id: 34
title: "[Core C25] Live review capsules and qualified turn timing"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/34"
parent: 2
children: []
blocking: [35, 53]
blocked-by: [17, 28, 33]
created: "2026-11-09T08:01:49Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c25-live-review-capsules-and-qualified-turn-timing"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C25", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "d36fe7c96024ec0b8792f90d550fbf86b09e2001368075a168154aa942bb605a"}
---

# [Core C25] Live review capsules and qualified turn timing

**GitHub issue:** [kburson/aitm#34](https://github.com/kburson/aitm/issues/34) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C25 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c25-live-review-capsules-and-qualified-turn-timing), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C09 / #17](../17/story.md), [C23 / #28](../28/story.md), [C58 / #33](../33/story.md).

**Blocking:** [C26 / #35](../35/story.md), [C46 / #53](../53/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3 h · **Depends on:** C09, C23, C58 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/reviews/turns.py; src/aitm_core/reviews/timing.py; src/aitm_core/cli/review_turns.py; packages/aitm-core/tests/integration/test_c25.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `open_review(request) -> LevelRecord; record_turn(level, response) -> OperationResult; complete_review(level, bundle) -> OperationResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_live_backfill_same_fact: open before first turn without precommit, ingest provisional response, complete then reimport => one normalized turn. Claim/prior-submit anchors and hashes reproduce derivation; registration reuse/interruptions/exclusions keep response duration Unknown; state-boundary attribution and concurrent actor/wall totals stay distinct.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c25.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** An elapsed outer bound is not engagement. Changed bytes under same turn identity conflict; corrected interpretation appends provenance.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: An elapsed outer bound is not engagement. Changed bytes under same turn identity conflict; corrected interpretation appends provenance.

Own available live/completion interfaces here; C51 composes the later C26 final importer. Earlier SAR optional reminder; do not invent a dependency cycle.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:01:49Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
