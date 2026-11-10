# #113 independent post-CI source review

Recorded November 10, 2026. Declared manual, off-platform review in a separate Claude Code session. The provider reported `claude-opus-5-5`, with high effort requested. No native GitHub review was submitted.

Review packet SHA-256 `1f84f8bb53a3166cbfce21a1fa8a772c40933777eb7047d825cdef7881a254e5`. Exact six-file diff SHA-256 `869878ace6bf2109ff4c7de5f72a03bab2d4a0ad9694adba7d5c3f143e647783`. [Hosted attempt](https://github.com/kburson/aitm/actions/runs/42841994451/attempts/1).

## PASS: AITM #113 M03 source review

I found no blocking findings in candidate `83fe253ed2a979bb23b52f0a3280591d662112a6` (tree `3e4d46fe…`, base `338ff338…`). This review is based only on the supplied packet. I had no live access and ran nothing independently. The CI, rehearsal and digest results below are what the packet reports.

### Schema identity
- **Admission:** `_read_snapshot` reads `user_version` and builds the identity from it in one snapshot. `_validate_identity` then checks that version against the supported set, `application_id`, WAL mode, the schema fingerprint for that version, and the project and key row.
- **Mismatched tags:** a v1 tag with v2 tables, and a v2 tag without them, are both refused (`test_schema_tag_requires_its_exact_tables`).
- **Compatibility values:** `SCHEMA_VERSION`, the v1 DDL and the default `_supported_schema()` are unchanged. `LEGACY_FINGERPRINT` pins the v1 fingerprint in CI.

### Transaction, rollback, stale and concurrent cases
- **Guarded upgrade:** it runs inside `_write_transaction`, under the writer lease, with `BEGIN IMMEDIATE`, a key re-check and v1 identity validation.
- **Order of checks:** the sequence check comes before the idempotent return. Each DDL statement is a separate `execute`, and `user_version` changes in the same transaction. The new v2 identity is validated and `require_writer()` runs before commit.
- **Rollback:** any exception rolls back through `with conn`. The interruption test fails after both the DDL and the version update. Reopening as v1 then re-checks the exact v1 tables, which proves no table was left behind.
- **Stale sequence:** refused with `ConflictError`, and the view is unchanged.
- **Stale handle:** a v1 handle is refused after the upgrade, because `reader()`/`_write_transaction` see the identity mismatch (asserted through `project.as_of()`). The upgrade doesn't advance the usage sequence or rewrite v1 rows.

### Backup
- The v1 manifest `format` string is byte-identical.
- v2 is selected only from a validated v2 identity, and `_candidate` decodes `monitor_as_of(head)`.
- Verifying a v1 bundle against a migrated v2 ledger is refused. The v2 backup round-trip passes `verify_backup`.
- Old runtimes reject v2 bundles through their exact-v1 checks.

### Installer, both directions
- The old embedded probe sees unchanged v1 symbols, so the old installer can still certify the new wheel for v1.
- The new probe emits `[legacy, v2]` only when the wheel has `MONITOR_SCHEMA_VERSION`. The host accepts the flat legacy form only for a v1 target, so a v2 target requires a v2-capable wheel.
- Booleans are rejected. All other identity fields are still compared exactly.
- The rehearsal reports all four combinations, the old console refusing without changing any bytes, and byte-identical exports.

### CLI
- The two `--project` options have separate destinations (`legacy_state_dir` and `project_id`). The mixed form exits 2, and legacy commands still require `--project`.
- `monitor report` exits 1 with `monitor-report-unavailable` and opens no ledger.

### Monitor payload
- The payload format string is versioned. Provider and surface must agree, and the time value and time basis must agree.
- Provider cost is kept as separate tick evidence.
- Each row's key and revision must match its payload.
- Monitor types are separate from the legacy `Revision`/`LedgerBatch` union.

### Test file as a CI control
It adds 7 cases (5 named plus 2 parameterized), consistent with 563 → 571 tests. The signed result shows coverage of 91.3% for product code and 94.8% for helpers, and all six jobs succeeded on the exact head.

### Non-blocking findings and evidence limits
1. `test_old_binary_refuses_monitor_schema` re-implements the v1 version gate instead of running old code. The real old-binary proof exists only in the off-CI rehearsal, and that showed `collection-failed` rather than the specific schema refusal.
2. The v2 fingerprint isn't pinned anywhere. The new-wheel `[legacy, v2]` probe acceptance and v2-target acceptance are proven only by the rehearsal, not in CI.
3. No CI coverage for:
   - restoring a v2 bundle
   - `observed_at=None` with an `UNKNOWN` time basis
   - `provider_cost=None`
   - provider/surface mismatch, a bad format string, or the "Monitor revision identity changed" path
   - a v2 tag with drifted v2 DDL
4. No upgrade-specific test with two writers at once; this relies on the existing lease tests. The bodies of `require_writer`, `_connection`, `_collector_failure`, the generic codec's allowlist behaviour and the other `_identity` callers aren't in the packet. Any of those callers left on the default v1 identity would fail closed on a v2 store.
5. Nothing at the database level enforces `monitor_revisions` as append-only. I couldn't tell whether the legacy tables have that enforcement.
6. The CLI test doesn't assert that no ledger is read, or that a non-UUID `--project` is rejected.

The trusted exact-tree verifier is still pending after this disposition.

## Implementer disposition

The exact installed v1 wheel was exercised again against the isolated migrated store. Its actual `Ledger.open` raised `Unsupported ledger schema`, and the database, WAL, key and registration bytes matched before and after. The rehearsal separately exercised new-wheel support on v2 and the CLI refusal. The current hosted scope covers v2 backup creation and verification and the legacy restore regression suite. Coordinated migration and rollback remain M16. The code and test control were accepted at the reviewed tree without rework.
