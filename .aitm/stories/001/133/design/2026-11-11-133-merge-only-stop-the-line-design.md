# #133 Merge-only Stop the Line design amendment

The owner directed this policy change. It replaces the workspace pause
and all-workspace restart barrier in §6 and the related acceptance
cases in §7 of the [previously accepted design](test-impact-analysis-design.md).
The exact accepted baseline and its reviews remain available for
provenance. This amendment and its [delivery plan](../plan/2026-11-11-133-merge-only-stop-the-line.md)
are for team review before changed leaf implementation or cutover.

## Scope

Stop the Line governs updates to AITM's protected default branch
`refs/heads/trunk`. Background agents keep coding, pushing their feature
branches to origin, and receiving CI results. Story-to-epic,
feature-to-feature, and other non-default-target PRs follow their own
parent-branch policy. They can sync to and merge into that parent while
trunk is held. An epic-to-trunk PR follows the same trunk hold and
refresh rules as every other trunk PR.

An ordinary PR starts in draft. Opening it or pushing a new head runs
TIA against its actual target, with the existing trustworthy full
fallback when selection confidence is insufficient. PR-level test
failure holds that PR. The existing #103 full PR gate remains in force
until a separately approved TIA cutover.
[GitHub draft PRs](https://docs.github.com/en/pull-requests/reference/pull-requests#draft-pull-requests)
· [GitHub PR workflow events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request).

## One shared flag

Use one protected, versioned GitHub ref in AITM as the authoritative
trunk line state. Its record carries repository and target identity,
`OPEN` or `HELD`, version, reason, tested trunk SHA and run attempt,
and, where applicable, incident owner, exact eligible repair, and
recovered trunk SHA and release generation. The ref OID changes
with each committed state transition. The release generation changes
only when a hold clears. CI artifacts retain the evidence. The ref stores
the decision and evidence references. An internal journal or independent
continuity witness can support recovery without adding a second flag
that agents must consult.

Trusted scheduled-result processing authenticates evidence from the
qualifying full trunk suite, scheduled every four to six hours. A
verified failed test, other unresolved full-gate failure, or unavailable
required evidence puts or keeps trunk in `HELD` with the appropriate
reason. Early authenticated shard failure counts. A missing shard
cannot hide it. Duplicate or delayed evidence is reconciled by exact
SHA, run attempt and incident version. A stale green result cannot
clear a current hold. A distinct verified unresolved failure advances
the incident version and invalidates earlier repair and recovery
authorization.

Agents fetch the live flag before marking a trunk PR ready and before
requesting a merge. While held, only the nominated repair may leave
draft to seek review and run full validation. Ordinary drafts stay
draft and an already-ready ordinary PR remains merge-blocked. A missing
or unverified flag defers those trunk
actions while normal background work continues. There is no background
agent polling requirement. Draft status is a workflow convention.
The actual trunk update is enforced on GitHub by a qualified route
available only to the trusted merge service. It checks the current
flag version and the exact PR head, base, and tested tree at mutation.
The proposed writer restriction is static once qualified and installed.
An incident changes the flag through the qualified route.
Already-ready PRs are subject to the same gate. The default branch
identity and exact PR target are checked by the service, so retargeting
a feature PR to trunk cannot carry its old allowance across.

## Hold, repair, and reopen

| Event | Required behavior |
| --- | --- |
| Routine scheduled run starts | Keep existing `OPEN` admission while CI runs. This revision uses the committed GitHub hold as the enforcement boundary. |
| Trusted failure or evidence hold | Stop admitting new trunk merges when the result is accepted for processing. Commit `HELD` through the host ordering mechanism. Agents can continue working and pushing. |
| Fix claimed | Record one owner and at most one nominated repair PR in the incident. A claim carries no merge permission. Nomination allows that PR to seek review and validation. |
| Repair eligible | Bind one reviewed PR to the current incident version, literal trunk target, exact head, current base, and tested merge tree. Require a full candidate pass and all existing review and gate-change requirements. Ordinary PRs remain blocked. |
| Authorized repair lands | Keep `HELD`. Consume the repair authorization with the merge. Immediately request a fresh full run on the confirmed result. Bind recovery to that exact commit and incident version. A new repair requires new authorization. |
| Delayed failure with an already-landed fix | Record the failure and hold. Recognize an earlier repair only with exact full PR proof, independent review, evidence it resolves all recorded defects, and readback that current trunk contains the fix. Run fresh full validation on that current trunk SHA. |
| Repaired trunk passes | Clear `HELD` only after a complete trusted full pass on the repaired commit, read back as current trunk. Record the recovered SHA and new release version. No all-workspace acknowledgment is required. |
| Infrastructure-only interruption | Retain the hold until the cause is resolved and a fresh full run passes on current trunk. A recorded source defect still requires repair and verified recovery. |
| Run fails again, state drifts, or evidence is ambiguous | Keep `HELD` and retain the evidence. Reconcile pending writes before retries, repair, or reopening. |

The CI failure observation and the GitHub flag update are separate
events. The proposal stops new service dispatch on failure processing
and orders outstanding writes against the durable GitHub `HELD`
transition. A conclusively earlier host merge enters the incident
baseline. A previously sent merge that loses the host race cannot land
after `HELD`. Ambiguous ordering keeps the authority held. This revision
chooses no routine pre-run hold. A guarantee from CI detection time
rather than the durable flag commit would require a separate change
to this policy. [#158 host qualification](../../158/plan/2026-11-11-158-merge-only-qualification.md).

## Pending trunk PRs after reopening

A pre-release receipt cannot authorize a subsequent trunk merge.
Resolve the live trunk HEAD, merge or rebase that revision into the
PR head, and push the updated feature or epic branch. The resulting
PR update starts a new CI cycle. If the head already contains current
trunk, request fresh validation for the same tuple rather than making
an artificial commit. Bind the new TIA or full-fallback receipt to
the current release generation, actual target, current base and head,
and tested merge tree. The trusted CI entry point captures the generation
when it admits the new run after reopening. Completion after reopening
cannot refresh a run admitted during the hold. Obtain the review
required for the refreshed candidate. The service checks actual ancestry and the exact receipt
again at the merge boundary. If trunk moves again, refresh and
revalidate again.

The recovery barrier therefore applies per trunk-bound PR. One
disconnected workspace or stale draft cannot delay other eligible PRs.
An epic may continue to integrate story changes during the hold, then
refresh the epic head from live trunk and pass its own CI before
delivery to trunk.
