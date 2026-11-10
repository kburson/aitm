---
schema: "aitm.story/v0"
id: 103
title: "GitHub CI and repository quality gates"
kind: "story"
state: "refine"
issue: "https://github.com/kburson/aitm/issues/103"
parent: null
children: []
blocking: []
blocked-by: []
created: "2026-11-10T00:45:16Z"
updated: "2026-11-10T02:54:54+00:00"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/manual-delivery-checklist.md"
files: {"draft": null, "events": "events.jsonl", "design": ["design/github-ci-quality-gates-design.md"], "plan": [], "attachments": []}
expansions: []
trips: []
---

# GitHub CI and repository quality gates

[GitHub issue #103](https://github.com/kburson/aitm/issues/103)

As an AITM contributor, I want reproducible checks on each source story PR so exact test evidence, independent review and prompt verified closure are possible.

[Reviewed design](design/github-ci-quality-gates-design.md) proposes GitHub Actions for the current Python package, lint and validation for Markdown, JSON and YAML, and a TypeScript lane when a package exists. The owner set a 90% product coverage floor and values behavioral tests. The design starts with full applicable tests and preserves coverage as execution is parallelized.

Standalone infrastructure backlog item. Review the design and refine the estimate before authorizing development. [Manual delivery checklist](../../../manual-delivery-checklist.md).

Design accepted on exact SHA-256 `d48fc2bd0b1973c48a39b4b197a9ab7e97d77db7bdd34980e58022037d4c1ed0` after [SAR](design/reviews/sar-2026-11-09-ci-design/review-manifest.md), [independent manual SPR](design/reviews/spr-2026-11-09-ci-design/review-manifest.md), and [native Claude XPR](design/reviews/xpr-2026-11-09-ci-design/review-manifest.md).
