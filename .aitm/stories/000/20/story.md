---
schema: "aitm.story/v0"
id: 20
title: "[Core C12] Hook chaining and readiness diagnostics"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/20"
parent: 2
children: []
blocking: [22, 42, 64, 65]
blocked-by: [11, 19]
created: "2026-11-09T08:00:49Z"
updated: "2026-11-09T13:53:09Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c12-hook-chaining-and-readiness-diagnostics"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C12", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "a3e29e3eb2be73f24ec8d5cc37c42f3ca0683e47a6b3952ef0589ba58e70e9b0"}
---

# [Core C12] Hook chaining and readiness diagnostics

**GitHub issue:** [kburson/aitm#20](https://github.com/kburson/aitm/issues/20) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C12 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c12-hook-chaining-and-readiness-diagnostics), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C06 / #11](../11/story.md), [C11 / #19](../19/story.md).

**Blocking:** [C17 / #22](../22/story.md), [C35 / #42](../42/story.md), [C63 / #64](../64/story.md), [C49 / #65](../65/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3 h · **Depends on:** C06, C11 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C11. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/setup/hooks.py; src/aitm_core/setup/doctor.py; src/aitm_core/cli/doctor.py; src/aitm_core/services.py; src/aitm_core/setup/init.py; src/aitm_core/cli/setup.py; packages/aitm-core/tests/integration/test_c12.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `install_hooks(repo, policy) -> HookReport; doctor(context) -> ReadinessReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_hook_chain: preserve existing hooks/core.hooksPath; block ordinary planning commits and invalid pre-push candidates, permit review branches. Write root /.aitm/ ignore, diagnose broader foreign .aitm/ entry. Generic/manual host protection reports exact instructions and separate readiness facets. Invoke real aitm init and doctor to prove the hook installer is reached and foreign hook results retained. Doctor consumes the lane-probe port; C35 later wires the selector and C36/C37 provide platform profiles. In test_c12.py prove actual production init resolves the delivered hook installer. The missing lane-probe case deliberately unregisters that slot in a test composition so it remains true after C35; later production selector proof is in test_c35.py.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c12.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Hooks are optional and bypassable; core integrity must still pass with all hooks absent.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Hooks are optional and bypassable; core integrity must still pass with all hooks absent.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:00:49Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `a3e29e3eb2be73f24ec8d5cc37c42f3ca0683e47a6b3952ef0589ba58e70e9b0`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C12",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "0c0449af795c161103dd73c886c0a4f56eac17ac4f36959018220897af94d35b"
}
```
