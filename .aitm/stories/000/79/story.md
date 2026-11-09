---
schema: "aitm.story/v0"
id: 79
title: "[Core C76] Source commit guard and retained source evidence"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/79"
parent: 2
children: []
blocking: [80, 61, 62, 81, 65, 82, 66]
blocked-by: [37, 38, 40, 42, 45, 46, 47, 48, 49, 63, 64]
created: "2026-11-09T13:42:10Z"
updated: "2026-11-09T13:53:09Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c76-source-commit-guard-and-retained-source-evidence"
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C76", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "cd996ca3e63bba34abbda6cda18d03e7a801f126a690ea43c1bf7fb25dfa5e9d"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Core C76] Source commit guard and retained source evidence

**GitHub issue:** [kburson/aitm#79](https://github.com/kburson/aitm/issues/79) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C76 capability and proof below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is a 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c76-source-commit-guard-and-retained-source-evidence). S is the bounded ≤4 h scope; P1 follows the foundational core priority. The estimate includes local verification and source review, reuses delivered prerequisite contracts, and is not measured actuals or a calendar promise. Resplit/review at JIT if the cap is not defensible; expansion is not planned overflow.

**Blocked by:** [C28 / #37](../37/story.md), [C29 / #38](../38/story.md), [C31 / #40](../40/story.md), [C35 / #42](../42/story.md), [C38 / #45](../45/story.md), [C39 / #46](../46/story.md), [C40 / #47](../47/story.md), [C41 / #48](../48/story.md), [C42 / #49](../49/story.md), [C62 / #63](../63/story.md), [C63 / #64](../64/story.md).

**Blocking:** [C79 / #80](../80/story.md), [C65 / #61](../61/story.md), [C66 / #62](../62/story.md), [C78 / #81](../81/story.md), [C49 / #65](../65/story.md), [C75 / #82](../82/story.md), [C67 / #66](../66/story.md).

Dependencies include shared-file serialization. Required interfaces and evidence must actually be delivered; a closed issue alone is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

This exact parent section is input to the leaf's later own Design/Plan/JIT, not an acceptance of those documents.

**Estimate:** 3 h · **Depends on:** C28, C29, C31, C35, C38, C39, C40, C41, C42, C62, C63 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C29, C31, C63. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/machine/source_guards.py; src/aitm_core/machine/guards.py; src/aitm_core/machine/transitions.py; src/aitm_core/services.py; packages/aitm-core/tests/integration/test_c76.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `evaluate_source_exit(snapshot, attempt) -> GuardResults; capture_source_commits(attempt, source) -> SourceCommitEvidence`. Domain records live with this producer and reuse the existing typed evidence/guard contracts.

- [ ] **Test first:** test_source_commit_guard exercises real story/defect Develop-exit promote with the production source-edge evaluator registered in StoryExitGuards: exact subject prefix [#<positive decimal story ID>] including its trailing space, no substring matching; reject [#12] for story 1, embedded prefixes, missing trailing space, nondecimal/zero/negative IDs, commits outside the recorded attempt branch or before its pinned baseline, and empty/tagged merge-only changes with no implementation delta. Preflight/evaluation retains matching source commit IDs and reviewed head/tree in typed evidence/read-set; recheck on CAS/source changes. C31 trip preflight remains first. Reuse C39/C40/C41 source-mapping fixtures to prove squash/rebase target messages without the prefix preserve valid source evidence; target-message text alone is insufficient. Register only the Develop-exit evaluator here through services.py and C28's edge-dispatched port. Until C79 supplies Test/Review exit evaluators those required edges remain unknown/unavailable, not passing. Prove this with explicit unregistered-edge fixtures. Existing C29/C62 spike/epic substitutions stay intact.
- [ ] **Implement:** the named bounded contract and production adapter within these paths; no hidden later wiring.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c76.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Bounded source-commit selection, retained evidence and one edge registration over delivered Git/delivery interfaces. C79 separately owns completion composites and signoff wiring. Re-estimate/split before Develop if the 3 h bound is not defensible.

## JIT reminders and likely defects

Retain every negative assertion under Test first; these identify likely failure cases, not just the nominal path. Risk boundary: Bounded source-commit selection, retained evidence and one edge registration over delivered Git/delivery interfaces. C79 separately owns completion composites and signoff wiring. Re-estimate/split before Develop if the 3 h bound is not defensible.

Pin current source/prerequisite deliveries before Develop, follow the common plan verification/source-review/delivery cycle and preserve exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's scoped planning authority. GitHub issue creation: `2026-11-09T13:42:10Z`; local bootstrap record: `2026-11-09T13:53:09Z`. No unavailable core command, leaf acceptance, runtime guard, JIT, implementation clock or delivery is claimed. The initial epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `cd996ca3e63bba34abbda6cda18d03e7a801f126a690ea43c1bf7fb25dfa5e9d`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.
