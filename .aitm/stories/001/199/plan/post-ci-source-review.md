# #199 independent exact source review

Reviewer **Claude Opus 5.5, medium**. Off-platform verdict, November 10, 2026 (America/Chicago). Signed hosted run 42931801378 attempt 1. Native GitHub review is absent. The reviewer received the complete exact replacement diff, accepted pickup and split, authenticated receipt and raw replay.

# Independent post-CI source review: AITM #199 M08b1

## Verdict: PASS for the exact candidate

This verdict applies only to head `a1cde1c364560bed6bca3dcd6f85d021e2fb52f1` and tree `9899ff4990510ebc9de09566fb08efcb33f9d112` against trunk `1452999b2f0f5a90161e39862458029c0084772c`. I reviewed only the packet: no tools, no edits, and no GitHub actions.

I found no blockers.

## Evidence checks
- **Tree and CI:** The hosted `tree` and `reviewed_tree` are both `9899ff49…`, and they match the candidate. All six required jobs are listed and passed.
- **Raw replay:** It shows `passed: true`, 948 tests, no failures, and 919 baseline tests. The coverage figures (10,236/11,175 product, 778/821 helpers) match the frozen local gate.
- **Superseded run:** The earlier failure, a renamed baseline test, is explained and kept. `test_late_claude_revision_keeps_its_original_native_scope` keeps its exact name again, and the new case has its own name (`…_after_ordinary_mark`).
- **#119 blockers:** The split receipt lists all #119 blockers, including the folded proof in #204.

## Source verification

**Collector only on the final, verified read (`adapter.py`)**
- `read_revisions.clear()` runs before the scope-enrollment rescan.
- Witnesses are added only after the last successful `AdapterBatch` is built.
- Every early return and the failed-rescan path add nothing. `test_…_withheld_after_failed_rescan` covers this.

**Exact predecessor**
- Each witness links back to the actual previous `Revision` object from the same read, through `id()` lookup into that read's observations.
- A predecessor from an earlier read never gets a position in `_revision_positions`, so it gets no witness. `test_…_requires_predecessor_in_fixed_read` covers this.
- Any publish without evidence (withdrawal, aggregate, tier invalidation, unwitnessed terminal) clears the position, so no later edge can chain through it.

**Real physical untimed position**
- `SidebandFrame._prefix` is filled from the scanner prefix, and the witness uses `frame.ordinal`.
- The diagnostic still uses `timed_ordinal`, exactly as before.
- `test_claude_cost_state_checks_its_physical_row` covers both directions (disabled and re-enabled).

**Source key and material**
- `verified_revision` raises if the source ledger is not the approved `_ServiceEvidence` key.
- It checks `prefix_ref` and recomputes both material fingerprints from the paired observation objects.
- Both prefix and material derivations are keyed and separated by namespace. No raw rows cross the boundary, and `test_…_bind_each_committing_row` checks the repr.

**Scope and time preservation**
- The proof requires the same boundary, `observed_at`, time basis, key, proof position and end.
- The route must be `ROUTED` and must equal the predecessor's route.
- The tests cover a same-project mark, a real handoff, and a later timestamp.

**Full affected span and current writer state**
- `_revision_capture_chain` walks every edge back to the original position.
- When counters change, it checks `[predecessor, later+1)` for the original owner. When they don't, it checks only the later row.
- The writer's view is confirmed before and after the proof. A Registry change after the batch was issued raises an error, which the disable case in the late-revision test covers.

**Tamper, clone and wrong-writer cases**
- A replaced file with the same bytes raises an error.
- `replace(batch)` and a foreign `ScopeState` raise errors.
- `replace(observation)` returns `None`.

**Terminal contributor eligibility**
- Witnesses are issued only when the excluded baseline is `_ZERO` and every qualified contributor has a counter origin in the same read.
- Each contributor span `[origin, last counter-or-stop + 1)` must be eligible for the original owner.
- A terminal-kind witness with no contributors is rejected in both the adapter and ScopeState.
- Tests cover disabled counters on the target's own earlier revision, on another contributor, and on a distinct later stop.

**Nested parent lineage**
- A foreign, missing, late-repaired, foreign-after-reset, or unverified-at-origin parent drops the counter position.
- Same-parent-after-reset and linked parents keep it, and the 9-case parametrized test covers all of these.

**Legacy and schema compatibility**
- `AdapterBatch` encoding is shown equal to the legacy output in every new adapter test.
- The checkpoint and result formats are unchanged.
- `_revision_witnesses` is `repr=False, compare=False`, runtime-only, and private.

**Phase boundaries**
- Nothing writes to the journal or ledger, releases a cursor, mutates a claim, or reclassifies a diagnostic.
- Quota, `OVERLAP_UNVERIFIED` and `UNRECONCILED_USAGE` behave exactly as before.

## Follow-up notes (not blockers)
1. **Possible crash instead of a clean hold:** `verified_revision` dereferences `cursor.checkpoint.provider.ordinal` without checking for `None`. Elsewhere `provider_checkpoint` is treated as possibly `None`. I don't see a way to reach that state with witnesses present, but a `None` check returning `None` would be safer.
2. **Possible duplicate dropping:** `observations` is now a dict keyed by `id(revision)`. If `result.revisions` ever held the same object twice, the dict would silently remove one, and that would also change the legacy path. The equality tests and the 919 kept baseline tests show no such case today. Consider a list plus a separate id map.
3. **`prefix_ref` is not checked against the file:** ScopeState only validates its format. The actual custody check comes from the confirmed fixed read (`view(..., _confirm_publication=True)`). M08b2 should rely on that confirmation, not on `prefix_ref`, for current custody.
4. **Strict contributor rule may over-hold:** The original owner must be eligible for every contributor's span, including other projects' requests on a shared stream. That errs on the side of holding, so it is safe. It may hold some valid terminal proofs, which M08b4 can revisit.
5. **Stale checklist text:** `delivery-checklist.md` still says "Hosted run 42930421313 is pending". That was the superseded run; update it to run 42931801378 and its pass. The unrelated Codex owner-custody failure, which also reproduces on literal trunk, should get its own tracked issue.
6. **Remaining work for later leaves:** M08b2 must still bind the proof to the exact issued batch, recheck custody before writing, and match the saved claim's original scope against `predecessor_material`. Content disputes stay in M08b3. Dispositions and quota coverage stay in M08b4. The folded intent stays in M08b5, and #119 stays blocked until it lands.
