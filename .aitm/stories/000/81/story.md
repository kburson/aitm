---
schema: "aitm.story/v0"
id: 81
title: "[Core C78] Installed transition explanation and unknown guards"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/81"
parent: 2
children: []
blocking: [65, 66]
blocked-by: [23, 37, 38, 63, 79, 80]
created: "2026-11-09T13:42:12Z"
updated: "2026-11-09T13:53:09Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c78-installed-transition-explanation-and-unknown-guards"
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C78", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "bd4adf06c90fcf02bf0930bbdec5d477aa951740", "raw-sha256": "19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8", "section-sha256": "7dc89ec29bd73668378447ef5794a5cd3553a46a9cc79b686e006e4f9160f3cd"}
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Core C78] Installed transition explanation and unknown guards

**GitHub issue:** [kburson/aitm#81](https://github.com/kburson/aitm/issues/81) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Separate full-file validation completed:** the core design and parent implementation plan passed separately authorized native XPR, with complete actual input retrieval verified in every round. [Plan validation](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md). The historical procedure limitation is retained in its audit and resolved by these new records. This does not establish leaf Design/Plan/JIT acceptance or implementation authority.

## User story

As a developer delivering aitm-core, I want the bounded C78 capability and proof below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is a 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c78-installed-transition-explanation-and-unknown-guards). S is the bounded ≤4 h scope; P1 follows the foundational core priority. The estimate includes local verification and source review, reuses delivered prerequisite contracts, and is not measured actuals or a calendar promise. Resplit/review at JIT if the cap is not defensible; expansion is not planned overflow.

**Blocked by:** [C18 / #23](../23/story.md), [C28 / #37](../37/story.md), [C29 / #38](../38/story.md), [C62 / #63](../63/story.md), [C76 / #79](../79/story.md), [C79 / #80](../80/story.md).

**Blocking:** [C49 / #65](../65/story.md), [C67 / #66](../66/story.md).

Dependencies include shared-file serialization. Required interfaces and evidence must actually be delivered; a closed issue alone is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

This exact parent section is input to the leaf's later own Design/Plan/JIT, not an acceptance of those documents.

**Estimate:** 3 h · **Depends on:** C18, C28, C29, C62, C76, C79 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C18. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/cli/read.py; packages/aitm-core/tests/integration/test_c78.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `explain_command(story, refresh=False) -> TransitionExplanation`. Domain records live with this producer and reuse the existing typed evidence/guard contracts.

- [ ] **Test first:** test_installed_explain invokes the installed command with C28's real pinned transition evaluator and current production kind/exit registrations. Assert pinned state/policy, next kind-appropriate edge, every guard's pass/fail/unknown reason, pending side effects and exact next command for story/spike/epic fixtures. Freshness-dependent conditions that cannot be proved remain unknown, never pass. Ordinary explain performs no fetch/write/model call; explicit --refresh uses C08 then repins. Assert absent required evaluator reports unavailable/unknown. Keep lazy loading of only selected guard/extension modules; C52 measures this complete path including interpreter, not C18's earlier partial view.
- [ ] **Implement:** the named bounded contract and production adapter within these paths; no hidden later wiring.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c78.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Thin read-only adapter over the same guard engine; no parallel implementation of transition logic or hidden refresh.

## JIT reminders and likely defects

Retain every negative assertion under Test first; these identify likely failure cases, not just the nominal path. Risk boundary: Thin read-only adapter over the same guard engine; no parallel implementation of transition logic or hidden refresh.

Pin current source/prerequisite deliveries before Develop, follow the common plan verification/source-review/delivery cycle and preserve exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's scoped planning authority. GitHub issue creation: `2026-11-09T13:42:12Z`; local bootstrap record: `2026-11-09T13:53:09Z`. No unavailable core command, leaf acceptance, runtime guard, JIT, implementation clock or delivery is claimed. The initial epic Refine estimate remains unchanged.

## Current decomposition reconciliation — 2026-11-09

The current accepted parent section is published `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, full-plan SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`, section SHA-256 `7dc89ec29bd73668378447ef5794a5cd3553a46a9cc79b686e006e4f9160f3cd`. This record and GitHub issue keep the same permanent identity. Estimate and dependency revisions are manual bootstrap planning facts; no native reconcile/transition or runtime acceptance is asserted. [Reconciliation receipt](../2/plan/leaf-reconciliation-receipt.json).

[Design phase retrospective](../2/design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan phase retrospective](../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md) review the planning work, not this leaf's future Review→Done sign-off.
