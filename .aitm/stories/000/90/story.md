---
schema: "aitm.story/v0"
id: 90
title: "[Usage U06] Pricing and quota availability"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/90"
parent: 83
children: []
blocking: [91]
blocked-by: [86, 88, 89]
created: "2026-11-09T14:42:19Z"
updated: "2026-11-09T23:17:20+00:00"
last-branch: "codex/aitm-usage-u06"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md"
files: {"draft": "draft.md", "events": "events.jsonl", "design": ["design/design.md"], "plan": ["plan/implementation-plan.md", "plan/jit.md", "plan/pickup-review.md", "plan/source-review.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 83, "key": "U06", "path": ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md", "publication": "6ee371590ff3ce0cb5a108bdd1e89cfb17bc2300", "raw-sha256": "07919dde4475310b7fe277791206f611ce5cd615eeaed491d3a619e61142daf5", "section-sha256": "60f4e2f8f6a19994486f509191eb87e653b35c4f93b73edbcb58409a75d686f2"}
---

# [Usage U06] Pricing and quota availability

[GitHub issue](https://github.com/kburson/aitm/issues/90) · [Parent #83](../83/story.md) · Done

**Required predecessors** [#86](../86/story.md), [#88](../88/story.md), [#89](../89/story.md)

## Accepted parent decomposition

**Files** `src/aitm_usage/{pricing,accounting}.py`, `src/aitm_usage/rates/2026-11-09.json`, `tests/test_accounting.py`.

**Contract** `price(usage: UsageObservation, rates: RateCard) -> PriceResult` and `quota_snapshot(raw: QuotaEvidence) -> AccountObservation`, and `account_observations(batch: AdapterResult, rates: RateCard) -> LedgerBatch`. Use Decimal, versioned public rate references and explicit currency. Support the standard rates evidenced in #73 with applicable context and cache classes. Unsupported modes, tiers, models or incomplete category evidence return an Unknown price. Keep actual spend Unknown absent attributable billing. AccountObservation includes a pseudonymous account key, bucket, reset window, source, timestamp and observed precision. V1 records retained inline or structured observations. Additional active sampling is later work.

- [ ] Write `test_standard_rates_and_account_only_evidence` from sanitized #73 vectors. Verify cached input subtraction, supported long-context treatment and Claude cache-write TTL, with reasoning counted once. Check that unknown rates leave tokens visible, a changing same-window quota fixture leaves per-agent burn Unknown, and absent billing evidence remains Unknown.
- [ ] Run `test_accounting.py` to show failure, implement independent price, quota and spend records, then pass leaf verification.

## Accepted amendment

[Revised implementation plan](../83/plan/usage-capture-replan.md). Extend types.py with AccountObservation and independent price and spend records and their static codecs. Interpret the shared QuotaEvidence envelope from U01. Verify write and recovery without raw account handles.

## Current pickup

[Design](design/design.md) · [Plan](plan/implementation-plan.md) · [JIT](plan/jit.md) · [Scoped review](plan/pickup-review.md). This is a manual Develop admission for the dedicated worktree at the pinned base.

[Source verification and independent review](plan/source-review.md). Staged for the reviewed #83 integration. Delivery evidence is recorded when the package lands.

Protected source and project Mac activation verified. [Qualified activation receipt](../83/attachments/activation-receipt.json) SHA-256 `9ec31a4f320a6a36eed2bde0970697444db5bdf6cff4eefbef80c75a7b4d5062`. The production service and ledger remain active.
