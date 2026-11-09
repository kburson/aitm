---
schema: "aitm.story/v0"
id: 71
title: "[Core C69] Read-only release checker and dual-platform workflow"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/71"
parent: 2
children: []
blocking: [72]
blocked-by: [70]
created: "2026-11-09T08:04:31Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c69-read-only-release-checker-and-dual-platform-workflow"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C69", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "7775cd9009a35e67d6bbce33439e8409f511313b8295c2d4c143e092b16fba60"}
---

# [Core C69] Read-only release checker and dual-platform workflow

**GitHub issue:** [kburson/aitm#71](https://github.com/kburson/aitm/issues/71) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C69 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c69-read-only-release-checker-and-dual-platform-workflow), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C53 / #70](../70/story.md).

**Blocking:** [C60 / #72](../72/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3 h · **Depends on:** C53 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/packaging/release_checker.py; tests/packaging/conftest.py; tests/packaging/test_release_checker.py; tests/packaging/test_published_release.py; .github/workflows/core-post-release.yml; docs/release/core-checker.md.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `qualify_published(manifest: ReleaseManifest) -> ReleaseEvidence; pytest --release-manifest PATH option; read-only core-post-release workflow`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_release_checker_fixtures: success and mismatched version/hash/source, missing/uncertain artifact, omitted manifest and unsupported evidence; checker cannot publish/dispatch. conftest.py registers --release-manifest. Live test_published_release is excluded from ordinary fixture collection and must fail clearly if explicitly invoked without a manifest. The post-release workflow accepts a completed observed-release manifest and runs C59 isolated runner/full suite_manifest.json on macOS/Linux plus the declared warm-laptop budget lane; it has read-only artifact access and no publication capability. Fixture-test the workflow/option/checker and required-suite collection before source review. Missing required host/capability leaves released proof pending.
- [ ] **Implement:** the named qualification/checker contract within these paths; no missing product behavior is hidden here.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/packaging/test_release_checker.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Checker/workflow source must be reviewed and delivered before C60 uses it. It is test infrastructure outside the target wheel; never a pre-release assertion that a release exists.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Checker/workflow source must be reviewed and delivered before C60 uses it. It is test infrastructure outside the target wheel; never a pre-release assertion that a release exists.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:04:31Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
