# #182 independent pickup review, round 2

Reviewer **Claude Opus 5.5, high**. Off-platform, exact pickup and split on November 10, 2026.

# Re-review of the revised #182 M07b pickup and M07c split

I reviewed only the packet and used no tools. I could not compute the SHA-256 values, so I accepted `f30d0b70…` (pickup) and `95511261…` (split) as given, along with the unchanged parent plan pin `8899a4d1…`.

## Verdict

- **M07b pickup (#182): PASS.**
- **M07c launcher split (#100 child): PASS.** All three conditions from the first review are now part of the pickup.

## H1–H6 dispositions

- **H1 (adoption record): fixed.**
  - The adoption check now reads one named record, `monitor-adoption-v1.json`. It is authenticated, one-way and kept in the pinned legacy ledger. It binds the project UUID, ledger key, physical identity and adoption identity.
  - **No record:** behavior stays legacy, even when the monitor registry is missing or corrupt, and a test covers that case. An invalid or substituted record is refused without mutation. A record that exists without matching monitor admission fails closed.
  - **Ownership:** M07b adds the reader and a test writer that takes the legacy lock. M16 owns the real writer under that same lock.
  - **Lock order:** the memo and receipt checks don't take a lease. The collector keeps its lease-then-lock order, and the monitor lock is never taken while the legacy lock is held. I found no deadlock cycle.
- **H2 (grant revocation race): fixed.**
  - Grant revocation, rebind and rotation, witness changes, and updates to a bound project or adoption identity all take the coordinator lease, then the monitor publication lock.
  - M16 must use the same order or cancel admission under that lock.
  - A test covers revocation winning between the producer's first selection and its locked check.
  - Grants and witnesses live outside the M06 registry schema, and tests pin the existing registry bytes.
- **H3 (retry bytes): fixed.** The seal is a fixed MAC over only the request, grant ID and generation, and protocol. It contains no witness, timestamp or randomness. A test covers a retry after a witness renewal.
- **H4 (reader capability): fixed.**
  - Witness issuance needs a capability that only the real inbox reader can create, after it verifies a sealed probe under the lease. The probe never enters the real inbox.
  - Tests try fake and foreign-writer capabilities.
  - Validity is capped at 60 seconds in UTC, with at most 5 seconds of future clock skew.
  - The pickup says plainly that this is a correctness check between processes of the same user account.
- **H5 (terminal status): fixed (option 2).** M07b reports only queued or unavailable for scope commands. M11 owns the stored terminal result, including keeping a hold distinct from a rejection and keeping the first stored result.
- **H6 (adopted legacy envelope): fixed.** The envelope carries the exact `encode_command` bytes and the verified Claude session reference, both bound to the seal. The adopted route uses monitor ordering and skips the legacy order and halt checks; M16 owns halt behavior.

**First-review items also covered:**
- The native-grammar negative cases are listed, and the receipt JSON's separators and trailing newline are pinned.
- The baseline is recorded: 748 product and CLI tests, 182 helper tests, and 9,096/9,981 product and 778/821 helper lines covered.

## M07c conditions

1. **Launcher chosen by receipt:** done. Each receipt rejects the other launcher variant, and an actual upgrade from old to new is tested.
2. **Hostile thread ID values:** done.
   - The optional assignment is generated outside `shlex.join` using quoted shell expansion, and set-but-empty stays distinct from unset.
   - Every hostile and ordinary value from the first review is listed, along with the check that other environment variables are cleared.
   - The CLI still checks the value against the project's session marker.
3. **Local only:** done. There is no production install or service change.

Dependencies and ranks are correct: M07c depends on #182 and blocks #118, the direct #117→#118 and #182→#118 links stay, and the ranks are 215, 217 and 220.

## Budget and checkpoint

- **Budget:** the buckets add up: 1.20 + 0.95 + 0.75 + 0.40 + 0.45 = 3.75 hours. It's still tight, but the first-review fixes fit within the 0.45 reserve. Reopening before 4 hours remains the real control.
- **2.25-hour checkpoint:** the arithmetic now works. The first two buckets total 2.15 hours, and every gate at the checkpoint (mixed queue, witness refusal, Claude adoption race) falls inside them. A miss now has a named action: stop and re-review splitting out the CLI and native recognizers before spending reserve.
- **Total:** M07b plus M07c comes to 5.0–5.5 hours, which is over the 4-hour cap and so confirms the split. M07c's 1.25–1.75 hours is credible.

## Carry-forward notes (not blocking)

- **Recheck on every legacy write:** the recheck under the legacy lock is written as covering "memo and command", but the only race test is for Claude. During implementation, apply the recheck to every pre-adoption legacy command write, not just Claude's, and add one non-Claude race case.
- **Conflict results:** an ID conflict or an already-terminal ID should come back as a sanitized unavailable result, since M07b has no third scope outcome.
