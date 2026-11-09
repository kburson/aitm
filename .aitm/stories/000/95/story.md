---
schema: "aitm.story/v0"
id: 95
title: "[Usage U10] Qualification validator and on-host runbook"
kind: "story"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/95"
parent: 83
children: []
blocking: [96]
blocked-by: [94]
created: "2026-11-09T14:42:23Z"
updated: "2026-11-09T21:18:15+00:00"
last-branch: "codex/aitm-usage-u10"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md"
files: {"draft": "draft.md", "events": "events.jsonl", "design": ["design/design.md"], "plan": ["plan/implementation-plan.md", "plan/jit.md", "plan/pickup-review.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 83, "key": "U10", "path": ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md", "publication": "6ee371590ff3ce0cb5a108bdd1e89cfb17bc2300", "raw-sha256": "07919dde4475310b7fe277791206f611ce5cd615eeaed491d3a619e61142daf5", "section-sha256": "3626e7aafcb1b9d6d7cab4e11adefdc22097ee458e4af5dd2b3f8b567d050aa1"}
---

# [Usage U10] Qualification validator and on-host runbook

[GitHub issue](https://github.com/kburson/aitm/issues/95) · [Parent #83](../83/story.md) · Develop

**Required predecessors** [#94](../94/story.md)

## Accepted parent decomposition

**Files** `README.md`, `src/aitm_usage/{qualification,cli}.py`, `tests/test_activation_receipt.py`, `tests/fixtures/activation/receipt.json`.

**Contract** `validate_activation_receipt(receipt: ActivationReceipt) -> QualificationResult`. Expose the validator as `aitm-usage qualify --receipt <file> --json`. The on-host runbook uses that installed command, both observed local provider routes and actual launchd. Require approved project scope, collector version, both provider routes and client versions, heartbeat, source watermarks, private state permissions, unattended startup, restart and supported backup/upgrade rehearsal, coverage, sanitized sample keys and export parity. Require verified scope-marker evidence on both local provider routes, including marker-first and observation-first processing. Validate labeled real controlled or normal project evidence. Reject fixture-only evidence for activation.

- [ ] Write `test_activation_requires_live_both_providers_and_parity` for fixture-only, stale heartbeat, one missing provider, missing scopes, duplicate records after restart, and receipt privacy. Require correct proof from one real shared planning session with epic hydration and at least two child scopes, overlapping author and reviewer, including graduation and the inclusive rollup, and authorized development and housekeeping. Development ownership can be exercised in a controlled worktree with a clearly labeled proof basis.
- [ ] Run `test_activation_receipt.py` to show failure, implement validation and runbook, then pass leaf verification.

## Current pickup

[Design](design/design.md) · [Plan](plan/implementation-plan.md) · [JIT](plan/jit.md) · [Scoped review](plan/pickup-review.md). This is a manual Develop admission for the dedicated worktree at the pinned base.
