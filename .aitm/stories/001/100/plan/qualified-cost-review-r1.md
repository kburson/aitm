[20:13:15]
# HOLD: Epic #100 qualified-cost R1, parent-plan re-acceptance

I did not recompute the SHA-256 (`05d81bf8…e10`) because I can only read the supplied text, not the file bytes. Whoever acts on any later PASS must recompute it first.

## Checks that pass

- **Live Claude exclusion:** The text clearly excludes all Claude Code builds, including 2.1.318, ordinary, supervised and foreground Agent modes, on both macOS and Linux. Epic #2, C01 and production cutover stay excluded.
- **Matrix shape:** The non-Claude scope matches the design, and macOS Codex CLI stays the mixed-root negative case. Hookless Grok and the Linux gates are kept.
- **Final graph sets:** The planned sets match the snapshot. #119 goes from {…,210,295} to {…,210,replacement}, and #129 from {128,134,135,137} to {128,134,137,replacement}. #295, #298 and #135 keep their incoming edges, and the remaining open child list reconciles.
- **Graph order:** New edges are added before old ones are removed, and the old gating edges are kept if any step fails.
- **Downstream separation:** The replacement only writes to the journal. #119 (M09) turns the change into a publication candidate without an ACK, M12 fences it, and M13 and M14 report and export it under their existing gates.
- **Unrelated scope:** #297, #204, #296 and #282 are preserved, and so are the hookless Grok, cross-project and privacy NA-1 outcomes.

## Blocking findings

**B1. Superseded clauses are not named, so contradicting text stays in force.**
R1 says "Unspecified safeguards stay in force" but never lists what it replaces. These accepted clauses still conflict with R1's graph:
- **R3:** M08b6 (#295) is a "direct Epic #100 child" that "Blocks #119".
- **R3:** "#119 starts its own independent Refine and JIT only after verified delivery of the replacement". The replacement it means is #295.
- **Carrier amendment:** the carrier (#298) "directly belongs to Epic #100", "#295 blocks only #119", and "#119's direct prerequisite set remains {118,199,201,202,203,209,210,295}".
- **R3 milestone sections:** NA-1, M09, M12, M13, M14, M17, M18 and M19.

Fix: add a supersession list in the same form the #297 amendment used.

**B2. The replacement depends on the journal schema that #295 was supposed to build, and #295 is now out of the release.**
In R3, #295 adds `JournalChange.coverage`, `JournalCoverage`, `coverage_changes`, `expire_coverage` and `cursor_for`. #210 came before it, so none of these exist on trunk. Four specific problems follow:
- **Wording:** R1 says the replacement "adds" `UNQUALIFIED_SOURCE` to R3's field. In fact it would have to create the field.
- **Record shape:** R1's exclusion record has policy generation, observed time and no expiry, and lasts "while retained and current". R3's `JournalCoverage` has a held/gap state and a bounded expiry.
- **Test that can't run:** `test_unqualified_source_gap_replays…` requires an "existing R3 held interval" to stay replayable. That cannot exist in this release.
- **Text with no source:** M09's "existing overlap hold/gap" and M13's "held/expired overlap coverage" have no producer in the first release. M09 also keeps "Later support of this carrier requires M09-Folded", where "this carrier" no longer has a clear meaning.

Fix: say the replacement introduces the smallest coverage field and readback it needs, with its own record shape. State how #295 later extends it. Remove the R3-hold test clause or make it conditional. Make the M09 and M13 overlap wording independent of the reason code, or move it to the sibling epic.

**B3. Who owns the allowlist, and how it gets filled, is undefined.**
- **Circular gate:** "The allowlist is empty until those existing release qualifications pass." But M17, M18 and M19 need sources admitted before they can produce the receipts that fill it.
- **Bypass risk:** "Private qualification policy or package allowlist" leaves room for a user-editable file that could enable Claude without the review R1 requires.
- **No owner:** no story owns writing receipts into the allowlist, and its relationship to each adapter's existing qualified matrix isn't stated.

Fix: ship the allowlist in the package and bind it to receipts. Limit admission during qualification to the isolated candidate. Let private config only narrow the allowlist, never widen it. Name the owning story.

**B4. The amended NA-1 negative Claude case can't be checked exactly, so the receipt validators can't enforce it.**
- **Conditional input:** "including the unsupported Claude carrier when observed" makes the outcome optional. R3's rule to record and verify an applicability decision was dropped.
- **Contradiction:** "unauthorized Claude installation … belonging to the approved disposable source scenario". If the installation is unapproved, the new policy refusal is never actually tested.
- **Impossible on Linux:** "retained authorized historic usage" can't be produced on the Linux targets.
- **Undefined reference:** M18 still names "the unsupported Claude Agent negative case from amended NA-1", which R1 never defines.

Fix: list the required excluded inputs for each target, such as an attempt to approve a real Claude install of a recorded exact build and genuine transcript input. Where an input isn't available, require a verified applicability record. Define where historic usage comes from on each target.

**B5. #83 compatibility weakens existing requirements and leaves out M16.**
- **"May" versus "include":** "An independently authorized legacy #83 baseline may be displayed" conflicts with the design's "Include that baseline in the first monitor report and compatible export" and with M13 "Expose the legacy baseline". The new authority it adds is undefined.
- **Two rate cards in one report:** showing the baseline at the frozen rate card conflicts with M13's snapshot token, which binds a single rate-card digest. Under the design, the frozen rate card applies only to the fixed-sequence #83 export.
- **M16 missing:** the design's "Resume existing streams at verified continuity" and M09's late-legacy-revision path are changed by "no … late Claude revisions", but M16 isn't in the list of affected clauses.

Fix: keep including the baseline under the existing gates. Limit the frozen rate card to the #83 export. Add an M16 clause: adopted Claude streams can still be read but stay frozen, coverage after the cutoff is unavailable, and late revisions are refused with a coverage indication.

**B6. The issue text to read back exactly is not defined.**
The procedure says "verify … exact issue text", but R1 doesn't say which bytes form the replacement's issue body. The sibling epic's body isn't specified at all.

## Non-blocking notes

- **Stale issue bodies:** moving #135 and #295 "intact" leaves body text that says "prerequisite of #129" and "Blocks #119". The "reconcile planning" record should log this mismatch.
- **Snapshot gaps:** the snapshot omits #204's outgoing edges (expected {296}) and #297's children. #119's outgoing set {120,122,296} is in the snapshot but isn't listed among the endpoints to keep unchanged. Listing all of these would make the readback exact.
- **M11 line:** "M11 owns operational scheduler continuation" gives M11 a duty but no edit or test.

As stated, this acceptance does not authorize any code. The replacement still needs its own independent Refine/JIT and the existing delivery gates.
