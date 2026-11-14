[07:10:46]
# PASS: Epic #100 qualified-source release amendment R3

**Digest:** `75d073bda40f545f53f0dac6429dca571875592b864f72a37d17509698d0fd3c`

I independently re-accept these exact R3 bytes as an amendment to the frozen Epic #100 plan and the #199 M08b5 split. I checked them against the R1 and R2 findings, the frozen context, the #272 findings and the supplied live graph. I did not fetch any other evidence. This acceptance covers work scope and plan only. Refine and JIT for M08b6, #119 and M09-Folded must each pass independently.

## R2 disposition

| R2 | Status | Basis |
|---|---|---|
| **B1.** M08b6 Files, Contract and the typed handoff | **Resolved** | **Files:** names the journal, scope and registry modules, the journal tests and an allowlisted fixture.<br>**Contract:** keeps `prepare` and `reserve_batch`, adds `JournalChange.coverage: JournalCoverage \| None` (mutually exclusive with disposition), and defines the `JournalCoverage` fields.<br>**Producers:** coverage changes come only from the authenticated prepare path and `expire_coverage()`. No caller assertion can create or settle one.<br>**Handoff:** M09 reads changes through `coverage_changes(after_sequence)` and turns them into candidates with the existing `publication_candidate(change)`, after checking change identity and sequence.<br>**Cursor:** `cursor_for` is named. Coverage has its own sequence and cannot move the cursor.<br>**Checklist:** red on literal trunk, then green with the three test files and locked lint, then commit. |
| **B2.** M09-Folded scope against its edges | **Resolved (option a)** | It stops at the M09 candidate boundary: an actual destination ACK and one atomic M09 `PublicationCandidate`. It makes no fence or snapshot claim. Fencing, reports and exports are left to a future carrier qualification, which must pass before any support claim. |
| **B3.** M09-Folded creation and verification | **Resolved** | The procedure creates it as a direct Epic #100 child with the exact title and records its number against the stable key. It verifies incoming = {#204, #119} and zero outgoing edges by native readback. All of this happens after the M08b6 edge is verified and before the #204 edge is removed. If any step fails, #204 → #119 is kept and the swap stops. |
| Non-blocking: refusal mode | **Resolved** | A refusal keeps the same keyed hold and timer. Tests 2 and 4 cover both modes. |
| Non-blocking: unverified late child | **Resolved** | It stays independently unresolved, has zero charges and cannot change the existing interval. |
| Non-blocking: held state in M09 | **Resolved** | M09 can publish both held and expired journal-only changes. |

## Acceptance checks

**Substantive acceptance**
- The first release covers independently qualified provider, version and platform combinations. The Claude Agent overlap is explicit partial coverage.
- Overlap creates no usage claim, estimated correction, ACK or cursor advance. Prior claims are kept.
- The affected stream holds at its last verified checkpoint. The backlog is half-open, or ends at an explicit unknown.
- Expiry or retention loss records a gap and retires the replay state, with no progress over the lost interval. Work resumes only at a fresh native boundary under current authority.
- An independent stream still reaches its own route.

**Existing gates**
- The evidence requirements for consent, scope, ownership, single-charge accounting, destination ACK, privacy, qualification and release are preserved.
- In M09, only the folded sentence and the folded test are replaced.
- M12, M13, M14 and M17–M19 are additive. #83 bytes and C44 identities and payloads are unchanged.
- The amendment excludes Epic #2, C01 and cutover, and #282 has no release dependency.

**Graph swap**
- After the swap, #119's prerequisites are exactly {118, 199, 201, 202, 203, 209, 210, M08b6}. That is the live set minus #204 plus M08b6. Everything except #204 is closed.
- #204 status and its incoming set {203, 210, 270} are checked as unchanged.
- The procedure reads back both new issues and both dependency sets after the swap.
- The edges form no cycle.
- #119's Refine and JIT start only after M08b6 is delivered.
- M10, M11, Grok and all later ordering are intact.

**#204 scope**
- #204 keeps original-owner proof, child membership, terminal closure, accounting inclusion and folded intent. This matches the frozen M08b5 exit clause, now that a changed parent plan has been re-accepted.

**Downstream qualification**
- Each stage has its own named test or receipt requirement:
  - M12: fsync fence on the coverage gap.
  - M13: partial status without rewriting the previous snapshot.
  - M14: gap appears only as versioned monitor metadata.
  - M17: deterministic NA-1 isolation.
  - M18 and M19: per-target exact-build containment evidence, or a verified applicability/exclusion decision.
- No release claims a folded positive.

## Non-blocking notes for Refine/JIT

1. **M08b6 JIT:**
   - Confirm that `prepare` and `reserve_batch`, which R3 says to "Keep", exist on trunk. The supplied frozen excerpt shows only `reserve(candidate, progress)`.
   - Make sure the `JournalCoverage` field matches any coverage representation that M08b4 already records through `record_disposition`.
2. **M08b6 tests:** have tests 2 and 4 read `coverage_changes()` explicitly. That shows M08b6 delivers the reader that M09 consumes, including its exact sequence after reopen.
3. **Unknown-range refusal:** make sure the "broader coverage indication with unknown range" also follows the bounded expiry rule, so a stream whose identity can't be verified cannot stay blocked forever.
4. **M09-Folded Refine:** read "withdraws only the proven child" as the exact proven child set, consistent with M08b5's "all proven children".
5. **Graph execution:** "Then remove only the direct #204 edge" appears before the M09-Folded step, which is explicitly ordered "before removing the #204 edge". Run M08b6 create and verify, then M09-Folded create and verify, then re-check the #119 set, then remove #204 → #119, then read back.
6. **Board entry:** consider giving M09-Folded the same board-entry check as M08b6.
7. **M09 test name:** `test_unqualified_claude_overlap_publishes_gap_without_project_write_or_ack` should also cover the held state.
