---
schema: "aitm.review-response/v0"
level: "xpr"
story: 133
role: "reviewer"
round: 1
artifact_path: ".aitm/stories/001/133/design/test-impact-analysis-design.md"
artifact_base_commit: "06eb425c91e94f838942ef39baa6fa641a56ffca"
artifact_digest: "sha256:8c99b0029127336f941c5ba79baee0e26ebb2a3627a43b8397b5bab5f05307dc"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  effort: "high"
reviewer_session: "sha256:94d6b7014ee526a5269981b34d8de38170e07567d6d2a536b45e04fa57b35e99"
session_identity_kind: "native-fingerprint"
started_at: "2026-11-10T16:13:06.376Z"
submitted_at: "2026-11-10T16:15:46.326Z"
start_basis: "claim"
start_source: "native/spec/2026-11-10-test-impact-analysis-design-review-d895f6d52c2abd3dcb7ec33bd40b2bee/review-d895f6d52c2abd3dcb7ec33bd40b2bee-review-manifest.md#claim-claim-4382ea1e-9b3d-4dd9-96be-cf021787f843"
finding_ids: ["R1-F001", "R1-F002", "R1-F003"]
answered_finding_ids: []
native_source: "native/spec/2026-11-10-test-impact-analysis-design-review-d895f6d52c2abd3dcb7ec33bd40b2bee/review-d895f6d52c2abd3dcb7ec33bd40b2bee-reviewer-response-1.md"
native_source_digest: "sha256:d49fa0ce8c2b5a740362aa592f9476edc628d02d6fc7d51ab29efe8792403d5b"
---

Mode: `normal`

## Summary

Independent cross-provider round-1 review of
`.aitm/stories/001/133/design/test-impact-analysis-design.md` at blob
`ae10ab6c1a4b552be834a33b8ac7f443a707425d` (commit `06eb425`).

**Read coverage.** I retrieved the artifact in this round with fresh,
contiguous, numbered Read calls of 20 lines each, at the exact path named
in the invitation: 1-20, 21-40, 41-60, 61-80, 81-100, 101-120, 121-140,
141-160, 161-180, 181-200, 201-220, 221-240, 241-260, 261-280, 281-300,
301-320, 321-340, 341-360, 361-380, 381-400, 401-420, 421-440, 441-458.
A request for line 461 onward reported that the file has 458 lines. Every
call returned all of its lines, with none abbreviated or truncated.
Coverage is lines 1-458 of 458 (complete). This is round 1, so there is
no prior author disposition to check.

**What the design gets right.** I checked the design against the user
decisions this review must preserve, and each one is stated:

- The 3/6/10-minute budgets are at lines 249-253. Lines 255-261 define
  how they are measured, as elapsed time rather than summed time.
- An isolated PR failure blocks only that PR, and unrelated PRs and agents
  continue (lines 293-296). Acceptance evidence covers this at line 442.
- A scheduled trunk test failure blocks ordinary merges and ordinary
  governed code work (lines 298-301, 319). Merges and work stay blocked
  until three things happen, in order. First, an exact authorized repair
  candidate passes the full suite (320, 346-354). Second, repaired trunk
  passes its full suite (321-322). Third, every roster workspace has a
  verified update receipt (323, 410-432).
- A disconnected roster member holds restart (lines 418-421). Acceptance
  evidence covers this at line 444.
- The affected-only gate cutover still needs its own approval (lines
  272-278, 455-456). Full PR validation stays required until then
  (lines 45, 273-274).

The following areas are sound for a design-level specification:

- Dependency explanations: witness paths, edge kinds, base and candidate
  graphs (lines 105-120).
- Conservative uncertainty fallback, which is never narrowed to a package
  (lines 95-103, 124-143).
- Shard inventory, exact-attempt custody, and trusted-collector separation
  (lines 147-199).
- Merge-boundary authority with host-conditioned final mutation (lines
  364-391).
- Workspace roster and generation fencing (lines 395-432).

**Material issues remain.** I found three unresolved design issues. All
three are in incident and merge authority, at the edges of the state
machine:

1. The scheduled full gate can fail without a failing test, for example
   on a coverage-floor miss, an undisposed inventory change, a new skip
   or xfail, or another required check. The design does not say what
   trunk state that produces. After cutover, this is exactly where
   selected mode moves detection.
2. An evidence hold has no authorized merge path for a fix to a problem
   on trunk. The only release it defines is a passing run on unchanged
   trunk, so a defect in trunk's own source can deadlock merges.
3. With one active repair candidate per incident, and a full suite that
   candidate must pass, the design contradicts its own "eventual repair
   set" language when the incident holds more than one independent
   verified failure.

Details follow.

## Findings

### R1-F001 — Scheduled full-gate failures that are not failing tests have no defined trunk state or release path

**Where.**

- Lines 205-209: the scheduled gate compares complete outcomes with the
  last trusted baseline. This "moves detection of runtime changes in
  unselected tests to the full gate".
- Lines 217-219: the 90% line floor and the CI-helper floor apply to
  "every full gate".
- Lines 196-198: "A missing required case or an undisposed inventory
  change blocks the gate".
- Lines 298-324: the state table.

**Problem.** Section 6 defines only two kinds of scheduled-run failure:

- a verified failing test, which is a workspace-wide stop (lines 298-301,
  319); and
- missing or untrustworthy evidence, which is an evidence hold on merges
  (lines 302-303, 310-314).

The scheduled full gate can also fail with trustworthy evidence and no
failing test:

- package line coverage falls below the 90% floor;
- the CI-helper coverage floor is missed;
- a new skip, a new xfail, or a removed or deselected required case
  appears without a disposition;
- the installed-wheel smoke check or another required non-pytest check
  fails.

None of these is a "failing test", and none is missing evidence. So the
design does not say:

- whether trunk is still Healthy;
- whether ordinary merges or code work are blocked;
- who owns the repair; or
- what releases the state.

This matters most after cutover. The selected PR gate checks only
changed-line coverage of affected packages (lines 222-228) and only the
outcomes of selected tests (lines 203-205). Two things can then reach
trunk unchecked:

- A change in package A can lower coverage of unchanged code in package
  B. One way is for B's unselected tests to stop reaching B's code
  through A.
- An unselected test can start skipping.

The design states that the scheduled run is where this is caught. It
gives that run no consequence for these outcomes. An implementer could
reasonably record trunk as Healthy and keep admitting merges. That
silently gives up the full-coverage and full-inventory guarantees that
#103 enforces today.

**Required resolution.** Classify every way the scheduled full gate can
fail. For each class, define:

- its trunk state;
- whether it blocks merges, work, or both;
- who owns it; and
- what releases it.

Here is one reasonable shape. It preserves the user's decision that a
test failure triggers the full stop, and it does not widen that stop. A
non-test full-gate regression with verified evidence opens a durable
merge hold. Ordinary code work continues. The hold uses the same
exact-candidate repair authority as an incident, and a passing full run
on the repaired trunk releases it.

Add acceptance evidence for the chosen state of at least two cases:

- a coverage-floor miss caused by a change whose selected PR passed; and
- an undisposed new skip in an unselected test.

### R1-F002 — An evidence hold has no authorized merge path when its cause is on trunk

**Where.**

- Lines 302-303: an infrastructure interruption or overdue result "blocks
  ordinary trunk merges while evidence is restored".
- Lines 310-314: a failed workflow without trustworthy outcomes triggers
  an evidence hold, and missing evidence cannot establish an
  infrastructure-only diagnosis.
- Lines 341-344: a verified infrastructure-only failure recovers when "a
  new full run passes on current trunk".
- Lines 346-354: repair-candidate authority is tied to "the incident".

**Problem.** Some failures that produce no trustworthy test outcomes
come from trunk's own content, not from runner infrastructure.

Examples on trunk:

- a broken dependency lock;
- an install or setup step the full lane needs;
- a workflow or controller change that crashes before tests run;
- a pinned toolchain that has been yanked.

In each case the scheduled run produces no trustworthy outcomes. The
design then applies an evidence hold that blocks ordinary merges.

The only release the design gives is a full run passing on current
trunk (line 343). That cannot happen until trunk changes. Trunk cannot
change, for three reasons:

- ordinary merges are held;
- the repair-candidate path (lines 346-354) is defined for an incident
  with a recorded failing test, and an evidence hold is not one;
- line 344's exception clears an incident without a source PR, which
  does not help when a source change is required.

A cause on trunk can also never be verified as "infrastructure-only".

The result is a merge deadlock with no defined authority to break it.
The other path is an undocumented manual bypass, which undermines the
fenced merge authority in lines 364-391. The state table's last row
(324: "Continue diagnosis and repair or CI recovery") is written for an
open incident. It does not cover a hold that never became one.

**Required resolution.** Define the authority, scope, and proof
requirements for a source repair that lands while an evidence hold is
active. One option is a rule that an evidence hold diagnosed as caused by
trunk becomes an incident-like hold. It would use the same bound repair
candidate, exact full-suite proof, and conditional merge, but would not
pause workspaces, because no failing test has been verified. State that
a gate-defining repair still needs the independent disposition in lines
59-64.

Add acceptance evidence for one case: a scheduled run that cannot
produce outcomes because of a defect committed to trunk, recovered
through the defined path.

### R1-F003 — "One active repair candidate" plus "the full suite must pass" contradicts the "eventual repair set" when an incident has several independent failures

**Where.**

- Lines 334-338: retain each distinct verified unresolved failure, and
  "Reconcile all retained failures against the eventual repair set".
- Lines 346-348: "Bind one active repair candidate to the incident at a
  time. Its scope is the failure and its cause. Require the full suite on
  its exact proposed merge".
- Line 320: an authorized repair candidate passes the full suite.

**Problem.** Suppose an incident holds two verified failures, F1 and F2,
with independent causes. The second one may have arrived through a later
scheduled run or during workspace updates (lines 339-340). Then:

- A candidate scoped to F1 alone cannot pass the full suite, because F2
  still fails.
- "Repair set" in line 338 implies that several repairs may land in
  sequence. That needs either intermediate merges whose full suite still
  fails on known incident failures, or a rule that each repair must fix
  every retained failure.
- "Its scope is the failure and its cause" in line 347 suggests a narrow
  scope, which conflicts with the second reading.

The text supports both readings, and they lead to very different
authority:

- Reading A: one candidate must fix every retained failure and pass the
  full suite. This is consistent with the user's decision that "a full
  repair candidate passes". The repair can grow large, and its scope rule
  must allow that.
- Reading B: sequential partial repairs may merge while known incident
  failures still fail. This weakens the "full repair candidate passes"
  decision. It also needs an exact rule that the only failures allowed
  are the retained, incident-recorded test IDs, with no new failures.

An implementer choosing either reading is guessing at merge authority
during a stop.

**Required resolution.**

1. State which reading applies.
2. If it is Reading A, which is my recommendation because it follows the
   user decision as written, change line 347 to: the active candidate's
   scope covers every retained verified failure in the current incident
   version. Change line 338 to drop "repair set", or define it as the
   history of superseded candidates.
3. If it is Reading B, state that a partial repair's full suite may fail
   only on exactly the retained failure IDs of the current incident
   version. Record this as a refinement the user must approve, because it
   relaxes "full repair candidate passes".
4. Add acceptance evidence for a two-failure incident under the chosen
   rule.

## Required changes

1. **R1-F001.** Define the trunk state, blocking scope, ownership, and
   release path for scheduled full-gate failures that are not failing
   tests. These include coverage-floor misses, undisposed inventory
   changes, new skips or xfails, and failed required non-pytest checks.
   Add acceptance evidence for a coverage-floor miss after a passing
   selected PR, and for an undisposed new skip in an unselected test.
2. **R1-F002.** Define the authorized source-repair merge path, with its
   authority, scope, and proof, for an evidence hold caused by trunk's
   own content. Add acceptance evidence for a scheduled run that fails
   to produce outcomes because of a committed trunk defect and is
   recovered through that path.
3. **R1-F003.** Resolve the contradiction between one active repair
   candidate scoped to "the failure", a full suite that candidate must
   pass, and "the eventual repair set" for incidents with more than one
   independent retained failure. Add acceptance evidence for a
   two-failure incident.

## Optional suggestions

1. The user decided that a disconnected roster member holds restart, and
   lines 418-421 and 444 forbid withdrawal from satisfying that
   obligation. I do not propose changing that. However, a workspace that
   is permanently lost, such as a destroyed machine or deleted clone, then
   holds the restart barrier indefinitely, and the design says nothing
   about it. Consider stating explicitly that this is the intended
   outcome. Alternatively, reserve for a separate human decision whether
   an owner-authorized retirement could release the barrier. Such a
   retirement would revoke the workspace identity and generation, so
   lines 423-424 would still fence any re-entry. Do not adopt this
   without that separate decision.
2. Line 81 says to "fall back or block when the evidence is unfit".
   Consider rewriting it with the same rule as lines 184-186: use full
   mode when full evidence can be established, and block otherwise. Then
   the rename and deletion path reads as clearly as the selector-failure
   path.

## Decision

revisions-requested
