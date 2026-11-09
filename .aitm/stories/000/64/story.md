---
schema: "aitm.story/v0"
id: 64
title: "[Core C63] Installed extension discovery and command/init composition"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/64"
parent: 2
children: []
blocking: [79, 65, 82, 66, 69]
blocked-by: [20, 14, 15, 50, 3, 63]
created: "2026-11-09T08:04:02Z"
updated: "2026-11-09T13:53:09Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c63-installed-extension-discovery-and-commandinit-composition"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C63", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "a3388b811dad08bf625075fd7a851b03cf2bed2b2cd4b7407e2fcdd5f1c717c2"}
---

# [Core C63] Installed extension discovery and command/init composition

**GitHub issue:** [kburson/aitm#64](https://github.com/kburson/aitm/issues/64) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C63 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c63-installed-extension-discovery-and-commandinit-composition), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C12 / #20](../20/story.md), [C13 / #14](../14/story.md), [C14 / #15](../15/story.md), [C43 / #50](../50/story.md), [C01 / #3](../3/story.md), [C62 / #63](../63/story.md).

**Blocking:** [C76 / #79](../79/story.md), [C49 / #65](../65/story.md), [C75 / #82](../82/story.md), [C67 / #66](../66/story.md), [C59 / #69](../69/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3 h · **Depends on:** C12, C13, C14, C43, C01, C62 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C62, C01, C12. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/ext/discovery.py; src/aitm_core/services.py; src/aitm_core/cli/app.py; src/aitm_core/setup/init.py; tests/fixtures/extension-package/; packages/aitm-core/tests/integration/test_c63.py.

**Consumes:** C13 registration/factory/init-step contracts, C12 setup composition and C14 constrained ingress. **Produces:** `discover_installed(policy: PolicySnapshot) -> Registry; mount_extension_command(registry, route) -> CommandHandler; run_provider_init(registry, context) -> InitStepResults`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_installed_extension: build/install a disposable package exposing aitm.extensions with a command, guard/action, typed owner/provider and safe fake init step. Ordinary installed aitm and init discover it through importlib.metadata, select only committed enabled versions/order, mount the route and invoke its init contribution. Disabled policy never invokes it; missing required provider/owner is reported unavailable, not applied. Registry/ownership errors remain enforced through real ingress. Warm reads keep unused factories lazy.
- [ ] **Implement:** wire pinned registry into services, CLI dispatch and init contributions at the named call sites; no hosted endpoint or foreign package config changes.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c63.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** this leaf proves generic installed integration with a fixture package, not GitHub or harness functionality. Existing hooks/config remain preserved and plugin code is trusted in-process, not sandboxed. Budget reuses C13/C14 logic and C12 init ports; no second registry implementation.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: this leaf proves generic installed integration with a fixture package, not GitHub or harness functionality. Existing hooks/config remain preserved and plugin code is trusted in-process, not sandboxed. Budget reuses C13/C14 logic and C12 init ports; no second registry implementation.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:04:02Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `a3388b811dad08bf625075fd7a851b03cf2bed2b2cd4b7407e2fcdd5f1c717c2`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C63",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "dc042b5c8674bb8d3589f75e8c4aca9fc27d49d22153ec8f9820aadcc881dd0f"
}
```
