---
schema: "aitm.story/v0"
id: 3
title: "[Core C01] Package foundation and command result contract"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/3"
parent: 2
children: []
blocking: [4, 5, 11, 64]
blocked-by: [83]
created: "2026-11-09T07:59:36Z"
updated: "2026-11-09T14:43:23+00:00"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c01-package-foundation-and-command-result-contract"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C01", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "19886f6e7f6edf99ea5845662d405c09cb9d860aecc6ad23c63d285a94597c92"}
---

# [Core C01] Package foundation and command result contract

**GitHub issue:** [kburson/aitm#3](https://github.com/kburson/aitm/issues/3) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C01 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3.5 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c01-package-foundation-and-command-result-contract), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Project sequencing prerequisite** [#83 continuous agent usage capture](../83/story.md). The installed collector and on-host activation receipt must be available before Develop. The accepted Core plan excerpt below retains its original internal dependency scope.

**Blocking:** [C02 / #4](../4/story.md), [C03 / #5](../5/story.md), [C06 / #11](../11/story.md), [C63 / #64](../64/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3.5 h · **Depends on:** none · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/conftest.py; tests/__init__.py; tests/support/__init__.py; tests/integration/__init__.py; tests/unit/__init__.py; tests/platform/__init__.py; tests/performance/__init__.py; tests/packaging/__init__.py; uv.lock; src/aitm_core/cli/catalog.py; tests/unit/conftest.py; src/aitm_core/__init__.py; src/aitm_core/models/__init__.py; src/aitm_core/store/__init__.py; src/aitm_core/reviews/__init__.py; src/aitm_core/machine/__init__.py; src/aitm_core/verification/__init__.py; src/aitm_core/delivery/__init__.py; src/aitm_core/migration/__init__.py; src/aitm_core/ext/__init__.py; src/aitm_core/providers/__init__.py; src/aitm_core/index/__init__.py; src/aitm_core/reducers/__init__.py; src/aitm_core/setup/__init__.py; src/aitm_core/rules/__init__.py; src/aitm_core/execution/__init__.py; src/aitm_core/cli/__init__.py; pyproject.toml; packages/aitm-core/pyproject.toml; src/aitm_core/models/common.py; src/aitm_core/cli/app.py; src/aitm_core/services.py; packages/aitm-core/tests/integration/test_c01.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `CommandResult(operation_id, local, publication, pending, evidence, recovery); main() -> int; StoreAnchor, RefObservation, RefreshResult and ServicePorts structural records`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_installed_entrypoint: wheel installs on Python 3.13, aitm --help works without Node, JSON schema/version and distinct refused/conflict/integrity/pending exit codes round-trip. Imports make no Git/network/model call. Define mandatory ports for policy resolution/refresh, validation gate, write authorization, attempt preflight, init hooks, action retry and lane selection; absent required implementation returns unavailable. No permissive production fallback. Create regular packages with empty __init__.py files for every listed package; root aitm_core.__file__ must resolve to the installed wheel. Own lazy core route catalog in cli/catalog.py: a fixed route-to-module table for the complete CLI map below, loaded by cli/app.py without importing unused modules. A missing not-yet-delivered module reports unavailable, not success; each later command module exports its declared handler without editing this catalog. C09 cli/dispatch.py is the operation/publication executor, not the route registry. Install tests/unit/conftest.py autouse guards rejecting subprocess creation and network socket access before any unit leaf; integration tests verify those guards with deliberately failing temporary test cases. Pin Python/runtime/dev/build dependencies and root uv.lock: Pydantic, Typer, RFC8785 and strict-YAML support, pytest, Ruff and the chosen uv-compatible wheel builder. C03 may refine canonicalization dependencies under its explicit serialized manifest ownership; other later dependency additions require a coordinated allowlist/contract revision before edits, not an implicit permission. Own pytest import configuration: --import-mode=importlib in the package
  pyproject.toml, with tests/conftest.py adding only the resolved test-package parent to the harness import path. Tests are a regular tests package with the listed subpackage markers; helpers use qualified imports such as tests.support.shared_store and tests.packaging.installed_runner. Refuse a preloaded foreign tests package rather than silently importing it. Prove a cross-directory helper import in the integration scaffold and prove the test path setup does not add src/ or an editable core installation. Missing module/port negative vectors use deliberately unregistered test compositions and remain valid as later implementations land. The fixed lazy route catalog includes split, decompose, idea open and entity-scoped sync/unbind from the updated accepted design. Missing later handlers report unavailable; their owners install separate modules without editing the catalog. Declare mandatory KindRequirements, AggregateEvidence and StoryExitGuards slots with producer-owned protocols from C28/C29/C76/C79. Missing required kind/edge evaluators return unavailable/unknown; no generic story guard is applied to exempt kinds.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c01.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Keep scaffolding bounded to the core package; no meta-package or extension implementations.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Keep scaffolding bounded to the core package; no meta-package or extension implementations.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T07:59:36Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `19886f6e7f6edf99ea5845662d405c09cb9d860aecc6ad23c63d285a94597c92`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C01",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "fa26bded4a3b931eaa626d634fa6b810d99d00265582df24ec1485a4dd27ba8c"
}
```
