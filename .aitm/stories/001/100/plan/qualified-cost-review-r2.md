[20:18:10]
# PASS: Epic #100 qualified-cost R2

There are no unresolved blocking findings. All six R1 blockers are resolved, and I found no actual gate conflict.

**Integrity limit:** I only had the text you supplied, with no way to read files or compute hashes. So I have not checked any of the four SHA-256 values. I also never saw `replacement-body.md` or `sibling-body.md` as separate bytes, only the two blocks fenced inside R2. Before anyone acts on this PASS, they must:
- recompute all four digests;
- confirm both body files match the R2 fenced blocks byte for byte, using the single-final-newline rule.

## R1 blockers

| # | Status | Basis |
|---|---|---|
| B1 Supersession | Resolved | There is now an explicit supersession list covering the design matrix, source continuity, adoption and wake clauses. It covers R3 M08b6 and its graph text, including the Refine/JIT-after-delivery rule, which now points at the replacement. It also covers the carrier's parentage and prerequisite set, #135's parentage and its #129 link, the full sections NA-1, M09, M12–M14 and M17–M19, and the additions to M10, M11, M15 and M16. |
| B2 Journal schema | Resolved | The replacement now introduces `JournalChange.coverage`, `JournalCoverage` and `coverage_changes` itself, with its own record shape: `UNQUALIFIED_SOURCE`, policy generation, observed time, no expiry. #295 extends it later through discriminated decoding that stays backward-compatible. The test that needed an R3 hold is gone ("Do not assume a #295 R3 hold exists"). The overlap and held/expired wording in M09 and M13 is removed, and so is the stray "this carrier" reference. |
| B3 Allowlist ownership | Resolved | The packaged release allowlist ships empty. A separate isolated qualification profile admits only Codex or Grok, pinned to exact tuples, and cannot be imported or used to admit Claude. Private config can only narrow the allowlist. M17 rejects anything that widens it. #128 owns the macOS receipt, and #129 owns the Linux receipts and the final catalog. The replacement owns the reader, the predicates and the fail-closed gate. |
| B4 NA-1 negative case | Resolved | Each target must include an attempt to enroll a real Claude installation, a genuine transcript from that target, and a recorded exact tuple. An applicability record is allowed only for a missing mode. The validator must require the negative outcome, the observed tuple and the applicability disposition. Where historic data comes from is now defined per target. M18's undefined "Agent negative case" reference is replaced. |
| B5 #83 compatibility | Resolved | The baseline is included in the first monitor report and compatible export under the existing authority. The report uses one rate-card digest. The frozen rate card applies only to the fixed-sequence #83 export. The new M16 clause keeps Claude history in place, marks coverage after the cutoff as unavailable, refuses Claude observations and revisions after the baseline, and covers excluded-provider pending commands. |
| B6 Exact issue text | Resolved | Both bodies are fenced exactly, and the comparison rule is stated. The bodies themselves are consistent with the R2 contract. |

## Confirmations

- **Safeguards kept:** host targets (M18 macOS; M19 Linux arm64 and x86-64), provider matrix, attribution and privacy, NA-1's cross-project and hookless Grok outcomes, all other Linux gates, signed delivery, no production cutover, no Epic #2 or C01.
- **Graph matches the snapshot:**
  - #119 prerequisites: {118,199,201,202,203,209,210,replacement}.
  - #129 prerequisites: {128,134,137,replacement}.
  - #295: prerequisites {210,298}, no dependents.
  - #298: prerequisites {210}, dependents {295}.
  - #135: prerequisites {114}, no dependents.
  - Remaining open #100 children: 119–129, 134, 137 and the replacement.
  - Endpoints to stay unchanged: #100 in {101,102} and out {2}; #297 children {204,270,296}; #204 out {296}; #119 out {120,122,296}.
  - Order is safe: new edges and sibling assignments are verified before only #295→#119 and #135→#129 are removed. The old gating edges stay if anything fails.
  - There are no cycles.
- **Fixtures kept separate from qualification:** fixtures and the Claude adapter are for internal or later work only. Scratch grants never qualify a release tuple. Isolation receipts are rejected as evidence for enabling production. Container evidence is rejected. Deterministic coverage checks that every Claude version and mode is refused.
- **No code is authorized:** the replacement still needs its own Refine, JIT, Test, Review, delivery and Close. Any split outside the listed seams needs separate acceptance.

## Non-blocking notes

1. **`cursor_for` correction:** R2 says trunk already has `cursor_for`. My R1 statement that it was missing was an inference from R3, not something I verified. The carrier's monitor-readback receipt of the "still-held public cursor" supports R2's version. JIT should confirm the exact name and path.
2. **Leftover R3 parent line:** R3 M08b6 still says "Epic #100 direct child" for #295. It isn't named in the supersession list, though the Decision section and the graph procedure clearly move #295. The note reconciling the stale references should cover #295's parentage as well as its #119 reference.
3. **Growing extent:** an excluded source that keeps growing has no defined rule for its extent. Refine should choose between one persistent open-ended record and a new record per extent, so the journal and publications can't keep churning.
4. **M15 readiness during qualification:** M15 says readiness binds to "its signed qualification". It should also say what the isolated candidate binds to during M18 and M19, which is the qualification profile.
5. **Garbled validator wording:** "a target receipt that mixes no positive and negative evidence" is awkward. It should read "lacks either positive or negative evidence".
6. **NA-1 and/or mismatch:** the minimum rule says "installation *or* transcript", but the procedure requires both. The required procedure governs, but the wording should be tightened.
7. **Missing final-state checks:** the graph procedure doesn't verify the sibling's exact child set {135,295,298}, its Project entry, or #210's final outgoing set.
