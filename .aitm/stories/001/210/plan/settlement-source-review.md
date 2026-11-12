# #210 independent exact source acceptance

Claude Opus 5.5 high, isolated local CLI. Literal trunk `22f265b6aa7c24050c2d798d7e16c1796701cf64`, head `ede095d8ce46d6d1dc5138a849259cfc74e34787`, tree `6f1ae4a5707f2344bbeb4c15efdb823480866feb`. Review packet SHA-256 `9d362c689471293866d76d07a5186bba957272c856142743b9f1f08712850d33`.

[10:17:00]
PASS

There are no blocking findings. The source matches the accepted M08b4c JIT and its binding conditions B–E. I found no publication, ACK, CI gate change, Epic #2, C01 or production cutover in the eight changed paths. This PASS is source acceptance only. It does not merge or close #210, and it does not start #204 or #119.

## Verified against the exact diff

**Capture and completion (`sources/codex.py`, `sources/adapter.py`)**
- A witness requires a self-rooted turn with no tainted, parallel or compaction context.
- The output must be a `MONITOR_DISPOSITION` output that matches the call. The order must be output < REQUEST < changed counter, and the counter must sit at completion − 1. Timestamps must not go backwards from the turn start to the close.
- The close may not carry an error and may not contain unknown fields. Pre-cutoff rows, compaction, attempt errors and warnings all invalidate the trace.
- `_read_codex` also requires zero walk diagnostics, every frame committed, completion as the last frame, and `frames.cursor == _capture_limit`.
- Ordinary `AdapterBatch` output is unchanged. All 27 disproofs, and the normal path, assert that the ordinary read and the completion-opted read are equal.

**Side proofs (`monitor_scope.py`)**
- `_settlement_side` requires `release_previous` and a provider checkpoint ordinal equal to the completion ordinal.
- The full scope snapshot must still equal the batch-time `_completion_scope`. The command must not appear in scope history.
- `_restorable_owned_route` checks the prior route at the span start and at every event endpoint inside the span.
- `_completion_span_current` checks that the original prefix bytes are unchanged and that the current physical cursor equals the read cursor. This gives before/after pinned custody.
- `_require_settlement_side` re-derives the whole proof and compares it for equality inside the write transaction. A copied proof fails the `_settlement_sides` identity check.

**Grants**
- `_route_requests` holds the inbox publication lock and pins both grants through the journal commit.
- `verify_again` re-checks the envelope bytes, the grant revision and `require_witness` before commit.
- Grants are not consumed. An exact retry returns the same sequence. After expiry a retry refuses ("Scope consumer is unavailable"), and `as_of` still returns the pair. This settles condition C.

**Journal (`monitor_journal.py`)**
- `settle_disposition` requires two different issuers on the one writer and the same scope digest on both sides.
- `_build_settlement_change` requires:
  - the first claim
  - exactly one ownership dispute
  - no content dispute
  - no v4 proposal for any of the four IDs
  - no reuse of IDs from an earlier pair
- `_check_distinct_sides` requires different projects, grants, source IDs, locators and incarnations, and owner sequence < rival sequence.
- `_advance_settlement_side` checks that the old prefix chains into the new one. It refuses on:
  - an unresolved hold in range
  - an unsettled receipt
  - another copy of the disputed key
  - unrouted usage that isn't excluded
  - any claim result other than PENDING or REPLAY
- Both progress rows, any new claims and the pair row are written under one sequence. The commit is read back, and both prefixes are checked again after commit.

**Effective routing**
- `prepare`, `_fresh_view`, `_reserve` and `_complete` use `_journal_view` inside the store transaction.
- `_paired_frontier` excludes everything up to and including the completion.
- `_paired_receipts` aliases only the first following TURN, and only when it has the same receipt and the same `epoch_ref`.
- The legacy `ScopeView view()` is not touched by the diff. `_journal_view` is called only from `_fresh_view` and `_settled_side`. Any other caller therefore reads the original snapshot by construction, which satisfies condition D.

**Conflicts and expiry after commit**
- A legacy resolution, a changed hold, a changed route or a v4 proposal stalls only the affected source (tested). The rival still routes.
- After the hold expires to GAP, the effective view still shows it RESOLVED (tested).
- Late same-turn usage produces `COVERAGE_GAP` with no observations. The cursor holds on replay and after restart.
- A clean later turn routes after restart.

**Store (`_monitor_journal_store.py`)**
- New stores stay at v4. `_enable_paired` performs transactional DDL and sets `user_version` only inside the first pair's write.
- A rollback leaves the store at v4. Every refusal test asserts `user_version == 4`.
- `as_of` for sequences before the pair equals the v4 projection.
- The old binary's stored-version allowlist {1..4} in `_validate_identity` refuses v5. Locally, `literal_trunk_v4_reader_refused_v5: true`. This settles condition E.

**#204 extension point:** `_build_settlement_change(connection, key, owner, rival)` runs inside the pinned write transaction and returns `(change, inserted)`.

## Evidence comparison

| Item | Result |
|---|---|
| Hosted vs local results | Same base, head and tree. The candidate test sets are identical at 1,216. Coverage matches exactly: product 11272/12276, helpers 806/849. |
| Baseline count | Local has 1,102 against hosted 1,101. The difference is the one local-only control, `test_usage_console_help`. |
| New tests | 114 new test IDs (1,216 − 1,102), from 19 new functions. My count from the diff agrees: 77 + 1 + 36 tests and 8 + 1 + 10 functions. |
| Hosted `tested` commit | `tested` is `57f1d2e`, not the head. The receipt binds `tree` and `reviewed_tree` to `6f1ae4a`. |
| Native capture | Rows 249 < 253 < 254 = 255 − 1, and completion is the last of 256 rows. This matches the predicates the code enforces. |

## Non-blocking findings

1. **JIT step-1 negatives not present as tests.** These are missing:
   - a missing rival or a single-sided call
   - a legacy proposal made before commit
   - the same issuer used for both sides
   - a GAP side (`release_previous=False`)
   - a key with no dispute
   - a content-disputed key
   - a same-project pair

   The source refuses each of these before any write: the `settle_disposition` type and issuer guard, `_settlement_side`, the `pending` check in `_completion_span_current`, the checks in `_build_settlement_change`, and `_check_distinct_sides`. Add the tests before #204 extends `_build_settlement_change`.
2. **A corrupt pair payload stalls all journal routing, not just one source.** `_effective_releases` calls `_settlements`, which raises globally, and `as_of()` at the tip fails too. This is stricter than condition B's wording ("stalls that source"), but it is unavoidable because a payload that fails its MAC can't name its source. Record this in the delivery record.
3. **Alias and epoch negatives are missing.** No test checks that a following TURN with a different receipt or epoch is not aliased. No test changes the epoch between issuance and commit.
4. **The late-usage test is loose.** It accepts either branch: the cursor is `None` and `prepare` raises, or `reserve_batch` returns `()`. Both keep the cursor, but the test doesn't pin which one happens.
5. **`prepare` candidates are slightly stricter.** They now come from `view._proofs` rather than `batch.observations`. This is fail-closed, and the baseline suite passes.

## Residual limitations

- **Native proof doesn't cover the pair.** The native proof is one Desktop side, read by the launcher built from `6abd6f4`, not from the head. The paired positive (two sources, two projects, a durable dispute) is synthetic only. No native pair was run.
- **Quota-bound pairs are untested.** No test covers a pair with two quota bindings. In production, both issuers' five-minute bindings must still be valid at commit, otherwise the settlement refuses (fail-closed).
- **Things I could not check.** I saw only the diff. I could not see the unchanged bodies of `view()`, `_validate_identity`, `_claim` or `_write_progress`, or other uses of `_Marker`. My judgement there rests on the passing baseline suite. I did not verify the hosted attestation signature.
- **Future pruning risk.** The effective view needs the original hold and its `held_route_target` to stay in scope state. If retention ever prunes them, that source stalls.
- **Rollback is manual.** Rolling back means restoring the pre-upgrade private store, and the source makes no backup.
- **#204 needs a versioned payload.** `_PairedSettlement` is a closed, canonically encoded payload whose identity comes from a MAC. Adding folded intent will need a versioned payload or a separate table so existing v5 rows still validate. The current method also takes no intent parameter.
- **Delivery-record items.**
  - Condition A: closure of #210 is still undetermined. The unsupported cases must be reconciled against the accepted scope:
    - undisputed single-owner holds
    - GAP-only or mixed outcomes
    - same-project content disputes
    - legacy, missing-rival and unrelated-diagnostic cases

    The M08b4c assignment's wording, "exact effective state and any proven settlement", doesn't clearly exclude an effective GAP. #204 and #119 stay blocked until that reconciliation is done.
  - Condition F: link the owner's approval of the completion anchor.
  - Condition C: state that settlement does not consume grants.
