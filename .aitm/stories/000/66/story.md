---
schema: "aitm.story/v0"
id: 66
title: "[Core C67] Complete installed CLI surface audit"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/66"
parent: 2
children: []
blocking: [68, 69]
blocked-by: [65, 56, 64, 51]
created: "2026-11-09T08:04:10Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 2.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c67-complete-installed-cli-surface-audit"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C67", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "2b3e83bb81e6ffa5a8d44ad26364deb12ee229d838ef3b6012795d557d71d341"}
---

# [Core C67] Complete installed CLI surface audit

**GitHub issue:** [kburson/aitm#66](https://github.com/kburson/aitm/issues/66) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C67 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 2.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c67-complete-installed-cli-surface-audit), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C49 / #65](../65/story.md), [C51 / #56](../56/story.md), [C63 / #64](../64/story.md), [C44 / #51](../51/story.md).

**Blocking:** [C52 / #68](../68/story.md), [C59 / #69](../69/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 2.5 h · **Depends on:** C49, C51, C63, C44 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/integration/test_cli_surface.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `audit_cli_surface(required_routes) -> RouteCoverageReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_cli_surface parametrizes every route and option in the complete CLI map: installed lazy registration, help, argument validation and versioned JSON/unavailable statuses. Assert init --planning-branch and all documented global/route options are exposed; no new unmapped command is shipped. Collect a route-to-positive-operational-test ledger from C49/C50/C51/C65/C66/C68/C59 instead of claiming help alone proves behavior. Future suite names are declared references; Gate C/D validates their actual collection once all owners are delivered.
- [ ] **Implement:** the named qualification/checker contract within these paths; no missing product behavior is hidden here.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_cli_surface.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** A missing command/wiring returns to its owning leaf; this audit cannot implement absent product behavior.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: A missing command/wiring returns to its owning leaf; this audit cannot implement absent product behavior.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:04:10Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
