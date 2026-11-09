---
schema: "aitm.story/v0"
id: 72
title: "[Core C60] Publish and qualify the exact released core"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/72"
parent: 2
children: []
blocking: []
blocked-by: [70, 71]
created: "2026-11-09T08:04:35Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 2.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c60-publish-and-qualify-the-exact-released-core"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C60", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "2aa13ab9c3838ef90ea7f847503cf2b8920a44fedb7a5c3c45886bba038cf172"}
---

# [Core C60] Publish and qualify the exact released core

**GitHub issue:** [kburson/aitm#72](https://github.com/kburson/aitm/issues/72) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C60 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 2.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c60-publish-and-qualify-the-exact-released-core), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C53 / #70](../70/story.md), [C69 / #71](../71/story.md).

**Blocking:** none.

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 2.5 h · **Depends on:** C53, C69 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** docs/release/core-m1.md; docs/release/core-m1-evidence.json.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `release-operation receipt and exact released C5 evidence manifest`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** First re-run delivered C69 checker fixtures to prove the observer before any live release. Then, only with separate release-task authority, observe/dispatch/reconcile the delivered C53 once-per-release operation for (version, delivered source, expected artifact hash). Existing conflicting artifact blocks; lost result queries exact workflow/version/provenance before retry. After publication, obtain observed-release.json and run the delivered read-only C69 checker/workflow against that exact immutable wheel. C59 runner executes the full C5 manifest on both OSes and the declared warm-laptop lane, including local-only/two-clone/repair/migration/import/budgets and containment. No source import, candidate substitution or required skip can pass C5.
- [ ] **Implement:** the named qualification/checker contract within these paths; no missing product behavior is hidden here.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/packaging/test_release_checker.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

- [ ] **Post-publication verification:** run `uv run --package aitm-core pytest packages/aitm-core/tests/packaging/test_published_release.py --release-manifest <observed-release.json> -q` through the delivered read-only workflow on the named hosts, retain the complete C5 manifest/results in core-m1-evidence.json. Fixture PASS is pre-operation observer evidence only; this leaf cannot be accepted as released qualification until the post-publication PASS and all required suite reports are retained. Publication/dispatch is outside pytest; retries of the checker cannot publish.

**Risk/boundary:** Evidence-only release follow-on; no new harness implementation. Target source is delivered C53, observer source is delivered C69, and neither depends on this evidence commit. No production C6 adoption or epic closure. External waits are not implementation engagement; missing credentials/capability remains a blocker, not permission repair.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Evidence-only release follow-on; no new harness implementation. Target source is delivered C53, observer source is delivered C69, and neither depends on this evidence commit. No production C6 adoption or epic closure. External waits are not implementation engagement; missing credentials/capability remains a blocker, not permission repair.

Use the delivered C69 observer and C59 isolated runner against the exact released wheel. Fixture PASS alone is not released C5 acceptance.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:04:35Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
