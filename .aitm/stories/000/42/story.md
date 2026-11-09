---
schema: "aitm.story/v0"
id: 42
title: "[Core C35] Captured-export test execution and receipts"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/42"
parent: 2
children: []
blocking: [43, 44, 45, 50, 52, 57, 61, 65]
blocked-by: [20, 41, 31, 40]
created: "2026-11-09T08:02:23Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c35-captured-export-test-execution-and-receipts"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C35", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "9b81e2841c2d17fb1109a552faa12fce8b659c899ba02f133c4e9b0a06df68a6"}
---

# [Core C35] Captured-export test execution and receipts

**GitHub issue:** [kburson/aitm#42](https://github.com/kburson/aitm/issues/42) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C35 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c35-captured-export-test-execution-and-receipts), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C12 / #20](../20/story.md), [C32 / #41](../41/story.md), [C34 / #31](../31/story.md), [C31 / #40](../40/story.md).

**Blocking:** [C36 / #43](../43/story.md), [C37 / #44](../44/story.md), [C38 / #45](../45/story.md), [C43 / #50](../50/story.md), [C45 / #52](../52/story.md), [C61 / #57](../57/story.md), [C65 / #61](../61/story.md), [C49 / #65](../65/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3 h · **Depends on:** C12, C32, C34, C31 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C31. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/verification/run.py; src/aitm_core/verification/receipts.py; src/aitm_core/cli/test.py; src/aitm_core/verification/lanes.py; src/aitm_core/services.py; src/aitm_core/setup/doctor.py; packages/aitm-core/tests/integration/test_c35.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `run_verification(admission, prepared, assurance) -> VerificationResult; LaneAdapter.probe(resources) -> ContainmentCapability; LaneAdapter.command(prepared) -> ProcessLaunch; select_lane(policy, platform) -> LaneAdapter`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_captured_run: real passing/failing subprocess and retained logs; read-only inputs/separate writable roots; uv prepared env/no-sync/offline, no bytecode and redirected pytest cache. Persistent mutations or weaker-than-policy assurance produce diagnostic result. Receipt binds actual capture, command transformation and output hashes. Wire selector into real test/deliverable executor and doctor/init readiness port. Contained selects platform adapter C36/C37; missing/failing probe returns pending before admission/launch, with no fallback. Every ProcessLaunch executes through C32 and receipt records selected/proven assurance. In test_c35.py prove actual production execution/init/doctor resolve the installed LaneAdapter selector; C12 deliberately-missing-slot negative vectors remain unchanged.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c35.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Explicitly allow bounded captured-export only under selected policy; do not assert it prevents chmod self-mutation, undeclared host reads or arbitrary network.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Explicitly allow bounded captured-export only under selected policy; do not assert it prevents chmod self-mutation, undeclared host reads or arbitrary network.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:02:23Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
