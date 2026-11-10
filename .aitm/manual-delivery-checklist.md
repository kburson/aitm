# Manual delivery checklist

Use one checklist per story while the workflow is manual. Keep the checklist with the story on `planning`, for example at `.aitm/stories/<bucket>/<id>/plan/delivery-checklist.md`. Keep distinct attempts and revisions in the same checklist with dates and evidence links. Use the story's own acceptance and target. An epic release, integration or activation gate applies to a child only when the child's accepted scope actually owns that gate. The [approved Core design](stories/000/2/design/core-design.md#verification-delivery-and-sign-off) informs the evidence model.

## Copy for each story

- Story, implementing agent and closure owner
- Attempt, accepted design/plan/JIT and dependencies
- Story branch, parent target branch and pinned base
- PR, exact head SHA and reviewed tree
- Required CI jobs, validated CI route for the parent branch and validation scope
- Independent reviewer and verdict
- Verified delivery result, retrospective/sign-off and time the last required gate passed

### Before Develop

Use the owner's delivery instruction for actions within the reviewed scope, including ordinary pushes, CI, review, merge and closure. Ask once if an action falls outside that scope or the owner explicitly reserved the decision.

- [ ] Identify the CI route for the declared target and scope. If the story builds or repairs that route, Develop may proceed under the existing delivery authorization. Record the missing route as work to complete. Require passing CI on the exact candidate before Review and merge.
- [ ] Name the closure owner, normally the implementing agent. That owner verifies delivery, obtains the implementing agent's signed retrospective, and reconciles the issue and Project status. Keep the implementing agent available until their own retrospective is signed.

### Develop → Test

- [ ] Confirm the story's accepted scope, dependencies, current attempt, owner, baseline, expected target and required tests and validations. Declare the parent branch explicitly. Use the epic integration branch when that is the agreed parent. Use a separate PR for the eventual aggregate release when required.
- [ ] Commit the story changes, push its branch to `origin` and open its own PR into the declared parent branch. Reference the story, scope, validation requirements and planning checklist. Keep automatic issue closure out of the PR so merge can be followed by verified delivery, sign-off and housekeeping.
- [ ] Read back the PR base, head and exact head SHA on GitHub. Record the clean source/tree and the base used for verification. Publish the Test checkpoint on planning and reflect Test on the GitHub Project.

### Test → Review

- [ ] Run every required CI test and validation. Record the job names, run URLs, outcomes and tested SHA in planning. Verify on GitHub that the jobs actually covered the current PR head and applicable base. If CI uses a synthetic merge commit, record its identity and the exact base and head it combined. A passing job on a different head or base provides evidence for that earlier candidate.
- [ ] Move to Review only after all applicable required checks pass on the exact candidate. Give an independent external agent the accepted design, plan, scope, pinned base, exact passing SHA or tree and CI evidence. Have the reviewer inspect specification compliance and quality, and produce a dated verdict with findings and evidence. The implementer and reviewer are separate actors.
- [ ] Link the review record from planning and reflect the reviewer, verdict and exact reviewed SHA on the GitHub PR. Use a native GitHub review when supported. For off-platform review, link the sanitized review record in the PR and label it as off-platform. Record the native review as absent if no native review was submitted. Respect any branch requirement for native approval.

### Failed checks or review → Develop

- [ ] Keep the failed run or verdict, its head, findings and disposition. Return failed review to Develop in planning and on GitHub and fix the findings in the story branch. Route changes in scope, ownership or prerequisites back through planning and refresh the pickup before resuming.
- [ ] Push the replacement head. Run fresh required CI and obtain fresh independent review on that same passing head. Recheck both if the head, applicable base or validation inputs change. Retain superseded results with their original identities.

### Review → Done

- [ ] Before merging, reread the current PR head, base, branch requirements, required checks and effective review. Merge through the normal authorized GitHub path only once the exact candidate is eligible.
- [ ] Verify the merge on the declared remote parent. Record the PR URL, reviewed head/tree, merge method, merge SHA, delivery timestamp and proof of the reviewed source landing. For fast-forward or ordinary merge, verify the expected tree or content mapping as well as ancestry. For squash/rebase, record the source-to-target content mapping. Reconcile uncertain outcomes from the remote before retrying.
- [ ] Obtain a dated retrospective and sign-off from the implementing agent after delivery verification. Record agent identity, story and attempt, reviewed source, delivered result, delivered verdict, confidence, design/plan/delivery alignment, successes, misses, lessons, and measured or Unknown timing. Link the authored record under `retro/`. An unavailable author is a sign-off gap. Any late reconstruction carries its actual author and date as a separate record.
- [ ] Finish required housekeeping for this story. Publish the evidence on `planning`, link it from the issue or PR, and record dependency effects. Release only the story's own locks, session or temporary resources as applicable after sign-off and evidence retention. Give any nonblocking housekeeping its own follow-up and owner.
- [ ] The last required gate passing triggers immediate closure. Record which gate passed and when. The closure owner closes the GitHub issue and marks the Project item Done before picking up unrelated work. Read both back. Record the planning Done checkpoint and the GitHub issue closure timestamp separately and link the observations on planning. If closure stalls or only part of it succeeds, retain the confirmed facts and record the exact blocker, owner and next action. Reconcile the missing action before declaring closure complete.

For an operational or other non-source deliverable, the accepted plan must name its own verifiable target and applicable gates. Record the immutable deliverable, real validation, independent review of that version and verified result. Any source changes in that story follow the PR gates above.

## Missing evidence

Keep a required gate open for missing, pending, skipped, stale, failed or unavailable evidence. Record which gate is affected, the exact candidate, what GitHub actually shows, the cause if verified, and what will satisfy it. For example, when a repository has no matching workflow, record **CI unavailable** and the absence of checks on that head. An exact local run can be retained with its command, environment, inputs, head and outcome as local verification. A local pass, PR comment or retrospective cannot stand in for missing CI or a required native approval. An explicitly authorized exception under the applicable policy must identify the authority, exact scope, omitted gate, substitute evidence and resulting disposition. Preserve the actual missing status in both records.

Keep private transcripts, raw logs with sensitive contents, machine paths, credentials and personal provider identifiers out of Git. Publish sanitized evidence, safe links or digests as appropriate. Leave historical closures and their evidence gaps intact when adding late records.

## Planning and GitHub evidence

| Record in planning | Reflect and verify on GitHub |
| --- | --- |
| Story, owner, attempt, dated state changes, accepted scope, declared parent and branch, exact source, base and PR link | Issue linked to PR, correct head/base and current Project status |
| Expected checks, exact runs and outcomes, local validation separately, stale or missing gates and any authorized exception | Actual check and status results on the exact head, plus a clear link to limitations or exceptions |
| Independent review, reviewer, exact SHA, dated verdict, findings and rework history | Native PR review when available, or linked off-platform verdict with its provenance |
| Delivery mapping, target commit, retrospective and sign-off, housekeeping and closure observations | Merge result on the declared target, issue evidence link, closed issue and Done Project status |

## Epic acceptance

Track child delivery and closures as they happen. Keep the epic's aggregate tests, release or activation evidence, unresolved scope decisions, and dated epic retrospective and sign-off in the epic record. Close the epic after the required children are delivered or explicitly scope-resolved and the epic clears its own gates.
