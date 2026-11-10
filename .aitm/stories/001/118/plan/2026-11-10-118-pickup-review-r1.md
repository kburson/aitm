# #118 independent pickup review, round 1

Reviewer **Claude Opus 5.5, high**. Off-platform exact pickup and split on November 10, 2026.

**Verdict: HOLD on the pickup and HOLD on the split.**

Both holds share one root cause and can be fixed by editing the documents. No new code or rescoping is needed. Without tools I could not check the two SHA-256 values, the closed state of #117/#182/#194, PR #198, the baseline numbers, or any source outside this packet.

## M08a pickup: HOLD

**B1. Changed content under the same key gets two different outcomes.**
- The claim section says "competing project **or different content** under that key records one exact deduplicated dispute." The same section says "M08a safely holds potential late revisions." Those two rules conflict when the same owner sends changed content.
- The split's own audit says adapter records carry neither a predecessor edge nor the later evidence position. So M08a cannot tell a Claude update apart from content that genuinely can't be compared.
- If that case is recorded as a dispute, the dispute is committed and the cursor can move past the update. M08b then inherits a dispute it can't reinterpret, because the later evidence span is gone.
- **Fix:** disputes cover competing projects only. Any same-owner content that isn't byte-identical is held, and the earlier cursor stays in place.

**B2. The packet doesn't show the cursor side of "same-read".**
- `VerifiedScopeBatch` carries only a final cursor (`cursor`, `_native_cursor`). It has no starting cursor.
- `Registry` keeps its capture progress in in-memory dicts on each instance (`_frontiers`, `_verified`, `_completed`). Nothing shows that `ScopeState.read_source` accepts a prior cursor supplied by the journal and re-delivers the unstaged rest of a read after a restart. If it reads from its own progress marker instead, held data that the journal never staged is skipped.
- `_recheck_batch` only asserts `batch.cursor is not None` on the Grok path. Native batches may have `cursor=None`, which would leave nothing for `progress: StreamCursor` to bind to.
- **Fix:** cite the `read_source` signature and how native cursors get filled in. Also move "reopen with the old cursor and replay the rest through `read_source`" into the two-hour gate.

**B3. Scope boundaries aren't counted as obligations.**
- A batch's `boundaries` share its single final cursor with its observations. The whole-batch rule only requires claims for observations.
- A boundary at the end of a batch, with no observations after it, would have no hold to block the cursor.
- **Fix:** progress may advance only when every boundary in `batch.boundaries` has a durable ScopeState event or hold.

**B4. The 3.75-hour estimate and two-hour checkpoint aren't credible as written.**
- The gate needs the store (budgeted 1.10), the native same-read proof (0.85) and the first-claim rollback (part of the 0.90). That is about 2.2–2.4 hours of the plan's own budget, so the gate is set up to miss.
- The store work is also under-costed. The existing `_create_store` uses `staging.rename(root / STORE_NAME)`. That rename replaces an empty directory sitting at the target, and it uses paths rather than the pinned directory handles after the pin check. A true no-replace directory publish on macOS needs `renameatx_np(RENAME_EXCL)` through ctypes, which isn't in the existing helpers.
- **Fix:** either gate at two hours on store genesis, publish and reopen plus the native same-read handle and prior-cursor replay, and move rollback after the gate; or accept that the slice will probably reopen.

**Amendments to make (not blocking on their own):**
- **Key setup:** `source_evidence()` creates a new key when both the file and the state are missing. When only the state is missing, it adopts the file and saves state. The journal must require `view().source_key_id is not None` before calling it, or add a read-only accessor. A new accessor changes the registry module, which isn't in the Files list.
- **Writer binding:** `_ISSUED_VIEWS` is global, and `resolve_route` never checks the lease, so an issued view outlives its writer. The journal must issue a fresh view through its own `ScopeState.view(batch)` at write time. That path checks the lease via `_recheck_batch`. It must never reuse the view it used for preparation.
- **Test names:** name the accepted tests `test_competing_project_claims_cannot_double_charge` and `test_reservation_and_cursor_commit_together`.
- **Copy deduplication:** this rests on the unshown claim that adapter keys don't depend on the source or locator. Add the copy case to the two-hour gate.

**What passes:**
- Lease custody: `_recheck_batch` calls `registry.lease` and requires an identity match on `_batches`.
- Copied batches and observations are refused, because lookups match by identity (`is`).
- Registry equality is rechecked.
- The physical prefix is rechecked through `_capture_position`.
- The schema checks, the 0600 file permissions and `synchronous=FULL` are specified.
- Claim, pending payload and cursor roll back together.
- Grok stays held until an admitted capture proof exists.
- The slice makes no destination writes, sends no ACKs and fakes no causal proof.

## M08b split: HOLD

The cut itself is correct. Causal succession and dispositions go to the new child, which depends on #118 and blocks #119. #118 stays a direct prerequisite of #119, and rank 225 fits. The handoff between the two halves is what's missing:

**S1. Same root cause as B1.** The split says a stale or copied revision "cannot … release an existing dispute." That is only safe if M08a never commits a same-owner revision as a dispute. State that in both documents.

**S2. Data that M08a must store for M08b isn't specified.**
- M08b needs overlap queries over half-open position spans and capture-epoch eligibility for claims already made.
- M08a's spec never requires storing each claim's stream key, span or epoch. It also refuses any schema it doesn't support and never repairs one.
- **Fix:** M08a stores these fields now, or the split gives M08b an explicit schema-version migration. Saying M08a stores are dormant and never created in a real account would also cover it.

**S3. Accepted test not assigned.** Assign `test_causal_revision_survives_stale_replay_after_restart` to M08b by name.

**S4. Folded-usage replacement has no producer (a known risk, not blocking).**
- No component produces the verified covering proof that folded-usage replacement needs today. M11 owns Grok admission and comes after M09.
- If M08b has to "resolve or split" this, M09's `test_folded_replacement_and_child_withdrawal_share_view` is blocked. That means either reordering the accepted plan or getting a change re-accepted.
- Say now that this outcome needs plan re-acceptance and is not a quiet re-split.

**What would flip both to PASS:**
1. B1/S1: one rule for same-owner changed content, which is held.
2. B2: source showing the prior-cursor seam, or that seam moved into the gate.
3. B3: boundaries counted as obligations.
4. S2: the per-claim span and epoch fields stored, or a migration plan.
5. The accepted test names mapped.
6. The gate rebalanced or the reopen risk accepted.
