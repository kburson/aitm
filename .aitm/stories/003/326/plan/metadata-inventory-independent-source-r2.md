[13:44:59]
SOURCE_326: PASS

The three held test proofs are now covered. The product blobs are byte-identical, and the signed and locked evidence binds to the new head and tree. Nothing in the new proofs conflicts with the accepted product, so the product acceptance stands without reconsideration.

## Hold conditions: resolved

1. **Directory and root witness supersession is now proved.**
   - `test_superseded_directory_witness_holds_catalog_without_staging` runs three cases:
     - **During walk:** a marker is touched in `nested` after `scandir` on its fd and before the post-witness.
     - **Root revalidation:** the marker is touched in the root just before `_revalidate_catalog`.
     - **Nested revalidation:** the marker is touched in `nested` just before `_revalidate_catalog`.
   - Each case asserts:
     - a "Complete metadata" hold on two consecutive calls in the same cycle (same-cycle refusal);
     - `marker.exists()`, which guards against an inert patch;
     - a changed directory witness;
     - an empty cache;
     - success in a fresh cycle with the same `stream_ref`.
   - Both patches restore themselves after one use. The second same-cycle call therefore meets stable metadata, so its hold proves the cycle refused rather than re-walked.
   - `test_inventory_rechecks_root_identity_even_without_existing_registry_match` calls `_inventory_discover` directly, which bypasses the capture-root check that masked the earlier test.
     - A replacement directory holds. A replacement that walked silently would have returned an empty walk, so the hold is meaningful.
     - The original directory, once restored, still holds within that cycle.
     - No cache entry is staged, and a fresh cycle yields 2.
2. **Reuse under the renewed writer is now asserted.**
   - An `_open_snapshot` recorder first proves that `parked` is opened in the baseline cycle, so the hook is live. It then proves that `parked` is not opened under the restarted writer.
   - `test_midcycle_key_identity_change_refuses_existing_writer_cache` keeps the same writer and registry and changes only `source_key_id` in the middle of the cycle. The result is "authority changed", which exercises `guard()` rather than the cache namespace.
3. **Grok open counts are now exact.**
   - `selected-verifier-opens == 1` and `selected-native-opens == 1` replace the earlier `>= 1` assertions.
   - With `updates.jsonl` relative opens pinned to exactly one, a parked descriptor-relative open now fails the test. This meets the stated minimum of exact counts.

## Evidence

- **Product blobs.** Five blobs are identical between `2e1c8f1f` and `ba579af0`: `350e5da3`, `a69ff3b2`, `9971108f`, `5963de99` and `8788b907`.
- **Diff scope.** The recovery diff touches only `tests/test_monitor_inventory.py`.
- **Locked local run.** Tree `4b322edd` passed 1429 tests (`product.log`) plus 19 focused tests.
  - The prior run had 1424 tests. The recovery adds 3 parametrized cases and 2 new tests, giving exactly 1429.
  - Product coverage is 13519/14888, identical locally and hosted.
- **Signed hosted Test.**
  - Status is `pass`. Head `ba579af0` and tree `4b322edd` match the reviewed tree.
  - The base is `d7552d6a`, which equals the prior base.
  - The six control blobs match the previous verified gate exactly.
  - The subject digest is `8d8bff64…`, from artifact 14178095030 in run 43753448120, attempt 1.
- **Open-audit trace.** The trace (`3870a29a…`) matches the new exact assertions:
  - native 1/0/2/1
  - Grok 1/0/1/1/1/1
- **Scope.** Behaviour, gates and scope are unchanged.

## Non-blocking notes

- All of the new holds share the "Complete metadata" message. The tests therefore prove the behaviour but do not show which branch fired.
  - For example, the revalidation cases may trip on the file fingerprint's directory ctimes rather than the dedicated directory-witness branch.
  - Either way the result fails closed.
- The key-ID test simulates rotation by monkeypatching `writer.view`; it does not rotate a real key. The key-digest variant is not separately exercised. The hold asked for a key-ID *or* digest change, so this is acceptable.
- The Grok counts are exact but not attributed to a directory. A missing selected open swapped for an extra parked open would still count 1. However, the selected read must succeed and the parity tests cover it, so this residual is theoretical.

## Next

Verified delivery and native Close still apply, unchanged.
