[13:08:45]
JIT_326: PASS

This verdict covers JIT only. It does not authorize Develop beyond the scope of record, and the signed Test, independent source review, verified delivery and native Close all still apply.

## Prior nine Refine conditions

| # | Condition | Status |
|---|---|---|
| 1 | Base | **Met.** Trunk is `f235fe00`. The `scan.py` blob is `ccb5e12126768028aa17206ba1c045c967a6d8ac`. Develop branches from trunk, not from the current `codex/aitm-325-native-host-watch` branch. |
| 2 | Route containment | **Met.** Both routes are module-local. The native route is `_native_delta` → `_approved_candidate` → `_current_candidate`, all in `monitor_registry.py`. The Grok route is `_read_grok` → `_grok_admission` → `_current_grok`, all in `monitor_scope.py`. An optional keyword-only inventory argument reaches both without touching `monitor.py` or `service.py`. |
| 3 | Lease semantics | **Met with no new authority.** `writer()` yields a fresh `Registry` and nulls `_writer` in `finally`, so `.lease` raises once the writer closes. That closure is the observable expiry. Reuse across a renewal is bound only to facts that already exist: physical registry, key ID plus digest, approved root and exact metadata. No owner token or TTL is added. |
| 4 | Grok fresh authentication | **Met.** The JIT brackets `verify_origin(path)` with equal pre- and post-probes before caching. |
| 5 | Cache composition | **Met.** The cache stores only the typed origin and its fingerprint. Chain, `_identity` and `stream_ref` are rebuilt from the current walk and the current `_ServiceEvidence`. |
| 6 | Racy timestamps | **Met, subject to pin 4 below.** |
| 7 | Holds, not skips | **Met.** The new walk holds on error. The swallowing behaviour of `_transcripts` stays legacy-only. |
| 8 | Open audit | **Met.** Opens are classified by flags (`_DIRECTORY_FLAGS` versus file) and by known directory fds. `scandir` raises `os.scandir`, not `open`. |
| 9 | Legacy entry paths | **Met.** The pinned bodies are unchanged. With `inventory is None`, the no-inventory branch executes the current enumeration and every admission check. |

## Further checks

- **Six edit paths.** Five of the paths already exist in the supplied tree. `test_monitor_inventory.py` is the only new file.
- **Existing key.** It is enforceable with the current code.
  - Check `view().source_key_id is not None` before calling `source_evidence()`.
  - With a recorded ID, `source_evidence()` never publishes a key. A missing key raises "unavailable".
- **Grok authority.** It stays with the existing verifier. `read_delta` still re-checks `verify_origin(source.path) != origin` and `_qualified`, so the sideband witness can only invalidate the cache.
- **Updated-sibling uniqueness.** The JIT re-checks every fingerprint before returning, and that catches a content change that leaves directory metadata untouched.
- **Durable state.** #121 is open and still owns activation, the journal, scope and the service. #326 adds no write.
- **Graph.** #115, #120 and #304 are closed.
- **Budget.** The estimate is 3.5 h, with the checkpoint at 1.75 h and the cap at 4.0 h.

## Binding Develop pins

These are not new scope; they make the conditions above exact.

1. **Bind to the writer object.**
   - The inventory binds to the yielded writer `Registry` and to the identity of its `_PinnedPath`.
   - Every operation refuses if `registry.lease is not bound`. This also covers `ScopeState.registry`.
   - Whatever `_PinnedPath.check()` verifies remains the only lease authority.
2. **Use a full-fingerprint comparison for brackets and pre-return revalidation.**
   - Compare the chain, directory ctimes, `st_size`, `st_mtime_ns`, `st_ctime_ns`, `st_nlink == 1` and `S_ISREG`.
   - `_Snapshot.same_path` is insufficient because it ignores the stat fields.
3. **Use a complete cache key.**
   - Every entry keys on exact physical path, fingerprint, and provider or parser kind.
   - Grok entries also key on the verifier object identity, the approved profile identity and the sideband witness.
   - If the verifier is opaque and no witness is supplied, Grok cached origins are not reused.
4. **Measure the racy guard from origin verification time.**
   - An entry is cacheable only if its ctime and mtime are strictly earlier than the pre-probe instant minus a documented granularity.
   - Size that granularity for coarse Linux kernel timestamps, not only for APFS.
   - Future timestamps are never cached.
5. **Treat authenticated non-candidates the same way as positive results.**
   - A non-candidate is a file that was opened and authenticated, and that legacy discovery would yield nothing for. This includes a verifier result of `None`.
   - Such a result is cacheable under the same guards as a positive origin, which keeps parity with legacy behaviour.
   - Exceptions, unreadable entries, raced entries and over-cap entries are never cached and always hold.
6. **Prove locator equivalence.**
   - Build inventory locators through new `scan.py`/`adapter.py` helpers.
   - On an unchanged fixture, assert that every inventory-built locator equals the legacy-discovered locator field by field. The fields are `_registration`, `_path`, `_identity`, `_native_surface`, `_ledger` and `stream_ref`.
7. **Make the bounds named constants.**
   - Path, directory, entry and depth limits become named constants in `scan.py`.
   - Exceeding any of them holds the result rather than truncating it.

## Stop conditions

These remain as of record:

- an edit outside the six files
- a change to the `_directory`, `_DIRECTORY_FLAGS` or `_file_id` pins
- any new lease, owner or authority surface
- automatic admission of a live source
- a projection beyond 4.0 h at the 1.75 h checkpoint

Epic #2, C01, production cutover and #204 stay excluded, and all Epic #100 gates are preserved.
