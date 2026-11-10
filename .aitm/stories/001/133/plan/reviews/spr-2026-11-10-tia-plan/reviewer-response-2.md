---
schema: "aitm.review-response/v0"
level: "spr"
story: 133
role: "reviewer"
round: 2
artifact_path: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
artifact_base_commit: "d80a08d4eac326a9662adfb587d5a8ff5f42f790"
artifact_digest: "sha256:a19051013a8b05fb55cc4b5454404ee63001a95bb2a32d3ba218e8871d9487d8"
agent: {"host": "codex", "provider": "openai", "model_id": "gpt-6.1-sol", "effort": "high"}
role_session: "codex-collaboration:/root/tia_plan_spr"
session_identity_kind: "distinct-collaboration-participant"
started_at: "2026-11-10T16:34:44Z"
submitted_at: "2026-11-10T16:36:39Z"
start_basis: "recorded UTC bound"
finding_ids: ["SPR-04", "SPR-05", "SPR-07", "SPR-08"]
answered_finding_ids: []
---

## Summary

I read the author's round-one response and then independently retrieved all 732 numbered lines of the revised candidate without truncation. The contiguous ranges were 1–92, 93–184, 185–276 and 277–368 at 16:34:49Z, then 369–460, 461–552, 553–644 and 645–732 at 16:34:54Z on November 10, 2026. The declared raw SHA-256 matched at 16:34:44Z before retrieval and at 16:34:58Z and 16:35:51Z after retrieval. I verified the accepted design digest and rechecked its incident and workspace acceptance language. A read-only check found 35 unique leaf keys, 35 declared estimates at or below four hours, and backward-only declared dependency edges. This confirms the written graph's order. The findings below identify semantic dependencies and missing acceptance paths.

The plan retains full #103 validation during qualification and requires separate authorization for implementation and activation. The collection, control disposition, and broken-base proof now have bounded owners.

## Findings

1. **SPR-01 resolved.** T20/T21 (lines 435–473) explicitly qualify stop ordering against both unsent and ambiguous in-flight intent. An unproven host route blocks implementation, further merges remain fenced on unknown ordering, and a verified earlier commit enters the incident baseline.
2. **SPR-02 resolved.** T07–T09 and T11–T12 (lines 221–271 and 289–317) distinguish qualified complete collection, classification, assignment and observed execution. They exercise a hidden newly collected ID before assignment and refuse truncated or unverifiable collection in full and selected modes.
3. **SPR-03 resolved.** T10 (lines 273–287) owns the exact control diff and ordered trusted inventory dispositions. T14 forces full mode on a control change, T15 and T23 consume ordered dispositions, and the listed gate consumers reuse the same approval rules.
4. **SPR-04 partially resolved.** T18 owns the protected append-only witness, canonical replay and restore drill (lines 394–411). T17, however, says it cannot initialize Healthy without continuity proof from T18 (lines 378–392), while T18 declares T17 as its predecessor. T25 can issue leases with only T17 as a predecessor (lines 521–535). A complete T17/T25 delivery could either require an unavailable later implementation or accidentally treat fixture or local store state as live Healthy. Specify the closed pre-continuity behavior and the entry point where the verified witness becomes mandatory for every live allowance and dispatch.
5. **SPR-05 partially resolved.** T26–T29 own native hooks, notification and challenged effective-state observations (lines 537–595). T30 states re-observation at release and next admission, but its published entry points only acknowledge and release (lines 597–614). The earlier T25/T27/T28 paths can admit a new mutation after Healthy without invoking T30. No leaf owns the wiring between the re-observation check and that actual admission path. The positive restart trace at T34 can pass even when a workspace rolls back the fix after acknowledgment, or a new or reopened workspace presents no applicable proof. Design lines 452–461 require the actual next admission check.
6. **SPR-06 resolved.** T22 (lines 475–489) qualifies the independently pinned alternate controller and exact full repair candidate under a broken base, exercises red and missing/misattributed evidence, and blocks T23 on capability refusal.
7. **SPR-07 partially resolved.** T33 adds a passing selected PR followed by a scheduled coverage *or* unselected outcome regression and separately mentions generic inventory holds (lines 657–675). The scenario can pass without the explicit undisposed skip in an unselected test required by design line 475. PR isolation is described as other PRs remaining eligible, which can be shown without actually validating and merging an independent PR while its agent continues work, as required by design line 472. T35 owns the active-stop rollback trace (lines 694–706), but its predecessor T34 also owns recording rollback evidence (lines 688–694). The rehearsal evidence handoff runs backward unless T34 supplies only the bound starting state.
8. **SPR-08 [P1] The authority can recognize a repair request without an assigned incident owner or a singular eligible repair.** The incident record (line 112) has a repair intent but no accountable owner or eligible repair PR field. T16 folds evidence, T19 authenticates request roles, and T21 checks actor separation and the version (lines 365–376, 413–433 and 456–473). No leaf owns appointment and durable binding of the incident owner and the one eligible exact repair candidate before merge admission, or the decision that a merge-only hold needs a source/control repair. A second reviewed, full-passing PR can otherwise contend for the repair slot on the same active version even though the accountable owner designated a different PR. Design lines 304–312, 338–350 and 356–366 require these authority decisions.

## Required changes

- **SPR-04** Give T17 a closed storage seam that can be delivered independently, with no live Healthy or authority issuance before the T18 proof is connected. Identify the live gate through which T25 and merge dispatch consume verified continuity. Test attempted admission or dispatch through the normal entry points when only the store or an inconsistent witness is available.
- **SPR-05** Assign the actual adapter or endpoint that invokes T30's current-state check before a lease is issued. Keep this wiring downstream of the observation and guard producers. Rehearse a valid acknowledgment followed by a reverted effective workspace and an ordinary native mutation, then show a new or reopened workspace with a stale base is refused and an updated one can proceed.
- **SPR-07** Require separately observable coverage-floor and undisposed unselected-skip cases after selected PR validation. Record an actual independent validate/merge and continuing agent work during the isolated-PR failure case. Make T34's bound incident and roster trace the input to T35, with T35 owning the resulting rollback evidence. Split the rehearsal further at JIT if these traces exceed a four-hour leaf.
- **SPR-08** Assign authenticated appointment, durable incident/owner/PR binding and active-version admission to named leaves and interfaces. For a merge-only hold require evidence from the authorized incident owner of a trunk-source or control cause that needs a repair PR. Test that a second full-passing PR and a stale or unauthorized assignment are refused, and a verified external interruption can recover through the separately authorized diagnosis and fresh full-run path.

## Optional suggestions

None.

## Decision

Revisions requested.
