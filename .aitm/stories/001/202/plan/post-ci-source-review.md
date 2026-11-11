# #202 independent exact source review

Claude Opus 5.5 medium, local off-platform review. Date 2026-11-11T02:22:09+00:00. Head `897bdd0b900db1a72dc20f898724d8a88c9e1b8a`, tree `906680801e3f6d0a121248fe20fb4c80397478aa`, literal trunk `5324a80bad7730b2bdb4a2b87acf00f7171305c0`. Review packet SHA-256 `2fc62599336e0d4bd4c17ffc080f809d0565948d84283d2a05a4fe135763c563`. Native GitHub review absent.

PASS

**Scope and limits.** I reviewed only the evidence you supplied. I made no tool calls, edits or external requests. I could not hash or re-run anything, so this verdict covers the bytes as presented. The candidate is `897bdd0b` with tree `906680801e3f`, on literal trunk `5324a80b`. In the hosted record, the tree equals `reviewed_tree`, all six jobs are recorded, `status: pass`, and the raw replay shows `failures: []`. Each of the four changed files stays inside its assigned task. No #203 disposition, #204 folding, destination ACK, Epic #2, C01 or production cutover is authorized or implied.

## Migration and storage (`_monitor_journal_store.py`)

- **Version map.** `_supported_schema` maps each version explicitly: 1 is the base schema, 2 adds `_REVISION_SCHEMA`, and 3 adds the shared `_CONTENT_DISPUTE_SCHEMA`. Any other version raises. Fresh creation in `_initialize_database` runs the same CREATE, so fresh and upgraded stores match. `_assert_exact_legacy_upgrade` checks this against the retained literal `_V2_REVISION_SCHEMA` and v3 DDL.
- **Upgrade transaction.** `JournalStore._upgrade` validates the exact prior version and foreign keys. For v1 it adds the revision table and checks the intermediate schema against the exact v2 tuple before adding the content table. It sets `user_version=3` once, then re-validates identity and foreign keys. `test_legacy_upgrade_uses_one_transaction_and_only_final_version[1|2]` traces exactly one `BEGIN IMMEDIATE`, one `COMMIT`, one `PRAGMA USER_VERSION = 3`, and 2 or 1 CREATE statements.
- **Rollback.** Failure is injected after the DDL and version change, before COMMIT, for both old versions. The tests check that bytes, sidecars, schema and rows are unchanged and that a retry succeeds. The baseline test `test_v1_upgrade_rolls_back_after_ddl_and_can_retry[interrupt|replace-directory]` keeps its name and now triggers on PRAGMA 3. `test_v2_upgrade_rolls_back_after_ddl_and_can_retry` is new.
- **Refusals.** Mixed, unknown (0 or 4) and foreign-key stores are refused with storage identity and durable bytes unchanged. `test_exact_v1_validation_refuses_v2…` now uses a literal `_create_v2_store` fixture instead of building through the current writer.
- **Old readers.** The old v1 reader (`1452999b`) and v2 reader (`5324a80b`) each refused at the schema-version gate (`gate_versions [3]`, "Unsupported routing journal schema version"). The DB, WAL and SHM SHA-256 hashes are identical in both runs. This meets the condition that the refusal must come from the right gate.
- **Constraints.** The table is STRICT. Foreign keys to `claims` and `commits`, BLOB typing and PRIMARY KEY uniqueness are enforced, and `synchronous=2` is confirmed (`test_content_dispute_table_enforces_private_strict_foreign_keys`).

## Dispute logic (`monitor_journal.py`)

- **Precedence.** In `_reserve`, an exact first-material match with an ownership dispute still returns ownership DISPUTED. When a content dispute exists, genesis falls through to HELD instead of REPLAY. A key with only an ownership dispute returns HELD before any content creation. A different-project contender still goes through the earlier ownership branch.
- **Order.** In `_reserve_revision`, the existing-content branch runs before the #201 `_revision_by_material` REPLAY lookup, and creation runs only after it. A known material therefore REPLAYs, as the exact-archive r3A test shows. After a dispute, common, r4A and unrecorded material return HELD.
- **Member replay.** `_matches_content_edge` matches the whole edge. A contender replay also needs the same `position` and the same cursor locator and incarnation. Accepted-child replay is not bound to a source, as the plan allows.
- **Dispute creation.** `_record_content_dispute` checks, in order:
  - The common row is a durable v2 row, so a genesis-only predecessor is HELD (`test_claude_genesis_alone…`).
  - The predecessor proof is re-issued from the same batch and must match the common row's whole edge under `_same_revision`.
  - The contender's usage must differ from the first claim and from every accepted row (`_distinct_accepted_child`, including the equal-r4A case with a different revision number).
  - There must be exactly one direct child.
  - Both ordinals must be greater than the common ordinal.
  - The prefix must differ from the child's.
  - The incarnation must differ from the child's, so a locator-only move is HELD (`[relocated]`).
  - `_original_capture` must pass on the contender's own source.
  - The contender's source ID must differ from the original's, which is checked before this function is called.
- **Atomic write.** `_record_sequence` writes the parent commit before the child row. The final custody fault injection leaves `as_of()` equal to `saved`, and the retry then succeeds.
- **Read validation.** `_stored_content_dispute` covers every extra read-time check from the pickup review: `accepted == _accepted_edge(child, original)`, child predecessor equals common, `common.seq ≤ child.seq ≤ dispute.seq`, the contender's source differs from the original's, and the ordinal and material rules. Tampering with the accepted prefix makes `as_of()` raise, while `as_of(saved.sequence)` still matches.
- **History.** `JournalView.content_disputes` defaults to `()`, filters on `sequence ≤ limit`, and orders by `(sequence, key)`. Claims stay unchanged and the earlier view stays stable after reopen.

## Required fixtures

All required fixtures are present and use real Claude native fixtures:
- r3B HELD, then r3A PENDING, then r3B DISPUTED.
- Stale and exact-archive REPLAY with no new row.
- The common prefix equal across two physical sources.
- The re-read outcome matrix `held/held/disputed(/held)`.
- Cursors `None` for both sources.
- The rewritten common prefix HELD.
- Ownership precedence in both orders.
- A common-usage repeat as REPLAY, plus the guard against the real durable common payload.
- Disabled capture HELD.

## Non-blocking observations

1. **Baseline test count.** The CI replay reports `baseline_tests: 969`, but the local gate retains 970 baseline test IDs. Both runs report 996 candidate tests and zero failures, and the local check lists all 26 new IDs (970 + 26 = 996). I cannot explain the difference from the evidence. It should be explained in the record, but it does not show a regression.
2. **Moved `assert`.** In `_reserve_revision`, `assert cursor is not None` now runs for every verified proof, not only after the original-position check. If `_native_cursor` could ever be `None` there, the code would fail with an assertion error instead of returning HELD. The full suite passes, so this is not shown to be reachable.
3. **Thin coverage.** These cases have no new test or only a weak one:
   - With both dispute types recorded, a contender replay isn't re-checked.
   - The "different original scope" control relies on the existing #201 scope gate and has no new #202 test.
   - The cursor-unchanged check only compares against `None`.
   - The `_original_capture` refusal on the contender's source isn't isolated, because the disabled-capture case already fails at `verified_revision`.
4. **Coverage numbers.** Raw product coverage went from 10,360/11,301 to 10,461/11,407, so 5 of the 106 new statements are uncovered. Helper coverage is unchanged at 778/821.

**Blocking findings:** none.
