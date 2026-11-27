<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-d69706914b83ab63954983955c19e200"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/2/plan/2026-11-26-configured-workflow-implementation-plan.md"
artifact_commit: "9015a4f31d11cb6a27365004c9a4ecfe16cb8a19"
artifact_blob: "7a829d3d8f188823ec4c7ca22e155ce7ab3e54be"
artifact_digest: "sha256:059c4732b2234924a2e45e5e84a702dac79e2f404fca9e4096ef58a66cc6d2cd"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:0ffb2736ba16f3bda0f21bcb2b01de963d25567b5e97b12aa7409ba76d021bcf"
  identity_source: "runtime"
started_at: "2026-11-27T03:57:28.963Z"
submitted_at: "2026-11-27T03:59:51.994Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Reviewed the implementation plan (blob `7a829d3d`) together with the mini-epic ledger, the legacy rule crosswalk, the accepted baseline leaf ledger (`leaf-stories.md`) and the test-path convention in `core-implementation-plan.md`. I did not check the SHA-256 digests of the supporting files, because this review had no shell access beyond the join/submit commands.

Verified consistent:

- **Counts.** The 21 epics' child counts add up to 106. That is 89 retained plus 17 new keys (C90–C106). Each epic's hours equal the sum of its child rows, and the epics total 371.5 h. The 17 new keys total 59 h, so the existing leaves now total 312.5 h against the 297.25 h baseline.
- **Integration uplift.** Retained-scope owners match the "+0.5 h" rule against the baseline: C56 3→3.5, C08 3.5→4, C14 3→3.5, C18 3.5→4, C21 3.5→4, C26 3.5→4, C34 3→3.5, C41 3.5→4, C51 3.5→4, C64 2.5→3, C66 3→3.5, C67 2.5→3, C69 3→3.5. C78 went 3→4 with revised scope.
- **Epic sizes and rules.** Every Core epic has 4–6 children, and every child is ≤ 4 h. C104, C105 and C106 match the "final owner already at 4 h" rule (C17, C29, C88).
- **Topological order.** For all 21 epics, every cross-epic child prerequisite appears in that epic's "Trunk prerequisites" column. Every column entry points to an earlier sequence number, so the claimed order is valid.
- **Inherited edges.** Spot checks confirm baseline edges carry forward with additions only: C04, C28, C49, C87, C88.
- **Crosswalk tallies.** The registrations add up to 54: 11 entry, 3 resident and 40 exit. Exactly six rows are "Decision needed", and they match the six omissions listed in the plan's Legacy policy section.
- **Test paths.** The new-child paths follow the baseline `tests/{unit,integration}/test_cNN.py` convention.

The decomposition is well structured. The remaining issues concern three things: what each integration owner must wait for, how the integration work of new-key owners is budgeted, and who owns and gates the open legacy-parity work.

## Findings

1. **Integration-owner readiness is prose-only; several owners don't depend on the siblings their slice proof exercises.**
   - The ledger says the owner "waits for the required child deliveries" and calls these "delivery readiness checks, separate from the leaf's own code prerequisites". But it never lists which siblings each owner waits for.
   - The reconciliation step ("read back every proposed new edge … prove a full group-level topological order") only covers the listed prerequisites. So a native graph built from this ledger could let an owner be picked up and land the slice on trunk before its siblings deliver.
   - Concrete cases:
     - Epic 10: owner C34/#31 depends only on C33. Yet the slice proof is "Fence a stopped attempt, prove single-use admission", which is C31/C32 behavior.
     - Epic 3: C14 doesn't depend on C23, C80, C90 or C92.
     - Epic 12: C41 doesn't depend on C42 or C73.
     - Epic 14: C78 doesn't reach C75.
     - Epic 18: C66 doesn't depend on C65, C70 or C50.
   - Every cross-epic edge rests on the producer's trunk receipt, so an early owner landing would produce a receipt that downstream epics treat as covering children that never landed.

2. **New-key integration owners carry substantive new scope at the 4 h cap with no integration share.**
   - The plan says integration "adds 0.5 h to existing bounded owners where it fits". Where it doesn't fit, it adds a dedicated integration leaf (C104/C105/C106).
   - C94, C95, C96 and C101 are new children at 4 h. Each also owns the shared-resource preparation, the composed-delta verification and the trunk landing.
   - Neither the plan nor the ledger shows whether their 4 h includes the integration work. If it does, the substantive scope is 3.5 h, and the C93/C94 split, the selection-policy contract, Plan-resource provisioning and CLI/MCP parity were never sized to that. If it doesn't, these four rows break the stated cap rule.

3. **Open legacy-parity questions outside the six "Decision needed" rows have no sized owner or pickup gate.**
   - The Legacy policy section deals only with the six "Decision needed" registrations. Many "Changed" or "Mapped" crosswalk rows still contain unresolved decisions that change leaf scope. Examples:
     - Review Exit 1: whether general blockers gate merge admission, closeout or another operation. This affects C79 and C88.
     - Develop Exit 1 / Test Exit 1: repeated dependency enforcement at Dev exit.
     - Develop Exit 2: whether the handoff marker needs a recorded fact.
     - Plan Exit 9: ownership overrides.
     - Ready for Plan Exit 3 / Plan Exit 2: which pools count toward capacity.
   - The crosswalk's "Remaining behavior and policy evidence" section and "Rules outside the state arrays" table call for real investigation: reading legacy guard functions and tests, resident-action internals, hooks, and a verb-to-state table. No ledger child or estimate owns that work. C46/#53 inventories legacy data, not rule semantics.
   - Even for the six, the plan says only "Resolve … in #12/#37 and the owning migration or planning leaves". It sets no point by which each must be resolved. C07/#12 is in epic 2 and C28/#37 in epic 9, so the policy outcome could arrive after the code it constrains has landed.
   - The plan says a later mandatory rule needs "its own acceptance evidence and a bounded owner". That protects parity claims, but it doesn't keep JIT pickup of an affected leaf from going ahead on an unsettled question.

4. **Minor: the optional-package epics don't follow the declared structure, and the Cost epic's closure is tied to the Core release.**
   - The ledger says to "use the same four-to-six-child structure", but neither the TIA epic nor the Cost epic names an integration owner.
   - The Cost epic contains #228 and #229. These are Core timing follow-ups that the plan says "remain after #72". The epic is described as having publication "independent of the Core M1 release", yet it can't close until after the Core release and those timing qualifications. #228/#229 also fit the cost-capture package poorly.

## Required changes

1. For each mini-epic, state the integration owner's readiness set. The default can be "all direct siblings", with any listed exceptions. Record these sets as dependency edges, or as an explicit readiness relation that the reconciliation readback verifies. Add them to the "prove a full group-level topological order" step. Make each slice's proof name only behavior its owner actually waits for (fixes the C34 / epic 10 mismatch).
2. For C94, C95, C96 and C101, either give the substantive vs. integration split inside the ≤ 4 h estimate, or move the integration duty to a dedicated integration leaf (as with C104–C106) and rebalance. Update the epic hours and totals if anything changes.
3. Give the legacy-parity investigation a sized owner: one or more new children, or explicitly extended scope on existing leaves with revised estimates. List the open questions embedded in "Changed" or "Mapped" crosswalk rows next to the six decisions. For each item, name the leaf whose JIT pickup must hold until it is resolved, or until it is explicitly kept as project policy. At minimum, gate C07/#12, C28/#37, C79/#80 and C88/#241 on the decisions that constrain them.

## Optional suggestions

1. Name an integration owner for the TIA and Cost package epics. Consider moving #228/#229 out of the Cost package epic into a post-release Core qualification group, or say explicitly that the Cost epic's closure waits on #72.
2. State in the plan that the supporting-artifact digests are re-verified as part of reconciliation readback. This review couldn't check them.

## Decision

revisions-requested
