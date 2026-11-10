# #182 independent source review, attempt 1

Reviewer **Claude Opus 5.5, medium**. Off-platform packet verdict, November 10, 2026 at 22:01 UTC. Exact head `2c7b141b334312b3ed3670dbfa664a8383d89743`, tree `ddefec5c7d7dca6041f3af20cc82ee230794262e`, base `a495d60a87ac4ca764f019dc266e579f13f1787e`. Signed hosted run 42909159699 attempt 1.

# HOLD: AITM #182 M07b

This review uses only the packet. I did not use any tools, replay the tests or recompute the SHA-256 values. I treated the signed CI result (848 tests passing) as given. One blocker stands between this candidate and closure.

## Blocker B1: the adopted route ignores legacy outcomes that are already final

**Source:** in `scopes.py`, the new `enqueue_command` only checks `ledger.command_receipt(command)` when `adoption_id is None`, and only for non-Claude commands. When the first read of the adoption record finds an adoption, the code goes straight to `enqueue_adopted_scope` and never checks the legacy receipt.

In the trunk code, every call checked the legacy receipt first. This conflicts with three pickup requirements:
- "Read-only legacy receipts and exact pre-adoption semantics remain compatible"
- "Preserve the five legacy invocations and their output"
- "If a terminal ID is already visible, refuse to publish a replacement"

`AdoptedRequest` also accepts any `encode_command` bytes, with no check for an existing legacy outcome.

**Reproduce with the existing fixtures in `test_scope_legacy.py`:**
1. Set up `legacy` and `invocation(ledger, "mark", provider=Provider.CLAUDE)`. Run it, then run `scopes.drain_inbox(writer, (BoundaryEvidence(boundary),))` as in `test_pre_adoption_claude_records_memo_and_replays_receipt_despite_monitor_state`. A retry prints `{"command_id": "…115", "status": "accepted"}`.
2. Run `commit_adoption(ledger, ADOPTION)`.
3. With a registered legacy grant and an advertised witness (as in `test_adopted_legacy_requires_the_compatible_reader_witness`), run the same command again.
   - **Expected:** the durable `accepted` receipt, and the monitor inbox stays empty.
   - **Actual:** `{"command_id": "…115", "status": "queued"}`, and an `AdoptedRequest` for that ID lands in the monitor inbox.
   - Without a witness, it returns `unavailable` instead of `accepted`.
4. The same happens with `correct`, and with `bind` for both Codex and Claude.

**Effect:** a command that already has a final legacy outcome is re-proposed under the same ID. The CLI output changes, and M11 is invited to apply it twice. The adopted fence was meant to stop legacy writes, not legacy reads.

**Fix:** before the adopted route publishes, do a lease-free `ledger.command_receipt(command)` for every scope command, Claude included. Do it after the adoption is found and again after the legacy lock is released, and return that receipt when one exists.

**Regressions to add:**
- Accepted and rejected outcomes before adoption, then a retry after adoption, for all five invocations. Relationship commands show nothing because each run gets a fresh UUID.
- The race variant: the outcome is committed between the first read and adoption.

## Checked and passing (from source)

- **Authority and witness:**
  - No grant can be issued from the CLI. `register`, `advertise`, `revoke` and `withdraw` need `writer.lease` and take the locks in lease-then-publication order.
  - Grant, witness, command seal and commit each use their own domain tag.
  - The witness tag binds the encoded `_Grant` (account, project, ledger key, authority key, adoption ID, generation), the protocol, issue and expiry times, and the probe digest.
  - Timing is UTC-only, valid for at most 60 seconds, with at most 5 seconds of future skew. `now == expires` is refused.
  - Proof custody: the proof must be the same object (`is`) from the same reader, and the revision must match. Fabricated, foreign and stale proofs are refused. Probes never enter the inbox.
  - The scoped credential cannot forge a witness (tested).
- **Revocation:** the check runs again under the monitor publication lock in `open_grant`, after the early `preliminary_grant` read. Replayed or modified grant revisions fail the revision name and commit-seal checks.
- **Commit points:** the witness time and pinned project and destination are checked again inside `_publish` before the rename, and again afterwards before any acknowledgement. When expiry hits after the commit, no acknowledgement is sent and a retry produces identical bytes. Witness data is kept out of the envelope, so renewal does not change the bytes.
- **Mixed queue:**
  - The 256 limit counts scope entries only, and retries of pending entries skip it.
  - Type and byte mismatches across formats raise a conflict.
  - `apply_pending` skips scope entries, and `discard` refuses them.
  - The exact old control bytes and registry bytes are tested.
  - A bad seal does not block controls.
  - Uninitialized authority creates no state.
- **Legacy race:**
  - The adoption record is checked again under the legacy lock.
  - The memo is written only in the branch that has not been adopted.
  - The monitor path runs only after the legacy lock is released (the `flock` probe proves it).
  - The exact `encode_command` bytes and the verified Claude session are bound in `AdoptedRequest.__post_init__`.
  - Relationship UUIDs are fresh on every run.
  - A missing or corrupt registry leaves the command in legacy mode, and an invalid adoption record is refused with no writes.
- **Native grammar:** exactly 7 parts, `shlex.join` round-trip, canonical absolute path, recognized only in neutral readers (`project_root is None`), duplicate `cmd` refused, exact receipt pattern. Claude may drop the single final line feed; nothing else is normalized. Only the first target joins (tested end to end from real CLI output).
- **Out of scope:** no `install.py`, launcher, service wiring, scope application or retirement, or migration writer. The adoption writer exists only as a test fixture.

## Not blocking (record or hand on)

1. The producer's `_authority` reads the root source key to check witnesses and commits. That goes beyond "give the producer only the scoped credential", though it is acceptable under the OS-account trust model. With a symmetric MAC, the producer cannot check a witness using only its credential.
2. `ScopeInboxReader.iter_verified` stops at the first bad seal, which also hides valid scope proposals queued after it. M11 should skip or isolate those.
3. `MarkRequest.destination_binding` and the Handoff binding are not checked against the grant's project at admission. M11 must check them.
4. In neutral mode, the Claude `_RouteWalk` now sets `session = None` when the session is not explicit. Non-marker Bash calls now get `kind = None`, not whatever later branch handled them before. CI passes, but please confirm this was intended.
5. Check that `ConflictError` is a subclass of `LedgerError`. If it isn't, a scope ID conflict in `_enqueue_scope` will escape as a traceback rather than printing `unavailable`.
6. Evidence alignment:
   - The pickup was made against trunk `41b4e1e…` with 748 baseline tests; the replay uses base `a495d60…` with 747. Please state the reason.
   - CI `tested` is `2074ab2e…`, not the head, though the tree `ddefec5c…` matches. Please confirm `tested` is the PR merge commit.

**Verdict: HOLD on B1.** After the receipt check and its regressions land, a fresh signed CI run on the new tree should be enough for PASS. None of the other areas needs another look.
