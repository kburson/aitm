---
schema: "aitm.story/v0"
id: 146
title: "[#133 T09] Implement qualified execution observation"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/146"
parent: 133
children: [268, 274, 275, 276]
blocking: [149, 168]
blocked-by: [144, 145]
created: "2026-11-10T16:51:17Z"
updated: "2026-11-13T05:16:25Z"
last-branch: "planning"
estimate: {"agent-hours": 4.0, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-12-146-trusted-observation-replan.md", "plan/146-linux-rehearsal.json", "plan/reviews/2026-11-12-146-trusted-observation-replan-review.md", "plan/2026-11-12-146-product-observation-findings.md", "plan/reviews/2026-11-12-146-product-observation-review.md", "plan/product-observation-readback.json", "plan/product-trial-1-receipt.json", "plan/product-trial-2-receipt.json", "plan/product-trial-3-receipt.json", "plan/product-trial-4-receipt.json", "plan/2026-11-12-146-bounded-product-slice-plan.md", "plan/2026-11-12-146-bounded-product-slice-findings.md", "plan/reviews/2026-11-12-146-bounded-product-slice-review.md", "plan/bounded-product-slice-readback.json", "plan/2026-11-12-146-full-suite-observation-plan.md", "plan/2026-11-12-146-full-suite-observation-findings.md", "plan/reviews/2026-11-12-146-full-suite-observation-review.md", "plan/full-suite-independent-inventory.py", "plan/full-suite-observation-readback.json", "plan/2026-11-12-146-selected-observation-plan.md", "plan/2026-11-12-146-selected-observation-findings.md", "plan/reviews/2026-11-12-146-selected-observation-review.md", "plan/selected-observation-readback.json", "plan/selected-prior-attempt-dtrace.log", "plan/selected-diagnostic-streams.zip"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T09", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "96f92716c462213744f98c10b0db9cc163f768fe3bd4bbe4bf9f56644378389d"}
---

# [#133 T09] Implement qualified execution observation

[GitHub issue #146](https://github.com/kburson/aitm/issues/146) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L305)

**Required predecessors** [T07 #144](../144/story.md), [T08 #145](../145/story.md).

The planning estimate is 4 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T09. Implement qualified execution observation — 4h, P1, T07/T08

**Owns** `tools/ci/tia/observe.py`, `test_tia_observe.py` and the
qualified T07 execution adapter.
**Interface** `observe(candidate, collection, assigned_ids, runner_identity) -> Observations`.

- [ ] `test_candidate_cannot_supply_authoritative_outcomes` and
  `test_failure_observed_if_worker_exits_before_finalize` verify
  positive and negative evidence for the assigned subset.
- [ ] Keep controller, credentials and evidence channel outside
  candidate code. Match runtime observation to the prior complete
  collection and exact assignment. V(observe) and native qualification
  repeat on the exact implementation. Split or replan before Develop
  if the approved mechanism exceeds four hours.

## Qualification hold

Backlog / BLOCKED. #144 and #145 ended without qualifying collection and execution. A qualified replacement is required. [Current replan](../133/plan/2026-11-12-133-advisory-and-qualification-replan.md).

## Pickup order

Rank 50 is the next unresolved story. Its trusted collection and execution qualification hold remains active. [Rank order](../../001/133/plan/2026-11-12-133-rank-order.md).

## Current Rank 50 qualification replan

The local synthetic rehearsal demonstrated controller-owned inventory and external verdicts on Linux. A bounded same-repository macOS/APFS pilot is the proposed qualification route. No available route met the pilot's entry criteria. #146 remains open and blocked on qualification, and #148 and #267 remain held by Rank order.

[Reviewed replan](plan/2026-11-12-146-trusted-observation-replan.md) · [Linux rehearsal](plan/146-linux-rehearsal.json) · [Independent review](plan/reviews/2026-11-12-146-trusted-observation-replan-review.md).

## Authorized Rank 50 pilot

[#268](../../002/268/story.md) owns the disposable macOS/APFS spike. Production qualification and the Rank 60 pickup holds stay active.

## Reviewed #268 pilot result

[#268](../../002/268/story.md) verified worker/controller separation and receipt custody for the allowlisted synthetic catalog. The evidence covers seven fixture invocations on hosted macOS/APFS. #146 remains blocked on complete product collection and execution and native child coverage. Rank 60 stays on hold.

## Product observation after #268

The hosted comparison extended the separate macOS/APFS worker to the pinned product suite. The controller reproduced the earlier 1,216-ID collection, and the independent review distinguishes directly observed process results from worker-reported test IDs, phases and coverage. Product qualification remains outstanding.

[Findings](plan/2026-11-12-146-product-observation-findings.md) · [Independent review](plan/reviews/2026-11-12-146-product-observation-review.md) · [Run readback](plan/product-observation-readback.json).

## Diagnostic recovery and bounded product slice

The follow-up retained the full pytest streams, identified trial-environment failures and tested two pinned product obligations through a separate controller observation route. The production qualification remains outstanding.

[Findings](plan/2026-11-12-146-bounded-product-slice-findings.md) · [Independent review](plan/reviews/2026-11-12-146-bounded-product-slice-review.md) · [Run readback](plan/bounded-product-slice-readback.json).

## Full pinned product-suite observation

The macOS/APFS trial checked dynamic pytest collection against an independently reconstructed inventory and traced assigned outcomes and required native children. The independent review records the scope and remaining production qualification work.

[Findings](plan/2026-11-12-146-full-suite-observation-findings.md) · [Independent review](plan/reviews/2026-11-12-146-full-suite-observation-review.md) · [Run readback](plan/full-suite-observation-readback.json).

## Alternative qualification spikes

- [#274](../../002/274/story.md) tests admission for immutable reviewed product and observer inputs.
- [#275](../../002/275/story.md) tests a canonical CI warning and manual repair workflow.

Both spikes are Rank 50. Their experimental results do not activate production behavior or change the Rank 60 holds.

## Reviewed selected-mode and negative evidence

The independent review accepted the exact pinned selected execution and the observed live negative cases. Actual previous-attempt bytes were refused locally against the new attempt identity. #146 production qualification remains open.

[Findings](plan/2026-11-12-146-selected-observation-findings.md) · [Independent review](plan/reviews/2026-11-12-146-selected-observation-review.md) · [Readback](plan/selected-observation-readback.json).

## Controller-owned catalog spike

[#276](../../002/276/story.md) tests an independently observed catalog of two product behaviors and exact canonical #103 required-ID evidence. It is a Rank 50 supplement experiment.

## Terminal replacement

GitHub Closed / Not Planned, Project 24 Done / Replaced. [Reviewed #133 replan](https://github.com/kburson/aitm/blob/62b2c5f5af388a1b889c8440d91bc89a365effbd/.aitm/stories/001/133/plan/2026-11-12-133-ci-warning-manual-recovery-replan.md).

## Retained diagnostics

[Archive of all 114 verified selected trial streams](plan/selected-diagnostic-streams.zip).
