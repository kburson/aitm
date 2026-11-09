---
schema: "aitm.story/v0"
id: 84
title: "[Usage U01] Package and private durable ledger"
kind: "story"
state: "plan"
issue: "https://github.com/kburson/aitm/issues/84"
parent: 83
children: []
blocking: [85]
blocked-by: []
created: "2026-11-09T14:42:16Z"
updated: "2026-11-09T15:05:15+00:00"
last-branch: "codex/aitm-usage-u01"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md"
files: {"draft": "draft.md", "events": "events.jsonl", "design": ["design/design.md"], "plan": ["plan/implementation-plan.md", "plan/jit.md", "plan/pickup-review.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 83, "key": "U01", "path": ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md", "publication": "6ee371590ff3ce0cb5a108bdd1e89cfb17bc2300", "raw-sha256": "07919dde4475310b7fe277791206f611ce5cd615eeaed491d3a619e61142daf5", "section-sha256": "0d587ef665cd23fa8f0fb240100f9b0440d33f97f58a84ea87887e0ab4dd8c02"}
---

# [Usage U01] Package and private durable ledger

[GitHub issue](https://github.com/kburson/aitm/issues/84) · [Parent #83](../83/story.md) · Planning

**Required predecessors** None.

## Accepted parent decomposition

**Files** `pyproject.toml`, `uv.lock`, `src/aitm_usage/{__init__,cli,types,ledger}.py`, `tests/test_ledger.py`.

**Contract** `Ledger.initialize(root: Path, project_id: UUID) -> Ledger`, `Ledger.open(root: Path, project_id: UUID) -> Ledger`, `apply(batch: LedgerBatch) -> int`, and `as_of(sequence: int) -> LedgerView`. Define typed observation, revision, scope marker, diagnostic and cursor envelopes, including shared Registration, Eligibility, SourceBoundary, AdapterResult and a versioned sanitized ProviderCheckpoint. Acquire a nonblocking process-held exclusive file lock per project before any write path. Keep the lock file stable across the database lifetime so the kernel releases ownership on process exit. Open status and backup reads without a writer lease. Initialize a missing ledger explicitly and validate identity/schema on every ordinary open. A transaction appends revisions and moves the cursor and provider checkpoint together. The checkpoint preserves the counter baseline, verified logical epoch and ordinals, and the minimum sanitized request prefix for partial reconciliation. Apply only allowlisted fields to the ledger, inbox and checkpoint. Reject extra raw fields before writing any inbox file. Pseudonymize accepted source references before persisting any private or exported record. Store pseudonyms with a project key and include a key identifier in metadata.

- [ ] Write `test_atomic_cursor_and_revisions` with a forced exception between append and cursor advance, a second writer, same-key same-payload retry, and same-key conflicting immutable payload. Assert rollback, writer refusal, lease release on process exit, idempotence and explicit conflict. Verify state permissions and that unsupported schema and mismatched project/key fail before writes.
- [ ] Run `test_ledger.py` to show failure, implement the package, typed ledger and private state initialization, then pass leaf verification.

## Current pickup

[Design](design/design.md) · [Plan](plan/implementation-plan.md) · [JIT](plan/jit.md) · [Scoped review](plan/pickup-review.md). This was the manual Develop admission. Source candidate `be02ad0562669552c810643efb874f5cd3d41881` is preserved on its dedicated branch. [Planning amendment under review](../83/plan/usage-capture-replan.md). The source review requires changes before integration.
