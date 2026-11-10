<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-baca25051170651fc4512589bc73be80"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
artifact_commit: "03af51301e6de2665e7c85e759ef133d285791b6"
artifact_blob: "2a249109fba9be97f43369cb2d55961541df3927"
artifact_digest: "sha256:3549515f497a736d5cc101cb2f28aacc5c69f666936a3bdcd0d624ca1b133a07"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:1acdf73fcbb80586e286552155f58ea364355a0fa6bf788f441a1f726bf2e2ee"
  identity_source: "runtime"
started_at: "2026-11-10T16:39:35.636Z"
submitted_at: "2026-11-10T16:42:36.947Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Round 1 independent cross-provider review of
`.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md`
(artifact blob `2a249109fba9be97f43369cb2d55961541df3927`, 775 lines).

Coverage: I read the whole artifact fresh, from the exact invitation
path, in contiguous numbered Read calls of at most 40 lines each:
1–40, 41–80, 81–120, 121–160, 161–200, 201–240, 241–280, 281–320,
321–360, 361–400, 401–440, 441–480, 481–520, 521–560, 561–600,
601–640, 641–680, 681–720, 721–760 and 761–775 (EOF). No range was
abbreviated or skipped. I also ran a Grep for `probe|regression` to
confirm one finding. I read these parts of the accepted design
`.aitm/stories/001/133/design/test-impact-analysis-design.md` in
small chunks: the heading index, lines 198–235 (§4 exact-base and
coverage), 248–291 (§5), 292–335 (§6 failure table), 336–422 (§6
incident and merge authority), 423–463 (§6 workspace delivery) and
464–489 (§§7–8). I grepped the design for `103|coverage`. This is
round 1, so there are no earlier author dispositions to verify.

Overall the plan is strong and closely follows the accepted design:

- **Trusted observation.** T07 is a spike that gates T08 and T09 and
  stops their descendants if the boundary fails. T22 qualifies the
  broken-base route separately.
- **#103 preservation.** The plan keeps unrounded 90% product and
  CI-helper coverage, child-process evidence, wheel and file checks,
  and full exact-base comparison (Global constraints, T13, T32).
- **Fallback and mode boundaries.** T06 never mints hosted proof,
  T14/T32 stay advisory in shadow, and T36 handles rollback.
- **Conditional merge.** T20 is a host-qualification spike and T21
  implements against it.
- **Broken-base repair.** T22, T23 and T24 cover it.
- **Health ordering.** T15/T16 rank a verified failing test above
  merge-only holds, and Unknown never counts as healthy.
- **Continuity fencing.** T17, T18, T19 and T31 cover it.
- **Workspace pause and restart barrier.** T25–T31 and T35 cover it.

The dependency edges I checked are transitively sound. T15→T13→T12
reaches T10 and T09. T22→T15/T19. T31→T30→T24/T28/T29 makes the shared
edits to `authority_io.py` and the harness adapters serial. T32→T14
does the same for `tia-shadow.yml`.

The non-authorization boundary (lines 768–774) is explicit and
correct. Plan acceptance does not open Develop, approve host
mutations, install credentials, enroll agents or cut over.

Five material issues remain:

1. T34 is beyond the four-hour leaf limit.
2. The plan defers the representative 3/6/10-minute sample matrix and
   window, which the design reserves for the plan itself.
3. T35 does not require the restart barrier to be proven across both
   supported harnesses for every enrolled roster member.
4. No leaf owns or binds the "incident regression probe" that T26,
   T29 and T30 consume.
5. The §7 selection proof cases are not enumerated as executable
   assertions.

## Findings

1. **T34 exceeds the four-implementation-agent-hour leaf limit, and
   T19 is at risk (lines 421–448, 695–716).**
   - **What T34 bundles into one 4h leaf.** Design §7 assigns four
     acceptance rows here: PR isolation, escaped defect (the blocking
     part), merge-only holds, and broken-base repair. In concrete terms
     the leaf must:
     - merge an independent PR and observe its native agent continue;
     - keep a failed PR blocked;
     - rehearse a verified escaped failure and a second verified cause;
     - rehearse coverage, inventory and evidence merge-only holds;
     - run a selected-PR-then-scheduled-coverage-floor-miss run and a
       separate undisposed-skip run, each recording a denied merge and
       an allowed workspace operation;
     - refuse already-green, queued and alternate update routes;
     - replay the race fixtures and reconcile an ambiguous merge;
     - run broken-base full validation;
     - make the combined full-passing repair with a conditional host
       mutation;
     - produce a full current-trunk proof.
   - **Why that cannot fit.** That is at least six or seven distinct
     hosted scheduled, repair or recovery runs. Each needs its own
     fixture setup, failure injection, binding and trace verification.
     Even with queue time excluded (line 39), the fixture authoring and
     trace binding alone is not credible inside four agent-hours.
   - **Why the split matters.** The plan relies on a JIT split clause
     (lines 37–38). But an acceptance leaf this dense invites partial
     traces that get relabelled as complete, which line 766 prohibits.
   - **T19 at 3.5h.** It combines:
     - a scoped hosting-API read identity;
     - the independent freshness and missed-dispatch check;
     - qualification of a new SSH forced-command endpoint with
       identity- and generation-bound credentials;
     - a cross-clone authenticated request;
     - merge-identity separation;
     - authentication of owner appointments and repair binding;
     - activation pinning and drift refusal;
     - the `require_current_authority` live gate.

     That is also beyond a credible 3.5h for one TDD leaf.

2. **The plan does not fix the representative 3/6/10-minute sample
   matrix and window (lines 53–56, 672–693).**
   - **What the design requires.** §5 item 3 says "The plan sets the
     sample window and representative test set before taking
     measurements". §8 reserves "the sample window" for this plan.
   - **What the plan does instead.** T33 delegates the job: "Pin the
     candidate matrix, cold/warm profiles, hosted-minute budget and
     sampling rule before collecting". The only window definition is
     "a proposed minimum 20 comparable runs per window". It has:
     - no window boundary (run count or calendar span);
     - no representative candidate classes;
     - no statement of which modes (serial, full-sharded, selected)
       are measured against which envelope.
   - **Cutover rule gap.** The cutover rule (lines 689–692) tests only
     "the full target at p95". It does not require the unit (<3 min)
     and integration (<6 min) envelopes to be reported per mode and
     window. So representative 3- and 6-minute evidence can be omitted
     and still meet the stated criterion.
   - **Consequence.** The acceptance evidence for timing is not
     executable as written. A reviewer of the later cutover proposal
     cannot check that the sample set was chosen before measurement
     rather than after.

3. **T35 does not prove the all-roster restart barrier across both
   supported harnesses (lines 718–734; design lines 436–437, 473–474).**
   - **What the design requires.** "Qualification must show the
     required behavior across the supported harnesses and across
     clones".
   - **What the plan provides.** T27 and T28 qualify Codex and Claude
     adapters separately. T35, the only end-to-end restart rehearsal,
     owns "two-clone rehearsal fixtures". It does not name either
     harness, and it does not require release to wait for every roster
     member.
   - **The coverage gap.** Two clones cannot cover all of these at
     once:
     - both harnesses;
     - an affected base and an earlier base (escaped-defect row);
     - a connected and a disconnected-before-notification workspace;
     - the withdrawal and invalid-conflict refusals.
   - **Consequence.** The trace that gates cutover (line 772) can show
     a release with no Claude (or no Codex) workspace ever held at the
     barrier. It can also skip proving that release is refused while
     *any* enrolled member's receipt is missing or stale.

4. **No leaf owns the incident regression probe (lines 112–113, 568,
   606–612, 629).**
   - **Where the probe is consumed.** `WorkspaceReceipt` carries
     "incident regression results". T26 runs "the incident probe". T29
     takes `probe` as an input and runs "the approved probe". T30 uses
     "the incident regression probe on effective state".
   - **What is missing.** The `Incident` record (line 112) has no probe
     field. No leaf defines how the probe is derived from the incident
     version: for example, the verified failing test IDs plus selection
     over local changes and conflict resolutions. No leaf defines who
     approves it, or how it is bound to the incident version.
   - **Consequence.** A probe that is too narrow, client-chosen, or
     stale lets a conflict resolution or local change that undoes the
     fix pass T29/T30. This is exactly the case design §6 (lines
     443–446) and the §7 "Repair and restart" row require to be
     rejected. A new incident version (a second failure) also needs to
     invalidate the old probe, and nothing binds that.

5. **The §7 selection proof cases are not executable assertions (lines
   178–207; design line 468).**
   - **What the design requires.** §7 asks for "a direct import, a
     multi-hop witness, a cross-package path, a fixture or subprocess
     declaration, a changed test, and a positively classified non-test
     change", each with the "reported path and exact selected ID"
     verified.
   - **What the plan names.** T04/T05 cover import alias, relative
     import, re-export and cycle; renamed former consumer;
     cross-package subprocess; and known edge plus unbounded reader.
   - **What is missing.** No assertion covers a multi-hop witness, a
     fixture-scope declaration, a changed test file selecting itself,
     or a positively classified non-test change, each with an
     exact-path and exact-ID check. The "Coverage and delivery
     boundary" table (line 759) maps §7 only generically to "owning
     leaf assertions".

## Required changes

1. Split T34 into separately estimated leaves of four hours or less,
   each with its own trace and dependencies. For example:
   - (a) PR isolation and escaped-defect route blocking: the
     independent merge with its agent continuing, the failed PR held,
     and refusal of already-green, queued and alternate routes;
   - (b) merge-only holds: coverage-floor miss after a selected PR,
     undisposed skip, and an evidence hold from broken scheduled setup;
   - (c) broken-base full repair, conditional mutation, ambiguous-merge
     reconciliation and the full current-trunk proof.

   Update the T35 dependencies and the coverage table to match. Either
   re-estimate T19 with an explicit breakdown that fits, or split it.
   One option is (i) the hosting-API evidence read and the independent
   freshness check, and (ii) the restricted workspace command endpoint
   plus the `require_current_authority` gate.
2. Make the plan itself pin, before any measurement:
   - the representative candidate classes for timing and selection
     (at least one each of: single-package unit-only change,
     multi-package/integration change, CI-control change that forces
     full, test-only change, and a positively classified non-test
     change);
   - the window definition (run count and/or calendar span);
   - the cold/warm profiles and the hosted-minute budget.

   Require T33 to report all three envelopes (<3 min unit, <6 min
   integration, <10 min full) per mode (serial, full-sharded,
   selected) and per window, at p50 and p95. Tie the cutover rule to
   that complete report. If the exact values must stay proposals, say
   that the plan proposes them and that changing them before
   measurement requires plan review.
3. Require T35's roster to contain at least one enrolled Codex Desktop
   session and one enrolled Claude Code session across separate clones.
   It must cover an affected base, an earlier base, and a workspace
   disconnected before notification. Add an assertion that release is
   refused while any roster member's current receipt is missing, stale,
   withdrawn or from an older incident version. Raise the clone count
   or split the leaf if that does not fit in four hours.
4. Assign ownership of the incident regression probe:
   - Add a probe field to `Incident` or `WorkspaceReceipt`.
   - Have one leaf derive and bind the probe to the incident version,
     with authority approval. T16 or T24 is the natural owner.
   - Define its minimum content: every verified failing test ID for
     the current version, plus selection or full fallback over the
     workspace's relevant local changes and conflict resolutions.
   - Make T29 and T30 consume only an authority-bound probe for the
     current incident version, and test that a stale or client-supplied
     probe is refused.
5. Add named T04/T05 assertions for the six §7 selection cases (direct
   import, multi-hop witness, cross-package path, fixture or subprocess
   declaration, changed test, positively classified non-test change).
   Each must check the exact reported witness path and the exact
   selected test ID.

## Optional suggestions

1. Rename `test_second_failure_refences_stop` (line 371). "Refences"
   reads like a typo for "references". If "re-fences" is meant,
   `test_second_failure_advances_stop_version` would be clearer.
2. Clarify T24's "Failing tests still enter workspace delivery"
   (line 537). It probably means that a failing-test incident still
   requires the workspace-update phase after recovery, unlike a
   merge-only hold.
3. Drop or justify T35's dependency on T33 (line 718). The restart
   rehearsal does not consume timing results, and the edge needlessly
   serializes the restart rehearsal behind long measurement windows.
4. Make the coverage floor in T13 (line 325) explicitly per active
   product package, as design line 218 states.
5. Name the owner of design line 407, "During a stop, defer ordinary
   delivery validation against stopped trunk". T16 or T25 are
   candidates.

## Decision

revisions-requested
