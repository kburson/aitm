# #133 Merge-only Stop the Line implementation plan amendment

**Goal** Keep routine agent work and non-default branch integration
moving through a trunk incident, with one GitHub flag and a
host-enforced repair-only trunk exception.

**Spec** [Merge-only design amendment](../design/2026-11-11-133-merge-only-stop-the-line-design.md).
Read it with the [exact accepted baseline](test-impact-analysis-implementation-plan.md).
This amendment supersedes overlapping behavior and acceptance tests
for future pickup. The previously reviewed bytes and live issue
dependency graph are retained while affected leaves are replanned.

## Delivery sequence

1. **Authenticate full trunk health and publish one state.** Revise
   T15–T20 (#152–#157). Schedule the full suite every four to six
   hours. A six-hour off-hour slot is the proposed starting schedule.
   Pin the workflow, deadlines and tested SHA in reviewed policy.
   Use the existing scheduled evidence, incident reducer, durable
   intent and continuity seams to publish the protected GitHub flag.
   Restrict publication to the trusted authority. The continuity
   witness remains evidence for restore and in-flight recovery.
   Retarget authority reads to trunk PR promotion and merge. Remove
   workspace mutation and lease requirements from this feature.
   Test early failure, incomplete, duplicate, older and newer
   evidence, missing schedule, stale reads, and concurrent repair
   claims. Verify ordinary feature pushes and CI stay available.
2. **Qualify cloud enforcement.** T21 (#158) follows the
   [same-repo qualification plan](../../158/plan/2026-11-11-158-merge-only-qualification.md).
   Require an exact-base/head/tree mutation, one permitted writer
   route, refusal for ordinary trunk updates while held, and causal
   ordering of any already-sent merge with the GitHub flag.
   Use fixture evidence for CI and incident transitions in T21.
   Hosted GitHub writes must be real. Integrated CI, repair, and
   restart qualification follows in T36–T40. A receipt qualifies the
   route only after real hosted evidence and independent review.
   Keep T22 (#159) blocked on both #157
   and #158 until its own pickup prerequisites pass.
3. **Bind a repair and release on repaired trunk.** After qualified
   dependencies, revise T22–T25 (#159–#162). Preserve the exact
   repair candidate, independent review, full candidate proof, and
   trusted validation path for a broken base. Allow only the bound
   repair while held. Merge it through the qualified route and
   dispatch the full suite on the confirmed result. Replace the
   workspace-update transition with a conditional release of the
   same flag after a complete green result for current repaired
   trunk and current incident. Retain the exact reviewed,
   full-passing already-landed fix recognition for delayed failures.
   Its causal proof and a fresh full pass on current trunk are
   required. Hold on a stale success, partial repair, second
   unresolved cause, or ambiguous host response.
4. **Run and verify post-release PR CI.** T34 (#171) owns the
   trusted hosted validation entry point and release generation
   attestation, using a fixture flag in shadow. Preserve PR head
   synchronization triggers. Exercise an exact-PR redispatch when
   the head is already current, and refresh validation on a base
   retarget. The dispatcher resolves the live PR, target, head, base
   and flag itself, and binds the new run to that generation at
   admission. T22 checks that proof before merge. Repurpose T39
   (#176) to prove the flow on real hosted CI. Reject old green
   checks, including same-tuple runs admitted before release that
   finish afterward. Deny stale ancestry, a trunk advance after
   new CI, and a trunk retarget with only epic evidence. An offline
   workspace has no effect on reopening or another refreshed PR.
5. **Rehearse isolation, recovery, and rollback.** Revise T36–T38
   and T40–T41 (#173–#175 and #177–#178). In one hosted trace,
   produce a genuine scheduled failure, continue pushes and
   feature-to-epic merges, deny a ready ordinary trunk PR, admit
   the single repair, and release only on a fresh full pass of
   repaired trunk. Keep separate negative-evidence and
   infrastructure scenarios. Show that switching validation
   back to full keeps a live merge hold and pending intents.
   Keep the #103 gate throughout shadow and qualification.
   T14/T34–T35 shadow, coverage, and timing qualifications still
   govern selected-mode cutover.

## Scope and dependency reconciliation

| Accepted baseline area | Effect on pickup |
| --- | --- |
| T26–T33 (#163–#170) | Workspace probe, enrollment, native pause, effective-working-tree receipts and all-workspace acknowledgment are superseded for Stop the Line. Hold pickup under the old scope. Review any independently justified reuse separately. |
| T36, T37 and T39 (#173, #174, #176) | Old T33 dependencies are tied to the superseded workspace design. Replan the named host and PR-refresh evidence and reconcile those native edges before picking up these leaves. T39 still consumes T38's exact repair trace. |
| T41 (#178) | Consume the revised T39 PR refresh and release rehearsal, with T35 and T40 evidence. Keep incident and unresolved intents across rollback. |
| Existing unrelated TIA and CI stories | Their accepted scopes, ranking, delivery evidence and dependencies remain applicable. |

The current estimates and native edges are historical until affected
leaves are individually rebaselined. This amendment sets future
planning direction. It grants no implementation, app installation,
protection change, or live gate cutover authority.
