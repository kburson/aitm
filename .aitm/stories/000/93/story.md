---
schema: "aitm.story/v0"
id: 93
title: "[Usage U12] Integrated restart, enrollment and privacy proof"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/93"
parent: 83
children: []
blocking: [94]
blocked-by: [92]
created: "2026-11-09T14:42:21Z"
updated: "2026-11-09T23:17:20+00:00"
last-branch: "codex/aitm-usage-u12"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md"
files: {"draft": "draft.md", "events": "events.jsonl", "design": ["design/design.md"], "plan": ["plan/implementation-plan.md", "plan/jit.md", "plan/pickup-review.md", "plan/source-review.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 83, "key": "U12", "path": ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md", "publication": "6ee371590ff3ce0cb5a108bdd1e89cfb17bc2300", "raw-sha256": "07919dde4475310b7fe277791206f611ce5cd615eeaed491d3a619e61142daf5", "section-sha256": "63b9a18289b7be20fb80a925e1979de281ea1c5b25384225f69e2f36f55e7237"}
---

# [Usage U12] Integrated restart, enrollment and privacy proof

[GitHub issue](https://github.com/kburson/aitm/issues/93) · [Parent #83](../83/story.md) · Done

**Required predecessors** [#92](../92/story.md)

## Accepted parent decomposition

**Files** `tests/test_service_process.py`, `tests/fixtures/service/`, and `src/aitm_usage/service.py` for the controlled test seam and any integration repair. U08 owns the preceding service changes.

**Contract** Drive the U08 commands against real temporary SQLite state and both adapters in a separate OS process. Control the failure point without weakening the normal write lease. Preserve end-to-end coverage evidence.

- [ ] Write `test_real_service_crash_enrollment_and_private_state`. Prove the unbound approved-root reviewer produces no usage, a proven queued marker admits exactly the eligible segment, and surrounding unrelated segments remain excluded. Exercise both marker arrival orders and the first child request. Kill the service with SIGKILL once between scans and once after an append inside an uncommitted batch. Start a fresh process and assert lock release, rollback and exactly-once catch-up.
- [ ] In the same test use valid and malformed provider records and marker commands with canary values. Establish durable valid writes and scan every byte of private state, including SQLite and WAL or journals, logs, cursor and rejected or inbox files. Inspect status JSON and export JSONL and manifest. Exclude only the known private pseudonym key from the byte scan. U09 extends the scan to the backup bundle.
- [ ] Run `test_service_process.py` to show failure, add the controlled process proof and required integration fixes, then pass leaf verification.

## Current pickup

[Design](design/design.md) · [Plan](plan/implementation-plan.md) · [JIT](plan/jit.md) · [Scoped review](plan/pickup-review.md). This is a manual Develop admission for the dedicated worktree at the pinned base.

[Source verification and independent review](plan/source-review.md). Staged for the reviewed #83 integration. Delivery evidence is recorded when the package lands.

Protected source and project Mac activation verified. [Qualified activation receipt](../83/attachments/activation-receipt.json) SHA-256 `9ec31a4f320a6a36eed2bde0970697444db5bdf6cff4eefbef80c75a7b4d5062`. The production service and ledger remain active.
