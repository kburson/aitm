[13:47:28]
AMEND_121_GROK: PASS, subject to conditions C1–C8 below, which become part of the registered leaf bodies.

**Source verification (against the supplied snippets)**

- **`_stream`** rejects any `locator._source` that is not exactly `CandidateSource`. In `prepare`, the Grok branch calls `_grok_admission`, swallows `LedgerError/OSError/ValueError`, and then reaches `_stream`. That call raises "Journal source has no verified native session". The raise happens before `cursor_for`, `read_source` or any reservation, which matches `journal_prepare: held` with the view unchanged.
- **`_source_checkpoint`** requires exactly `SourceCheckpoint`. `_read_grok` requires exactly `GrokCheckpoint`. Even past `_stream`, the cursor would be refused, so this is a second, independent block.
- **Scope:** the Grok branch of `read_source` sets `admitted = frozenset()` and `native_cursor = None`. `_eligible` also short-circuits `GROK_BUILD_MACOS` to empty. This is confirmed in the post-inventory (#326) snippet as well as at `d7552d6a`.
- **Registry:** `_native_delta` goes through `_approved_candidate` and `ProviderAdapter()`, not `_grok_reader`. That supports "frontier requires a Codex/Claude `CandidateSource`". The supplied snippet shows this only through the call path, not an explicit type check.
- **Restart:** `_read_grok` always calls `read_delta(current, None)`, so no prior Grok cursor is honoured. Restart continuity is therefore genuinely unowned today.
- **Conclusion:** the gap is real, upstream of #121, and spans storage (journal codec and cursor type) and authority (scope eligibility). #121's three wiring files cannot close it without new ownership.

**Obligation fit**

- **M11c covers the M18/M19 positive Grok outcomes:**
  - Story-bound marked turns: receipt plus owner and story proof.
  - Hookless completion counted once in its interval with no story: terminal native accounting evidence plus a physical project interval.
  - Closed exclusion of unauthorized profiles.
- **M11d covers the M09 and M11 obligations:** reserve/hold/ACK, idempotent replay, journal-only policy refusal with no ACK or cursor, and preserved codecs.
- **Grok release scope:** first-release Grok stays in scope, with no waiver, synthetic usage or simulated qualification.
- **Scope limits preserved:** the empty allowlist, #304 isolated profile, #128/#129, #137, #204, Epic #2, C01, cutover and the Claude exclusion are all unchanged.
- **Sizing:** the split is the smallest that fits the 4h caps (combined 7.25h). The file sets are disjoint and the order is strict: M11c → M11d → #121.

**Conditions**

1. **C1 – Linux surface identity.** `_read_grok` and `_eligible` hard-code `NativeSurface.GROK_BUILD_MACOS` for every Grok source.
   - M11c must carry the qualified tuple's actual surface and must never label a Linux Grok source as macOS.
   - If a Linux Grok surface value needs a file outside M11c's four files (e.g. where `NativeSurface` is defined), that triggers Stop → Refine.
   - #137 keeps carrier qualification. It does not absorb this typing.
2. **C2 – No downgrade of contradicted markers.** A marked turn whose receipt is missing, mismatched or contradicted is held or excluded. It must never fall back to hookless project-only admission. The receipt and terminal-evidence branches are type-selected, not either-satisfies. M11c tests this directly, not only M11d.
3. **C3 – Single admission proof.** `prepare` currently admits Grok twice: directly, then again inside `read_source → _read_grok`. It also swallows admission errors and falls through.
   - M11d must bind one admission proof per prepare.
   - It must remove the swallow-then-continue path.
   - It must keep the `_LiveSourceUnavailable → _record_live_exclusion` refusal path intact.
4. **C4 – Re-pin the reproduction on post-#326 trunk.** The journal snippet is from `d7552d6a`, which predates the #326 commits. M11c's start verification must rerun the controlled reproduction on the trunk that contains the #326 merge. It must record that commit and the blob IDs for `monitor_journal.py` and `monitor_scope.py`.
5. **C5 – Fix M11d's file set at Refine.** Name the exact guarded writer module(s) and the targeted journal test file. Any unnamed file, new schema or migration beyond the stated codecs triggers Stop → separately reviewed extraction.
6. **C6 – Graph integrity.** The supplied state data does not establish the status of #117 or #119.
   - Before registration, confirm their state.
   - If either is open, its rank must precede 248 or 249 respectively.
   - Confirm 248 and 249 are free and preserve rank order relative to #121 (250) and its dependents #123/#125.
7. **C7 – Disjoint from #121.** Before registration, confirm that #121's three accepted product files do not overlap M11c's or M11d's owned files. If any do overlap, that file's ownership moves upstream and #121's scope text is narrowed, not widened.
8. **C8 – Evidence boundary.** All proofs use retained fixture or isolated-issuer evidence with no repeat paid turn. M11c's restart test must show a prior `GrokCheckpoint` actually being passed to `read_delta`, replacing the current `None`.

**Registration**

- Register M11c and M11d as top-level children of Epic #100 at the proposed ranks and estimates with C1–C8 embedded.
- Add M11d as a direct prerequisite of #121.
- Leave all existing #121 prerequisites, dependents, estimate and gates unchanged.
- Each leaf keeps its own Refine, JIT, Test, source, delivery and Close gates. Neither leaf activates release or writes the allowlist.
- The owner's existing Full-Auto authorization covers this registration once this exact acceptance stands.
