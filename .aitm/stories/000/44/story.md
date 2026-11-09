---
schema: "aitm.story/v0"
id: 44
title: "[Core C37] Linux contained-lane probe and profile"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/44"
parent: 2
children: []
blocking: [69]
blocked-by: [42]
created: "2026-11-09T08:02:32Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c37-linux-contained-lane-probe-and-profile"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C37", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "67bf5154ed34f6067a7e29e334401abdf1f63d1b9cdd3ddf378f7a3432d8bc7a"}
---

# [Core C37] Linux contained-lane probe and profile

**GitHub issue:** [kburson/aitm#44](https://github.com/kburson/aitm/issues/44) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C37 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c37-linux-contained-lane-probe-and-profile), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C35 / #42](../42/story.md).

**Blocking:** [C59 / #69](../69/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3.5 h · **Depends on:** C35 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/verification/containment_linux.py; packages/aitm-core/tests/platform/test_c37.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `probe_linux(resources) -> ContainmentCapability; linux_profile(inputs, outputs) -> ProcessProfile; linux_adapter() -> LaneAdapter`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_linux_containment: supported user/mount/network namespace and filesystem profile confines process tree, sources/environment read-only and outputs writable; remount/privilege escape fails. Disabled namespace/kernel/helper capability returns diagnostic pending, never downgrade. The selector loads this adapter by platform through C35 fixed registration. Test actual installed aitm doctor/init and aitm test under committed contained policy, asserting the managed descendant process uses the profile and receipt names contained. Separately committed captured-export policy still runs its bounded nominal lane.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/platform/test_c37.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Run on actual Linux; no sysctl/global permission edits. Capability tests distinguish supported enforcement from denial-path-only proof.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Run on actual Linux; no sysctl/global permission edits. Capability tests distinguish supported enforcement from denial-path-only proof.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:02:32Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
