# #117 independent split and M07a pickup review

Claude Opus 5.5, high effort, reviewed the exact M07a pickup and split against trunk `d769b3169724eeb9ef4b4aee47d3ab4c4489072d` on November 10, 2026.

# Verdict: PASS on the #117 M07a pickup and PASS on the split

I reviewed only the packet and used no tools. I took the base, pickup and split SHA-256 values as given, because I can't recompute them from the packet. I found no blockers.

## Earlier blockers B1–B6

| Item | Status | Where |
|---|---|---|
| **B1** Adoption race | Assigned to M07b. Adoption is rechecked, and the session memo and command are published under the same legacy inbox publication lock. The race test is required. | Split, "M07b constraints" |
| **B2** "Queued" acknowledgement with nothing to consume it | Assigned to M07b. The same witness gate now covers both explicit and adopted producers; without it they return a sanitized unavailable result. The M06 drain skips scope proposals in order, without retiring them or blocking control commands. M11 publishes the outcome before a scope command is retired. | Split |
| **B3** Conflict grouping key | Fixed in M07a. The key is source, verified stream, **target native ordinal** and before-generation. Both requested tests are named. | Pickup, "Native order" and "Work" sections |
| **B4** Grok expected result | Fixed. The test asserts the marker join and both positions from the ordered M05 fixture, and routing is held for missing capture proof. M07a creates no Grok capture epoch and no Grok handoff takes effect. | Pickup |
| **B5** Signature drift | Fixed. The exact accepted signature and the `VerifiedBoundary` export are back, kept distinct from the registry's capture proof. | Pickup |
| **B6** Four-hour cap | Fixed. The work is split along the recommended line. M07a's budget is 1.25 + 0.80 + 0.55 + 0.40 + 0.50 reserve = 3.5 hours, with a concrete two-hour checkpoint and a rule to reopen before 4.0 hours. M07b gets its own Refine and JIT, and may split out the launcher. | Pickup and split |

Optional refinements R1, R3 and R4 were also absorbed: the scoped producer credential, the UUID semantics for retries versus reruns, and overflow becoming a gap plus the 1 MiB fail-closed limit. R2 and R5 were not carried forward (see items 5 and 6 below).

## Accepted obligations are preserved

- **Files and interfaces:** `monitor_scope.py`, its test file and both exact interfaces are in M07a. The `monitor_control.py` admission, the `cli.py` `monitor scope mark|handoff|dispose --request FILE` command and the launcher (the `install.py` change) are in M07b.
- **Four accepted tests:** three are in M07a's first step and `test_expired_hold_releases_no_usage` is in its second step. M07a also covers the bounded lineage and scope-span return, UTC expiry across restart, the Develop owner missing destination proof, and running green with `test_scopes.py`.
- **Holds:** anchor contradiction holds both totals, a handoff overrides only the verified stale lineage, and replay holds are bounded provenance-only with gaps.
- **Legacy and queue rules:** legacy scope and relationship receipts with idempotent queue IDs, the rule that a command cannot acknowledge a queue write without an admitted consumer, and the rule that an enqueue receipt is never proof of scope are all in M07b. M07b inherits the parent's exact M07 section and ownership.
- **Delegated owners:** M08, M09, M11, M13, M14 and M16 are unchanged in both documents.

## M07a is independently useful dormant source

It delivers a verified routing, handoff and hold engine, proved against real delivered Codex and Claude adapters and the M05 fixtures. It writes nothing to destinations or services, keeps the M06 wire bytes unchanged and doesn't depend on M07b. Its scope fits under the cap with reserve.

## The split boundary and #118 gating hold

- M07b depends on M07a. Both documents require #117 to be closed before M07b enters Develop.
- #118 is gated on both #117 and M07b, and both edges are recorded explicitly. The new child sits at rank 215.
- The missing numeric GitHub issue for M07b is acceptable as native recording pending after acceptance.

## Optional improvements (not blockers)

**For the M07a pickup:**
1. **Authority rejection test.** "Validate authority" is accepted, and the prose says an unauthorized proposal cannot create a conflict, but no RED case is named for it. Add one: an unregistered or wrong authority is rejected and produces no conflict and no hold.
2. **Name the M07b seam.** The split promises "a typed, writer-bound acceptance seam", but the pickup only exposes the two interfaces. Name the authority type or parameter that accepts the operator now and the integration grant later, so M07b extends M07a rather than reopening it.
3. **Two-hour checkpoint consequence.** State what happens if the checkpoint is missed. For example, reopen and move Develop destination proof or the Grok projection out of scope.
4. **Persisted stream identity.** Positions include the native session or stream, but "provider identifiers [stay] transient". State that the snapshot persists only keyed or derived stream and source references, such as the existing observation-key derivation. Restart and conflict grouping depend on this.
5. **Snapshot growth and clock.** Name who compacts resolved transition history, presumably M09, so the dormant 1 MiB fail-closed limit isn't a permanent dead end. Also state that a clock earlier than first-seen never extends or resets an expiry.

**Carry into the M07b JIT:**
6. **R2:** keep the accepted `--request FILE` grammar exactly, with no `--request-id` unless its source is defined, and set `allow_abbrev=False` so the recognizer and argparse accept the same input.
7. **R5:** in the launcher, distinguish an unset `CODEX_THREAD_ID` from an empty one.
8. **Named tests:** add "scope envelope ahead of a control command doesn't block it". Also list the five legacy entry points (`scope mark`, `development bind`, `scope correct`, `item alias`, `item parent`) individually instead of "the existing legacy path".

**Traceability:**
9. The pickup cites publication `be326aa…` with section hash `f2e8d78…`, while the split cites the plan hash `8899a4d…`. Record both identifiers in one place so a verifier can check them together.
