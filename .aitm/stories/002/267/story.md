---
schema: "aitm.story/v0"
id: 267
title: "[#133 T35L] Measure local TIA and testmon advisory performance"
kind: "story"
state: "review"
issue: "https://github.com/kburson/aitm/issues/267"
parent: 133
children: []
blocking: [172]
blocked-by: [143]
created: "2026-11-12T20:01:44Z"
updated: "2026-11-13T10:17:51Z"
last-branch: "planning"
estimate: {"agent-hours": 3.0, "size": "M"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-12-133-advisory-and-qualification-replan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-13-267-measurement-plan.md", "plan/reviews/267-plan-review.md", "plan/measurement/2026-11-13-267-measurement-plan.md", "plan/measurement/benchmark-notes.md", "plan/measurement/evidence.json", "plan/measurement/manifest.py", "plan/measurement/measure_diagnostics.py", "plan/measurement/measure_testmon.py", "plan/measurement/prepare.sh", "plan/measurement/raw-manifest.sha256", "plan/measurement/recheck-baseline.sh", "plan/measurement/recipe.md", "plan/measurement/report.md", "plan/measurement/report.py", "plan/measurement/run-matrix.sh", "plan/measurement/run-profile.sh", "plan/measurement/seed.py", "plan/measurement/summarize.py", "plan/measurement/publication.sha256", "plan/reviews/267-formal-review.md", "plan/delivery.json"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T35L", "path": ".aitm/stories/001/133/plan/2026-11-12-133-advisory-and-qualification-replan.md", "publication": "dc1317219fdc255a86b63c9ce5170a06bd61cca3", "raw-sha256": "61c760529ed13971453a11ede1455a692a170a29d110472a39e1beaf4a131d97", "section-sha256": "56892d2d98ede1115e132a994c3f87ac780e631d78ac8f5369fb56554fba84df"}
---

# [#133 T35L] Measure local TIA and testmon advisory performance

Parent #133. Required predecessor #143, delivered. Rank 60, 3 implementation agent-hours, M, P2.

Measure local TIA and advisory pytest-testmon using disposable fixture changes on a pinned AITM revision with the normal #143 command and pinned tool versions. Compare serial full-reference inventory and outcomes, #143 advisory selection and testmon suggestions. Predeclare the expected impacted or outcome-changing IDs for each seed. Count misses against that expectation. Include a non-code change, unavailable or stale history and uncertain impact that chooses full fallback. Record missing and extra IDs, elapsed time and runner/fixture conditions. If measuring parallel execution, record the approved 80% worker calculation, private fixtures, reconciled outcomes, and capability limits.

Deliver a sanitized report and repeatable local recipe. Its results are advisory evidence for #172. This leaf owns its fixture and report. Runtime changes have their own reviewed pickup.

[Reviewed replan](https://github.com/kburson/aitm/blob/dc1317219fdc255a86b63c9ce5170a06bd61cca3/.aitm/stories/001/133/plan/2026-11-12-133-advisory-and-qualification-replan.md)

## Pickup order

Rank 60 pickup is blocked by owner sequencing until Rank 50 #146 is resolved. [Rank order](../../001/133/plan/2026-11-12-133-rank-order.md).

## Rank 60 advisory pickup

The Rank 50 replacement is recorded. The prior Rank 60 pickup hold has ended. Keep the existing advisory scope and completed prerequisite #143. Its measurements are retained for advisory evaluation under the revised #133 plan. [Replan](https://github.com/kburson/aitm/blob/62b2c5f5af388a1b889c8440d91bc89a365effbd/.aitm/stories/001/133/plan/2026-11-12-133-ci-warning-manual-recovery-replan.md).

## Predeclared measurement

[Plan](plan/2026-11-13-267-measurement-plan.md) · [Independent plan review](plan/reviews/267-plan-review.md).

## Reviewed local advisory measurement

[Sanitized report](plan/measurement/report.md) · [Exact outcomes](plan/measurement/evidence.json) · [Reproduction recipe](plan/measurement/recipe.md) · [Independent review](plan/reviews/267-formal-review.md).

## Delivery

[Verified measurement delivery](plan/delivery.json).
