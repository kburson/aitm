# #116 independent pickup review

Declared-manual Claude Code review. The provider reported `claude-opus-5-5`, with high effort requested. Accepted JIT SHA-256 `8bb64d9fea9c0f32dccc8078968f55cf423cf72dd4428da80d31a191f21cbdaa`.

## Round 1

**FAIL.** Identity rules and capture epoch ordering match accepted M06. The blockers are in command custody, the read and lock model, and the apply path.

**Blockers**

1. **Reads while the coordinator holds the lease are not defined.** `_lease` takes an exclusive non-blocking `flock` and raises `WriterActive`. Once a writer holds the coordinator lease, these three would fail or block:
   - `monitor command status`
   - the legacy `register` and `source add-anchor` refusal check
   - `enqueue`

   M06 needs to state how these read the registry without the lease: a validated, consistent snapshot read that never creates the monitor root and returns "not adopted" or "unavailable" when the root is absent.

   For the legacy refusal, specify two checks. The first runs before taking `project_guard`, so an adopted project returns `project-adopted-use-monitor` instead of `writer-active` once the later coordinator holds the original writer guard. The second runs again under `project_guard`, so a pre-adoption request can't race the adoption cutover owned by M16.

2. **Inbox custody is incomplete against the handoff.**
   - **Publication lock:** the handoff has M16 freeze ingress under the writer guard *and an inbox publication lock*. The pickup never defines that lock. `enqueue` must take a lock that is separate from the coordinator lease, and M06 must expose it for M16.
   - **Retries after cleanup:** once queued bytes are cleaned up, only the applied or rejected receipt is left. That receipt must keep the canonical payload digest. `enqueue` must check it, so an exact retry returns the original receipt without republishing, and a different payload under the same UUID is still a conflict.

3. **No defined path from queued to applied.** The runtime loop is deferred to a later leaf, yet M06 requires seeing "applied" from the normal CLI, crash replay between application and cleanup, and bootstrap under the same contract. To fix this:
   - Name the writer-side apply/drain entry point that runs under the coordinator lease. Bootstrap and tests should both use it.
   - State whether each new CLI command only enqueues or also bootstrap-applies when no writer is active.
   - State that a `VerifiedBoundary` can only come from M04 native boundary verification. If config, CLI input or tests can construct one directly, the rule "CLI JSON cannot supply proof" means nothing.

4. **The estimate needs restating after items 1–3.** 3.75 h leaves 0.25 h under the 4 h cap. The fixes add a lease-free snapshot read and an inbox publication lock, and the packet's primitive list has neither. Restate the estimate within the cap, or reopen planning now instead of at the 2-hour checkpoint.

**No blockers in:** source and physical identity (clones, anchors nested in either direction, aliases, shared source approvals with separate project edges, metadata changes), capture epoch ordering (half-open intervals, unsplittable crossing spans treated as gaps, no backfill of the disabled interval, revoked-root read refusal), status sanitization, CLI parsing, and the base and dependency statement.

This review uses only the packet text; I didn't verify the digest, trunk state or hosted jobs.

## Round 2

**FAIL.** One blocker remains. Prior blockers 1–4 are resolved by the revised text.

**Remaining blocker: the locked rechecks don't cover writes the source makes before taking each lock**

The two legacy locks match the handoff:
- **Project writer guard** (`ledger.writer()`): non-blocking, raises `WriterActive`, and M09 retains it during custody.
- **Legacy inbox lock** (`_publication(inbox)`): a blocking `flock` that is independent of the ledger lease.

M16 holding both through adoption and committing before release is consistent with "freeze legacy ingress at that boundary." The gap is in the code that runs between the first (preliminary) check and the second (locked) check:

1. **`source add-anchor` writes its staged payload outside `_publication`.**
   - `stage_source_anchor` runs as `command_factory`. It calls `_private_child(project, ANCHORS_NAME, create=True)` and `_publish_exact(...)` on the project root.
   - Only after that does `enqueue_command` take the inbox lock.
   - If adoption commits between the preliminary check and staging, the legacy path writes into adopted state. The locked recheck then refuses the queue write, but the write has already happened. That breaks "refuses mutation for adopted state."
   - The phrase "recheck the staged payload … under the lock" doesn't say that staging moves inside the lock.
   - **Fix:** put the locked recheck, the staging writes and the queue publication in one `_publication` critical section. `enqueue_command` must accept the lock it is already holding instead of taking it again. `flock` on a second open file description conflicts even within the same process, so nesting the call as-is would self-deadlock.
   - **Fallback:** keep staging outside the lock and state that a staged payload with no queue entry is inert. It must not appear in M16's manifest, and something must own its cleanup.

2. **`register` calls `Ledger.initialize(root, …)` before `ledger.writer()`.**
   - That call sits between the two checks and outside the guard.
   - **Fix:** state that `initialize` doesn't write to an existing ledger (including one with a migrated schema), or move the recheck so it runs before `initialize` can write.

Either fix has to fit inside the stated 4.0 h. That is exactly the cap with no margin, so if this refactor doesn't fit, reopen planning now instead of at the 2-hour checkpoint.

**No other blockers.** I checked:
- Lease-free snapshot reads and the absent-root meanings.
- Lock order across all four locks: no cycle, because the writer guard is non-blocking and only M16 holds both publication locks.
- Retries before and after cleanup: they stay consistent because cleanup needs the publication lock and runs after the receipt is committed.
- `apply_pending`, bootstrap and the enqueue-only CLI.
- `VerifiedBoundary` only coming from the source verifier.
- The exact `project-adopted-use-monitor` reason, and pre-adoption requests keeping their old behaviour.

This review uses only the packet text. I didn't check the SHA-256, trunk state, #114 closure or hosted jobs.

## Round 3

### PASS

The last prior finding is resolved, and none of the items resolved earlier have regressed. No blocking issues remain.

### Final finding: writes made before the lock is taken

**1. `source add-anchor`: resolved.** Revision 3 puts four steps in one critical section under the legacy inbox lock: the locked adoption recheck, creating the private staging directory, staging the raw proposal, and publishing the command. It also says to split `enqueue_command` where the lock is already held and reuse the body that runs under it, without taking a second `flock`. That is the fix the prior review asked for, and it also avoids the self-deadlock it warned about. Because M16 commits adoption while holding the same lock, the recheck reads a state that adoption can't change under it. The anchors directory is no longer created before the lock.

**2. `register`: resolved.** An existing ledger now goes through the read-only opener first, and adoption is rechecked under the project writer guard before anything is published. `Ledger.initialize` is used only when no store exists. If a store appears in the meantime, the text says initialize only validates and opens it. The baseline supports this: `_create_store` runs only on `not _path_exists(store)` inside the guard, and the lease is created only when the store is absent. This meets the prior review's own condition for this fix: state that `initialize` doesn't write to an existing ledger. The text also says to reread adoption when the writer lock is refused, so a takeover that has already committed returns `project-adopted-use-monitor`.

### No regressions
- **Lock order:** The anchor producer now holds only the inbox lock while it pins and reads the project. It doesn't take the writer guard or the coordinator lease under it, so no lock cycle is introduced. The order across all four locks is unchanged from what the prior review checked.
- **Unchanged items:** Lease-free snapshot reads and the absent-root meanings, retries before and after cleanup, `apply_pending`, bootstrap and the enqueue-only CLI, `VerifiedBoundary` coming only from the source verifier, the exact refusal reason, and pre-adoption requests keeping their old behaviour.
- **Hours:** The estimate is still 4.0 h, now stated as including the snapshot, publication-lock and custody work. The text says to reuse the existing primitives to stay within it. Since the plan claims the work fits, reopening planning now isn't required.

### Non-blocking notes for implementation and review
- **Inbox directory creation:** `enqueue_command` creates the inbox directory with `create=True` before taking `_publication`. The lock is held on that directory's file descriptor, so creation can't move inside the lock. After adoption this does nothing, because M16 holds that inbox's lock, which means the directory already exists. That makes it inert, but a test or comment should keep it that way.
- **What `initialize` does to an existing store:** The packet doesn't show the bodies of `project_guard(..., initialize=True)` and `_ensure_private_directory`. The claim that `initialize` "only validates" an existing store depends on both leaving existing state untouched. Implementation review should confirm that.
- **Wording of the `register` recheck:** The text ties the recheck under the writer guard to the existing-ledger path. It should also apply after `initialize`. In practice, if the guard is still held during custody, a writer-lock refusal followed by the reread already covers this, but saying so explicitly would remove the ambiguity.

I used only the packet. I didn't check the SHA-256, trunk state, whether #114 is closed, or the hosted jobs.
