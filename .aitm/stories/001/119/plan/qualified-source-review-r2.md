[05:16:40]
# HOLD

R2 fully resolves R1 findings 1, 2 and 5 and the graph-swap procedure. Findings 3 and 4 are only partly resolved, and the gaps below still block re-acceptance.

## R1 disposition

| R1 | Status | Basis |
|---|---|---|
| 1. Same-stream progress | **Resolved** | Later ordinary rows on the affected stream are held. The backlog runs from the checkpoint to the latest verified observation boundary, half-open, or ends at an explicit unknown. Expiry or retention loss records a gap and retires replay state under the existing design rule. Expiry gives no progress over the lost interval. Work resumes only at a freshly verified native boundary. |
| 2. Scope versus dependencies | **Resolved** | The new title is journal-only. Labels move to M13, the fence to M12 and exports to M14. The independent-stream test does not depend on #119. |
| 3. Fixture outcomes and contract | **Partial** | Outcomes for retry, late child, unrelated diagnostic and dual-locator are now stated, and the fixture is sanitized and allowlisted. **The contract is still missing.** See B1. |
| 4. Folded-positive location and cycle | **Partial** | M09-Folded is named, has incoming {#204, #119} and no outgoing edges, so there is no cycle. The M09 text replaces the folded test. **Its scope and creation have new gaps.** See B2 and B3. |
| 5. Export scope | **Resolved** | M14 applies to the versioned monitor export only. #83 bytes and C44 identities and payloads are preserved. M13 and M14 use the same allowlist, with no raw paths, provider IDs or sibling identity. |

## Blocking findings

**B1. M08b6 has no Files or Contract block, and its handoff to M09 has no type.**
- R1-3 asked for the contract and tests to be named the same way as the other leaves. R2 names the tests, but every other leaf also has `**Files**`, `**Contract**` signatures and a red/green/commit checklist. M08b6 has none of these.
- M08b6 says it produces a "coverage receipt for later milestones." M09 consumes "a verified journal-only Claude overlap gap" through `publication_candidate(change: JournalChange)`. Nothing says which method produces that `JournalChange`. It might extend `RoutingJournal.record_disposition(...)`, add a new method, or come from the hold record directly.
- The "publicly supported cursor readback" API is also unnamed.
- **Fix:**
  - Add Files.
  - Add the exact contract, for example the `record_disposition` variant and the coverage-record type and fields that M09 consumes.
  - Name the cursor readback API.
  - Add the red → green → commit checklist with the test files to run.

**B2. M09-Folded's scope depends on M12 and M13, but its edges don't include them.**
- It requires "exactly one **fenced** atomic publication candidate" and says "historical snapshots are immutable." `FencedPublication` is M12's output (`RecoveryFence.protect`), and snapshots belong to M13.
- Its only incoming edges are #204 and #119 (M09), and it "may proceed only after both prerequisites finish." So it either has dependencies the graph doesn't show, or it can't be satisfied when it becomes eligible.
- Because there's no ordering against M12–M14, it may also land after them. No fence, report or export test then covers atomic visibility of the folded withdrawal. The original plan got that implicitly from M09 being earlier.
- **Fix:** pick one of these:
  - **(a)** Limit it to the M09 level, as in the frozen M09: an unfenced `PublicationCandidate` that uses the actual ACK, with no snapshot claim.
  - **(b)** Add incoming edges from the M12 and M13 issues (and M14 if exports are in scope), and name the end-to-end fenced, report and export assertions.

  Either way, keep zero outgoing edges.

**B3. Creating and verifying M09-Folded isn't part of the graph procedure.**
- The swap procedure creates and verifies only M08b6.
- M09-Folded has no step that creates it or verifies its edges, and its timing relative to removing #204 → #119 isn't set. That means a wrong edge, such as Folded → #119 (a cycle) or Folded → M08b6, wouldn't be caught.
- "Recorded against the stable key before assignment" is ambiguous: "assignment" could mean the ID or the work.
- **Fix:**
  - Add a step that creates M09-Folded with the exact title as a direct child of Epic #100.
  - Verify its incoming set is exactly {#204, #119} and its outgoing set is empty. Put this either before or after the swap, but say which, and say what happens if it fails.
  - Reword the ID-recording sentence so it has one meaning.

## Non-blocking (fix with the resubmission)

- **Refusal mode:** "Native locator ambiguity as a refusal before reserve" should state that it persists the same keyed `OVERLAP_UNVERIFIED` record and bounded hold timer. Otherwise a stateless refusal could pass tests 2 and 4 while leaving that stream blocked forever, which is R1-1 again. Require tests 2 and 4 to cover both modes.
- **Unverified late child:** say what happens to a late child that can't be verified against the same stream and incarnation. It is presumably handled as a new unresolved observation under the same rules.
- **Held overlap in M13:** M13 includes held overlap coverage, but M09 names only a "gap" candidate. Say that the held state is published through the generic journal-only coverage event.

## Checks that passed

- **#119 prerequisite set:** the current set plus M08b6, minus #204, is exactly {118, 199, 201, 202, 203, 209, 210, M08b6}. That matches the supplied state; everything except #204 is closed.
- **Edge swap:** the replacement is verified before the #204 edge is removed. If verification fails, the #204 edge stays. #204's status and incoming chain (#272/#273) are checked and unchanged.
- **Parent order:** M08b6 comes after #210 and before #119. M10, M11, Grok and later ordering are unchanged. #282 and Epic #2/C01/cutover are excluded. M09-Folded doesn't depend on M11.
- **Containment:** no claim, estimated correction, ACK or cursor advance from overlap. Prior claims are preserved, and the independent stream progresses under the same writer.
- **M09 text:** the folded test is replaced with the negative control. The journal-only coverage candidate has no fabricated ACK.
- **M12–M14:** the gap is fenced before fsync. Report labels require authorized scope. Existing snapshots stay byte-for-byte unchanged. No cost adjustment comes from a gap.
- **NA-1 and M17–M19:**
  - Negative containment is checked per surface, with a recorded applicability or exclusion decision.
  - M18 replaces "folded overlap" with the negative case.
  - All other NA-1, macOS, Linux and signed-delivery gates are kept, and there is no folded-positive release claim.

To re-review, resubmit R3 with:
- the M08b6 Files, Contract and checklist;
- the M09-Folded scope and edges, using option (a) or (b) from B2;
- the M09-Folded creation and verification step.
