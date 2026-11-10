---
schema: "aitm.story/v0"
id: 113
title: "[M03] Versioned project persistence"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/113"
parent: 100
children: []
blocking: [114]
blocked-by: [112]
created: "2026-11-10T13:57:51Z"
updated: "2026-11-10T14:00:46Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 100, "key": "M03", "path": ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md", "publication": "be326aa06bbf0180969ecadb8df74cf4a37a62c4", "raw-sha256": "8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21", "section-sha256": "df2d7922319a140b5fbe506f594657ef954abe757616d04228476cda55f3432d"}
---

# [M03] Versioned project persistence

[GitHub issue #113](https://github.com/kburson/aitm/issues/113) · [Parent #100](../100/story.md) · [Accepted plan leaf M03](../100/plan/multi-project-usage-monitor-implementation-plan.md#m03-versioned-project-persistence)

**Required predecessors** [M02 #112](../112/story.md).

This Backlog record is bound to the accepted parent plan at `be326aa06bbf0180969ecadb8df74cf4a37a62c4`. Before Develop, obtain the applicable leaf design, Refine estimate, plan and JIT approval. Validate the four implementation agent-hour cap at JIT. Paths in the accepted excerpt are relative to `packages/aitm-usage`.

## Accepted plan excerpt

### M03. Versioned project persistence

**Files** Create `S/monitor_types.py` and `T/test_monitor_ledger_version.py`. Extend version checks and serializers in `S/ledger.py` and `S/types.py`. Update format selection in `S/backup.py`, installer probes in `S/install.py` and CLI dispatch separation in the same leaf.

**Contract** `Ledger.upgrade_monitor_schema(expected_sequence: int) -> LedgerIdentity` and `Ledger.monitor_as_of(sequence: int) -> MonitorLedgerView`. Use the existing transaction sequence and append-only revision storage with an explicitly versioned monitor payload. Keep legacy decoding separate and retain `Ledger.as_of` and the legacy renderer for frozen views. Make the new runtime open and verify legacy and monitor schemas and their respective backup formats. Validate the declared version against its own schema fingerprint and legacy serialization, including installer probes. Bump the database schema version only under the guarded, rehearsed M16 migration. M03 supplies compatibility without invoking migration in production. Carry native host surface, normalized time basis, coverage and optional provider cost separately.

- [ ] Write `test_schema_upgrade_preserves_legacy_identity_and_export_bytes`, `test_old_binary_refuses_monitor_schema`, and `test_mixed_or_interrupted_upgrade_rolls_back`. Assert the legacy snapshot and key are unchanged and a stale expected sequence refuses migration. Add `test_new_runtime_accepts_unmodified_legacy_store_backup_and_installer_probe`. An old runtime refuses a migrated store without writing. `test_legacy_global_state_and_report_project_uuid_are_separate` covers both invocation forms and their mixed-form refusal.
- [ ] Run red. Implement versioned dispatch and transactional upgrade. Run green with `test_ledger.py`, `test_export.py` and `test_install.py`. Commit M03.
