---
schema: "aitm.story/v0"
id: 80
title: "[Core C79] Test and Review exit composites with atomic signoff"
kind: "story"
state: ready-for-plan
issue: "https://github.com/kburson/aitm/issues/80"
parent: 484
children: []
blocking: [61, 62, 65, 66, 81, 82, 238, 239, 510]
blocked-by: [42, 45, 46, 49, 63, 79, 497, 503, 506, 507]
created: "2026-11-09T13:42:11Z"
updated: "2026-11-27T06:32:11.294Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c79-test-and-review-exit-composites-with-atomic-signoff"
plan-origin: {"story": 2, "publication": "0945941c6c024b6dd621202b2456696ae1df0154", "path": ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md", "ledger-sha256": "0a2c7e2fba1085745032f6e2a6f4c758bda0885e728c6a40042415633d755893", "runtime-acceptance": false, "key": "C79", "parent": 484}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":484,"design_sources":[2],"scope_entry":"C79","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json"}
---

# [Core C79] Test and Review exit composites with atomic signoff

## Accepted workflow reconciliation

[Core plan](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md) · [Delivery ledger](https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-core-mini-epic-ledger.md) · [Native reconciliation receipt](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-26-core-native-reconciliation-receipt.json).

Current parent: [#484](https://github.com/kburson/aitm/issues/484). Key: C79. Estimate: **4 h**. Blocked by: #42, #45, #46, #49, #63, #79, #497, #503, #506, #507.

Move the old Test check into the Dev candidate guard. Bind pre-push proof to exact source and test inputs, require tagged/composed source and resolved expansion, and combine authenticated hosted CI with pre-Review and final closeout through typed ports. C95 owns selection policy.

The earlier decomposition below is retained as historical provenance. Current behavior and tests follow the accepted replan.

**GitHub issue:** [kburson/aitm#80](https://github.com/kburson/aitm/issues/80) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C79 capability and proof below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

The baseline estimate of 3 implementation agent-hours (P1/S) comes from the [accepted parent plan](../2/plan/core-implementation-plan.md#c79-test-and-review-exit-composites-with-atomic-signoff). S is the bounded ≤4 h scope; P1 follows the foundational core priority. The estimate includes local verification and source review, reuses delivered prerequisite contracts, and is not measured actuals or a calendar promise. Resplit/review at JIT if the cap is not defensible; expansion is not planned overflow.

**Blocked by:** [C76 / #79](../79/story.md), [C35 / #42](../42/story.md), [C38 / #45](../45/story.md), [C39 / #46](../46/story.md), [C42 / #49](../49/story.md), [C62 / #63](../63/story.md).

**Blocking:** [C65 / #61](../61/story.md), [C66 / #62](../62/story.md), [C78 / #81](../81/story.md), [C49 / #65](../65/story.md), [C75 / #82](../82/story.md), [C67 / #66](../66/story.md), [C85 / #238](../../002/238/story.md), [C86 / #239](../../002/239/story.md).

Dependencies include shared-file serialization. Required interfaces and evidence must actually be delivered; a closed issue alone is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

This exact parent section is input to the leaf's later own Design/Plan/JIT, not an acceptance of those documents.

**Estimate:** 3 h · **Depends on:** C76, C35, C38, C39, C42, C62 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C76, C42. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/machine/completion_guards.py; src/aitm_core/machine/guards.py; src/aitm_core/machine/transitions.py; src/aitm_core/services.py; src/aitm_core/signoff.py; packages/aitm-core/tests/integration/test_c79.py.

**Consumes:** delivered source/evidence/guard contracts and the C76 Develop-exit evaluator. **Produces:** `evaluate_completion_exit(snapshot, attempt, edge, proposed_close=None) -> GuardResults`. Register the Test/Review edge evaluators in the existing StoryExitGuards port; do not create an alternate guard engine.

- [ ] **Test first:** test_test_exit_binding uses actual promote and the production evaluator to require a tool-produced passing receipt for the current clean source and attempt/generation; stale/dirty/wrong-attempt receipts refuse with the specific reason. test_review_exit_composite compares effective review, verified source-to-target delivery, retrospective and every applicable lifecycle proof on the same source/attempt, rejecting mixed evidence and target-message substitution. Wire signoff.py to the same registered evaluator using C42's proposed atomic retrospective/outcome plus existing authoritative facts; no prior-signoff requirement or second commit is introduced. Exercise one real signoff success and one mismatch refusal, proving all-or-none outcome publication. Reuse delivered source/review/delivery fixtures and retain C76 source evidence. Explicitly unregister each required edge to prove unavailable rather than pass; default production composition resolves all story exit evaluators. Kind-specific spike/epic paths remain C29/C62 responsibilities. Later C49/C65/C66/C68 prove complete real lifecycles.
- [ ] **Implement:** the bounded composite evaluation and explicit production call-site registration within these paths.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c79.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Reuse C42's transactional signoff constructor and producer fixtures. This is evidence comparison and wiring, not a new runner, delivery engine or retrospective schema. Re-estimate/split at JIT if three hours is not defensible.

## JIT reminders and likely defects

Retain every negative assertion under Test first; these identify likely failure cases, not just the nominal path. Risk boundary: Reuse C42's transactional signoff constructor and producer fixtures. This is evidence comparison and wiring, not a new runner, delivery engine or retrospective schema. Re-estimate/split at JIT if three hours is not defensible.

Pin current source/prerequisite deliveries before Develop, follow the common plan verification/source-review/delivery cycle and preserve exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's scoped planning authority. GitHub issue creation: `2026-11-09T13:42:11Z`; local bootstrap record: `2026-11-09T13:53:09Z`. No unavailable core command, leaf acceptance, runtime guard, JIT, implementation clock or delivery is claimed. The initial epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `b780dff78b37e38aa62830b75a68917d9367a5ad9375fa5c6354c25c622c0b75`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.

<!-- aitm-core-lifecycle-reconciliation -->
## Governed PR lifecycle amendment

Expose the exact verified-delivery and required-completion record from the successful sign-off path for later retirement admission. Prove failed or stale sign-off does not qualify and pending cleanup does not revoke verified delivery. C85 owns the terminal dispatch and cleanup.

The current planning estimate is **3.5 implementation agent-hours** (P1/S). The baseline decomposition recorded **3 h**.

New dependent leaves [C85 / #238](../../002/238/story.md), [C86 / #239](../../002/239/story.md).

[Amendment reconciliation](../2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md). This is a Backlog planning update.

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **40** · **P1/S** · **4 agent-hours**. Design accepted for this manual workflow through issue #484 with scope entry **C79**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md).
