# #182 independent source re-review, attempt 2

Reviewer **Claude Opus 5.5, medium**. Off-platform packet verdict, November 10, 2026 at 22:14 UTC. Exact head `7f77a50fe3320ee706474aff93e8d30fde374c9c`, tree `9737a9685e928c57e922cc8a68343ae195b9bacf`, base `a495d60a87ac4ca764f019dc266e579f13f1787e`. Signed hosted run 42911743453 attempt 1.

# PASS: AITM #182 M07b repair, attempt 2

**Basis:** I used only this packet and no tools. I did not recompute the repair-diff SHA-256 or rerun any tests. I took the signed run 42911743453 as given.

**Revision checked:** head `7f77a50f…`, tree `9737a968…`, base `a495d60a…`. The signed head, reviewed tree and base all match the packet. The 867 tests are the earlier 848 plus 19 new ones: 14 parametrized, 1 pending-receipt test, 1 changed-bytes test, 2 race tests and 1 typed-queue test.

## B1: PASS

- **CLI adopted route (`scopes.py`):** every command on the adopted route now does a lease-free `ledger.command_receipt(command)` before `enqueue_adopted_scope`. That includes Claude, and it covers both an adoption found on the first read and one that wins the race. The check sits outside the legacy lock, so it runs after the lock is released.
  - The trunk Claude path already calls `command_receipt` while holding the legacy publication lock. So the receipt read cannot itself take that lock, and the "never take the monitor lock while holding the legacy lock" rule still holds.
- **Typed queue (`monitor_control.recheck`):** for an `AdoptedRequest`, `require_unseen_legacy` runs under the monitor publication lock in the same recheck as the grant, destination and witness checks. Any receipt (accepted, conflict or pending) or a byte conflict raises `LedgerError`.
  - `ConflictError` is a subclass of `LedgerError`, so this becomes a sanitized `unavailable`. Explicit (non-adopted) requests are not affected.
- **Read-only receipt parity, observed adoption:** pinned for mark and bind on both providers, plus correct, alias and parent, each with accepted and conflict outcomes.
  - Exact stdout and trailing newline, empty stderr, no monitor entry, no memo, and the ledger sequence is unchanged.
  - The pending receipt returns before any monitor state exists.
  - Changed bytes still give the legacy `inbox command conflict` with exit 1.
- **Adoption-winning race:** pinned for Claude and Codex. The receipt and the adoption commit both land inside the first legacy-lock acquisition, so the recheck switches to the adopted route. The command still returns the durable `accepted`, never touches the monitor root and writes no memo.
- **No repeated publication through the typed queue:** pinned by `test_typed_adopted_producer_cannot_republish_durable_legacy_command`. Even with a valid grant and witness it raises, writes no inbox file and leaves the stored receipt unchanged.
- **Exact original pre-adoption output:** the new code runs only after the pre-adoption block has already returned. That block, its memo branch and its receipt return are unchanged.

## Regressions: none found

- Retrying an adopted command that is queued but not yet terminal still produces identical bytes. `require_unseen_legacy` only checks legacy receipts, not monitor entries.
- The explicit scope route, mixed-queue limits, drain skipping and old control and registry bytes are untouched.
- The repair adds no runtime activation, installation or scope application.
- Coverage is 9,638/10,538 product lines and 778/821 helper lines, both above baseline.
- The changes to the existing `invocation` correction fixture (`receipt_ref` going from `None` to a scope receipt) are needed so the original marker can be accepted. CI is green with them.

## Not blocking: hand on to M11 and M16

1. **A pending command still in the legacy inbox can be published twice.** If a legacy command was queued but never drained when adoption commits, it has no receipt. A retry then publishes it to the monitor inbox while the legacy inbox still holds the same ID. This is not a regression: it isn't a visible terminal ID, and the pickup leaves the legacy inbox in place on purpose. M16 must either stop the legacy collector draining after the fence or reconcile the two entries.
2. **Post-adoption receipts are only fully checked if the collector honors the fence.** If the legacy collector can still commit after adoption, it doesn't hold the monitor lock, so a receipt could land between the check and the rename. The recheck that runs after the commit would then withhold the acknowledgement, but the entry would stay queued. M11 should check the legacy receipt again before applying an `AdoptedRequest`.
3. **Ledger lookup by path:** `require_unseen_legacy` opens the ledger by `record.grant.project.path`, not through the pinned handle. Publication is still safe because the pinned project recheck refuses any substitution, but a pinned handle would be cleaner.
4. **Lost fixture variant:** check that a correction replacement with `receipt_ref=None` is still covered somewhere now that the shared fixture changed.

Earlier notes 5 (the `ConflictError` subclass) and 6 (the 747 vs 748 baseline and the merge-commit `tested` value) are answered by the Observations section.

**Verdict:** PASS on B1, and no regression from this revision.
