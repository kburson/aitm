---
schema: "aitm.story/v0"
id: 91
title: "[Usage U07] As-of export and C44 compatibility proof"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/91"
parent: 83
children: []
blocking: [92]
blocked-by: [86, 90]
created: "2026-11-09T14:42:20Z"
updated: "2026-11-09T23:17:20+00:00"
last-branch: "codex/aitm-usage-u07"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md"
files: {"draft": "draft.md", "events": "events.jsonl", "design": ["design/design.md"], "plan": ["plan/implementation-plan.md", "plan/jit.md", "plan/pickup-review.md", "plan/source-review.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 83, "key": "U07", "path": ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md", "publication": "6ee371590ff3ce0cb5a108bdd1e89cfb17bc2300", "raw-sha256": "07919dde4475310b7fe277791206f611ce5cd615eeaed491d3a619e61142daf5", "section-sha256": "fea861f3410e15445e87d45afc00bd36b07026184cfb958f6e05b19d3d05b50c"}
---

# [Usage U07] As-of export and C44 compatibility proof

[GitHub issue](https://github.com/kburson/aitm/issues/91) · [Parent #83](../83/story.md) · Done

**Required predecessors** [#86](../86/story.md), [#90](../90/story.md)

## Accepted parent decomposition

**Files** `src/aitm_usage/{export,cli}.py`, `tests/test_export.py`, `tests/fixtures/receiver.py`.

**Contract** `export_as_of(view: LedgerView, rate_card: RateCard, destination: Path) -> ExportReceipt`. Snapshot a fixed ledger sequence. Produce deterministic UTF-8 JSONL and manifest with schema, project, cutoff and digest. Export stable pseudonymous source keys, observation revisions, explicit scope revision references, availability, and the immutable rate-card identifier and pricing basis using an allowlist. Do not include local paths, raw handles, key material or provider content. Receiver fixture models the C44 `ingest_usage(source, payload)` seam. Persist per-key accepted payload digests, pending and reconciliation dispositions and the watermark in a temporary SQLite receiver.

- [ ] Write `test_replay_cutoff_and_pending_finalization` with interrupted import, a withheld partial later finalized after restarting a fresh receiver from its durable watermark, a scope or pricing revision after acceptance, and a conflicting payload. Assert accepted identical retries are idempotent, pending keys survive advancing watermarks, corrections queue, and conflicts preserve prior acceptance. Verify identical fixed-cutoff exports after late ledger changes and a changed versioned price basis yields a distinct manifest. Feed a valid export source and canary-bearing malformed inputs, then check both JSONL and manifest for private material.
- [ ] Run `test_export.py` to show failure, implement deterministic export and the compatibility fixture, then pass leaf verification. Actual Core adapter adoption is a later reviewed integration.

## Current pickup

[Design](design/design.md) · [Plan](plan/implementation-plan.md) · [JIT](plan/jit.md) · [Scoped review](plan/pickup-review.md). This is a manual Develop admission for the dedicated worktree at the pinned base.

[Source verification and independent review](plan/source-review.md). Staged for the reviewed #83 integration. Delivery evidence is recorded when the package lands.

Protected source and project Mac activation verified. [Qualified activation receipt](../83/attachments/activation-receipt.json) SHA-256 `9ec31a4f320a6a36eed2bde0970697444db5bdf6cff4eefbef80c75a7b4d5062`. The production service and ledger remain active.
