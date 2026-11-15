[12:19:30]
REFINE_121: PASS

The exact three-leaf decomposition is accepted: W (M11a, Rank 245), I (M11b, Rank 247.5) and #121 (Rank 250). Each prior HOLD finding is now closed by the supplied source or the revised scope. This verdict does not authorize product implementation, and it does not waive any leaf's own Refine, JIT, Test or delivery gates.

## Verification from supplied source

**Command routes. Verified.**
- `project register` goes through `_submission` to `handler=_enqueue_command`, which calls `ControlInbox(...).enqueue(command)`.
- `scope mark|handoff|dispose` map through `REQUEST_TYPES` to `handler=_enqueue_scope`, which calls `ControlInbox(...).enqueue_scope(request)`.
  - These requests are then applied through the existing native receipt and authority path.
- None of these commands applies scope synchronously from the CLI, so no CLI edit enters #121.

**Park route. Verified as distinct.**
- `_park_session` calls `HookSender().notify(HookEvent(WakeKind.PARK, ...))`. It does not touch `ControlInbox`.
- It exits 0 only on `SENT`. Any `ValueError`, `LedgerError` or `OSError` becomes `UNAVAILABLE`, which fails closed.
- `_LinuxPeer` is present, which is consistent with the delivered #120 peer-credential check on the same-account private socket.
  - The supplied excerpt does not show the full socket body. Delivered and closed #120 is the authority for that check.

**Correction to my prior HOLD.** Finding 5 grouped park with the `ControlInbox` commands. That was wrong. Park is a #120 wake hint that only settles scheduler work. This matches M10/M11: a wake carries no durable scope or cursor authority, and losing a wake costs latency, never correctness, because reconciliation still covers it.

## Topology and custody

**File ownership.** The three leaves edit disjoint sets of files:

| Leaf | Files |
|---|---|
| W | `host_watch.py`, `test_host_watch.py` |
| I | `sources/scan.py`, `sources/adapter.py`, `sources/grok.py`, `monitor_registry.py`, `monitor_scope.py`, `test_monitor_inventory.py` |
| #121 | `monitor.py`, the `service.py` dormant entry, `test_monitor_watches.py` |

- The three accepted test names stay in their accepted file.
- The legacy scanner tests stay unmodified.

**Grok authority.** The supplied `_current_grok` calls `self._grok_reader.discover(source.root)`, which runs `verify_origin` on every `updates.jsonl`. That is the same parked-sibling reopen as `_current_candidate` calling `ProviderAdapter().discover`. Putting `grok.py` and `monitor_scope.py` in I is therefore required, and it is sufficient. Grok's surface, owner and cursor policy are explicitly preserved.

**Metadata authority.** The I scope meets the boundary requirement:
- The cache is bound to the lease, key and digest.
- Racy timestamp observations are treated as unverified.
- Inode aliasing is held.
- Separate approval checks are kept for authorities sharing one exact path.
- The unique-stream positive proof is retained.
- A subprocess audit hook covers the entire admitted read.

**Darwin shutdown ownership. Accepted as documented.**
- The owning thread creates, schedules, starts, stops, invalidates and releases the stream and its CF objects. This keeps every FSEvents call on the scheduling thread, which is the better design.
- The caller only sets the stop event and wakes the run loop.
- Bounded run-loop intervals close the race where a stop arrives during startup.
- The callback is released only after a successful join. This matches the retained arm64 probe (`dedicated_thread_stopped: true`).

**Linux ownership. Accepted.**
- `WatchSet` owns the fd, the bounded descriptor-to-directory map and the registered roots.
- Startup is published as a separate result.
- An enrollment race emits reconcile.
- Overflow emits reconcile and rebuilds the map.
- Closing the fd releases all registrations.
- When a bound is exceeded, the set emits coalesced timed reconcile for the same roots, so W never reads payloads.

**Release-host separation. Clean.**
- W's signed Test records exact-candidate Darwin arm64 and Linux arm64 smoke runs.
- #129/M19 keeps real arm64 and x86-64 qualification. The accepted M19 text already requires "recursive watch overflow" per target.
- The development receipt claims only the hosts it actually exercised.

**Graph. Accepted.**
- #115, #120 and #304 are closed.
- W and I each add one direct prerequisite to #121.
- #123 and #125 stay open and remain downstream of #121 only.
- W and I may run in parallel.

## Estimates per leaf (accepted)

| Leaf | Estimate | Size | Stop rule |
|---|---|---|---|
| W | 3.0 h | M | Stop at 4.0 h or on any required new product path |
| I | 3.5 h | M | Checkpoint at 1.75 h, re-refine before the fourth hour or on any authority expansion |
| #121 | 3.5 h | M | Return to Refine on any unrelated edit or projected over-cap integration |

- I rises from my prior 2.5 h because `grok.py` and `monitor_scope.py` are now in scope.
- M11 now totals about 10.0 h.

## JIT conditions of record (non-blocking)

1. **W.** If the bounded join times out, the `WatchSet` keeps the callback and CF ownership and reports a failed close. Prefer a process-lifetime leak over release, since release would risk use-after-free. Test this alongside repeated stop and startup failure.
2. **All leaves.** Confirm that `f235fe00` is on trunk and contains #120. The current checkout is the #120 branch.
3. **I.** Pin the exact legacy monitor entry paths, and leave `discover`/`_discover_sources` behavior unchanged.

Under your existing Full-Auto authorization, the Epic #100 child creation, Blocked-By edges and rank updates can proceed. I made none of those changes here.
