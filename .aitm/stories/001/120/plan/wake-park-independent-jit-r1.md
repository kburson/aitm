[10:57:03]
JIT_120: HOLD

The scope, graph, seams and physical-socket design hold up. The packet does not yet freeze the issuer contract, the frontier/cursor privacy boundary, the lease and durability ordering, the frame canonicality or the estimate that Refine made conditional. Each gap below is a packet-text fix. None needs a code change to clear.

## Verified

- **Graph and closure.**
  - Prerequisites #115 and #119 are closed. #121 (Rank 250) and #320 are open, and both rank after #120 at 240. This resolves Refine's missing item 1.
  - #121 owns the coordinator, cursor/resume recovery and the real resolver binding.
  - #320 owns the descriptors, adapter invocation, activation and the Grok marker producer.
  - Nothing in the product targets crosses into either.
- **Seams at `e9b92172`.**
  - `monitor_registry.py:91 default_monitor_root`
  - `monitor_registry.py:772 _approved_candidate`
  - `monitor_scope.py:991 _grok_admission`
  - `scopes.py:181/218/274 _private_child/_read_private/_publish`
  - `monitor_control.py:587 configure_monitor_commands`
  - `ledger.py:278 _pin_directory`
  - The JIT names `scopes._publish`, not `export.py:305 _publish`. That disambiguation is correct.
- **Endpoint.**
  - The 103-byte bound is the stricter Darwin limit applied to both platforms. That is conservative and correct.
  - The per-account Darwin path is 80 bytes. Neither feasibility control persists the path.
- **Credentials.**
  - Checked `getpeereid` and `SO_PEERCRED` are the right primitives.
  - Pinned argtypes/restype, a `socklen` equal to `sizeof(struct ucred)` (12), and a UID check before payload parse are correct.
  - The Darwin and Linux aarch64 controls answer Refine's missing item 3.
- **Stale reclaim.** Reclaiming only on `ECONNREFUSED`, under the lease, with an unchanged-inode proof is correct.
- **Scheduler semantics.**
  - Older-frontier no-op, the stale-stop guard and frontier-snapshot `finish` are consistent with one another.
  - Retryable failed or expired reservations, and restart dropping capabilities while keeping pending hints due, are also consistent.
  - Restart now has a named test. This resolves Refine's missing item 2.
- **Sender.** One frame, `SHUT_WR`, 30 ms total, and sent meaning transport only. This is nonblocking as specified.

## Hold conditions

1. **Issuer contract (`monitor_scheduler.py`).**
   - Name the resolver interface, for example `WakeResolver.resolve(request, *, lease) -> WakeResolution`.
   - Enumerate the typed outcome variants: resolved, unknown locator, wrong source type, and stop without a verified current turn.
   - State that `WakeHint` is mintable only through that resolution path, using a module-private issuer and no public constructor that accepts a frontier.
   - Name the writer/coordinator lease type and its file. The packet uses "writer lease" and "coordinator lease" but cites no symbol at `e9b92172`. Refine's `ControlInbox`, `_ServiceEvidence` and `SourceLocator` were cited only at `ab9db800`.
   - Add a test in `test_monitor_scheduler.py` proving that a parsed wire message cannot reach `Scheduler.notify` without resolution.
2. **Frontier versus cursor privacy.**
   - The packet persists a "pending frontier" but forbids persisting a cursor. Define the frontier type and state that it is neither the native cursor nor an offset derived from it.
   - The durable-privacy test must scan the wake subdirectory bytes for the raw path, session string, turn ID and cursor.
3. **Lease and durability ordering.**
   - State the process-local lease TTL as an injectable monotonic duration. The expired-scan test depends on it.
   - State that `notify` completes `scopes._publish` before the hint becomes due.
   - Define the behavior when publish fails, for example: refuse, and leave no in-memory-only due work.
4. **Frame canonicality.**
   - The tests require a "noncanonical frame" refusal, but the contract only says "strict." Pick one of these:
     - exact bytes equal to `json.dumps(sort_keys=True, separators=(",", ":"), ensure_ascii=True) + b"\n"`, or
     - an enumerated rejection set: NaN/Infinity, BOM, non-`int` or `bool` for `v`, and non-string locator.
   - State the locator byte bound.
5. **Linux non-follow chmod.**
   - On Linux, `os.chmod(..., follow_symlinks=False)` may raise `NotImplementedError`.
   - Name the exact mechanism the Linux control measured.
   - If that mechanism is unavailable, allow only this fallback: a `dir_fd`-relative chmod inside the pinned 0700 root after `lstat` proves `S_ISSOCK`, same owner and same inode, followed by the reconfirmation before `listen`. It must fail closed and never dereference.
   - On Linux, treat `EAGAIN`/`EINPROGRESS` from a saturated backlog as a live listener, never as stale.
6. **Measurable fairness (`test_full_project_does_not_starve_another_due_project`).**
   - Assert this bound: with G due groups, every group is selected within G consecutive `take_due(now, 1)` calls.
   - Assert that a capacity-held project does not consume its turn.
7. **Estimate and cap.**
   - Since Refine, the ingress contract has grown by:
     - the stale-socket probe and reclaim
     - inode reconfirmation before `listen`
     - pinned ctypes on two platforms
     - lease-held bind and cleanup
     - launcher discovery
   - The scheduler has also gained lease expiry and restart.
   - Refine's own trigger applies, so restate the slice split. If ingress exceeds 1.75 h or the total exceeds 3.5 h, return #120 to Refine. Stop at the 4.0 h cap regardless.

## Clarify in the same revision (non-blocking)

- Name the file that holds the generic launcher, presumably `sources/hooks.py`.
- Confirm that `sources/hooks.py` blob parity is covered by "host path."
- State whether parking a session with several turns settles every turn of that session.
- State whether a newer-frontier append bypasses the current retry backoff.

## Gates

All existing Refine, Test, signed hosted, independent source, verified delivery and native Close gates are preserved unchanged. #320 installers and the #121 coordinator remain excluded.
