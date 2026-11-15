[13:34:32]
SOURCE_326: HOLD

The product source conforms to the JIT and all seven pins. The hold is test-only: three proofs the JIT requires are missing or not enforced in `test_monitor_inventory.py`. No product edit, scope change or Refine is needed.

## Hold conditions (test file only)

1. **Directory and root witness supersession is not proved.**
   - The JIT requires proof for "superseded root and directory witnesses".
   - `test_replaced_approved_root_never_reuses_a_warm_origin` fails at the existing capture-root check ("identity changed"). That happens before `_InventoryCycle._catalog` runs.
   - As a result, none of these branches has a negative test:
     - the inventory root check `chain[-1][:2] != expected`
     - the pre/post `_directory_witness` comparison in `walk`
     - the directory-witness branch of `_revalidate_catalog`
   - The changed-sibling test only rewrites file content, which leaves directory metadata unchanged.
   - **Fix:** add a case that changes membership between catalog and revalidation, including in a nested directory. It should assert three things: a hold, a fresh-cycle requirement, and no cache staging.
2. **Same-key renewal reuse is exercised but not asserted.**
   - After the writer restarts, `test_cache_renews_through_same_authority…` checks only `stream_ref`.
   - **Fix:** add open tracking that proves the unchanged parked sibling stays unopened under the renewed writer.
   - **Fix:** add a mid-cycle key-ID or digest change on the same registry. The current foreign-registry case trips the cache namespace, not `guard()`.
3. **The Grok audit does not attribute descriptor-relative opens.**
   - `selected-native-opens` counts every relative `updates.jsonl` open, and the test asserts `>= 1`. A parked descriptor-relative open would therefore still pass.
   - The JIT requires attribution by flags *and* known directories.
   - **Fix:** track `O_DIRECTORY` opens so each relative payload open is attributed to its directory, or at minimum assert exact counts.
   - The recorded trace (1/1) is consistent with correct behaviour, but the committed test must enforce it.

## Verified

- **Scope and base**
  - Exactly six paths changed. The diff index lines match the base and candidate blob listings.
  - The base advanced from `f235fe00` to `d7552d6a`, and that advance touches only the two declared #325 files.
  - The `scan.py` base blob is `ccb5e121`.
  - All 11 pinned bodies are identical, including `GrokAdapter.discover`, both `read_delta` bodies and `_open_snapshot`.
- **Pin 1 (writer binding)**
  - The cycle binds to the yielded writer `Registry` and the identity of its `lease`. `guard()` re-reads `self.lease`, so `_PinnedPath.check()` remains the only lease authority.
  - `_require_writer` covers both `_current_candidate` and `ScopeState.registry`.
  - Writer close nulls `_writer`, and the cycle's `_active` flag fails closed. The expired and foreign cases refuse.
- **Pin 2 (full fingerprint)**
  - `_fingerprint` compares chain, directory ctimes, size, mtime and ctime, nlink and file type.
  - The pre/post probes around the origin load and every revalidation use `directories=True`. `_regular_info` enforces `S_ISREG` and `nlink == 1`.
  - Cache reuse uses the file-only fingerprint, which keeps ancestry identity. That matches the JIT's separation of directory and file witnesses.
- **Pin 3 (cache key)**
  - The key is path plus parser kind, with the fingerprint compared on hit. The namespace is lease identity, key ID and key digest.
  - Grok adds a verifier-scoped sentinel (reset on verifier change), the approved profile value and the witness.
  - With an opaque verifier and no witness, the inventory holds rather than caching. The legacy path still reads.
- **Pin 4 (racy guard)**
  - `before` is taken before the pre-probe, and the 2 s granularity is a named, documented constant.
  - Future and racy entries are neither reused nor stored.
- **Pin 5 (non-candidates)**
  - A `None` origin is staged under the same guards as a positive one.
  - Staging commits only after full revalidation, a witness check and a lease check. Exceptions, races and over-cap results are never cached.
- **Pin 6 (locator equivalence)**
  - Native parity asserts `stream_ref` plus `_registration`, `_path`, `_identity`, `_native_surface` and `_ledger`.
  - Grok parity covers path, snapshot identity, origin and root.
- **Pin 7 (bounds)**
  - Named limits cover roots, directories, entries, depth and path bytes, and every one of them raises to a hold.
  - `_INVENTORY_MAX_ORIGINS` is LRU eviction only, so exceeding it forces reauthentication rather than truncating results.
- **Existing key**
  - The `source_key_id is None` refusal happens before `source_evidence()`, so no key is published (this is tested).
- **Routes**
  - Native: `_native_delta` → `_approved_candidate` → `_current_candidate`.
  - Grok: `read_source` → `_read_grok` → `_grok_admission` → `_current_grok`.
  - These are retained unchanged: the carrier, capture limits, proof joins, `_require_live_source`, the cutoff, the exact-path check and the exactly-one-match check. `read_delta` still reverifies the selected Grok origin.
- **Implicit journal cycle**
  - `_active_inventory` applies only inside `_inventory_cycle`. Nested cycles refuse, and calls outside the cycle use the exact legacy discovery (tested).
- **Holds**
  - Duplicate stream, hardlink, symlink, cap, denied scandir, changed sibling at revalidation and same-cycle retry all hold.
  - The racy and future timestamp cases reauthenticate.
  - The Grok sideband witness invalidates the cache without bypassing the verifier.
- **Authority**
  - No new durable write, lease, TTL, owner token, journal state or release surface is added. The `Lock`s are in-memory only.
  - The carrier, key, publication, signed Test and delivery gates are untouched.
- **Evidence**
  - 1424 tests pass locally, and the hosted signed Test passes on tree `aac61dee` with controls identical to the prior gate.
  - The checkpoint traces are 1/0/1 for native and 1/0/1/1 for Grok.

## Non-blocking notes

- `_directory_witness`, `_locator_reference` and `_incarnation_reference` are not in the diff. I inferred they exist on the base from the passing suites; I did not inspect them.
- A non-race exception from the verifier or `_origin` (for example a `LedgerError`) propagates without marking the root held. It is still never cached, and any retry re-runs revalidation, so this does not fail open.
- An `OSError` from the initial `witness_for(root)` call in Grok `_inventory_discover` is not mapped to `_InventoryUnavailable`. It still refuses.
- Ancestor ctimes in the bracket fingerprints mean churn in the home directory causes holds. Legacy `same_path` behaves the same way.

## Return path

1. Amend `test_monitor_inventory.py` only. The five product blobs must stay byte-identical.
2. Re-run the locked local suite and the exact signed hosted Test on the new tree.
3. The re-review is then limited to the test file diff and blob equality for the product files.
