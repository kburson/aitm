[21:46:31]
**JIT_300: HOLD**

This review used only the evidence you supplied. I couldn't recompute the SHA `68cf2657…`.

**What already holds:**
- **Producer path (condition 1).** The Codex path runs `read_source` → `_approved_candidate(..., observed=True)` → `_require_live_source` at `monitor_registry.py:805`. Grok sets `observed` from `source_read_allowed` in `_read_grok`. Neither wraps the error, so it reaches `prepare` bare.
- **Privacy.** The payload holds only pseudonymized references, and there is no CLI or export.
- **Gates and scope exclusions** are unchanged.

**Findings to fix:**

1. **The "retained ApprovedSource" doesn't exist (C2/C3).** `_LiveSourceUnavailable` carries only `decision`, and `read_source` never exposes the `ApprovedSource` to `prepare`. Also, `_approved_candidate` already calls `_require_live_source` on a fresh `_source(view, ...)`, so the plan describes two different recheck calls. Freeze one: inside the write, run `_source(self._writer.view(), decision.source_id)` through the confirmation's single `_require_live_source(observed=True)` call. Compare that result to the decision with `==`.
2. **The confirmation function has no name (C2).** "The new ScopeState metadata-only confirmation" and "factor … out of `_read_grok` when needed" aren't exact. Freeze:
   - the method's name, signature and return value;
   - one Grok verification helper that is required, and that both `_read_grok` and the confirmation use;
   - `discover()` as the only native I/O. Explicitly rule out `read_delta`, `_capture_position`, `_verify_capture_tuple`, `_quota_binding_for` and `_admitted_readers`.
3. **The error mapping is incomplete (C3).**
   - Say what happens on lease loss. I'd recommend raising the existing lease error rather than hiding it behind the original refusal.
   - List exactly which exceptions map to the original refusal: `LedgerError`, `BoundaryUnavailable`, `_CaptureSourceLost`, `OSError`, `ValueError`, and `_LiveSourceUnavailable` that has a different decision or `None`.
   - "final authority validation" shows up in the tests but nowhere in the design. Freeze the order: lease → recheck → lazy upgrade → dedupe check or insert → second recheck? → lease → commit.
4. **Variants that can't be produced (C4).**
   - The readback asserts "valid ranges or unknown", which contradicts the codec that only accepts installation/unknown. Change it to unknown only.
   - Add explicit strict-decode rejection tests for the broader-root, known-range and unknown-reason discriminators.
5. **Schema edits aren't frozen (C5).** Name:
   - the new constant (e.g. `_COVERAGE_SCHEMA_VERSION = 6`);
   - the `_supported_schema` set changes: v6 added, `version == _PAIRED_SCHEMA_VERSION` changed to `>=`, coverage DDL at `>= 6`;
   - v6 added to the `_validate_identity` set, with a test that v7 is rejected;
   - the lazy enable helper: v4→v6 runs the paired and coverage DDL, v5→v6 runs coverage only.
6. **What a dedupe does to `commits` isn't stated.** When dedupe finds an existing row, it must allocate no sequence and write no `commits` row. Otherwise it leaves an orphan commit, and the history it reports would be wrong. State this and test it.
7. **The commit-gap audit is wrong as written (C6).** The JIT says "_tip alone reads commits", but the supplied grep shows other readers:
   - `monitor_journal.py:67` and `:1375` join to `commits` from their own event tables. Those are safe, but call them out.
   - `service.py:406` does `JOIN commits AS committed ON committed.sequence = receipt.sequence`, and `ledger.py:541` reads `MAX(sequence) FROM commits`. Neither is classified. Show whether they hit a different database or are keyed by receipts.
   - List every caller of `_tip`. In particular, rule out any consumer that treats the journal head moving forward as new claims, dispositions or a trigger for an ACK.
8. **Who reads the data, and the canonical bytes (C7).**
   - The pseudonymize domain labels and key for the identity and the seal aren't frozen.
   - The JIT never mentions #209. Confirm that `JournalCoverage`, `coverage_changes`, `source_coverage` and `JournalChange.coverage` don't collide with #209's coverage projection.
9. **The producer contradicts the JIT's own rule.** `_require_live_source` issues a decision in cases the JIT says must not become exclusions:
   - `len(installations) != 1`, which is ambiguity;
   - `profile.current` raising `LedgerError`/`OSError`/`ValueError`, which becomes `current=False`;
   - a missing `source_key_id`;
   - a lease mismatch on the profile.

   That conflicts with "do not reinterpret … ambiguity … as exclusions". Either state that all of these are recorded as `UNQUALIFIED_SOURCE` and add tests, or add a guard and its tests.
10. **The estimate wasn't redone.** The 2.5h breakdown (0.6/0.6/0.6/0.7) assumed a confirmation seam that already existed. The new ScopeState method and the `_read_grok` refactor add work that isn't in it. Re-split the estimate into slices that include them, and show it still fits 2.5h, or restate it. It must stay at or under 4h.
