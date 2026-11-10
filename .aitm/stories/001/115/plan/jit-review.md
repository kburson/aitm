# #115 independent pickup review

Declared-manual Claude Code review. The provider reported `claude-opus-5-5`, with high effort requested. Accepted JIT SHA-256 `b9b2205d7a06cb3184eaa9ced958989a59a5e57535930b4d69e16c3b92183f07`.

## Round 1

### FAIL

The packet is mostly sound. It should not enter Develop until two fixes are made. Both are small edits to the JIT and need no new evidence or planning.

### Blocking findings

**B1. The rule for matching snapshot time contradicts the capture it relies on.**
- **JIT:** "Compare snapshot time at second precision" is one of the conditions for binding a snapshot row to a native turn.
- **Capture:** "Both snapshot end times preceded the matching native completion timestamp by about ten milliseconds."
- **Problem:** Snapshot times carry milliseconds and are consistently earlier. Truncating both and comparing for equality fails whenever the gap crosses a whole second. That would hit roughly 1 in 100 correct turns at a ~10 ms gap.
- **Consequence:** The JIT doesn't say what a time mismatch leads to. At best a correct turn gets a false "no matching snapshot" gap. At worst, when the native completion arrives before the snapshot, the mismatch counts as a "subsequent changed snapshot … disputing an earlier keyed completion". M07/M09 would then remove a correct charge that was already reported.
- **Fix:** Use an ordered window: snapshot end ≤ native completion, and native completion minus snapshot end ≤ a stated limit (for example under 1 s). Alternatively, use time as a tiebreaker, not as an identity condition. Say what a mismatch produces. Add a fixture where the two times fall either side of a second boundary.

**B2. The pricing source isn't pinned, which the plan requires.**
- **Plan:** The coverage map says "Provider, rate-card … evidence must be reconfirmed at JIT." M05 also requires "separate rate provenance".
- **JIT:** It says the docs.x.ai page "establishes exact `grok-4.7` standard input, cache-read and output rates within its published 200K threshold." It gives no rate values, no retrieval date and no content digest or snapshot.
- **Problem:** A live web page can change. The implementer could write different exact Decimal rates into the versioned resource than the ones this JIT relied on, and a reviewer can't check them.
- **Fix:** Record the three rates, the 200K threshold, the retrieval date and a digest or snapshot reference in the JIT. Alternatively, ship Grok rate classes with no public rate at all. That costs nothing in M05, because `grok-4.7-build` stays Unknown anyway; use a test-only resource for the Grok rate-class test.

### Advisories

1. **Who verifies receipts is unclear.** The JIT says "a hook record without a verified receipt is no marker" and asks for forged-marker tests. It also says "M07 owns verification of owner authority." It doesn't say where M05 gets a verification key, what signature scheme is used, or where receipts are stored and how they're read safely. Define an injected verifier interface that returns verified or unverified plus a keyed scope reference, so M05 doesn't fix a receipt format that M07 may have to change.
2. **Cursor compatibility isn't specified.** `StreamCursor` holds only `checkpoint: SourceCheckpoint`, and `SourceCheckpoint` can't change. A Grok cursor therefore makes `StreamCursor` a union of types, stored through #113's versioned persistence. The JIT requires that old observations still decode unchanged, but it doesn't say the same for cursors. Add a strict decoding requirement and a test that Codex and Claude cursors saved before #115 decode unchanged.
3. **Retained proof can stall a stream forever.** Per-turn completion and receipt proof grows with session length. Hitting the limit returns a gap and holds the stream, which is safe but never recovers. Define when proof can be dropped (for example after the snapshot corroborates the turn, or when the session closes), or accept that the stall exists.
4. **The capture didn't use tools.** Model tools, MCP and web were turned off, so turns that use tools, make several calls or start subagents were never seen. Real Grok Build turns will likely contain row types the capture didn't show. State that an unrecognised row type in the pinned version holds the stream. Expect M18 to find held or folded rows.
5. **Retroactive dispute needs a consumer.** The JIT sends keyed disputes of already-reported turns to M07/M09. Confirm their accepted plan sections actually take this as an input; the packet doesn't show them.
6. **No test that Linux stays disabled.** Add a negative test that a stream with Linux or unknown origin produces zero observations. Don't add a Linux Grok `NativeSurface` value.
7. **Unspecified outcomes.** Say what happens when a conflict "where known" can't be tied to a specific observation; I'd hold the whole batch. Also say what happens when native seconds and milliseconds disagree.
8. **Pricing envelope from whole-turn totals.** A turn total can't show each request's size. Total input including cache ≤ 200K is a safe test, because no single request can exceed the total. Otherwise the estimate stays Unknown.
9. **Monitor export.** The plan says "Grok fields enter only the versioned monitor export." The JIT tests only that the fixed legacy export is unchanged. Say whether M05 adds Grok to the versioned export or defers it.
10. **Four-hour scope.** 3.75 h leaves 0.25 h of margin for a lot of new behaviour: lineage checks, prefix integrity, retained proof, retroactive disputes, folds and around 20 test cases. The two-hour checkpoint and the reopen trigger are the right controls; expect the trigger to fire.
11. **Linux split.** The M05-LG split satisfies the plan's rule for an unavailable Linux carrier.
    - M19 now has a hard dependency on finding an authenticated Linux Grok host.
    - Consider whether M05-LG also needs a dependency on M07, for receipt authority.
    - Inserting a rank between items spaced ten apart may mean renumbering.
    - If the delivery checklist requires dependency edges before Develop, recording the child "after pickup acceptance" is too late; I couldn't check this.

### What checked out

- **Capture vs production authority:** kept correctly separate. The capture used a disposable key and an unregistered workspace; M07, M18 and M19 own real authority.
- **Fail-closed design:** missing or mismatched origin gives zero observations and no cursor advance, and a reader's OS or directory names can't prove origin. Snapshot-only rows don't charge, and equal values never bind a turn. Turns without a hook are counted in their interval without a story, which matches M19.
- **Typed compatibility:** the legacy `Provider`, `ModelLabel`, `SourceCheckpoint`, fixed export and rate digest stay unchanged.
- **Pricing:** provider-reported ticks stay separate from estimates, and Claude's cache TTL buckets are never applied to Grok.
- **Tests:** the counts (7 native, 3 pricing/export, plus the v1 decoder refusal) match the accepted M05 section.

### Limits of this review

- I used only the supplied text and ran no tools. I didn't check either SHA-256, the trunk commit, or that the accepted plan bytes are unchanged.
- I didn't see:
  - the full accepted plan; I only had M05 and an excerpt of M19, and none of M04, M07, M09 or M18
  - the manual delivery checklist itself
  - the #101 report
  - the docs.x.ai pricing page
  - board state
  - code I'd need to judge compatibility: `SourceCheckpoint`, `UsageObservation`, `TokenCounts`, `Diagnostic`, `SourceEvidence`, `pricing.py`, and #113's persistence code
- I took the capture's claims at face value. Neither I nor the packet checked the Grok native format or the executable digest.

## Round 2

### PASS

Both earlier blockers are fixed in the text, and the amendments add no material regression. Nothing blocks the exact text. I worked only from the packet. I didn't check either SHA-256, the trunk commit, the live rate page, the board or the code.

### B1. Native snapshot time: resolved

- **Matching window:** Second-precision equality is gone. The JIT now uses an ordered window: the snapshot must end at or before native completion and less than 1 s earlier, comparing true instants across a whole-second boundary. This fits the capture's ~10 ms gap.
- **What a mismatch produces:**
  - A snapshot outside the window, or with no unique native candidate, gives a corroboration gap. It never produces a dispute or a charge.
  - A dispute needs a unique candidate in the window, by time and native order, whose allowlisted fields disagree. This closes the earlier way to falsely dispute an already-reported turn.
- **Rule order:** Native completion stays authoritative and decides intervals. Snapshot ordinals and equal values alone still never bind a turn.
- **Seconds vs milliseconds:** A disagreement between native seconds and milliseconds is now defined to make the native row invalid.
- **Fixtures:** A snapshot and completion straddling a second, and an out-of-window gap, are both required.

### B2. Exact rate provenance: resolved

- **Pinned source:** The URL, retrieval date (2026-11-10) and SHA-256 `cf3234…c440` are recorded. The SHA-256 matches the packet's source digest.
- **Rates:** The rates match the table: 2.00 uncached input, 0.50 cache read, 6.00 output (USD per million tokens).
- **Threshold:** "Below 200,000" matches the source, which bills the higher rate for any prompt that reaches 200k. A whole-turn input including cache that is below 200k is a sound limit for each request inside the turn.
- **Unknown cases:** `grok-4.7-build` stays Unknown. So does positive cache creation without a rate, which the table doesn't give. The legacy file and digest are unchanged.

### Regression check: nothing material

The earlier advisories were taken up without weakening the fail-closed behaviour:
- an injected receipt verifier
- a strict cursor union with a test that pre-M05 cursors still decode
- unknown row types hold the stream
- conflicts that can't be keyed hold the batch and cursor
- stalls at the proof limit are accepted as held until a later contract releases them
- a round-trip test through the versioned codec, with M14 owning export
- a Linux refusal test

### Non-blocking clarifications

1. **Ambiguous snapshot joins:** "No unique native candidate → corroboration gap" (still charged) conflicts with "ambiguous joins … no charge" when several candidates qualify. Both readings are safe against double charging. Pick one.
2. **Invalid native rows:** Say what happens to the cursor. I'd treat an invalid row like a truncated one: hold, don't skip, so usage isn't silently dropped.
3. **Where disputes go:** M08's `record_disposition` lists scope conflict, coverage change and folded replacement. It doesn't list an accounting contradiction. Either route snapshot disputes through `reserve`'s "incomparable content becomes disputed", or note that M08 must accept this kind.
4. **What the rate digest covers:** Say which bytes the digest covers, for example the raw markdown response. Keep a snapshot if the page can't be re-fetched byte for byte.
5. **Schedule:** Expect the four-hour reopen trigger to fire. The added scope leaves 0.25 h of margin.
