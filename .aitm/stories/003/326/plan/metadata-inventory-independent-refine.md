[13:02:40]
REFINE_326: PASS

The scope is accepted as written: six files, Rank 247.5, Size M, 3.5 h, with a 1.75 h checkpoint and a 4.0 h cap. I found no missing prerequisite and no extra file required on the supplied source. This verdict does not authorize Develop. The independent JIT, signed Test, independent source review, verified delivery and native Close all still apply.

## Verified from supplied source

**Codex/Claude path. Confirmed.**
- `Registry._current_candidate` calls `ProviderAdapter().discover(candidate._registration)`.
- That reaches `_discover_sources`, which calls `_open_snapshot` and `_origin` on every `.jsonl` under every root.
- So every parked sibling is opened today. Only a change inside `scan.py`/`adapter.py` plus a registry parameter can remove that.

**Grok path. Confirmed.**
- `ScopeState._current_grok` calls `GrokAdapter.discover`, which runs `_probe` and then `verify_origin(path)` on every `updates.jsonl`.
- This is the same reopen. `grok.py` and `monitor_scope.py` are required and sufficient for it.

**Service authority and capture constraints. Preserved if the inventory only replaces the enumeration step.** These checks stay after the match, unchanged:
- `_check_capture_root`
- the `_ServiceEvidence` type, `source_key_id` and `hmac.compare_digest` key pin
- `validate_source_ref`
- `len(matches) == 1` plus the exact path check
- the root identity check at `root_index`
- the platform, surface and provider tuple
- the Grok version/format tuple
- `_require_live_source`

**Read-only pins. Workable.**
- The new walk can reuse `_directory`, `_file_id` and `_directory_witness` without modifying them.
- `_transcripts` swallows `OSError`, so the inventory needs its own complete, bounded, hold-on-error walk.
- That walk is new code in `scan.py`. It leaves legacy best-effort behavior untouched.

**Durable writer. Confirmed as #121.**
- #326 adds in-memory evidence only.
- `pseudonymize` is a derivation, not a write.
- There is no journal, ledger, cursor or publication change, and no coordinator activation.

**Graph. Confirmed.**
- #115, #120 and #304 are closed.
- #326 blocks #121 only.
- W (#325) touches only `host_watch.py` and its test, so #326 can run in parallel with it.

## JIT conditions of record

1. **Base.** Branch from trunk at or after `f235fe00`, not from the #325 branch. Confirm that `scan.py` is blob `ccb5e121` on that base, so the pinned definitions match.
2. **Route containment.** Confirm that the selected-read entries both live in the two in-scope modules: the `_native_delta` caller in `monitor_registry.py` and `_read_grok` in `monitor_scope.py`.
   - Then the test can drive the full admitted read with an explicit inventory argument.
   - If threading the inventory requires `monitor.py` or `service.py`, stop and return to Refine. Those files belong to #121.
3. **Lease semantics.** Pin `Registry.writer()` and its validity check.
   - The cache binds to key ID plus digest.
   - Lease currency is checked on every use, so an expired or superseded lease refuses.
   - The cache should survive a renewal by the same key. Otherwise a per-cycle lease in #121 would reopen every sibling and defeat the purpose.
   - If no observable lease expiry exists, adding one is an authority expansion, so stop.
4. **Grok fresh authentication.** `verify_origin(path)` opens by path, after a separate `_probe`. Bracket it with equal pre- and post-probes, or with an opened-fd identity, before caching any result. Otherwise an origin could be bound to a replaced incarnation.
5. **Cache composition.** Cache hits must be rebuilt with the current walk's chain and the current ledger refs. Store only the typed origin and the file fingerprint, never a cached chain or a cached `stream_ref`.
6. **Racy timestamps.** Reauthenticate when ctime or mtime is at or after the walk start minus the filesystem granularity, or is in the future.
   - On Linux, `st_birthtime_ns` is 0, so identity rests on dev, inode, size, mtime and ctime. Accepted.
7. **Holds, not skips.** Inside the inventory, `_ChangedSource`/`OSError`, over-cap, an inaccessible entry, or a before/after witness mismatch each hold the positive result. They never drop the entry silently.
8. **Open audit.** The `open` audit event carries a name relative to `dir_fd`, and every Grok file is named `updates.jsonl`.
   - Classify opens by flags: file versus `_DIRECTORY_FLAGS`.
   - Assert exact file-open counts per cycle: baseline cycle, then unchanged cycle (selected file only), then changed-sibling cycle (selected plus one).
   - Alternatively, attribute each open to its directory fd.
9. **Legacy entry paths.** With no inventory supplied, these stay byte-for-byte on their current code:
   - `discover`, `_discover_sources` and `GrokAdapter.discover`
   - `_current_candidate` and `_current_grok`

   The existing scanner and Grok tests run unmodified.

## Stop conditions

Return to Refine on any of these:
- an edit outside the six files
- any required change to the `_directory`, `_DIRECTORY_FLAGS` or `_file_id` pins
- new lease or authority surface
- automatic admission of a live source
- a projection beyond 4.0 h at the 1.75 h checkpoint

Epic #2, C01, production cutover and #204 stay outside. All Epic #100 limits and delivery gates are preserved.
