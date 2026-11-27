# Legacy SDLC policy decisions

C110 [#497][story] qualifies the legacy evidence for the [accepted configured
workflow][design] and [implementation plan][plan]. The legacy source is commit
`c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905`, tree
`844ae26bb169e8618e45fc3b1aedb57f44896fe0`. The [guard][guards], [resident
action and evidence][actions] and [authority][authority] inventories give the
pinned sources, tests and limits of the legacy evidence. The [crosswalk][cross]
identifies the open choices carried forward here.

The dispositions below use obligations already specified by the accepted
profile. Kendrick Burson owns project policy choices about enabling additional
legacy checks, exception authority and production adoption. Implementers own
the named Core gates. Provider and migration owners must qualify their own
inputs. A project option needs its owner’s authorized decision, a committed
policy and bounded proof before it can affect admission. A required configured
input that cannot be resolved is unavailable. In enforce mode, that blocks
its guarded transition. The legacy inventory alone supplies no production
parity claim.

## Discussion, fields and snapshots

| Legacy evidence | Disposition | Owner and earliest gate |
| --- | --- | --- |
| Backlog `{discuss}` hard hold and clearance, including full-auto behavior, in [guard families][guard-family] | Backlog checks structured description completeness. The accepted profile has no dedicated discussion guard. Retain known old holds as historical unresolved evidence, including provenance. Marker disappearance cannot qualify clearance. If a project requires a current hold, define attributable issuance, clearance and migration first. | Project policy owner before enabling a discussion hold. C46/#53 before interpreting a legacy marker as resolved. C07/#12 and C28/#37 before admitting a profile with the extra guard. |
| Placeholder text, acceptance criteria and body fields in [guard families][guard-family] | Require current structured description and applicable refinement facts. Missing required facts block. Carry free-text placeholder detection and formatting as optional project lint. A checked box cannot supply a missing typed fact. | C07/#12 for committed policy representation, C28/#37 for admission and C46/#53 before importing a recognizable old placeholder as a typed field. |
| Refinement snapshot, rank, labels and start time in [guard families][guard-family] and [historical evidence][historical] | Pin current authored inputs and typed size, estimate and priority. Retain legacy snapshots and projections with their original coverage and uncertainty. Rank, labels and timing are project/provider fields unless the selected profile declares a typed requirement. | C28/#37 at the Refine boundary, C46/#53 at interpretation and M2 through C15/#16 and C43/#50 before accepting provider field authority. |

## Hierarchy, capacity and pickup

| Legacy evidence | Disposition | Owner and earliest gate |
| --- | --- | --- |
| Separate parent floors at Refine and Ready for Plan in [guard families][guard-family] | Require current applicable Design evidence at Refine and scoped parent plan/entry provenance for a child’s pickup. Apply real dependency dispositions and the selected capacity policy. Omit the generic parent state floors in the accepted profile. A separate coordination floor needs explicit project selection. | C28/#37 at the respective edges. Project policy owner and C07/#12 before enabling an extra floor. |
| Epic children readiness and later child-ahead gates in [cross-boundary behavior][guards-cross] | An epic Plan establishes accepted decomposition. Each child uses its scoped obligations and applicable target. Resource-only Plan preparation checks its own prerequisites and can make the shared ref available before sibling delivery. Aggregate closeout separately checks required children and applicable upstream delivery. | C28/#37 at Plan admission. C62/#63 and C83/#237 at aggregate and shared-resource qualification. C79/#80 at terminal verification. |
| WIP wave and a second pickup cap in [guard families][guard-family] | Enforce configured planning capacity at Plan entry, including the parking-state exit when present. Keep dependency dispositions independent. Project policy must define the counting scope, limit, deferral and exception authority before enabling a specific pool. The accepted example adds no second numeric pickup cap. A required unavailable capacity fact holds Plan admission. | Project policy owner and C07/#12 for the pool or added cap before selecting it. C28/#37 before admitting its configured behavior on either route. |

## Plan and actor evidence

| Legacy evidence | Disposition | Owner and earliest gate |
| --- | --- | --- |
| Deep-dive marker, approval binding, Plan Metadata, verification commands and forecast in [guard families][guard-family] and [historical evidence][historical] | Use typed current plan/acceptance, verification obligations and distinct per-stage estimate provenance. Standalone and epic pickup use current reviewed plans. A child JIT binds accepted parent entry, base, prerequisites and comparison. Material changes wait for the affected accepted peer-reviewed revision. A separate deep-dive stage and legacy metadata or forecast formats remain project or historical evidence. | C28/#37 at pickup, C93/#501 and C94/#502 at their proof gates. Project policy owner before requiring an extra deliverable. C46/#53 before claiming compatibility of imported fields. |
| Sole assignment, a full-auto claim and an ownership override in [guard families][guard-family] and [roles and exceptions][roles] | Preserve authenticated actor, scoped owner decision, exact issue/attempt/incarnation and required binding. An assignee label is a projection. No legacy override is admitted as authority from the body or from a login alone. A distinct assignment policy must supply its actor, scope, expiration and durable decision. | C16/#21 at actor binding, C88/#241 at managed admission. Project policy owner and M3 before any enabled assignment override is trusted. |

## Dependency, review and delivery boundaries

| Legacy evidence | Disposition | Owner and earliest gate |
| --- | --- | --- |
| Blockers repeated at Develop, Test and Review exits in [guard families][guard-family] | Check planning dependencies at Plan admission and pickup. At Dev exit and Review entry require applicable candidate evidence and resolved expansion. Pre-merge admission revalidates current candidate and governed authority. There is no duplicated legacy Test transition or blanket late general-blocker check in the accepted profile. A selected extra late check must name its pre-delivery boundary and cannot undo a verified landing. | C79/#80 before lifecycle proof and C88/#241 before managed merge admission. Project policy owner before selecting a new late blocker rule. |
| Code-complete handoff and reviewed scope in [guard families][guard-family] and [review evidence][review-evidence] | Reuse the exact source, accepted scope, verification evidence and requested review/finding dispositions. The old marker does not establish a separate approval. A project that needs a separate intentional handoff must specify its actor, timing and typed evidence. | C79/#80 for Review entry, C88/#241 for merge. Project policy owner before selecting an additional handoff fact. |
| Definition of Done, issue fields, pre-close completeness and dirty issue checks in [review evidence][review-evidence] | Qualify current candidate for Review. Then require effective independent review and verify the literal target delivery before authored closeout. At closeout retain documentation, acceptance, authored sync, disposition and sign-off. A dirty provider issue is an observation. Conflicting authored inputs stay outstanding until reconciled to current authoritative evidence. | C42/#49 at closeout evidence, C79/#80 at lifecycle cutover and M2 through C43/#50 at provider reconciliation. |
| Epic child disposition and reviewed source lineage in [guard families][guard-family] and [kind evidence][kind-evidence] | Distinguish delivered children from abandoned, superseded, duplicate and unverified outcomes. Verify required child scope, accepted scope resolutions and applicable aggregate or upward delivery. Rework cannot roll back the delivered attempt. | C62/#63 at aggregate scope, C79/#80 at terminal qualification and C88/#241 at the hosted delivery boundary. |

## Resident actions and evidence authenticity

| Legacy evidence | Disposition | Owner and earliest gate |
| --- | --- | --- |
| Develop verification and Test PR/quick CI in [registered actions][registered] | Local verification runs under the admitted lane and produces a candidate-bound receipt. Push requires current applicable proof and binding. Provider CI observation keeps pending, failed, stale and passed distinct. Bootstrap CI qualifies provisioning. Changed head, base or inputs require revalidation as appropriate. | C35/#42 at local verification, C43/#50 at provider observation, C79/#80 at Review entry and C88/#241 at mutation. |
| Review validation, waits, restarts and ambiguous effects in [state entry and recovery][resident-recovery] | Import independent source review on the applicable candidate. Preserve operation identity and disposition durably. Reconcile uncertain actions against their original correlation before a retry, including merge. Interrupted closeout resumes against verified delivery. A legacy cursor phase alone is insufficient evidence. | C43/#50 at recovery, C79/#80 at lifecycle restart and C88/#241 before new hosted effects. |
| Historical receipts, marker authenticity and evidence by kind in [historical evidence][historical] and [kind evidence][kind-evidence] | Retain parsed historical claims separately from qualified evidence. Bind proof to its story, source, candidate, attempt, authority, applicable policy and outcome. Code and commit-bearing docs use source proof. Spikes can qualify through pinned validated and reviewed deliverables. Pure aggregate facts qualify child scope and delivery. Uncertain imported kind or evidence stays unresolved. | C35/#42 at verification, C46/#53 at import interpretation, C77/#78 at kind normalization and C79/#80 at kind-specific lifecycle proof. |

## Operations, exceptions and provider policy

| Legacy evidence | Disposition | Owner and earliest gate |
| --- | --- | --- |
| Agent directives, home states, forward movement and actions-only in [operation classes][operations] and [roles and exceptions][roles] | Keep directive guidance separate from typed gates. Evaluate ordered source and destination facts against the pinned read-set. Admit or reconcile current actions without advancing when applicable, under the same durable operation identity. Explain and dispatch consume the same typed preconditions. | C28/#37 at edge admission and C63/#64, C87/#240 and C89/#242 at command parity. |
| Backward parking, resume and trip in [operation classes][operations] | Use explicit authorized recovery edges and retain reason, current attempt and lineage. The example has no general legacy parking demotion. A project-specific parking edge needs declared authority and structural validation before selection. A session rebind alone supplies no rework or reopen authority. | C28/#37 at operation admission and C31/#40 at trip handling. Project policy owner before an added parking route. |
| Full-auto, force and supersede in [roles and exceptions][roles] | Keep scoped exception evidence and legal operation checks mandatory. Enforce refuses blocked or unavailable guards. A separately authorized advisory transition can record an unverified result. Supersession records a non-delivery outcome and its replacement. A force or waiver cannot authorize managed effects or a delivered disposition without required proof. The evidence leaves additional host-wide full-auto authority unverified. | C07/#12 before profile selection, C28/#37 at transition admission and C88/#241 at external admission. Project policy owner before selecting optional waivers. |
| Activity, agent delegation, shell, issue and board adapters, worktree and evidence entry in [outside-state surfaces][surfaces] | Maintain bound identities, typed readback, admissible observation and execution scope. Core checks binding, current capability and admitted effect. Compatibility paths and hook observations alone cannot qualify provider or runtime enforcement. | C16/#21 and C32/#41 at binding/execution. C88/#241 at managed admission. M2 and M3 before host parity is claimed. |
| Blast radius, hooks, cost capture and runtime policy in [outside-state surfaces][surfaces] | Require scoped impact and explicit authorized expansion or a fenced disposition. The legacy target count supplies no project limit. Native hook observations need capability, identity and continuity proof. Cost capture is optional and requires explicit enrollment and qualified receipts. | C30/#39 and C31/#40 for expanded work or trip. Project policy owner for thresholds. M3, C12/#20 and C44/#51 before runtime or cost evidence is qualified. |

## Provider and migration handoffs

- **M2 through C15/#16, C43/#50 and C88/#241.** Verify the bound board, issue
  and source targets, projection/readback, provider identity, current required
  CI, supported merge transformation, and delivery on the literal target.
  Reconcile ambiguous writes by their durable identity. Historical issue/body
  markers remain observations until qualified.
- **M3 through C16/#21, C32/#41, C80/#233 and C89/#242.** Prove actual caller
  identity, scoped worktree and shell containment, hook installation and
  failure behavior, direct-host enforcement and command parity on the selected
  runtime. The C109 local evidence does not establish host-wide parity.
- **C46/#53, C47/#54 and C48/#55.** Inventory old aliases, phases, directive
  and receipt formats, evidence provenance and kind uncertainties. Preserve
  identities, attempt history and attribution. Prove stable preparation and
  atomic adoption, retaining an explicit outstanding result when historical
  evidence cannot be qualified.
- **Project policy owner.** Select any additional legacy obligation and its
  earliest gate before enabling it. Production adoption or a parity claim
  needs the selected rule and its bounded proof.

Issues #12, #37, #80 and #241 require this fixture on trunk before their affected
pickup. Other listed consumers cite the applicable decision at JIT. Unresolved
policy does not block generic Core contracts that already have a defined
behavior. It blocks affected admission when the selected profile needs a fact,
policy decision or host capability that remains unavailable.

## Typed decision vectors

Each vector supplies changes to a baseline with the other applicable
preconditions current and satisfied. The expected result applies only to the
named operation. These are design expectations for downstream tests. They do
not qualify an implementation, authorize an effect or establish host parity.

```json
{
  "schema": "aitm.design-policy-vectors/v1",
  "evidence": "design-expectations",
  "vectors": [
    {
      "id": "D01-accept",
      "group": "discussion-and-fields",
      "operation": "core.refine.complete",
      "facts": {
        "current_refinement": true,
        "estimate_hours": 3,
        "size": "S",
        "priority": "P1",
        "acceptance_present": true
      },
      "expected": {
        "decision": "accept",
        "reason": "current-typed-refinement"
      }
    },
    {
      "id": "D01-refuse",
      "group": "discussion-and-fields",
      "operation": "core.refine.complete",
      "facts": {
        "acceptance_present": false,
        "legacy_marker_present": true
      },
      "expected": {
        "decision": "refuse",
        "reason": "required-authored-field-missing"
      }
    },
    {
      "id": "D02-accept",
      "group": "hierarchy-and-capacity",
      "operation": "core.dev.prepare-integration-resource",
      "facts": {
        "accepted_epic_plan": true,
        "designated_integration_owner": true,
        "sibling_delivery_count": 0
      },
      "expected": {
        "decision": "accept",
        "reason": "resource-only-admission"
      }
    },
    {
      "id": "D02-refuse",
      "group": "hierarchy-and-capacity",
      "operation": "core.plan.admission-ready",
      "facts": {
        "planning_capacity_remaining": 0,
        "dependencies_satisfied": true
      },
      "expected": {
        "decision": "refuse",
        "reason": "configured-planning-capacity-exhausted"
      }
    },
    {
      "id": "D03-accept",
      "group": "planning-basis",
      "operation": "core.plan.pickup-basis-current",
      "facts": {
        "accepted_parent_entry": true,
        "current_jit": true,
        "material_scope_change": false
      },
      "expected": {
        "decision": "accept",
        "reason": "current-in-scope-jit"
      }
    },
    {
      "id": "D03-refuse",
      "group": "planning-basis",
      "operation": "core.plan.pickup-basis-current",
      "facts": {
        "material_scope_change": true,
        "revised_plan_peer_accepted": false
      },
      "expected": {
        "decision": "refuse",
        "reason": "affected-plan-acceptance-required"
      }
    },
    {
      "id": "D04-accept",
      "group": "actor-authority",
      "operation": "core.dev.binding-ready",
      "facts": {
        "actor_scope_matches": true,
        "binding_generation_current": true,
        "literal_target_verified": true
      },
      "expected": {
        "decision": "accept",
        "reason": "current-authorized-binding"
      }
    },
    {
      "id": "D04-refuse",
      "group": "actor-authority",
      "operation": "core.dev.binding-ready",
      "facts": {
        "assignee_matches": true,
        "actor_scope_matches": false
      },
      "expected": {
        "decision": "refuse",
        "reason": "actor-scope-mismatch"
      }
    },
    {
      "id": "D05-accept",
      "group": "dependency-boundaries",
      "operation": "core.dev.review-candidate-current",
      "facts": {
        "source_current": true,
        "expansion_resolved": true,
        "local_proof_current": true,
        "hosted_ci_current": true
      },
      "expected": {
        "decision": "accept",
        "reason": "verified-candidate"
      }
    },
    {
      "id": "D05-refuse",
      "group": "dependency-boundaries",
      "operation": "core.dev.review-candidate-current",
      "facts": {
        "source_current": true,
        "expansion_resolved": false,
        "hosted_ci_current": true
      },
      "expected": {
        "decision": "refuse",
        "reason": "required-expansion-unresolved"
      }
    },
    {
      "id": "D06-accept",
      "group": "review-and-closeout",
      "operation": "core.story.finalize-delivery",
      "facts": {
        "effective_review": true,
        "verified_delivery": true,
        "closeout_complete": true
      },
      "expected": {
        "decision": "accept",
        "reason": "verified-delivery-and-closeout"
      }
    },
    {
      "id": "D06-refuse",
      "group": "review-and-closeout",
      "operation": "core.story.finalize-delivery",
      "facts": {
        "effective_review": true,
        "reviewed_scope_current": true,
        "verified_delivery": false
      },
      "expected": {
        "decision": "refuse",
        "reason": "positive-delivery-missing"
      }
    },
    {
      "id": "D06-fence",
      "group": "review-and-closeout",
      "operation": "core.review.rework-authorized",
      "facts": {
        "verified_delivery": true,
        "actor_scoped": true
      },
      "expected": {
        "decision": "refuse",
        "reason": "verified-delivery-fence"
      }
    },
    {
      "id": "D07-accept",
      "group": "resident-actions",
      "operation": "core.pr.observe-ci",
      "facts": {
        "candidate_current": true,
        "hosted_result": "success",
        "host_authenticated": true
      },
      "expected": {
        "decision": "accept",
        "reason": "applicable-hosted-result"
      }
    },
    {
      "id": "D07-pending",
      "group": "resident-actions",
      "operation": "core.pr.observe-ci",
      "facts": {
        "candidate_current": true,
        "hosted_result": "pending"
      },
      "expected": {
        "decision": "pending",
        "reason": "await-current-hosted-result"
      }
    },
    {
      "id": "D07-refuse",
      "group": "resident-actions",
      "operation": "core.dev.review-candidate-current",
      "facts": {
        "hosted_result": "success",
        "receipt_head_matches": false
      },
      "expected": {
        "decision": "refuse",
        "reason": "stale-hosted-result"
      }
    },
    {
      "id": "D08-accept",
      "group": "operations-and-provider-authority",
      "operation": "core.pr.merge-and-verify",
      "facts": {
        "host_actor_scoped": true,
        "effective_review": true,
        "hosted_ci_current": true,
        "candidate_target_matches": true
      },
      "expected": {
        "decision": "accept",
        "reason": "exact-governed-merge-admission"
      }
    },
    {
      "id": "D08-refuse",
      "group": "operations-and-provider-authority",
      "operation": "core.pr.merge-and-verify",
      "facts": {
        "mode": "advisory",
        "host_actor_scoped": false,
        "hosted_ci_current": true
      },
      "expected": {
        "decision": "refuse",
        "reason": "managed-authority-unavailable"
      }
    },
    {
      "id": "D08-advisory",
      "group": "operations-and-provider-authority",
      "operation": "ordinary-guarded-transition",
      "facts": {
        "mode": "advisory",
        "transition_authorized": true,
        "guard_result": "unavailable",
        "structural_requirements_satisfied": true,
        "managed_effect_requested": false
      },
      "expected": {
        "decision": "unverified",
        "reason": "authorized-advisory-observation"
      }
    }
  ]
}
```

[story]: https://github.com/kburson/aitm/issues/497
[design]: https://github.com/kburson/aitm/blob/07755fa0bf8e5fabdcadbce0eb31a126b5cc6303/.aitm/stories/000/2/design/2026-11-26-configured-workflow-amendment-draft.md
[plan]: https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md
[cross]: https://github.com/kburson/aitm/blob/0945941c6c024b6dd621202b2456696ae1df0154/.aitm/stories/000/2/plan/2026-11-26-legacy-rule-crosswalk.md
[guards]: guard-facts.md
[guard-family]: guard-facts.md#guard-families
[guards-cross]: guard-facts.md#cross-boundary-behavior
[actions]: action-and-evidence-facts.md
[historical]: action-and-evidence-facts.md#verification-and-historical-formats
[review-evidence]: action-and-evidence-facts.md#review-source-and-closeout
[kind-evidence]: action-and-evidence-facts.md#kind-differences
[registered]: action-and-evidence-facts.md#registered-actions
[resident-recovery]: action-and-evidence-facts.md#state-entry-and-recovery
[authority]: authority-facts.md
[operations]: authority-facts.md#operation-classes
[roles]: authority-facts.md#directives-roles-and-exceptions
[surfaces]: authority-facts.md#outside-state-authority-surfaces
