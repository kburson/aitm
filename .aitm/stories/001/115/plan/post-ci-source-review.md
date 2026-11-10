# #115 independent exact snapshot repair review

Declared-manual Claude Code `claude-opus-5-5` with medium effort requested. Exact head `ddf87559f352a1f62f947b683e512d68348a1ecc`, tree `c1c9bc00e7845278b805d4f2828de3663a79c18e`. [Authenticated hosted evidence](https://github.com/kburson/aitm/actions/runs/42869601092/attempts/1). Native GitHub review was absent and the effective branch rule required zero approvals.

## Re-review of AITM #115 snapshot repair at ddf8755: PASS

I reviewed only the supplied packet. I did not verify anything live, replay CI or recompute the patch digest.

## B1 is closed

- **Unaffected turns and boundaries now advance.** The early `return AdapterBatch(diagnostics=disputes, cursor=cursor)` is gone. Observations and boundaries are now filtered by key against `disputed`, and the boundaries are stored as `(key, NativeBoundary)` so they can be filtered. The cursor commits through `_checkpoint(...)`.
  - In `test_internally_conflicting_snapshot_disputes_the_matched_turn`, a cold read now emits turn B's observation and boundary and drops only turn A's.
  - The new retained-dispute test checks that the cursor offset moves forward past A.
- **Keyed disputes are retained.**
  - A dispute is written into `walk.completions` as `snapshot_dispute`, which goes into the cursor.
  - Every read re-emits a dispute for each retained disputed completion.
  - A later clean snapshot cannot clear one: if the snapshot matches but `snapshot_dispute` is already set, the turn is still in `disputed`.
  - A dispute against an already emitted turn changes the cursor but not its offset, as the updated `test_snapshot_conflict_and_cache_categories` and `test_bounded_snapshot_records_all_keyed_disputes` show. This meets the requirement to "preserve keyed per-turn proof for an already emitted identity".
- **Native contradictions still hold the frontier.**
  - The duplicate check now copies `snapshot_dispute=old.snapshot_dispute` into the comparison, so a retained snapshot dispute can't make an identical native re-read look like a conflict.
  - A real differing native duplicate still raises `_Held(IDENTITY_CONFLICT, key)` on the unchanged hold path.
  - The overlap holds and their tests are unchanged.
  - This settles the open question from the prior review in favour of holding, which is consistent with the contract.
- **The new field is constrained.** `snapshot_dispute` accepts only `IDENTITY_CONFLICT` or `OVERLAP_UNVERIFIED`, and an excluded completion can't carry one.
- **Gaps don't double up.** A disputed turn gets no `UNRECONCILED_USAGE` gap on top of its dispute.
- **Evidence is consistent.** There are 630 tests, which is 629 plus the one new test, and the per-file counts add up. The extra `tools/ci` case is now explained: only the hosted candidate command collects it. As before, tying the tested commit `2b5208e` to tree `c1c9bc0` relies on the signed verifier.

## Not blocking, but worth a follow-up

1. **Only two dispute codes are allowed.** `_reconcile` does `code = hold.code` from `_stored_accounting`, then `replace(turn, snapshot_dispute=code)`. That `replace` sits outside the `try`. If `_stored_accounting` or `.reference()` can raise `_Held` with any other code, `__post_init__` raises a `ValueError` that nothing catches. I can't see those functions in the packet, so please confirm they only raise the two allowed codes, or map any other code to `IDENTITY_CONFLICT`. Either way the read fails closed and nothing is charged, but it would be a hold with no way out, which is what B1 was.
2. **Persistence after encoding isn't directly tested.** The test round-trips `first.cursor` through the wire format, but the read that follows uses the still-conflicting `changed` snapshot, which would recreate the dispute anyway. The clean-snapshot replay starts from `second.cursor` held in memory. So nothing yet shows that a set `snapshot_dispute` survives encode and decode and still holds against a clean snapshot. One assertion would cover it: run `_decode(_encode(second.cursor))` and then replay with `s.snapshot`.
3. **The cursor anchor may not bind the dispute.** From the prior review, the keyed anchor covers the prefix, incarnation, cutoff and inherited IDs. It may not cover the content of retained completions. If it doesn't, a tampered cursor could drop `snapshot_dispute`. That is the same trust level as the retained proof already in the cursor, so it isn't a new weakness.
4. **Disputes are re-emitted on every poll.** This is bounded by `_MAX_TURNS`, so M08 needs to deduplicate dispositions by key.

The prior non-blocking items 1–5 still apply. Everything above is source and fixture proof only, not native production admission (that stays with M07, M18/M19 and M05-LG), and nothing was activated in production.

## Implementer disposition

B1 is closed on the exact replacement. The accounting parser raises the overlap hold for multiturn evidence, and the reconcile branch maps invalid accounting or a changed accounting reference to the identity conflict. The checkpoint anchor includes the digest of the complete encoded retained completion tuple, including its dispute value. A supplemental scratch check on the exact tracked tree serialized the second cursor, decoded it, and replayed against the original clean snapshot. The dispute remained and the replay emitted no observations or boundaries. The check passed without a tracked source change. Repeated keyed disputes remain an idempotent journal input for M08. Live admission and release proof stay with the later accepted owners.
