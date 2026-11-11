# #202 independent JIT review, round 1

Claude Opus 5.5, high effort. Off-platform review of the full exact pickup. November 10, 2026 (America/Chicago).

# HOLD: #202 M08b3 JIT and private schema transition

**Digest reviewed:** `7924af3edf7b6e0411743b80bfef12e52089d5a6ec2fae08b90e6800fa7df095`

I reviewed only the packet and used no tools. The design is sound, but it has a contradictory fixture sequence, a gap that could record a fake dispute, a durable payload that isn't defined, and unclear file ownership. These have to be fixed before Develop.

## What passes

- **Four-hour cap:** 1.10 + 2.65 = 3.75 hours. The 2.25-hour checkpoint and the predeclared split are concrete and properly gated, including the rank and graph check before #202 changes. The corrections below add about 0.15 hours and still fit, with a thin margin.
- **Migration:**
  - The old v1 path runs one pinned `BEGIN IMMEDIATE`. It compares the intermediate schema to the exact v2 tuple and sets `user_version=3` once. Because `user_version` lives in the database header, it rolls back with the transaction.
  - There is no ALTER, no row rewrite and no executescript inside the upgrade. The v1→2 and v2→3 additions are separate statements.
  - Fresh v3 keeps the existing staging and custody behavior. Upgraded and fresh schemas will compare equal because the CREATE statements and their order are identical.
  - The rollback-and-retry injections for both old versions are correct.
- **Contender cannot gain authority:** the existing #201 gate (`position != original` → HELD) already blocks a different-source contender from positive succession. The plan keeps that gate and adds no owner transfer.
- **Common predecessor:** re-issuing `verified_revision(batch, witness.predecessor)` and matching the whole durable v2 edge (predecessor, material, ordinal, prefix) makes the contender an immediate, byte-authenticated child. The v1 limit is correctly fail-closed: genesis-only predecessors have no raw witness, so they stay HELD.
- **No fake reconciliation:** nothing is resolved, merged or replaced, and `PendingClaim` still shows the accepted head.
- **Release:** #203 owns disposition and release, #204 owns folding, and #119 is not released while either is open.
- **Baseline and #201 evidence:** consistent. Trunk is `5324a80`, tree is `d34be05`, #201 is Closed Completed and Done, and 970/182 tests passed.

## Mandatory corrections

1. **Fixture order contradicts itself.** Task 2 says "append authenticated r3A and stage on live", then says to present the contender "before the live child is durable." Rewrite it as:
   1. Append r3A to live without staging it.
   2. Present r3B and get HELD, with no row written.
   3. Stage r3A and get PENDING.
   4. Retry the identical r3B and get DISPUTED.

2. **Compare against every accepted state, not just the accepted child.** Today a contender is checked only against r3A. Its normalized typed usage must differ from every accepted state on the key, as of that transaction: genesis, the common predecessor, the accepted child and every later accepted descendant. Any match means HELD with no row. Otherwise a contender whose only difference is the revision number counts as a divergence, which the plan's own rule forbids. Examples are a terminal row whose usage equals r2, or a lossy archive whose r3B equals live r4A. Add RED controls for:
   - (a) a contender equal to the common predecessor's usage;
   - (b) a contender equal to a later accepted r4A;
   - (c) a qualifying dispute recorded after the head has moved past the child: the head is preserved and an r4A replay returns HELD.

3. **Archive negatives and prefix independence.**
   - An exact archive copy of r3A (same material, ordinal and prefix, different source), read before any dispute exists, must return REPLAY and write no content row.
   - A stale archive containing only r1 and r2 must write no row.
   - The positive RED must show, using the real producer, that `prefix_ref` is equal across the two physical locators. If `prefix_ref` turns out to be bound to the locator, HOLD at the 2.25-hour checkpoint for a new JIT.

4. **Carrier independence.** Require a different source ID and a distinct incarnation, meaning a different physical identity. Inequality of the locator/incarnation pair is not enough. The carrier must also differ from the source in the first claim's evidence.

5. **Precedence and return value must be explicit.**
   - The content-dispute check goes after the ownership branch and before #201's known-material REPLAY lookup.
   - A content dispute is never recorded on a key that already has any ownership dispute; the contender gets HELD. A RED proves this.
   - A different-project contender on a content-disputed key still records an ownership dispute in its own table. A RED proves this too.
   - A content DISPUTED result returns `ClaimDisposition(DISPUTED, key, owner, dispute_sequence)`.

6. **Define the durable payload exactly.** "Exact keyed normalized material" could mean the material ref or the stored usage. Because this is a permanent format, list the closed payload dataclass with exact field names and types before Develop. On read, also require that the common row and the accepted child row have `sequence ≤ dispute sequence`, and that the child's `predecessor` equals the stored common ref.

7. **"Active" is the wrong word for this schema.** `key PRIMARY KEY` with no update path allows at most one content dispute per key for the life of the store. Say that plainly, and record that #203 must add its own disposition storage. Recording a new dispute after a disposition would need #203's own schema review.

8. **Task 1 files and test mechanism.**
   - Name the exact baseline test ID and file for the existing PRAGMA-2 rollback injection.
   - List the exact files committed at the checkpoint. If that test lives in `test_monitor_journal.py`, the "two owned files" checkpoint and lane isolation conflict.
   - Say how "old v1/v2 readers fail closed on v3" is proved. For example: run the literal baseline package in a subprocess against a copy of the v3 store, then confirm the bytes are unchanged. The new code's own validator doesn't prove what old readers do.

9. **Delivery read-back.** The packet only shows #119 and #203 as live #202 edges. Also read back #204's direct #119 blocker edge before Develop and again before Close.

PASS needs a revised packet with a new digest that makes these changes.
