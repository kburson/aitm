---
schema: "aitm.review-response/v0"
level: "xpr"
story: 138
role: "reviewer"
round: 1
artifact_path: ".aitm/stories/001/138/design/pin-serial-baseline-design.md"
artifact_base_commit: "f7928d15ace3a4949ce67c42da37ea7371e05892"
artifact_digest: "sha256:afc748d5a3f07ecd92be59c5866af3fc919548d79f338380b750790be8dfeeb2"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  effort: "high"
reviewer_session: "sha256:2fb694d9ad80b4467c1bb5056516a998d517503f3ff8035c80ede39b6324374b"
session_identity_kind: "native-fingerprint"
started_at: "2026-11-10T18:48:09.624Z"
submitted_at: "2026-11-10T18:50:59.611Z"
start_basis: "claim"
start_source: "native/spec/2026-11-10-pin-serial-baseline-design-review-207875068d6dee69f700fcbc2b3b4131/review-207875068d6dee69f700fcbc2b3b4131-review-manifest.md#claim-claim-7ee3a258-5b1a-4329-8949-0865bee2a378"
finding_ids: []
answered_finding_ids: []
native_source: "native/spec/2026-11-10-pin-serial-baseline-design-review-207875068d6dee69f700fcbc2b3b4131/review-207875068d6dee69f700fcbc2b3b4131-reviewer-response-1.md"
native_source_digest: "sha256:6f92ed2ac6aca77db8d9d4f34a453181bbfb2a2391f4fce539257a6b5bf80929"
---

Mode: `normal`

## Summary

Cross-provider review of the #138 (T01) leaf design
`.aitm/stories/001/138/design/pin-serial-baseline-design.md` at artifact
commit `f7928d15ace3a4949ce67c42da37ea7371e05892`, round 1.

**Read coverage.** Fresh numbered reads of at most 40 lines each, using
the exact invitation path: lines 1–40, 41–80, 81–120 and 121–158. Line
158 is EOF (the last read returned 38 lines). No range was truncated.

**Sources compared.**

- Parent plan T01 section, local
  `.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md`
  lines 172–185. It matches the accepted excerpt in
  `.aitm/stories/001/138/story.md` lines 37–50 byte for byte, and the
  story's `plan-origin` pins publication `dbe0d68…`, raw SHA-256
  `ec4ee32a…` and section SHA-256 `116458af…` as cited at artifact
  lines 12–14. I also read the plan's global constraints (33–68),
  interface and verification rules (87–130) and timing recipe (132–168).
- #133 design, the sections on the baseline, coverage, timing and the
  verification table (lines 34–38, 204–221, 255–266, 470–471).
- #103 design: the verifier and coverage policy (lines 17–19, 42).
- #115 delivery checklist lines 57–85. This is the custody record cited
  at artifact line 26. The anchor `#snapshot-repair-review-checkpoint`
  resolves to the heading at line 69.
- #140 leaf design and story, to check ownership independence.

**Limits.** Shell and web access were unavailable in this session. I did
not recompute any SHA-256 and did not read GitHub run, job or artifact
metadata. The review checks internal and cross-document consistency
only. The repository's `tools/ci/` source and `policy.json` are not
present in this worktree, so I could not inspect the helper coverage
source scope directly.

**Confirmed as sound.**

- The PR evidence and the push-run evidence are distinct roles: lines
  20–34 against 35–46, and line 46 says "Keep this push proof and the PR
  proof separate even when their trees match". The PR-base outcomes are a
  separate role within the PR attempt (lines 32–33). Push mode
  deliberately lacks base and signer jobs (lines 41–42).
- Both roles are pinned to exact attempt 1. Supplied artifacts or
  timings from another attempt are refused (lines 139–141), and the
  first failing test is `test_baseline_rejects_mixed_attempts` (lines
  142–143). This matches the plan at lines 183–185.
- Timing `Unknown` rules: an `Unknown` must carry role, scope and reason
  and is distinct from zero and from an empty scope (lines 110–112). A
  missing measurement cannot fill a missing proof (lines 140–141). Cold
  and warm are defined consistently with the plan's recipe (lines 90–92
  against plan lines 149–151). The two warm samples are not presented as
  a cold comparison or as qualification (lines 112–113).
- No authority is claimed. There is no `FullProof`, observer
  qualification, merge authorization or Stop the Line (lines 82–84),
  which matches plan line 181.
- The counts reconcile with #115 line 73: 592 base identities plus 32,
  5 and 1 give 630. Product coverage 7,146/7,825 is about 91.32% and
  helper coverage 778/821 is about 94.76%, both above the unrounded 90%
  floor.
- The estimate breakdown sums to 2.5h (0.5 + 0.75 + 0.75 + 0.5) and
  stays under the plan's 4h leaf ceiling.

Four material issues remain (R1-F001 to R1-F004) and one lower-severity
contract gap (R1-F005). They concern the CI-helper inventory scope, an
archive-identity anomaly in custody, the #103 delivery boundary for new
`tools/ci/` code, a shared package path with #140, and the
trust-boundary input contract.

## Findings

**R1-F001 — High — The CI-helper per-node inventory is labeled Unknown, but the plan requires it to be pinned.**
Lines 65–69 bind only the helper test targets and the helper source
scope, and say "A separate per-node helper outcome inventory is Unknown
unless independently retained for that attempt." The plan at line 178
requires pinning "package/CI helper inventories". Its direct successor,
T02/#139, must "preserve … CI helper ownership" and "the full classified
inventory reconciles with the serial baseline" (plan lines 200–202). A
target list is not an inventory of obligations. The leaf's own rule
(lines 140–141) says Unknown is for a missing *measurement* and "cannot
fill a missing proof". An inventory is proof content, not a timing
measurement.
Failure scenario: #138 delivers a baseline with a helper target list
only. #139 then cannot reconcile the classified helper obligations, or
silently treats the target list as the inventory. The P1 justification
("direct #139 inventory prerequisite", line 154) is then not met. The
#115 record shows a 182-test helper run locally (line 67), but the leaf
does not say whether any hosted, attempt-bound evidence of those node
IDs exists.

**R1-F002 — High — The push Python archive ID is inconsistent with the PR attempt's archive custody, and the PR role pins no archive IDs.**
Line 43 binds the push run 42871778928 attempt 1 to Python archive
`13788584397`. The #115 checklist (line 71) records the PR run
42869601092 attempt 1 signed artifact as `13790255902`, archive SHA-256
`3ab42fd5…`. The push run was triggered by the merge at
2026-11-10T18:06:24Z (#115 line 79), after the PR run completed. GitHub
artifact IDs are allocated in increasing order, so an archive uploaded by
the later push run would be expected to have a larger ID than the PR
run's archive. Here it is about 1.67 million lower. Either the push
archive ID or digest is wrong, it belongs to a different run or attempt,
or the #115 record is wrong. I could not read GitHub metadata in this
session, so this is an anomaly to reconcile, not a proven error.
Separately, the PR role (lines 27–31) names only the signed *subject*
SHA-256. It does not name the provider IDs and archive SHA-256 values
for the base, Python, collector and signed archives it says to
"Require". This is less exact than the push role, even though #115
already records at least the signed archive ID and digest.
Failure scenario: the implementer binds the push role to an archive from
another run or attempt. This is exactly the cross-attempt substitution
that lines 139–140 forbid, but it would be anchored in the accepted
design.

**R1-F003 — Medium-High — The #103 delivery boundary for new `tools/ci/tia/` code is unresolved.**
Lines 128–130 recognize that `tools/ci/` additions are gate-defining.
Lines 146–148 say "The current #103 job does not collect the new leaf
test by default", and lines 127–128 put workflow and policy changes out
of scope. The design does not say whether `tools/ci/tia/baseline.py`
falls inside the #103 CI-helper coverage source scope. If it does, the
new module is measured but its test is not collected. The helper floor
at the current 778/821 lines tolerates at most about 43 newly uncovered
executable lines: 778/(821+x) ≥ 0.90 gives x ≤ 43. A projection with
envelope and refusal checks will plausibly exceed that. The #103 design
also counts unimported modules (line 42). If the module is outside the
scope, the new trust-boundary code ships with no required-gate test
execution and only a "focused run recorded separately".
Failure scenario: exact-head #103 validation for T01's own PR fails the
helper floor. The leaf has no allowed fix inside its scope, so delivery
stalls, or someone edits policy outside T01. Either way the 2.5h estimate
and the "Complete exact-head #103 validation" acceptance (lines 147–148)
are not achievable as written.

**R1-F004 — Medium — Both leaves add files under the new `tools/ci/tia/` package, but neither owns or settles how that package is imported.**
#138 owns `tools/ci/tia/baseline.py` (line 119) and #140 owns
`tools/ci/tia/snapshot.py` (line 125; #140 design line 9). Neither leaf,
nor the plan (lines 89–94), says whether `tools/ci/tia/` is an implicit
namespace package or needs `tools/ci/tia/__init__.py`. Nor does any of
them say how `tools/ci/tests/test_tia_*.py` imports it. Line 126 claims
"Neither leaf needs the other's source or proof."
Failure scenario: each leaf independently adds `tools/ci/tia/__init__.py`
(an unowned path) on its own pinned base. The second PR to land then
conflicts, or changes a file the other leaf delivered. That is an
undeclared ownership overlap, and with the gate-defining classification
it also needs its own exact-tree disposition. Alternatively one leaf
relies on the other's initializer and the independence claim fails.

**R1-F005 — Medium-Low — The canonical-JSON input contract and the Baseline record identity are incomplete.**
The plan (lines 96–100) requires "versioned canonical JSON at process
and trust boundaries" and "Reject duplicate keys, unsupported schema and
path escape before using receipts". The leaf's refusal list (lines
135–141) covers conflicting or duplicate *identifiers or digests*. It
does not cover duplicate JSON keys, an unsupported schema version on
`verified_ci103` or `timings`, or path escape in source and coverage
paths. Line 61 calls the output "a versioned comparison record" but
names neither its schema identity nor the minimum fields that #139 and
T35 consume. The leaf also does not say which existing trusted component
is "the trusted reader" (line 59). That includes who performs the
independent push-gate replay at line 45.
Failure scenario: a reader output with a duplicated `run_attempt` key is
parsed last-wins and passes the mixed-attempt check. Or a later schema
change silently changes the Baseline that #139 reconciles against.

## Required changes

1. **R1-F001.** Either pin the CI-helper per-node inventory for each role
   from attempt-bound retained evidence, naming its source, or state that
   it is a required proof whose absence blocks acceptance and triggers
   reassessment at JIT. In the latter case, define the explicit and
   labeled fallback that #139 may accept. That fallback might be an
   exact-tree local collection labeled as advisory, which would need
   parent-plan disposition. Do not label it a measurement `Unknown`.
   Update the #139 dependency statement to match.
2. **R1-F002.** Reconcile push archive `13788584397` against run
   42871778928 attempt 1 with authenticated readback (owning run, attempt
   and creation time), and correct the ID, digest or #115 reference if it
   is wrong. Pin the PR role's base, Python, collector and signed archive
   provider IDs and archive SHA-256 values at the same granularity as the
   push role. At minimum include signed artifact `13790255902` /
   `3ab42fd5…` from #115, or state explicitly that they are re-read at
   JIT and that their absence causes refusal.
3. **R1-F003.** Read the #103 policy's helper coverage source scope at
   the pinned base and state whether `tools/ci/tia/**` is inside it. State
   the expected exact-head #103 helper-floor outcome for T01's PR. Define
   the fail-closed action if the floor would fail, such as stopping for a
   parent-plan or policy disposition or splitting the leaf, rather than
   editing policy inside T01. State how the focused V(baseline) run is
   retained as delivery evidence. Adjust the estimate if the disposition
   work is not already covered.
4. **R1-F004.** Decide whether `tools/ci/tia/` is an implicit namespace
   package or has a package initializer, and how the focused tests import
   it. If an initializer is needed, assign ownership so that #138 and
   #140 can each deliver first without changing the other's paths, and
   make the matching statement consistent with the #140 design.
5. **R1-F005.** Add duplicate-key, unsupported-schema and path-escape
   refusal for `verified_ci103` and `timings`. Name the Baseline schema
   identity or version and the minimum fields that #139 consumes. Name
   the existing trusted reader or verifier component that supplies
   `verified_ci103` and performs the push-gate replay.

## Optional suggestions

1. Line 101: give the cold row its reason in the table, or in a note
   beneath it, as the leaf's own `Unknown` rule requires (lines 110–111).
   For example: no comparable cold sample exists in either attempt, and a
   cold run would be a new live experiment outside the 2.5h budget. The
   plan's first checkbox says "Retain cold and warm runs". Saying
   explicitly that no cold run is planned before JIT, together with the
   reassessment trigger at lines 155–156, will help the #139/T35
   consumers.
2. Lines 97–100: say that the lane total includes wheel smoke, so readers
   can see why 5 + 181 ≠ 187 and 3 + 111 ≠ 115 (line 104 implies this),
   and name the wall-clock source for "Python start after event".
3. Line 54: say which identities are re-read at JIT (delivery base,
   runner image, toolchain) and which stay frozen historical facts of
   the pinned pair, so a later image rotation does not look like a
   mismatch on historical records.

## Decision

revisions-requested
