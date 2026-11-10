# #113 independent design, plan and JIT review

Recorded November 10, 2026. Both rounds used separate declared-manual Claude Code sessions. The provider reported `claude-opus-5-5`; high effort was requested.

## Round 1

### FAIL: the plan needs two small changes before it can pass

Most of the plan matches the accepted M03 leaf and the delivered code. Two required gaps stop it from passing.

#### Required findings

**R1. The plan leaves out the read contract.** The leaf defines two methods: `Ledger.upgrade_monitor_schema(expected_sequence: int) -> LedgerIdentity` and `Ledger.monitor_as_of(sequence: int) -> MonitorLedgerView`. The JIT names only the first. "Read both views from one SQLite snapshot" doesn't commit to the second method or its return type.
- **Change:** in Design, add "`Ledger.monitor_as_of(sequence) -> MonitorLedgerView` reads from one snapshot. `Ledger.as_of` and the legacy renderer return byte-identical legacy views on v1 and v2 stores."
- The pinned v2 decoding test should go through `monitor_as_of`.

**R2. One installer direction is missing.** The JIT covers the new installer with an old wheel (exact v1 fingerprint) and with a new wheel (both fingerprints). It doesn't say what happens when the old installer probes the new wheel. The delivered `_probe_runtime` computes its expected value from its own `SCHEMA_VERSION` and `_supported_schema()`. So whether an old installer accepts the new wheel depends on whether those two symbols in the new wheel still give the v1 values.
- **Change:** state that the new wheel keeps `SCHEMA_VERSION` and `_supported_schema()` as the exact v1 values, so an old installer accepts the new wheel only as v1-capable. Put v2 behind new symbols.
- Or, if refusal is intended, state that.
- Either way, add the old installer with the new wheel to the separate old-wheel rehearsal.

#### Advisory (not blocking)

- **DDL atomicity:** don't use `executescript()` for the v2 DDL. Under legacy transaction control it commits the open `BEGIN IMMEDIATE` first. Use separate `execute()` calls.
- **Commit order:** do the sequence recheck, the v2 fingerprint and identity validation, and `require_writer()` before COMMIT, as `_apply` does.
- **Identity derivation:** `_read_snapshot` builds its identity from `_identity(project_id, key)` and `_validate_identity` compares against the `SCHEMA_VERSION` constant. Both need to dispatch on the stored `user_version`. `key_id` must not depend on schema version, because the leaf requires the key to stay unchanged.
- **Old-wheel refusal check:** name the durable state you compare before and after: database and key bytes, the WAL contents and lock/sidecar files. Opening a WAL database can create sidecar files without changing durable state.
- **Test set:** name the green set the leaf lists (`test_ledger.py`, `test_export.py`, `test_install.py`) plus the backup and CLI tests, rather than just "focused suite".
- **Field naming:** "usage availability" stands for the leaf's "coverage". Keep the field names aligned or map them in the types module.
- **`monitor report` route:** pin the exit code and message for the unavailable route.

#### What checks out

- **Transactions and DDL:** one guarded `BEGIN IMMEDIATE` transaction under the writer lease, with a stale-sequence refusal. It doesn't increment the usage sequence. A stale handle is refused because every transaction re-checks identity.
- **v1 refusal:** the delivered gate compares `PRAGMA user_version` with `SCHEMA_VERSION`, so a version bump makes the old runtime refuse the store. The committed test doesn't rely on repository history, which suits the shallow trusted-base CI.
- **Backups:** v1 manifest bytes stay exact, v2 needs a validated match, and mixed or cross-version restores are refused, with M16 owning migration.
- **Migration boundary:** M03 has no migration command and nothing in production calls the upgrade, which fits the leaf's rule that only M16 bumps the version. Production adoption stays reserved.
- **CLI:** argparse sends everything after the subcommand to the subparser, so `legacy_state_dir` and `project_id` can coexist, with a per-handler check and mixed-form refusal.
- **Scope and estimate:** the plan covers the leaf's file set and the five named tests. 3.75 hours against the four-hour cap is tight given six source files plus the old-wheel rehearsal. It's acceptable because the plan returns to Planning if it overruns, and R1 and R2 add documentation, not much effort.

#### Limits

- I reviewed only the supplied text and code excerpts. I didn't run code, check GitHub, recompute hashes, or see `_PROBE`, `_identity`, `Ledger.open`, `reader()` or how `types.py` derives the key.
- Two items depend on the #100 plan, which I didn't have: whether M05 owns Grok, and the 3.13.9 versus 3.13.18 Python observation.
- The R2 risk and the `key_id` concern rest on how those unseen functions behave.

## Round 2

### PASS: #113 M03 JIT revision 2

I reviewed only the text you supplied: the revised JIT, the prior review, the accepted M03 leaf, the delivered probe and admission excerpts, and the preflight. I didn't run code, check GitHub or recompute hashes, so the `e2043986…` content hash and the `8899a4d1…` plan hash are taken as given.

#### Prior findings

**R1 is resolved.**
- Design now states `Ledger.monitor_as_of(sequence: int) -> MonitorLedgerView`. It returns the legacy view and the monitor revisions from one SQLite snapshot.
- Design also requires `Ledger.as_of` and the legacy renderer to give byte-identical frozen output on both store versions.
- The Plan sends the pinned v2 decoding test through `monitor_as_of`, as requested.

**R2 is resolved.**
- `SCHEMA_VERSION` and the default `_supported_schema()` stay at the exact v1 values. The v2 tag and fingerprint sit behind explicit version dispatch.
- The delivered `_PROBE` imports those two symbols from the installed wheel. The old `_probe_runtime` builds its expected value from its own copies. Both give v1, so an old installer accepts the new wheel only as v1-capable.
- The Plan now includes the old installer probing the new wheel for a v1 ledger without starting any service.

#### Internal consistency

- **Old runtime refuses v2:** this still holds. The delivered gate compares `PRAGMA user_version` with `SCHEMA_VERSION`, which stays 1, so a store tagged v2 is refused. This matches the old-wheel rehearsal, and the committed test doesn't rely on repository history.
- **Version dispatch and key:** the new runtime must admit v2 while `SCHEMA_VERSION` stays 1. The JIT handles this by matching each declared version against its own schema and identity, without touching identity or key derivation. That keeps `key_id` independent of the schema version, which the leaf requires.
- **Probe direction:** probe output shape is set by whichever installer runs it. The new installer must accept legacy wheels that lack the v2 symbols, which "recognizes exact v1 from legacy wheels" covers. The two directions don't conflict.
- **Upgrade transaction:** the prior advisories are now built in. The DDL uses separate `execute` calls. The fingerprint and writer pins are revalidated before commit, and the expected sequence is rechecked inside the guarded `BEGIN IMMEDIATE`. A stale handle is refused after the version changes. The upgrade doesn't increment the sequence. All of this matches the leaf.
- **Migration boundary:** the upgrade method exists but nothing in production calls it, and M03 has no migration command. That fits the leaf's rule that only M16 bumps the version.
- **Old-wheel refusal check:** the bytes to compare are now named (database, WAL, key and retained authority). Lock and shared-memory bookkeeping are treated separately. The CLI exit code and stderr token are pinned, and the green test set is named.

#### Advisory (not blocking)

1. **Upgrade return type:** the JIT says "returned identity" but doesn't write out `-> LedgerIdentity`. The leaf already fixes it, so say it in the JIT too.
2. **Field naming:** "usage availability" still stands in for the leaf's "coverage". Either use the leaf's name or map the two in `monitor_types.py`.
3. **Missing v2 symbols:** the new probe should treat absent v2 symbols as v1-only. It should refuse partial or malformed v2 capability rather than relying on any import error.
4. **WAL check on close:** when the old runtime closes its read connection on a v2 store, SQLite may checkpoint the WAL. The rehearsal's WAL byte comparison would catch that, so don't loosen that assertion if it fails.
5. **Estimate:** 3.75 hours is still tight now that the reverse installer rehearsal is added. The return-to-Planning clause makes it acceptable.

#### Limits

- I haven't seen `_identity`, `Ledger.open`, `reader()`, how `types.py` derives the key, or the #100 plan. That plan is where M05's Grok ownership and the Python 3.13.9 versus 3.13.18 observation are defined.
- The preflight facts are taken as given: #112 Done, #113 Backlog, CI run 42839139388, and 116 baseline tests passing.

The first round reviewed [this draft](jit-round-1.md). The [accepted pickup](jit.md) is the exact second revision.
