<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-a3a1defe8eb6ac6a8528330111c2b9e6"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/001/181/plan/2026-11-11-181-slice-c-implementation-plan.md"
artifact_commit: "e98693314f846365902f106d283c90617027deb9"
artifact_blob: "79fb9f55375d95915af05e3d8cadbf7d5f2fecb2"
artifact_digest: "sha256:97b2e215b210d246be130db88198367daade5a394d778932c045492249228043"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:5a9319fe0105a3d572c11ffbae8a5a4cb3d599db00e32ec33a8528528ded2583"
  identity_source: "runtime"
started_at: "2026-11-11T12:45:35.547Z"
submitted_at: "2026-11-11T12:47:09.360Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I reviewed the Slice C implementation plan at `artifact_commit` e986933 (blob 79fb9f5). I checked it against the accepted design (`design/story-timing-dashboard-design.md`), the Slice C refinement (`plan/2026-11-11-181-slice-c-refinement.md`), the #181 story acceptance criteria (`story.md`), the A/B handoff (`attachments/2026-11-10-local-dashboard-handoff.md`), the coordination record (`attachments/timing-and-usage-coordination.md`) and the #190 delivery evidence.

Verified as correct:

- **Estimate total.** 2.25 + 4 × 3.75 + 3.00 = 20.25 h.
- **AC fixture.** 900 + 1,800 + 900 s = 3,600,000 ms, which matches the story's AC example.
- **#181 rollup.** The handoff records 13,754 ms direct plus 10,591,957 ms descendant work, totaling 10,605,711 ms. Rounded to four decimals this is 2.9460 h, which matches the refinement's board readback.
- **#111 elapsed.** 774,000 ms equals 12m 54s. It matches the backfill JSON and the #190 delivery checklist.
- **Design acceptance trace.** The plan maps design acceptance items 2C, 4C, 5C and 6C onto C02, C03, C04 and C05/C06.

The plan respects ownership boundaries. It adds no parallel timing or pricing engine and no interim automatic writer. It keeps Cost independent of Actual and gives each leaf explicit runtime holds.

Three issues should be fixed before acceptance:

1. Two pinned fixture values are not bound to the pins and cutoffs that make them reproducible.
2. The design's own parallel example fixture is not among the shared acceptance fixtures.
3. Estimate calibration is bundled into the Cost leaf. This gates it on M13/M14 rather than on Actual and C44, which conflicts with the design's ownership split.

## Findings

1. **C01 fixture expectations lack their pin, cutoff and snapshot identity (reproducibility).** C01 says to "pin the existing #181 partial rollup of 10,605,711 ms and #111 scoped elapsed of 774,000 ms" but names no planning commit or as-of for either value.
   - Under the design, a snapshot value depends on the planning commit, the UTC as-of and the usage selector. Later receipts can change the #181 rollup: the branch already has commits after the final dashboard pin, and #181 remains in Develop.
   - The handoff ties 10,605,711 ms to planning pin `3a28d392ad0c5782b1898b387a4ecbc8e694ecb1`, cutoff `2026-11-11T05:33:20Z`, snapshot SHA-256 `f500e972…c510` and dashboard SHA-256 `0fad4c85…7a1b`.
   - #190 ties 774,000 ms to the historical seed pin `17761cc1928fd916cf32a9c078d4a742bfcb32b8`, snapshot `e46da189…772a` and validation `3497de8b…1ab6`, with all-phase elapsed Unknown.
   - Without these identities, a C01 executor running against a later planning head could get a different #181 total. They would then either record a wrong expected value or chase a false parity failure.
   - "Run the delivered dashboard tests from trunk" likewise names no trunk commit. The refinement pins delivered source `bc8063b66522ed3a27c95d1bb0546f1e73249612`.

2. **The design's parallel example fixture is missing from the shared acceptance fixtures (coverage gap for elapsed, wall time and owner wait parity).** The design's Slice C gate requires that "the consumers reproduce the same fixture". The design's example fixture is:
   - children A and B overlapping from 09:30 to 10:30;
   - a 30-minute owner wait;
   - direct epic coordination;
   - expected 2h 45m elapsed, 2h 15m observed working wall time and 3.25 agent-hours Actual.

   C01 pins only the story-AC additive example (3,600,000 ms). That example has no elapsed, wall-time or owner-wait expectations. It also omits the AC's own variants: adding 1,800 s of owner wait leaves 1.0 h, and extra non-overlapping in-turn tool time raises Actual with Cost unchanged. C03, C05 and C06 must all prove separate Elapsed, Owner wait and parallel working wall time across Core, board and viewer. Without a shared pinned expectation, each leaf could build its own fixture, and parity between board and viewer would not be checked against a common, design-approved expected result.

3. **Calibration is coupled to the Cost/usage gates instead of Actual and C44 (dependency/ownership defect).** C04 is titled "Bind Cost and calibration independently", and its second bullet feeds complete estimates and outcomes into calibration. C04's pickup requires "C01, M13/M14 and C44". The dependency table also says to prove M14 delivery and C44 reconciliation "before production Cost and rubric ingestion".
   - The design and coordination record split ownership differently. C44 "owns … Close outcomes, compatible usage ingestion and calibration eligibility. The rubric consumes these outcomes." Calibration pairs an estimate with Actual for the same phase, attempt, actor/role scope and basis.
   - Calibration therefore depends on qualified Actual (C02/C03) and C44 outcomes, not on M13 fenced usage or M14 export.
   - As written, this has two consequences. First, timing calibration is blocked until the full monitor publication chain (#119–#124) lands, which contradicts the refinement decision to "release automatic Actual on its own evidence and writer gates. Cost may arrive later". Second, C04's pickup omits C02/C03, even though calibration consumes their Actual.

4. **Design acceptance item 5's authentication clause has no explicit verification step (trace gap).** Design acceptance item 5 (C) ends with "No unauthenticated provider data enters story totals." C04 tests foreign-project, disputed-scope and unpriced inputs. C03 tests "unsupported sources". Neither leaf names an unauthenticated or unqualified-route provider observation as a negative case for timing or Cost totals. The stop conditions cite item 5 as a completion requirement, so the plan should carry an explicit check.

## Required changes

1. **Bind the C01 fixtures to their sources (Finding 1).** In C01, bind each pinned expectation to its exact source:
   - 10,605,711 ms (13,754 direct plus 10,591,957 descendant) at planning pin `3a28d392ad0c5782b1898b387a4ecbc8e694ecb1`, as-of `2026-11-11T05:33:20Z`, with the recorded snapshot and dashboard digests;
   - 774,000 ms #111 implementation elapsed, with all-phase Unknown, at historical pin `17761cc1928fd916cf32a9c078d4a742bfcb32b8`, with its snapshot and validation digests;
   - the trunk commit (`bc8063b…` or the then-current pin recorded at JIT) used for the starting dashboard test run.
2. **Add the design's parallel fixture (Finding 2).** Add the design example fixture to C01's shared acceptance fixtures, with expected 3.25 h Actual, 2h 45m elapsed, 2h 15m observed working wall time and 30m owner wait. Also add the story-AC variants: plus 1,800 s owner wait leaves 3,600,000 ms, and plus non-overlapping in-turn tool time increases Actual with Cost unchanged. State that C03, C05 and C06 assert against these same pinned fixtures.
3. **Decouple calibration from the Cost gates (Finding 3).** Do one of the following:
   - move calibration into its own bullet or leaf with pickup "C02/C03 for qualified Actual and C44 estimate/outcome contracts", independent of M13/M14; or
   - keep it in C04 but state explicitly that the calibration step requires only C02/C03 plus C44, and is not held by M13/M14.

   Then update the dependency-table wording "before production Cost and rubric ingestion" so that only Cost is gated on M14. Rubric ingestion should depend on C44 outcomes. Adjust estimates if work moves.
4. **Add the unauthenticated-data negative case (Finding 4).** In C03 and C04, or in the C01 shared fixtures, add a negative case: an unauthenticated or unqualified-route provider observation must not enter Actual or Cost totals and must surface as a coverage gap.

## Optional suggestions

1. **Rounding.** C05 says Actual is "rounded once to four decimal hours". Name the rounding mode (for example half-up on the exact integer milliseconds). Also state the precision and rounding for the new Elapsed and Owner wait calendar-hours fields, so board readback comparisons are deterministic.
2. **New board fields.** C05 should state that the new Elapsed and Owner wait Project fields, and their coverage fields, are provisioned under M2 field authority. Readback should also verify field existence and type on the disposable and production projects, not just values.
3. **Epic elapsed endpoints.** C03 could call out the design rule that an epic's elapsed uses its own evidenced kickoff and verified finish, and that descendant starts are not substitutes. The parallel fixture would then exercise it.
4. **C05 pickup wording.** "C02/C03 for historical/native Actual" reads as either or both. Clarify that C05 may qualify historical Actual after C02 alone and native Actual after C03.
5. **Master-plan link range.** The plan links the master plan at `#L40-L53`, while the refinement cites `#L37-L53` for the same M2/M6 status. Align the two if the earlier lines are part of the evidence.

## Decision

revisions-requested
