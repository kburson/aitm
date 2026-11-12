[09:10:01]
PASS

I checked the amended JIT against the six findings and two minor items from the earlier HOLD, and against the four conditions in the accepted Refine. All of them are now resolved. Every existing check is still in place.

**Material findings**

1. **Reconciled changed counter (Condition 4): resolved.**
   - Step 3 now requires the positive report to identify, on its own, the fresh receipt-linked request, the reconciled changed-total counter under the cutoff, and the completion that follows it.
   - It also states that exact ordinal order cannot stand in for the parser's complete accounting witness.

2. **Binding or writer change during a scan (Condition 2): resolved.**
   - `monitor_scope` now rechecks the writer identity, lease, registry and binding straight after `read_delta` returns. It does this before any result is exposed or any verified batch is built.
   - It compares them with what it saw before the first scan. On any change it rejects the whole read, not just the witness, and clears the witness sink.
   - It rechecks again when it consumes the witness.
   - Step 1 adds a test that injects the loss of binding validity, or a writer change, partway through `read_delta`. The test asserts that the whole batch is refused and the sink is emptied.

3. **Test matrix: resolved.** Step 1 now includes the three missing controls:
   - a moved cutoff (Condition 3);
   - a foreign `ScopeState` or registry writer;
   - the same stream under a different approved source ID or physical source.

4. **Five-minute window versus "same binding": resolved.**
   - One five-minute binding must cover both live reads.
   - Expiry during either capture read refuses the run, and so does expiry before the control read (Step 4).
   - A retry needs a new writer, a new cutoff and fresh proof.
   - A binding that has already lapsed falls back to the unbound path. Its quota diagnostics then fail the control's "no native diagnostics" and "sole cause" checks, so it cannot pass as a valid control.

5. **Private copy of `_AccountAuthority` (Condition 1): resolved.** The JIT now says "private copy of the legacy … account authority shape, without importing service.py".

6. **Cause of the control's refusal: resolved.**
   - Step 4 requires the same account, writer and binding, and no native diagnostics.
   - It shows that later usage is the only cause by checking that the self-root command, account authority, scope and immutable prefix are unchanged, plus the clean later read and its new usage.
   - Any other failed check makes the control invalid.

**Minor items**
- **Idle chat at the first account check:** resolved. The first snapshot is now taken with the chat idle, before arming.
- **Unavailable snapshot:** resolved. Steps 3 and 4 now refuse the run explicitly when a snapshot is unavailable or mismatched.

**Checks still in place**
- The exact self-root check (root == turn), the canonical typed queued receipt, and zero raw diagnostics.
- The immutable frontier and prefix, owned qualification, and the original hold.
- The creator binding at ordinal zero, and the account only on full reads with no caller checkpoint.
- The same account value on both scans, derived with `pseudonymize("codex-account", backend_id)` and validated with the service key.
- No change to `codex.py`, the validator, schema, CLI, persistence or ordinary output.
- No raw account data in Git, and no authority survives a restart.
- The recorded limit that the snapshots can't detect a switch and switch-back.
- The 1.60 agent-hour budget, the rebase onto a separate branch with byte comparison, and settlement and delivery kept as separate gates.
- Epic #2, C01 and cutover stay excluded.

**Non-blocking risks (both fail closed)**
- **Tight time budget:** the full sequence must finish inside five minutes of writer-clock time. That covers the CLI queue, opening Desktop, waiting for close, the second snapshot, the positive read, the control turn, the third snapshot and the control read. If it runs over, the run is refused, a retry needs a new cutoff, and the 1.60-hour budget is spent.
- **Registry snapshot:** the binding includes a snapshot of the registry. If the positive read changes the registry, the control read will be refused for the wrong reason and the control becomes invalid. The implementation should confirm that both reads leave the registry untouched.
