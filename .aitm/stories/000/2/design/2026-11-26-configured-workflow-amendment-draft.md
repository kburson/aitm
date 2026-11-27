# Core #2 design amendment draft — Configured workflow and managed delivery

Draft for owner discussion · November 26, 2026

## Decision

Core constructs an N-state workflow at runtime from an ordered TOML array. Each state lists the published rules that apply on entry, while it is current, and on exit. AITM ships a default workflow using the same loader as project workflows. An installation can add or remove a parking state, or move supported rules between compatible stages, using configuration alone.

The proposed hosted code-delivery workflow is **Backlog → Design → Refine → Ready for Plan → Plan → Dev ⇄ Review → Done**. Dev includes local verification and waiting for required PR checks. Review includes independent source review, merge, verified delivery, and closeout. The workflow file introduces Design as a state and combines the former Test responsibilities with Dev. It uses Review for closeout and leaves the option of a separate Housekeeping state to a later configuration.

This draft amends the lifecycle and capability composition in the [Core design](core-design.md) and moves hosted working-branch and draft-PR provisioning from Backlog graduation to Dev pickup in the [governed PR design](2026-11-11-2-governed-pr-and-branch-lifecycle-design.md). It builds on the [legacy rule study](../../../../../docs/ai-task-manager-sdlc-analysis.md). Core continues to own permanent identity, the planning store, typed evidence, attempt and trip accounting, and the authority to commit state and admit external effects.

## Configuration and rule execution

The anchored code-default policy selects the workflow file and extensions. The loader resolves the file from that same pinned commit. Array order defines the ordinary forward edges. Explicit edge records attach preparation and transaction behavior or add a nonsequential edge. State IDs are permanent within an active profile. A label can change without changing an ID. Changing an ID, dropping an occupied state, or invalidating an active attempt or pending operation requires an explicit migration or reconciliation. Historical events and pending operations retain their original workflow revision and capability versions.

Each slot references a stable, versioned capability registered by Core or an installed, enabled extension. A guard reads a pinned snapshot and returns pass, blocked, or unavailable with a reason and evidence reference. The operation may refresh external observations before pinning. A directive makes versioned Markdown and expected deliverables available to the agent. An action uses a typed Core service to perform work, record results, or observe external changes. Capability contracts specify applicability, required facts, produced evidence, and whether the action is requested, queued, or observable through reconciliation. The file configures placement and order. Registry code owns execution and typed preconditions.

The engine validates IDs, array and edge references, slot types, provider capabilities, and schema versions. Duplicate state IDs and conflicting edge definitions are invalid. Required unresolved capabilities make affected operations unavailable. Explain must show the reason without dispatching effects. Stable rule IDs in history resolve against the recorded revision. Configuration grants no additional write authority. Each capability declares required predecessor facts and placement constraints in its registry metadata. Core validates those constraints on all reachable paths that use the capability. Core still checks actor, scope, current attempt and generation, exact inputs, and publication requirements before managed dispatch. The same rules apply through CLI and MCP.

The workflow validator distinguishes a parking state from an authority boundary. For the hosted code-delivery contract, every path that starts implementation must pass current planning and binding checks and apply the atomic attempt-start operation. Every path that makes a candidate reviewable must establish the required local and hosted verification. Every delivered path must pass current independent review, verified delivery, and closeout and apply terminal finalization. Core validates these obligations and the compatible placement of their operations against the resolved graph. A profile with a structural bypass is invalid. A valid profile can become temporarily unavailable because a required runtime capability or fact is missing. Alternate local or non-code delivery contracts must declare their corresponding evidence requirements. Projection, optional reporting, and parking may be omitted.

Enforce mode refuses an ordinary guarded transition on blocked or unavailable evidence. In advisory mode either result may permit an authorized, explicitly unverified state observation or transition and is recorded as such. A provisional implementation entry still has an identifiable attempt and an atomic clock record. Required actions with unavailable capabilities remain pending. In both modes, schema and graph validity, legal edges, identity, operation semantics, and storage integrity are mandatory. Missing evidence cannot authorize a managed execution, push or merge, create an effective passing review, or support a delivered disposition. An advisory close with incomplete delivery evidence uses the explicit unverified terminal route.

### Example project policy

This is the proposed shape and set of capability IDs. The IDs below describe interfaces for the amendment.

```toml
# .aitm.toml excerpt for a hosted installation
[workflow]
file = ".aitm/workflows/delivery.toml"

[extensions]
enabled = ["github", "harness"] # Add "tia" and/or "agent-cost" to enable them.

[test.selection]
strategy = "baseline" # Use "tia" to request an enabled selector.
on_unavailable = "baseline"
```

```toml
# .aitm/workflows/delivery.toml
schema = "aitm.workflow/v1"
id = "delivery"
contract = "core.hosted-delivery/v1"

[lifecycle]
terminal = "done"
non_delivery = "done"
reopen_design = "design"
reopen_plan = "plan"

[recovery]
design_rework = "design"
implementation_rework = "dev"
trip = "plan"
scope_pivot = "plan"

[[states]]
id = "backlog"
label = "Backlog"
onEnter = ["core.story.identity-recorded"]
action = []
onExit = ["core.story.description-complete"]

[[states]]
id = "design"
label = "Design"
onEnter = []
action = ["core.directive.author-design", "core.design.record-acceptance"]
onExit = ["core.design.accepted-current"]

[[states]]
id = "refine"
label = "Refine"
onEnter = ["core.design.accepted-current"]
action = ["core.directive.refine", "core.refine.record-estimate"]
onExit = ["core.refine.complete"]

[[states]]
id = "ready-for-plan"
label = "Ready for Plan"
onEnter = ["core.refine.complete"]
action = []
onExit = ["core.plan.admission-ready"]

[[states]]
id = "plan"
label = "Plan"
onEnter = ["core.plan.admission-ready"]
action = [
  "core.directive.plan-for-pickup",
  "core.plan.record-pickup-basis",
  "core.plan.record-decomposition",
  "core.dev.prepare-integration-resource",
]
onExit = ["core.plan.pickup-basis-current"]

[[states]]
id = "dev"
label = "Dev"
onEnter = ["core.dev.binding-ready"]
action = [
  "core.directive.implement",
  "core.verify.local-pre-push",
  "core.pr.push",
  "core.pr.observe-ci",
]
onExit = ["core.dev.review-candidate-current"]

[[states]]
id = "review"
label = "Review"
onEnter = ["core.dev.review-candidate-current"]
action = [
  "core.pr.observe-ci",
  "core.directive.independent-source-review",
  "core.review.record-disposition",
  "core.pr.merge-and-verify",
  "core.directive.author-closeout",
  "core.closeout.record-evidence",
]
onExit = ["core.closeout.complete"]

[[states]]
id = "done"
label = "Done"
onEnter = ["core.closeout.terminal-disposition-valid"]
action = ["core.retirement.reconcile", "core.backlog.project"]
onExit = []

[[edges]]
from = "plan"
to = "dev"
prepare = ["core.dev.prepare-binding"]
operation = "core.attempt.begin-or-resume"

[[edges]]
from = "review"
to = "dev"
kind = "rework"
guards = ["core.review.rework-authorized"]
operation = "core.attempt.resume-for-rework"

[[edges]]
from = "review"
to = "done"
operation = "core.story.finalize-delivery"
```

The example declares the delivered path and its ordinary review loop. Core's separately authorized trip, scope pivot, design rework, and non-delivery operations still apply. The `recovery` and `lifecycle` bindings provide typed destinations for Core operations. The validator requires valid destinations and refuses an ordinary or rework exit from the declared terminal state. Ordinary adjacency stops there even if the file contains later definitions. Non-delivery operations land at the declared terminal state through the separate disposition transaction for abandoned, superseded, duplicate, or advisory unverified outcomes. Terminal evidence recovery reconciles the recorded delivery or closeout in place. An authorized reopen uses the declared Design or Plan destination according to the evidence invalidation it causes. Core takes lifecycle meaning from typed operations and bindings.

Rules in each guard array run in declared order. On the ordinary forward path, Core runs source exit checks before any preparation. If preparation is needed it records a durable intent and runs that action while the source remains current. It then refreshes and repins, rechecks source exit and destination entry, and commits the state, effects on the attempt, and pending action records in one transaction. Shared host effects require verified publication and separately scoped dispatch admission. The engine never holds a planning lock while waiting for CI, a reviewer, or the host.

Order in `action[]` is presentation and progression order, with each action's typed prerequisites controlling eligibility. An agent can request verification again on a changed tree and record review findings while Review is current. Each capability declares whether it applies to a PBI kind and configured delivery mode. For example, a leaf skips epic decomposition and an aggregate skips a source push. A missing required provider is an unavailable prerequisite in a managed code-delivery lane. A separate Core-only policy can provide local delivery and review-evidence implementations using the same engine and typed capability contracts.

## Core design contracts amended by this profile

| Accepted Core or governed PR contract | Replacement here |
| --- | --- |
| Fixed Backlog through Done chain and Backlog exit requiring accepted design | Load the configured chain. Backlog exit requires complete description. Design exit requires current design acceptance, including the applicable own-design obligation for a decomposed child. |
| Design rework returns to Backlog | Design rework from Refine, Ready for Plan, or Plan uses the configured Design destination and invalidates superseded design-dependent facts. |
| Pre-implementation split records Refine → Backlog | The same typed split transaction keeps the permanent ID, converts the kind, and sends the epic to Design for accepted aggregate design before Refine. Refuse split with an existing attempt, expansion child, or unresolved execution or identity operation. Oversize found in Plan or JIT routes via Design rework to Refine before split. |
| Develop exit requires story-tagged commits and resolved expansion. Test exit requires current passing verification. | Dev exit checks tagged source and resolved expansion along with current verification. Preserve typed composed-source and non-code or aggregate alternatives where applicable. |
| Test or Review can return to Develop for implementation rework | CI failures stay in Dev. Review → Dev uses the explicit same-attempt rework edge. Trip and scope pivot use their dedicated fenced routes. |
| Graduation publishes a pending hosted provisioning action | Graduation records permanent identity and declared delivery target. Provisioning is admitted at pickup, including a resource-only route for the designated integration owner in Plan. |

## Plan → Dev

| Rule | Type | Contract |
| --- | --- | --- |
| `core.plan.admission-ready` | Entry guard | Require accepted design, complete refinement, satisfying planning dependency dispositions, and capacity under the configured planning policy. If Ready for Plan is enabled, use the same guard at its exit. |
| `core.directive.plan-for-pickup` | Directive | Tell the agent which planning path applies, identify exact source material, and name the planning deliverables. Author design and plan collateral under the numbered PBI on `planning`. |
| `core.plan.record-pickup-basis` | Action | Register the accepted plan or applicable JIT record. For child JIT, bind the accepted parent plan and entry, current source baseline, structured scope comparison, and any required peer-review acceptance. |
| `core.plan.record-decomposition` | Action | For an epic, register its decomposition from the accepted epic plan, issue or reconcile child identities, and retain entry-to-child mapping and scope dependencies. An interruption leaves incomplete decomposition visible. |
| `core.plan.pickup-basis-current` | Exit guard | Require a current planning basis, resolved blocking prerequisites and trip decisions, and a valid authorized target when this delivery lane uses one. An in-scope child JIT uses the accepted parent plan and its current JIT record. Any change to scope, acceptance criteria, or cross-child commitments requires accepted peer review of the affected plan revision before pickup. For an epic require sized decomposition traceable to the accepted plan. |
| `core.dev.prepare-integration-resource` | Action | In Plan, authorize the designated integration story to provision only its shared branch and upstream draft against the accepted epic plan, scoped role, and exact declared upstream. Verify and publish the resource and draft association before dependent pickup. Leave the integration story in Plan with its child-delivery dependencies and no implementation attempt. |
| `core.dev.prepare-binding` | Transition preparation action | Recheck pickup eligibility and claim or recover the exact resource intent. Provision the branch, draft PR, and worktree where applicable. Reconcile each external effect by its durable identity after an ambiguous response. |
| `core.dev.binding-ready` | Entry guard | Require verified binding for this PBI, candidate attempt, resource incarnation, and literal target. Check the initial base and draft identity for managed code delivery. Use an aggregate registration for a pure epic and a deliverable binding for a non-code spike. |
| `core.attempt.begin-or-resume` | Atomic operation | Start the planned attempt with Dev entry, or reconcile the already recorded attempt when the authorized route allows it. Record the pinned work binding and clock boundary in the same transaction. |

**Standalone story.** Author and peer-review the implementation plan close to pickup. Dev entry checks that the accepted plan still applies to its source baseline and declared prerequisites. Material drift returns it to planning for a current acceptance.

**Epic.** Author and peer-review the full implementation plan before decomposition. Freeze child entries with enough implementation detail to support pickup, including scope, deliverable, verification intent, and dependencies. Core retains the parent plan digest and child entry identity. An aggregate coordinates child work. It uses no source branch merely because its epic record exists. A branch-backed epic may designate an ordinary integration delivery story to own its shared branch and upstream PR. The aggregate can become active for coordination after accepted decomposition without waiting for all descendants to finish.

**Implementation child of an epic.** At pickup run JIT planning against the accepted parent's child entry. Compare the current base, dependencies, and assumptions and record the adjusted implementation checklist or plan. Record which parent plan and entry were used and why any local adjustment remains in scope. The draft permits implementation detail changes within the accepted scope. The pickup author submits a structured mapping to the accepted parent entry and records any proposed changes. Core can check exact digests and declared scope fields. An authorized plan owner resolves ambiguous or disputed scope and records the decision. A recorded JIT adjustment that stays within the accepted parent plan needs no second full plan review. Any change to scope, acceptance criteria, or cross-child commitments requires parent-plan reconciliation and peer review of the affected plan revision before pickup. Accepted design changes also follow the applicable design review policy. If scope is ambiguous, pickup stays blocked until an authorized scope decision resolves it and any required peer review is accepted. The existing design obligations for individual children remain applicable to the Design state.

Graduation issues the permanent PBI ID and records its relationship and declared delivery target. It creates no working ref or draft PR. At pickup a trunk-bound story branches from the pinned trunk tip and targets trunk. A branch-backed child branches from the verified epic integration ref and targets that ref. A child under a pure aggregate uses its separately declared authorized target. For an integration story that supplies a parent branch, provision its own branch and upstream draft under its distinct resource ownership before admitting dependent child pickup. Use the resource-only Plan action for this case. Its admission checks the accepted epic plan, declared integration owner, compliant target, and the prerequisites for provisioning. It excludes child deliveries from the provisioning dependency set. The branch and upstream draft become usable by children while the integration story waits in Plan. Ordinary Dev pickup still requires its implementation prerequisites, reuses the verified resource incarnation, and starts its attempt and clock only when Dev entry commits.

Branch and PR creation may require two external writes with separate dispatch records. Recover the same branch and draft after a lost response. If the host requires an ahead commit for the initial draft, use the reviewed content-free bootstrap route and classify its CI as provisioning evidence. If preparation runs long enough for the pickup basis to expire, retain the resource association and require a fresh basis before entering Dev. Start the implementation attempt and its applicable clock when Dev entry commits.

## Dev → Review and Review → Dev

| Rule | Type | Contract |
| --- | --- | --- |
| `core.directive.implement` | Directive | Implement the accepted plan with TDD, run tests as the work develops, satisfy the acceptance criteria, and address any open XPR findings for the recorded revision. Ask AITM for the managed verification and push operations. |
| `core.verify.local-pre-push` | Action | Run the selected test command in the admitted verification lane. Bind the result to the exact candidate source, attempt, and test policy. Retain selected obligations, execution result, and fallback reason. Reuse Core-authoritative captured-export and containment policy. |
| `core.pr.push` | Action | Require the current candidate's passing local proof plus the authorized binding and PR incarnation. Push through the governed provider, then verify remote head and current target. |
| `core.pr.observe-ci` | Action | Observe required checks for the exact PR candidate. Keep pending, failed, stale, and passed results distinct. Hosted policy can run a wider suite. |
| `core.dev.review-candidate-current` | Exit and entry guard | Require a stable source candidate with story-tagged commits or applicable composed-source proof, resolved expansion, current local verification, and authenticated required hosted results for the current PR, head, target/base, and tested tree as required by policy. Include previously requested finding dispositions on a rework candidate. |
| `core.directive.independent-source-review` | Directive | Give the independent reviewer the exact candidate and diff, requirements, applicable CI evidence, and outstanding prior findings. Request XPR with a disposition bound to that candidate. |
| `core.review.record-disposition` | Action | Import the independent, revision-bound verdict. Record findings as PR comments or threads when supported and save stable references and dispositions on `planning`. Retain the structured review evidence if projection to PR comments is pending. |
| `core.review.rework-authorized` | Rework edge guard | Require a recorded changes-requested verdict or explicit source invalidation before delivery, a current attempt, and authority to resume. The rework transaction retains historical evidence and withdraws current approval and merge eligibility. |
| `core.attempt.resume-for-rework` | Atomic operation | Keep the attempt and binding generation when still valid, retain elapsed implementation time and expansion use, invalidate candidate approval, and resume the applicable clock. |

Local verification can run on the final commit before push, or on a captured candidate whose tree, inputs, environment policy, and receipt are proved identical for the later managed push. New source or moved target invalidates the affected proofs. Dev remains current while hosted CI runs or fails. The agent can query required checks and continue addressing failures in Dev without crossing another state.

Review → Dev is an explicit rework edge. It uses its own guard and the Core rework transaction. It bypasses the normal Review exit and ordinary Dev entry checks because delivery and a new PR binding are inapplicable to same-attempt rework. Live binding, trip, and execution fences still apply. Reconcile any in-flight intent against its original candidate before admitting work for a replacement. A received old verdict remains attributable to its original candidate. An observed landing of a previously admitted candidate goes through delivery reconciliation.

| Change during Review | Required revalidation |
| --- | --- |
| Same source head and literal target, with target tip advanced | Invalidate the old hosted candidate proof and merge admission. Stay in Review while the provider obtains fresh CI for the new candidate if a trusted comparison proves the reviewed diff and review-bound requirements, inputs, and policy still match. Record the comparison and its link to the original XPR in the new effective review record. If equivalence cannot be proved, take Review → Dev and require current CI and fresh XPR. |
| Source head changes, including a pre-merge rebase, or the PR is retargeted | Invalidate candidate CI, XPR applicability, and merge admission. Re-enter Dev and obtain current source proof, CI, and XPR. Preserve prior findings and dispositions for the new review. |
| Approved squash, rebase, or merge transformation during delivery | Bind the allowed transformation and expected target result to the precise admitted candidate before dispatch. Verify the resulting mapping after dispatch. An agent-side rebase or changed target requires fresh admission following the rules above. |

Same-target refresh reuses review only on positive equivalence and still requires fresh hosted CI and exact pre-target admission. On a moving target, the hosting policy may provide a qualified merge queue or equivalent ordered check-and-admit path. Keep the operation pending when current authority cannot be established. The tool cannot use an ordinary rework edge to unwind a delivered attempt.

## Review → Done

| Rule | Type | Contract |
| --- | --- | --- |
| `core.pr.merge-and-verify` | Action | Require effective independent XPR, current required CI, exact approved head/base/tree and target, and current host and Core merge authority. Record intent before dispatch. Verify delivery and source-to-target mapping after merge, including the approved transformation where applicable. Reconcile a lost response before any further dispatch. |
| `core.directive.author-closeout` | Directive | After verified delivery, finish applicable documentation and story narrative. Record acceptance evidence, metadata, retrospective, and links to the delivered PR and revision. |
| `core.closeout.record-evidence` | Action | Validate and retain structured acceptance evidence, applicability, metadata, and sign-off against the verified delivery. Record missing items as outstanding. |
| `core.closeout.complete` | Exit guard | Require applicable documentation and acceptance evidence, current delivery and review provenance, and complete sign-off inputs. |
| `core.closeout.terminal-disposition-valid` | Entry guard | Check that the requested terminal disposition is supported by the current facts. Delivered requires verified delivery and applicable closeout evidence. |
| `core.story.finalize-delivery` | Atomic operation | Record final sign-off, terminal disposition, authoritative story metadata, and pending eligible post-close actions in the same transition transaction. |
| `core.retirement.reconcile`, `core.backlog.project` | Actions | Reconcile safe branch or worktree retirement and provider projections for the published terminal result. Preserve the merged PR and evidence. Hold retirement while dependents or unsaved source require custody. |

While Review is current after verified delivery, allow observation, evidence reconciliation, closeout, and terminal finalization for that delivery. Refuse implementation rework, trip demotion, scope pivot, design rework, and non-delivery closure. Retain late activity as historical evidence. Newly requested scope belongs to separate work. Until uncertain merge results are reconciled, fence an incompatible transition or new dispatch.

The effective independent review pass remains the implementation clock boundary. Pending merge or paperwork stays visible in Review, including after restart. Required authored closeout belongs before Done. Retryable external projection and safely deferred retirement can remain pending after Done. A project can move the authored closeout directive, action, and guard into an added Housekeeping state. It must then place the finalization operation on that state's edge into Done and retain verified delivery as an entry requirement. The runtime gets this placement from configuration.

For a pure epic, the corresponding Dev and Review facts cover child scope and delivery, with no epic code push or merge. For a research spike, a pinned deliverable and its validation, independent review, and archival proof satisfy the corresponding boundaries. Resolve those rules through explicit kind applicability under the accepted Core contracts. A full legacy rule crosswalk will decide the remaining differences in these lanes.

## Optional extensions

**TIA.** An independently versioned and published package registers a test selector and may expose an advisory command. Core invokes the selector inside `core.verify.local-pre-push` when committed policy selects it. The selector receives pinned base, source tree, and inventory/policy inputs. It returns the proposed obligations, reasons, provenance, and full-suite or unavailable disposition. Core applies test policy, admits execution, runs the selected or configured baseline tests, and issues the receipt. Set `extensions.enabled` to include `"tia"` and set `test.selection.strategy = "tia"` to use it. The example policy chooses baseline on unavailability. A project that requires the selector can set `test.selection.on_unavailable = "hold"`. A failed execution or invalid proof stays failed rather than falling back to a fresh passing claim. The hosted verifier remains authoritative for required PR checks. Extract project-specific path and runner configuration from the [existing TIA runner](https://github.com/kburson/aitm/blob/trunk/tools/ci/tia/local.py). Use the [#423 findings](../../../004/423/attachments/results.md) to set the initial advisory scope.

**Agent Cost Capture.** An independently versioned and published package reuses the existing `aitm-effort` capture, report, and export capability. Capture observes explicitly enrolled sessions and attempts across the workflow. The extension owns provider adapters, private receipts, pricing inputs, and optional sanitized reports. It registers its commands, typed producer, and permitted evidence namespace with Core. In a Core installation, publication goes through Core's constrained ingress and writer. Enable `"agent-cost"` in `extensions.enabled` to expose its producer and commands. A project can also append `"agent-cost.report-closeout"` to Review's `action[]` to build or link a pinned cost report after closeout evidence is recorded. That action reports pending or partial coverage without adding a required closeout guard. Disabled capture or incomplete telemetry leaves cost and coverage explicitly unavailable or partial. The default delivery path stays eligible. Qualifying activity for Core clock decisions uses its own evidence and coverage contract. The producer fixture is delivered in [#459](https://github.com/kburson/aitm/issues/459), Core owns the receiver in [#51](https://github.com/kburson/aitm/issues/51), and [#230](https://github.com/kburson/aitm/issues/230) owns live qualification outside M1.

Installation and project enablement are separate. Each package declares compatible Core API versions. Enabled configuration and the actual resolved versions are visible to `doctor` and recorded in decisions that use them. Held or unresolved plugin evidence retains its provenance on replay. Keep upstream provider collection and diagnostics usable as independent commands where their contracts allow.

## Agent interface

Expose one catalog and one state-changing dispatcher through CLI and MCP. An explanation request returns the pinned workflow ID and revision, PBI state, applicable Markdown directive, authoritative evidence, and next eligible action or blocking reason. A dispatch request names the PBI, typed operation and arguments, and the expected observation or operation ID. Core refreshes as appropriate and rechecks its own current facts. Actions retain operation IDs so the agent can reconcile a pending result after restart. Example sequence:

1. Request the next action. AITM reports that Plan is current and pickup is eligible.
2. Request entry into Dev. AITM records preparation and may report that draft PR verification is pending. A retry reconciles the existing intent.
3. In Dev, follow the implementation directive and request local verification, then push. AITM reports pending CI and the exact candidate. If the required host provider is unavailable, Explain reports that capability and a recovery action without dispatching a push.
4. Request Review when current CI passes. If the reviewer requests changes, AITM identifies the findings and admits the rework edge. If XPR passes, it exposes merge when authorized.
5. After verified merge, follow the closeout directive and record evidence. AITM evaluates Review exit and Done entry before finalizing.

The Markdown is guidance and an input to an agent session. Guards inspect typed evidence. Host enforcement for managed writes depends on the existing broker, runtime identity and isolation, and repository protections. Core can diagnose separately observed effects. Dispatch requires proof of authority and scope before it can claim a governed result.

## Reconciliation and acceptance

Treat introduction of this profile into an existing store as an explicit cutover. Keep existing IDs, attempt and clock history, and durable receipts. Keep legacy Backlog in Backlog. Enter Design on the next transition and evaluate any existing exact, current design acceptance through Design's normal guard. An eligible record may pass immediately with its actual evidence. For Refine, Ready for Plan, and Plan, retain the mapped state when existing design acceptance proves the current design and applicable policy. If it does not, record recovery to Design. Retain accepted plan and estimate facts by digest and recheck their applicability at pickup. Map legacy Develop or Test to Dev while retaining valid attempts, binding, clock, and attributable receipts. Require reconciliation for uncertain bindings and rerun verification whenever existing evidence cannot prove the new exit guards. Map pre-delivery Review to Review only when the current candidate satisfies the new Review entry contract. Route an unmerged legacy Review record with stale or insufficient evidence to Dev through a recorded recovery decision. An already merged record with incomplete paperwork resumes Review closeout for the verified delivery. Hold cutover for uncertain provider operations until their original intent has been reconciled. Existing managed branches or drafts may be adopted at pickup only after Core verifies the exact ownership, base, target, and incarnation. Unverified resources remain a reconciliation item. Terminal history retains its original workflow revision and disposition.

Revise the committed configuration, transition, kind-policy, resident action, installed extension and explanation leaves first. Check the captured test, exact review and delivery, atomic sign-off, installed walk, and governed PR leaves against the revised workflow. Preserve permanent leaf IDs where scope still fits. Re-estimate affected work once the workflow and rule crosswalk have been reviewed. Use the [current leaf ledger](../plan/leaf-stories.md) and [governed PR reconciliation](../plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md).

The amendment should require these installed-path proofs:

- Load the default config and another config without Ready for Plan. Both use the same runner, and the direct Refine → Plan entry still enforces planning admission. Show a third config with a separate Housekeeping state using the same closeout capabilities.
- Produce the three planned pickup bases. Admit an in-scope child JIT without a second full plan review. Separately change scope, acceptance criteria, and a cross-child commitment, and verify that each blocks pickup until the reconciled plan revision has accepted peer review. A draft PR appears only after an authorized pickup request. An ambiguous provider response resumes the same intake. A child remains pending when its literal parent resource is unavailable. Prove that a designated integration owner can create a shared resource in Plan, unlock child pickup, and keep its own attempt and clock unopened while awaiting child delivery. A declined or deferred PBI that never requests pickup has no remote work resources.
- Drive Plan → Dev → Review → Dev → Review → Done. Exercise stale local proof, pending or failed hosted CI, a new push or changed target, exact XPR rework, merge verification, and restart during post-merge closeout. Prove that a same-target advance with equivalent review inputs refreshes CI without another XPR, and that a changed source, target, or affected review input does require a new XPR. Exercise a trip winning the order before dispatch, a lost merge response, and refusal of trip demotion, pivot, and abandon after verified delivery.
- Exercise the same rule and action results through CLI and MCP. Refuse policy selected from a story worktree, stale candidate authority, and direct managed mutations outside the dispatcher on the qualified hosted route. Prove that enforced unavailable evidence blocks, advisory observation remains unverified, and a structurally bypassable profile is rejected in both modes.
- Install Core alone and exercise baseline delivery with local evidence and no plugin assumptions. Exercise TIA selected obligations and fallback with the hosted authority intact. Exercise Cost Capture as an independent producer with replay, missing coverage, and verified receiver behavior at the owning qualification boundary.

The draft chooses pickup-time provisioning, Review-owned closeout, optional TIA and Cost Capture, and JIT for implementation children only. Structural validation and the initial cutover mappings are draft design choices for review. The child JIT review threshold follows the owner direction recorded in Plan → Dev. Finish the full rule crosswalk before re-decomposition. Existing review-depth and production-adoption decisions remain with their owners.
