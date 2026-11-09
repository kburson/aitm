---
schema: "aitm.story/v0"
id: 70
title: "[Core C53] Release workflow, tutorials and candidate handoff"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/70"
parent: 2
children: []
blocking: [71, 72]
blocked-by: [69, 5]
created: "2026-11-09T08:04:27Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c53-release-workflow-tutorials-and-candidate-handoff"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C53", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "c115de2c349bb69e7ecd54c64be7ff7526557892e5220b2145847cf36bd66b69"}
---

# [Core C53] Release workflow, tutorials and candidate handoff

**GitHub issue:** [kburson/aitm#70](https://github.com/kburson/aitm/issues/70) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C53 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c53-release-workflow-tutorials-and-candidate-handoff), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C59 / #69](../69/story.md), [C03 / #5](../5/story.md).

**Blocking:** [C69 / #71](../71/story.md), [C60 / #72](../72/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3.5 h · **Depends on:** C59, C03 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C03. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** uv.lock; docs/learn/core-overview.md; docs/release/core-m1.md; packages/aitm-core/pyproject.toml; .github/workflows/core-release.yml; tests/packaging/test_release_workflow.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `release checklist consumes delivered source and candidate reports; workflow builds/verifies immutable artifact identity`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_release_candidate: validate workflow/config against a candidate wheel in disposable CI, assert source/version/hash mapping and refusal of mismatched artifact. Source-review and deliver release workflow, package metadata, tutorial and library-choice rationale through normal PR before any publication using them. Hand off exact delivered source and candidate proof to C69/C60. The release workflow supports a retained once-per-release operation identity and queryable source/version/hash mapping; an uncertain dispatch is reconciled before retry.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/packaging/test_release_workflow.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** This leaf does not require its own released artifact before source review. It implements/tests candidate preparation; release publication and post-publication consumer proof belong to separately authorized C60.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: This leaf does not require its own released artifact before source review. It implements/tests candidate preparation; release publication and post-publication consumer proof belong to separately authorized C60.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:04:27Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
