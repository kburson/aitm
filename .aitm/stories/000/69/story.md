---
schema: "aitm.story/v0"
id: 69
title: "[Core C59] Cross-platform wheel and CI qualification"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/69"
parent: 2
children: []
blocking: [70]
blocked-by: [43, 44, 65, 60, 56, 68, 64, 61, 62, 66, 67, 59, 82]
created: "2026-11-09T08:04:23Z"
updated: "2026-11-09T13:53:09Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c59-cross-platform-wheel-and-ci-qualification"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C59", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "111b1a495dfdfaf87b6c5119e20067c6ffcc0f6ce591eb3f90d124d434ecb04c"}
---

# [Core C59] Cross-platform wheel and CI qualification

**GitHub issue:** [kburson/aitm#69](https://github.com/kburson/aitm/issues/69) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C59 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c59-cross-platform-wheel-and-ci-qualification), publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C36 / #43](../43/story.md), [C37 / #44](../44/story.md), [C49 / #65](../65/story.md), [C50 / #60](../60/story.md), [C51 / #56](../56/story.md), [C52 / #68](../68/story.md), [C63 / #64](../64/story.md), [C65 / #61](../61/story.md), [C66 / #62](../62/story.md), [C67 / #66](../66/story.md), [C68 / #67](../67/story.md), [C70 / #59](../59/story.md), [C75 / #82](../82/story.md).

**Blocking:** [C53 / #70](../70/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact current parent-plan section follows. C-keys are stable plan identities; actual issue dependencies are mapped above. This is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3 h · **Depends on:** C36, C37, C49, C50, C51, C52, C63, C65, C66, C67, C68, C70, C75 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/packaging/harness-pytest.ini; tests/packaging/suite_manifest.json; tests/packaging/installed_runner.py; tests/packaging/test_wheel.py; .github/workflows/core-ci.yml.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `qualify_wheel(candidate_hash, platform) -> PackageReport; run_installed_suites(artifact, suite_manifest, platform) -> PackageReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_installed_matrix: build candidate wheel, verify hash, install in clean macOS/Linux environments and run actual CLI smoke, selected contained readiness/execution or explicit capability denial plus captured-export lane. CI collects all exact C49–C52 suites and platform tests and archives reports. User runtime needs no Node. Provide run_installed_suites(artifact, suite_manifest, platform): copy the reviewed test/fixture harness outside the source workspace, install only the target wheel and test dependencies in a fresh venv, clear PYTHONPATH/editable paths, and assert aitm executable plus aitm_core.__file__/distribution RECORD resolve to the installed artifact. This reusable runner executes the actual C5 suite manifest for candidate now and released wheel in C60; source checkout imports invalidate results. The isolated runner copies tests/support and conftest files with suites. All suites use its already installed target and invoke the same prepared consumer; wheel smoke checks the supplied artifact and does not build or install a different candidate. Candidate build is a separate outer preparation step. Shared C5 suite_manifest.json is owned here and lists core walk, CLI surface, lifecycle recovery, shared-store/execution/delivery races, C10 repair, v0 cutover/review import, C63 extension, performance/full guarded unit suite, wheel smoke and each OS platform suite. Candidate and released consumers use the identical manifest. Copy the entire required tests package skeleton, including root tests/conftest.py, every package marker, tests/support and packaging helpers, into the isolated harness and preserve C01 importlib mode with an explicitly
  supplied harness configuration. The copied conftest adds only that copied test-package parent; assert tests and helper modules resolve there and aitm_core resolves exclusively to the target installed wheel. No source src/ path or original checkout is on the import path. Own/copy minimal tests/packaging/harness-pytest.ini with reviewed marker definitions (including post_release) and required collection settings; run pytest with -c <copied-harness-pytest.ini> --rootdir <harness-root> --confcutdir <harness-root> --import-mode=importlib and explicit suite paths from the manifest. The harness root is the parent of the copied tests/ directory; configuration storage below tests/packaging never defines the discovery boundary. Candidate collection excludes the named live post-release suite; only C69/C60 explicitly selects it with --release-manifest. test_wheel.py asserts effective rootdir/confcutdir/import mode/config/markers and collected suite names, not merely intended arguments. Inside the isolated harness, assert the loaded plugin paths include the copied tests/conftest.py and tests/unit/conftest.py. Using the same interpreter/config/flags as the real suite, create disposable unit probes that attempt subprocess and socket access: the outer packaging test requires the expected guard failure and absence of a subprocess side-effect marker. An integration probe imports tests.support from the exact copied path. These probes verify active protection and root loading before any guarded-suite claim; probe failure is expected evidence handled by the outer test, never a skipped full-suite requirement. No original source checkout is consulted. Include test_preflight_consumers.py in
  the shared C5 manifest.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/packaging/test_wheel.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Candidate wheel proof is not released-package proof. CI platform/capability failures remain visible; no host-security-setting change to make probes pass.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Candidate wheel proof is not released-package proof. CI platform/capability failures remain visible; no host-security-setting change to make probes pass.

All nested suites reuse the same prepared consumer and exact supplied wheel. Smoke must not rebuild/reinstall another candidate.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T08:04:23Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `111b1a495dfdfaf87b6c5119e20067c6ffcc0f6ce591eb3f90d124d434ecb04c`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

Original plan-origin metadata (retained as historical source; old events/draft remain unchanged):

```json
{
  "kind": "accepted-parent-plan",
  "story": 2,
  "key": "C59",
  "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "publication": "55b94bbe77a19002ff077c122560cf185652d25c",
  "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
  "section-sha256": "37460f511c7792ceafa982d470dfe7ee35de38d932e5a4b8d405428de1c1bd02"
}
```
