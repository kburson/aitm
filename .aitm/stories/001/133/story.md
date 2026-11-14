---
schema: "aitm.story/v0"
id: 133
title: "Test impact analysis, CI sharding, and Stop the Line"
kind: "epic"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/133"
parent: null
children: [138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 267, 277, 278, 279, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294]
blocking: [2]
blocked-by: []
created: "2026-11-10T15:32:13Z"
updated: "2026-11-14T13:12:59Z"
last-branch: "planning"
estimate: {"agent-hours": 146.5, "size": "XL"}
priority: "P2"
origin: ".aitm/drafts/2026-11/20261110-0915-test-impact-analysis/draft.md"
files: {"draft": "draft.md", "events": "events.jsonl", "design": ["design/test-impact-analysis-design.md", "design/2026-11-11-133-merge-only-stop-the-line-design.md", "design/2026-11-11-133-test-execution-and-advisory-selection-design.md"], "plan": ["plan/test-impact-analysis-implementation-plan.md", "plan/2026-11-11-133-merge-only-stop-the-line.md", "plan/2026-11-11-133-test-execution-and-advisory-selection.md", "plan/2026-11-12-133-advisory-and-qualification-replan.md", "plan/reviews/2026-11-12-133-advisory-and-qualification-replan-review.md", "plan/2026-11-12-133-advisory-and-qualification-readback.json", "plan/2026-11-12-133-rank-order.md", "plan/2026-11-12-133-ci-warning-manual-recovery-replan.md", "plan/reviews/2026-11-12-133-ci-warning-manual-recovery-replan-review.md", "plan/2026-11-12-133-ci-warning-manual-recovery-readback.json", "plan/2026-11-14-133-behavior-driven-validation-plan.md", "plan/reviews/2026-11-14-133-behavior-driven-validation-plan-review.md", "plan/2026-11-14-133-behavior-validation-readback.json"], "attachments": ["attachments/2026-11-11-merge-fence-design-evidence.md"]}
expansions: []
trips: []
---

# Test impact analysis, CI sharding, and Stop the Line

[GitHub issue #133](https://github.com/kburson/aitm/issues/133)

As an AITM contributor, I want story validation to show which tests are
affected, run them on independent CI shards, and run the full suite
whenever impact is uncertain. If a defect escapes PR validation and
fails the scheduled trunk suite, hold ordinary trunk merges, deliver
one fully validated repair, and reopen after the full suite passes on
repaired trunk. Agents continue working, pushing and integrating into
non-default parents throughout the hold.

This is a follow-on to the delivered [#103 CI quality gates](../103/story.md).

## Current Stop the Line amendment

The owner directed a merge-only hold on trunk. One shared GitHub flag
controls trunk admission. Recovery is a full pass on current repaired
trunk, followed by a current-trunk refresh and fresh CI for each
pending trunk-bound PR. Feature pushes and feature-to-epic merges
continue under their normal target rules.

[Design amendment](design/2026-11-11-133-merge-only-stop-the-line-design.md)
· [Implementation plan amendment](plan/2026-11-11-133-merge-only-stop-the-line.md)
· [#158 hosted qualification plan](../158/plan/2026-11-11-158-merge-only-qualification.md).

The original exact reviews below retain their historical scope.
Changed leaves require replan and review before pickup. Use the
[design constraints and evidence from the #158 spike](attachments/2026-11-11-merge-fence-design-evidence.md)
when refining the later merge and recovery stories. A positive hosted
qualification receipt is required before any story relies on the merge route.

## Test execution and advisory selection amendment

Use `pytest-xdist` with 80% of available cores for eligible local Python
TIA tests. Run hosted shards on separate ephemeral instances. Evaluate
`pytest-testmon` as advisory evidence in [#172](../172/story.md). Keep the
full-suite fallback for uncertain impact and the [#197 delivery hold](../139/plan/delivery-checklist.md).

[Design amendment](design/2026-11-11-133-test-execution-and-advisory-selection-design.md)
· [Implementation plan amendment](plan/2026-11-11-133-test-execution-and-advisory-selection.md).

## Design review

The [graduated draft](draft.md) records the initial requirements. The
[design specification](design/test-impact-analysis-design.md) is the
accepted design. Use the [review intake](design/reviews/README.md)
to trace the exact revision and every review round.

Design accepted at raw digest `sha256:2558bcbdbcc4ed8871078428dd11ddd0381a21627d4dfb744fd13cb5832ce928` and Git blob `82581ae31746d3ddfbd5701568533d476daa15d2`.
[Manual SAR](design/reviews/sar-2026-11-10-tia-design/review-manifest.md) ·
[Independent Codex SPR](design/reviews/spr-2026-11-10-tia-design/review-manifest.md) ·
[Native Claude XPR](design/reviews/xpr-2026-11-10-tia-design/review-manifest.md).

Design acceptance preceded implementation refinement.

## Later product enhancement

After base optimizer proof, develop independent distribution and optional
AITM-Core runtime configuration as a separate enhancement.
[Proposed design](design/independent-deployment-enhancement.md) ·
[Proposed plan](plan/independent-deployment-enhancement.md).

## Accepted implementation plan

The [implementation plan](plan/test-impact-analysis-implementation-plan.md) was accepted at SHA-256
`ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7` and published at `dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84`.
[Manual SAR](plan/reviews/sar-2026-11-10-tia-plan/review-manifest.md) ·
[Independent Codex SPR](plan/reviews/spr-2026-11-10-tia-plan/review-manifest.md) ·
[Native Claude XPR](plan/reviews/xpr-2026-11-10-tia-plan/review-manifest.md).

#133 is the aggregate for 41 bounded Backlog leaves with 64
direct dependency edges. The [leaf catalog](plan/leaf-stories.md) gives
their verified issue numbers and estimates, totaling 146.5 implementation
agent-hours. The [readback receipt](plan/leaf-issue-receipt.json) binds
native links and Project identities to the exact plan.

The parent stops in Planning at plan acceptance. Child pickup and
operational activation have separate gates.

## Develop checkpoint

The owner advanced the epic from Planning to Dev after readback of the
accepted design and plan, all 41 native child links, and all 64 direct
dependency edges. The first pickup candidates are [#138](../138/story.md)
and [#140](../140/story.md). Each leaf has its own design, refinement,
plan and JIT gates.

## Disposable repository authorization

The owner approved one disposable GitHub repository for the #158 spike.
The [spike record](../158/story.md#one-time-repository-authorization)
and teardown receipt record its use and deletion. The owner declined
continual use of disposable repositories. Any follow-on qualification
or rehearsal that depends on another disposable GitHub repository
requires a revised plan before pickup.

## Current advisory and qualification replan

[Reviewed replan](plan/2026-11-12-133-advisory-and-qualification-replan.md) · [Independent review](plan/reviews/2026-11-12-133-advisory-and-qualification-replan-review.md).

Verified GitHub and Project synchronization is recorded in the [readback receipt](plan/2026-11-12-133-advisory-and-qualification-readback.json). The Rank 60 advisory backlog is [#148](../148/story.md) and [#267](../../002/267/story.md).

## Current pickup order

[Rank 50 #146 before Rank 60](<plan/2026-11-12-133-rank-order.md>). The Rank 60 advisory backlog is held until #146 is resolved.

## Advisory warning and manual recovery replan

Preserve #103 as the merge gate. Retain the signed #146 exact-scope observations and replace its unimplemented general production scope with a reviewed advisory warning and manual recovery chain. Local TIA and shard planning stay advisory.

[Amendment](plan/2026-11-12-133-ci-warning-manual-recovery-replan.md) · [Independent review](plan/reviews/2026-11-12-133-ci-warning-manual-recovery-replan-review.md).

## Replacement delivery sequence

[#277](https://github.com/kburson/aitm/issues/277) → [#278](https://github.com/kburson/aitm/issues/278) → [#279](https://github.com/kburson/aitm/issues/279)

## Adoption readback

[Live replacement and pickup evidence](plan/2026-11-12-133-ci-warning-manual-recovery-readback.json).

## Current behavior-driven testing and fast story validation

[Reviewed replan](plan/2026-11-14-133-behavior-driven-validation-plan.md) · [Independent review](plan/reviews/2026-11-14-133-behavior-driven-validation-plan-review.md). #103 remains in force during qualification.

## Verified ranked pickup

[Project and dependency readback](plan/2026-11-14-133-behavior-validation-readback.json) · [Behavior audit #285](../../002/285/story.md) · [Core standard #286](../../002/286/story.md).
