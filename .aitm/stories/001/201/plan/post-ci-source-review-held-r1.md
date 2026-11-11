# #201 independent exact source review, round one

Claude Opus 5.5, medium. Off-platform HOLD on exact head `8887c7142617014c9e3712c8b3eba22f21331cf1`, tree `eb1145db4bd3f7ab88c832c40e0ca180d335d798`, base `2eebb3b7f6b262d3ed4951ffde0cbcb5d3a5ade3`, after [signed hosted CI](https://github.com/kburson/aitm/actions/runs/42937140018/attempts/1).

# HOLD: exact candidate `8887c71` / tree `eb1145d`

I reviewed only the source in this packet, against the approved JIT `302b2220…`. I used no tools, so I couldn't recompute the diff digest or confirm the digests or CI identities. Nearly all of the plan is implemented and tested. One unplanned change to an existing path blocks the PASS.

## Blocker

**B1. The dispute check now runs before the changed-material hold, which changes an existing non-Claude path.**

- **Where:** `monitor_journal.py`, the same-owner tail of the existing reserve path, after `first = _stored_claim(...)`.
- **Before:** for the same owner, `digest != old_digest` returned **HELD** before the `disputes` lookup. A `revision != 1` same-owner observation also returned HELD at the top. So **DISPUTED** was only returned when the material was already recorded exactly.
- **Now:** the `disputes` lookup runs first. On a key with an existing dispute, these unrecorded inputs now return **DISPUTED** instead of HELD:
  - any same-owner changed digest, on any surface, including revision 1
  - any Claude revision before it reaches `_reserve_revision`
- **Why this blocks:**
  - The plan says to "preserve the current v1 first-claim and competing-owner path" and that "an apparent divergence remains held in #201", with #202 owning it.
  - DISPUTED has so far meant the material is durably accounted for. If the progress gate treats DISPUTED as settled, a divergence that was never recorded can let the cursor advance on non-Claude streams. Claude reads are less exposed because they read cold.
  - No fixture covers this. The added owner-replay assertion only covers exact first material.
- **Smallest correction:** keep the dispute check first, but return DISPUTED only for exact recorded material (`observation.revision == 1 and digest == old_digest`), and return `held` for everything else. Add one fixture: same-owner changed material on a disputed key returns `held`, with `as_of()` and `cursor_for` unchanged. Optionally, return DISPUTED for an exact whole-edge v2 match, but only after `verified_revision`.

## Verified against the plan

- **Write scope:** only the four permitted files changed. Private helpers like `_claude_revision_material`, `_capture_position` and `_ServiceEvidence` are imported and used read-only. No producer, codec, CI, destination, ACK, quota, scope disposition or runtime changes.
- **Strict schema upgrade:**
  - Fresh v2 and the migration share one `_REVISION_SCHEMA` constant, with no ALTER and no `executescript` inside the migration.
  - `_STORE` and the application ID are unchanged, and the v1 and v2 schema tuples are separate.
  - The migration runs under `BEGIN IMMEDIATE`, with v1 validation and an FK check before the DDL. It then sets `user_version=2` and repeats v2 validation and the FK check, all before the pre-commit `_check_store`.
  - Interruption and directory-replacement tests show rollback with identical bytes and storage identity, and the retry succeeds.
  - Wrong application, version, table, key or FK state is refused without modification.
  - v1 validation refuses a v2 store, and there is no downgrade path.
  - A test checks that a migrated store's schema equals a fresh v2 store's, and another checks that writes enforce FK, UNIQUE and STRICT.
  - Validation in `transaction()` still runs before the post-commit custody check.
- **Original claim:** the first claim stays immutable, and its digest is rechecked in reserve and in `as_of`. Scope, time basis, `observed_at` and every `ClaimEvidence` field are compared separately. The changed-scope fixture holds.
- **Physical custody:** `_original_capture` requires:
  - a unique enabled epoch joined on owner, source, stream, generation and boundary
  - a match on the source, locator and incarnation tuple
  - re-authentication of the epoch prefix with `fixed=historical`

  The archive fixture fails this check, replays the original and the known edge, holds the new edge, and leaves both cursors at None.
- **Whole-edge replay:** a known `(key, material)` must match the predecessor, the ordinal and `prefix_ref`. The three parametrized rewrites hold (before the original row, between edges, and the predecessor), with `as_of` unchanged.
- **v2 succession:** the predecessor must match the durable head's material and ordinal, the locator and incarnation must match, and the predecessor's fresh `prefix_ref` must equal the stored one.
- **Genesis limitation:** the v1-layout genesis needs only the exact normalized genesis material. The named fixture shows a raw rewrite after the epoch witness is accepted. This limitation still has to be recorded in the PR and the retrospective.
- **Same-read edges and `as_of`:** two edges at one sequence are ordered by `(sequence, later_ordinal)`. Only revision 3 is visible, `as_of(prior)` equals prior, claims keep first-insertion order, and the visible sequence is the revision's.
- **Restart:** an out-of-order stale replay after restart adds no rows or sequence.
- **Held cases:**
  - a singular reserve of the latest edge holds
  - the disabled intermediate holds
  - rollback on the final freshness check leaves nothing behind, and the retry succeeds
- **Earlier-cursor fixture:**
  - built from the real issued read and the journal's own progress encoding
  - the cold read still verifies both later edges
  - the only diagnostic is the quota diagnostic (`COVERAGE_GAP`), boundaries settle, the whole batch is replay or pending, and the cursor stays at the earlier value

## Follow-up notes (not blocking)

1. For genesis, explicitly assert `witness.predecessor_ordinal == original.start`. Today this depends on revision being part of the material.
2. `_original_capture` checks neither "confirmed" nor the epoch's end coverage directly. It relies on `verified_revision`'s capture chain. `epoch.position or …` relies on the object being truthy, so `is not None` would be safer.
3. Replace the control-flow `assert`s in `_reserve_revision` with explicit returns of `held`, so they survive `python -O`.
4. Stored first-claim digest checking in `as_of` and reserve is a new fail-closed rule for every surface. It's benign, but it should be recorded as an intentional hardening.
5. The open path's read transaction no longer revalidates identity after the yield. That is read-only and the upgrade revalidates, so it's harmless, but note it.
6. `foreign_key_check` runs only during the upgrade, not on a normal v2 open.

Re-review needs only the B1 diff plus its fixture, followed by a rerun of the six hosted jobs and the raw replay on the new head.
