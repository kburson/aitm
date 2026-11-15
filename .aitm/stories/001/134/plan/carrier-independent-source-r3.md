[10:49:32]
SOURCE_134: PASS. The invalid-frame case from R2 item 9 holds in both the cold and resumed variants, and nothing else is open.

I could only read the packet you supplied; this session had no shell or file tools, so I couldn't read the repository or run anything.

## R2 item 9: closed

- **Mid-stream invalid row:** the scanner gives a rejected row no `SourceFrame`. That leaves a gap in the ordinals, so the next accepted frame fails `frame.ordinal != self.ordinal + 1` in `step` and calls `retain_linux_gap`. The gap is set only once and stays set, and nothing clears it. When `turn_start` later overwrites `linux_unsettled`, it has no effect, because `linux_frontier` prefers `linux_gap`. So the scenario I raised in R2 can't happen when the invalid row is followed by a later frame.
- **Invalid ordinals after the last frame:** only the diagnostic tail in `committed()` handles these, because of its `entry.ordinal > self.ordinal` filter. It sets `linux_unsettled`, so the checkpoint is withheld. The next read starts again from the old cursor, sees the same row as a mid-stream gap, and makes it sticky. My R2 concern needed the tail branch to run before a later `turn_start` in the same walk, and the filter rules that out.
- **Cold test:** `rows[:22]`, then the malformed line, then the rest of the fixture, read by a fresh adapter. Result: `cursor is None`, no observations, and `MALFORMED_USAGE` is reported.
- **Resumed test:** a cursor was set after `rows[:22]`. Reading with only the malformed tail keeps that cursor, gives no observations and reports `MALFORMED_USAGE`. After the rest is appended, a cold restart still returns the same cursor with no observations.
- **Repaired controls:** for both variants, rewriting the clean fixture moves the cursor and produces the observation at ordinal 29. That shows the malformed row alone causes the hold.

## R2 weak spots: addressed

- The alias test now asserts `provider_checkpoint.client_version is pin` under the patched normalizer.
- `withholds_unpaired_marker` now asserts that no `UNSUPPORTED_FORMAT` diagnostic is reported.

## Production, hosted run and replay

- **Production code unchanged since R2:** `prior-production.diff` and `confirmation-production.diff` have the same hash, `64c39349…`. This round only changed tests.
- **Pinned files:** all six pinned files are identical at `4cfb4181` and at base `ab9db800`. The gate, lock, observer, policy and verifier match before and after; only the #319 workflow file changed.
- **Hosted run:** passed on head `91fd5583`, tested merge `12cdcfe6`. Its tree `eaecc1b6` matches the reviewed tree. The local locked run passed 1352 tests.
- **Private cold replay:** `source_commit` and `source_tree` match the head. The archived and reopened prefixes match (`5b7b06b3…`), and the line boundaries are complete. The marked response is 20836 tokens. After restart there is one ordinary observation, none replayed, and the keyed checkpoint is stable. `qualifies_live_cursor` is false and the sanitized fixture hash is `a63358dc…`. The raw capture hashes are recorded as provenance only.

## Notes (not blocking)

- **No red run, as expected:** production didn't change, so the new tests passed on their first run (`first-test.log`: 2 passed). They confirm existing behaviour rather than drive a fix.
- **Gap ordinal:** the gap is recorded at the next frame's ordinal (23), not at the malformed row (22). This doesn't matter while the checkpoint is withheld. #129 should keep it in mind if it uses the capture-fence position.
- **Malformed first line:** with no earlier cursor, the gap check can't fire for a bad ordinal 0. I expect classification refuses that file anyway, because the Linux carrier is classified from the first-ordinal `session_meta`.
- **Permanent hold:** once a file records a gap, its cursor never moves again. That is consistent with `qualifies_live_cursor: false`, and #129 needs to know.

The existing #129 release host gates stay in force.
