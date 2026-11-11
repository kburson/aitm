# #203 independent JIT review round 1

Claude Opus 5.5 high. Reviewed plan SHA-256 `e8db4df99b88a6d4a7ff87c218b3eccb93daec7a7753076fc404b4bbc5cdf8dc` on November 10, 2026 America/Chicago.

# HOLD

I accept the overall direction of this JIT. It still needs three precise amendments before Develop, and all three are about restart, idempotency and closed shape. I did not recompute the hash `e8db4df9…`, and I used no tools.

## Assessment

| Area | Result |
| --- | --- |
| **Custody and closed shape** | Mostly sound. v1 stays byte-compatible. The v2 payload is closed. Mixed, foreign and unknown formats refuse before mutation. A reader without a writer sees only events and holds. Gaps are in B2 and B3. |
| **Proposal-only unsettled terminal** | Sound. The terminal must be a TURN, it must be the final recognized boundary, there must be no cursor, and only BOUNDARY_UNVERIFIED may be present. Nothing is appended past the prepared read. The proof records no claim that later usage is absent. The hold, view, journal and cursors stay unchanged. |
| **Typed queue provenance** | Sound. The proof reuses `ScopeInboxReader.iter_verified` under the publication lock and matches command ID, project, hold and release_previous. It stores the envelope digest. A Mark or Handoff with the same ID, revoked authorization, or different bytes all hold. The parser's receipt ID alone is not enough. The supplied probe shows the real sealed request plus the canonical stdout passing through the ordinary parser. |
| **Real tests** | Sound. They use NativeScopeFixture with monotonic timestamps and positive deltas, with no backdated or zero-delta counter. They check source, session and stream equality (binding condition 8). The genuine later-usage control is included. |
| **Scope** | Sound. Only the two named files change. Journal, frontiers, effective hold, CLI, ACK and production are excluded. |
| **Old reader** | Sound. It refuses v2 at the strict codec and leaves the file byte-identical. No production caller passes `retain_route_target`, so this slice writes no v2 in production. |
| **Bounds** | Acceptable. 3.85 hours is under the 4-hour cap, with a measurable checkpoint at 2.25 hours. The scope is broad, so the checkpoint matters. |
| **Binding condition 2** | Met for issuance. With later usage, the parser still sees the receipt, issuance and reissuance refuse, and the cursor gives no settlement authority. The JIT does not cover `require` on a proof that was already issued. See B1. |
| **Restart and idempotency** | Incomplete. See B1 and B2. |
| **Graph** | Sound. Details below. |

## Required amendments

**B1. The JIT doesn't say how `require_route_disposition` behaves after issuance.**
- As written, `require` rechecks both source prefixes. Appending later usage leaves those prefixes intact, so `require` would apparently still return the record. Fresh issuance and reissuance, by contrast, refuse once later usage exists.
- State this asymmetry exactly, either way, and test it.
- Also state and test what `require` returns after:
  - `expire()` moves the hold from HELD to GAP;
  - a legacy `dispose` changes the same hold;
  - the queue item is consumed, withdrawn or revoked.
- This is the restart and adjudication contract that M08b4c (#210) will consume, and it ties into binding condition 3.

**B2. Legacy writers on a v2 file.**
- `hold()`, `expire()` and `dispose()` currently rebuild their output with `replace(state, …)` on `_ScopeSnapshot`.
- Add REDs proving two things:
  - Each legacy writer on a v2 file keeps v2 and carries `held_route_targets` and `route_dispositions` through byte-exact.
  - A default-path write on a v1 file stays v1 and stays byte-compatible.
- Also specify what happens when `hold(retain_route_target=True)` is replayed against an existing legacy hold that has no target. It must raise, not return the old hold unchanged. "Cannot be promoted" is ambiguous here.

**B3. Which hold states admit a proposal.**
- "Currently held or expired-GAP" leaves out two GAP sources:
  - holds created as GAP at birth, because `unresolved >= _MAX_HOLDS`;
  - holds already resolved by a legacy `_Resolution`.
- Say which states admit a GAP proposal, and whether retention is allowed on a hold that is GAP at birth.
- A hold that already has a legacy `_Resolution` must refuse. Otherwise "at most one disposition per hold" counts only `route_dispositions`, and two competing dispositions could exist for one hold.

## Not blocking, but put them in the JIT

1. **Possible side effects.** `_require_boundary` ends with `return self._apply(command, receipt)`. Nothing in the supplied evidence shows whether `_apply` has side effects. Confirm that the proposal path performs no write beyond the one scope record.
2. **Lock order and imports.**
   - `verify_route_disposition(command, terminal)` takes no reader, so `monitor_scope` must build `ScopeInboxReader` and `ControlInbox` internally. Say how this avoids an import cycle with `monitor_control` within the two allowed files.
   - Say whether the inbox lock is held across the scope publication, and in what order the two are taken.
3. **The stored prefix is not a cursor.** The `prefix: SourceCursor` field records a physical position. It must never be readable as a progress or replay cursor. Add an assertion that no cursor or journal path consumes it.
4. **A known limitation to note.** Once real usage is appended, a restart can never reissue the proof. M08b4c should plan around that.
5. **Evidence not in the readback.** Recheck these before Develop, as the JIT already requires:
   - #202's Project Done status;
   - #203's Rank 228 and status;
   - whether #204 and #119 are open;
   - the diff showing the only changes between the two baselines are in `attribution.py` and its test;
   - Ruff lint output (only format output was supplied).

## Native graph: gates intact

- **#209 (M08b4b)** is blocked by #203. It blocks #210 and #119. Rank 228.1, Backlog.
- **#210 (M08b4c)** is blocked by #209. It blocks #204 and #119. Rank 228.2, Backlog.
- **#204** is blocked by #203 and #210, so the original 203 → 204 edge is kept.
- **#119** is blocked by 118, 199, 201, 202, 203, 204, 209 and 210.
- All four are direct children of #100. There is no cycle, and #202 is CLOSED/COMPLETED.

Amend B1–B3 and resubmit the exact text. Nothing else needs to reopen.
