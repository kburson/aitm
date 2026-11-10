---
schema: "aitm.story/v0"
id: 103
title: "GitHub CI and repository quality gates"
kind: "epic"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/103"
parent: null
children: [104, 105, 106]
blocking: []
blocked-by: []
created: "2026-11-10T00:45:16Z"
updated: "2026-11-10T12:51:47+00:00"
last-branch: "planning"
estimate: {"agent-hours": 10.0, "size": "L"}
priority: "P1"
origin: ".aitm/manual-delivery-checklist.md"
files: {"draft": null, "events": "events.jsonl", "design": ["design/github-ci-quality-gates-design.md"], "plan": ["plan/implementation-plan.md"], "attachments": ["attachments/local-coverage-baseline.md"]}
expansions: []
trips: []
---

# GitHub CI and repository quality gates

[GitHub issue #103](https://github.com/kburson/aitm/issues/103)

As an AITM contributor, I want reproducible checks on each source story PR so exact test evidence, independent review and prompt verified closure are possible.

[Reviewed design](design/github-ci-quality-gates-design.md) proposes GitHub Actions for the current Python package, lint and validation for Markdown, JSON and YAML, and a TypeScript lane when a package exists. The owner set a 90% product coverage floor and values behavioral tests. The design starts with full applicable tests and preserves coverage as execution is parallelized.

Standalone infrastructure work. [Manual delivery checklist](../../../manual-delivery-checklist.md).

Design accepted on exact SHA-256 `d48fc2bd0b1973c48a39b4b197a9ab7e97d77db7bdd34980e58022037d4c1ed0` after [SAR](design/reviews/sar-2026-11-09-ci-design/review-manifest.md), [independent manual SPR](design/reviews/spr-2026-11-09-ci-design/review-manifest.md), and [native Claude XPR](design/reviews/xpr-2026-11-09-ci-design/review-manifest.md).

Refined as a **10.0-agent-hour P1 epic** with three independent leaves. Each leaf stays within four implementation agent-hours and closes on its own evidence. The local baseline was **530 passing tests and 90.9551% line coverage**. Hosted evidence remains a delivery gate. [Baseline](attachments/local-coverage-baseline.md).

[Implementation plan](plan/implementation-plan.md) accepted at exact SHA-256 `f81b4d18c36b1294c4bfc0635cf8bba67f231250a6a398dd92ddda63adb465fb` after [SAR](plan/reviews/sar-2026-11-09-ci-plan/review-manifest.md), [independent manual SPR](plan/reviews/spr-2026-11-09-ci-plan/review-manifest.md), [native Claude XPR](plan/reviews/xpr-2026-11-09-ci-plan/review-manifest.md). #103 remains in Planning. The leaves are [#104](../104/story.md), [#105](../105/story.md), and [#106](../106/story.md), in dependency order.

**Current Planning blocker.** #104 returned to Planning after the [live GitHub binding probe](../104/attachments/github-binding-probe-attempt-1.md). GitHub associated the run with the PR head and the observed metadata did not independently bind it to the exact synthetic merge. The bootstrap PR is held as a draft. The [reviewed ordinary PR binding amendment](../104/design/github-tested-merge-binding-replan.md) preserves the normal story PR and adds signed GitHub Actions identity evidence. A fresh JIT, separate execution authorization and a successful live proof still gate delivery. The original failure evidence remains historical.

The [#104 signing probe](../104/attachments/github-signing-probe-result.md) passed and closed the binding feasibility question for this route. Production CI and delivery remain separate gates.

The [#104 local delivery checkpoint](../104/attachments/local-delivery-checkpoint.md) records passing local verification and the remaining production authority gates. [#105](../105/story.md) and [#106](../106/story.md) have reviewed design and plan artifacts. Their predecessor gates remain open.

Full-Auto delivery resumed on November 10. The owner authorized recurring public attestations with the reviewed permissions and sanitized digests and metadata, and authorized #104 to enter Develop before the first CI result. Actual passing CI and independent review remain merge gates.
