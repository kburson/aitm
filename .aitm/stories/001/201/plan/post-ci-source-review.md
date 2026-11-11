# #201 independent exact source review, round two

Reviewer **Claude Opus 5.5, medium**. Off-platform verdict, November 10, 2026 (America/Chicago). Signed hosted run 42938964526 attempt 1. Native GitHub review is absent.

# PASS: `ae0e3a774e242af35210e57eeee499b789214afe`

- **Head:** `ae0e3a774e242af35210e57eeee499b789214afe`
- **Tree:** `d34be057faf72d4c157c0dbf4e43003ccf40612d`
- **Literal trunk:** `2eebb3b7f6b262d3ed4951ffde0cbcb5d3a5ade3`

I reviewed only this packet and used no tools. I could not recompute the whole-diff digest `fc3269a0…`, the delta digest `12890b38…`, the archive or subject digests, or the run and job identities. I took them from the receipt as given. Within the receipt, head, tree, `reviewed_tree`, base, PR 206, target `trunk`, status `pass` and attempt 1 all agree with your current values. The raw replay shows 970 tests from a baseline of 947, no failures, and the same coverage as the receipt: product 10360/11301, helpers 778/821.

## B1 is resolved
In the same-owner tail, the new logic does three things:

- **Exact recorded first material** (`revision == 1 and digest == old_digest`) returns **DISPUTED** at `min(sequence)` if the key has a dispute, and **REPLAY** if it doesn't. This is unchanged for keys with no dispute.
- **All other material on a disputed key** returns **HELD** through the `disputed is not None` check. That includes changed revision-1 material on any surface and any Claude revision. None of it can reach `_reserve_revision`, so unrecorded divergence on a disputed key is never reported as DISPUTED.
- **Keys with no dispute** follow the same path as before: revision 1 and non-Claude surfaces return HELD, and Claude revisions go on to `_reserve_revision`.

This is exactly the smallest correction asked for. The competing-owner path, the cursor rules, `_complete`, the migration, the producer and the gate controls are untouched in this delta.

## The native RED reproduces B1
- **Setup:** the test saves the COPY prefix before turn 3 is appended. It later rewrites only the suffix to turn 3 with `checkout=A, increment=5`. That keeps the key, routes to the same owner A and changes the material. It asserts that the route is A and that the usage differs.
- **Old code:** the dispute check ran first for every same-owner observation, so this input returned DISPUTED. That matches your report of the prior-branch result.
- **New code:**
  - The rewritten material returns `held`.
  - The COPY cursor is still `None` and the LIVE cursor still equals `live.progress`.
  - `as_of()` still equals `after`.
  - The existing exact owner-replay assertion still returns `disputed`, with `as_of` unchanged.

## Non-blocking notes
1. **Possible stalled cursor:** a key that has a recorded v2 revision and later gets a dispute would now return HELD on an exact replay of that revision, not REPLAY or DISPUTED. That fails closed (the cursor stalls instead of advancing wrongly). It only matters if the competing-owner path can record a dispute on a key that already has revisions, and nothing in the packet shows that path. #202 should own it.
2. **Test coverage:** the fixture covers one variant, the archive-style rewrite on the Claude surface. Same-owner changed revision-1 material on a disputed key on a non-Claude surface goes through the same `held` return but has no test.
3. **Earlier items still open:** the follow-up notes from the prior verdict still apply. Those are the genesis ordinal assertion, the `epoch.position is not None` check, the control-flow `assert`s, and recording the stored-digest hardening and the genesis limitation in the PR and the retrospective.
