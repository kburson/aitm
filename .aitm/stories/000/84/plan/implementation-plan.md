# Package and private durable ledger implementation plan

[Leaf design](../design/design.md) · [Accepted parent plan](../../83/plan/usage-capture-implementation-plan.md) at raw SHA-256 `07919dde4475310b7fe277791206f611ce5cd615eeaed491d3a619e61142daf5`.

**Estimate** 4 agent-hours including source review and verification. Stop and return to planning if the estimate ceases to fit.

**Files** `pyproject.toml`, `uv.lock`, `src/aitm_usage/{__init__,cli,types,ledger}.py`, `tests/test_ledger.py`.

**Contract** `Ledger.initialize(root: Path, project_id: UUID) -> Ledger`, `Ledger.open(root: Path, project_id: UUID) -> Ledger`, `apply(batch: LedgerBatch) -> int`, and `as_of(sequence: int) -> LedgerView`. Define typed observation, revision, scope marker, diagnostic and cursor envelopes, including shared Registration, Eligibility, SourceBoundary, AdapterResult and a versioned sanitized ProviderCheckpoint. Acquire a nonblocking process-held exclusive file lock per project before any write path. Keep the lock file stable across the database lifetime so the kernel releases ownership on process exit. Open status and backup reads without a writer lease. Initialize a missing ledger explicitly and validate identity/schema on every ordinary open. A transaction appends revisions and moves the cursor and provider checkpoint together. The checkpoint preserves the counter baseline, verified logical epoch and ordinals, and the minimum sanitized request prefix for partial reconciliation. Apply only allowlisted fields to the ledger, inbox and checkpoint. Reject extra raw fields before writing any inbox file. Pseudonymize accepted source references before persisting any private or exported record. Store pseudonyms with a project key and include a key identifier in metadata.

- [ ] Write `test_atomic_cursor_and_revisions` with a forced exception between append and cursor advance, a second writer, same-key same-payload retry, and same-key conflicting immutable payload. Assert rollback, writer refusal, lease release on process exit, idempotence and explicit conflict. Verify state permissions and that unsupported schema and mismatched project/key fail before writes.
- [ ] Run `test_ledger.py` to show failure, implement the package, typed ledger and private state initialization, then pass leaf verification.

## Pickup detail

Use the package-local dependency configuration and console script. Run the leaf test and package suite via uv on Python 3.13+. The tests exercise rollback, atomic cursor/state, replay, writer refusal and release, strict private paths and permissions, and identity/schema refusal. Leave provider readers, scopes and service execution to their owning leaves.

Use the exact parent-owned console entry `aitm-usage = aitm_usage.cli:main` and `--project <state-dir>` prefix. The default project state location is `~/Library/Application Support/aitm-usage/<project-uuid>/`. Use directory mode 0700, private files at 0600, SQLite WAL and a 1-second busy timeout on reader connections. Add a real installed entry-point smoke test and prove a read-only as-of snapshot while the writer lease is held. Leave status formatting to U08.
