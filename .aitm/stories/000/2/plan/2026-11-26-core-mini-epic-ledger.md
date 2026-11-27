# Core #2 Mini-Epic and Child Ledger

This is the proposed delivery map for the [configured workflow implementation plan](2026-11-26-configured-workflow-implementation-plan.md). The [legacy crosswalk](2026-11-26-legacy-rule-crosswalk.md) records the reasons to retain or change workflow scope. Keep all existing issue IDs. New C-keys and epic names are plan identifiers until native creation. This ledger proposes parentage and prerequisites. It does not claim any native changes.

The accepted Core baseline contains 89 leaves and 297.25 h. The proposed Core plan contains **21 mini-epics, 106 children, and 371.5 implementation agent-hours**. It retains all 89 existing Core leaves, adds 17, and includes integration and review effort. The optional packages and live timing/cost qualifications are listed separately. Every Core mini-epic has a named trunk integration owner. Estimates are bounded planning estimates, with JIT revalidation required.

The current [accepted leaf ledger](leaf-stories.md) is the source for inherited child scope, test commands, shared-file ordering, and the historical dependency graph. All prior graph edges carry forward. The exact prerequisites below include the proposed additions. For delivery sequencing, a cross-epic dependency requires the producer slice's verified **trunk landing receipt**, not product #2 closure. The Core packaging source is landed before C60/#72 independently qualifies the exact release. The proposed epics are sibling delivery epics under #1. #2 links the collection for coordination.

## Mini-epic trunk sequence

Each row declares the proof and branch/PR owner for its own slice. The numbered order is a valid topological order. Parallel execution may use any ready row after its required source receipts and authority are current. A prior row without an edge need not finish first.

| Sequence | Delivery epic | Children | Hours | Trunk prerequisites | Integration owner | Required slice proof |
| --- | --- | ---: | ---: | --- | --- | --- |
| 1 | Core records and reducers | 6 | 20 | #83 (completed) | C56 / #8 | Install the package and replay typed records into deterministic state from a fixture. |
| 2 | Trusted Git story store | 5 | 19 | 1 | C08 / #13 | Read and atomically write a pinned local store and refuse an untrusted fetch candidate. |
| 3 | Extension contracts and owned ingress | 6 | 21.5 | 1, 2 | C14 / #15 | Exercise an installed-interface fixture for safe provider and activity records; validate ownership and keep unsupported activity unqualified. |
| 4 | Store readback and publication recovery | 4 | 14.5 | 1, 2, 3 | C18 / #23 | Show a deterministic fresh-clone view, lost-publish recovery and forward-only repair. |
| 5 | Installation and worktree binding | 5 | 17 | 2, 3, 4 | C104 | Init a disposable store, bind a story and reconcile authored sync without foreign worktree effects. |
| 6 | Intake, numbering and graduation | 5 | 18 | 3, 4, 5 | C21 / #27 | Graduate a numbered Backlog story with a declared delivery target and zero remote work resources. |
| 7 | Design and plan review evidence | 5 | 15 | 1, 3, 4, 5 | C26 / #35 | Reconstruct, import, and invalidate actual reviewed document bytes under the applicable policy. |
| 8 | Planning and pickup evidence | 4 | 15 | 1, 2, 3, 5, 6, 7 | C94 | Verify all three planning bases and the peer-review boundary for material child-JIT changes. |
| 9 | Configured state transitions | 5 | 17.5 | 3, 4, 5, 6, 7, 8 | C105 | Load two differently shaped workflows and prove typed guards, directives, terminal routes and split/recovery destinations. |
| 10 | Attempt control and verification preparation | 5 | 18 | 2, 3, 4, 5, 6, 8, 9 | C34 / #31 | Fence a stopped attempt, prove single-use admission, and prepare exact captured inputs offline. |
| 11 | Managed local verification | 4 | 14.5 | 3, 5, 10 | C95 | Run exact-candidate baseline and selector fixtures in captured and qualified contained environments. |
| 12 | Source review, delivery and sign-off evidence | 6 | 21.5 | 1, 2, 5, 7, 9, 10, 11 | C41 / #48 | Bind review to exact source, verify target mutation and recover the sign-off inputs. |
| 13 | Durable actions and installed extension composition | 4 | 14.5 | 1, 3, 4, 5, 6, 9, 10, 11, 12 | C64 / #58 | Replay a retained action from a second clone; prove installed extension enablement and epic required-scope reconciliation. |
| 14 | Installed lifecycle guards and recovery | 6 | 21.5 | 3, 4, 6, 8, 9, 10, 11, 12, 13 | C78 / #81 | Exercise the installed guard and explanation paths, same-attempt rework, and post-delivery mutation fencing. |
| 15 | Managed branch and draft resources | 6 | 22 | 3, 5, 6, 8, 9, 13, 14 | C96 | Prove authorized pickup and integration-owner resource preparation, including loss of acknowledgment and absent parent. |
| 16 | Legacy adoption and workflow cutover | 6 | 21 | 1, 2, 4, 5, 7, 8, 9, 14, 15 | C51 / #56 | Preview and replay typed legacy migration and configured-workflow cutover in fresh clones. |
| 17 | Installed local lifecycle and evidence | 6 | 19 | 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16 | C67 / #66 | Run the local CLI through delivery for each accepted kind and audit the available route and replay surface. |
| 18 | Concurrency and recovery qualification | 4 | 13 | 5, 8, 9, 10, 11, 12, 13, 14, 17 | C66 / #62 | Use shared fixtures to prove ordered stops, delivery and store races with the real Core dispatchers. |
| 19 | Governed PR delivery decisions | 5 | 18 | 3, 11, 12, 14, 15 | C106 | Qualify exact push/CI/merge admission, same-target equivalence, composed source and safe retirement with broker fixtures. |
| 20 | Installed hosted delivery composition | 4 | 15.5 | 3, 14, 15, 17, 19 | C101 | Drive configured pickup, rework, delivery and resumed closeout through the same installed CLI/MCP dispatcher. |
| 21 | Core packaging and release qualification | 5 | 15.5 | 1, 4, 11, 13, 14, 16, 17, 18 | C69 / #71 | Land package, workflows and checker incrementally; separately qualify the exact released wheel. The release check follows the source landing. |


## Child assignments

An existing row links to its prior specification. The new plan supplies revised scope where indicated. Integration owners add the slice-level proof and final trunk landing, and remain within the four-hour cap. Each owner prepares the shared resource at authorized pickup when required. Before merging, the owner waits for the required child deliveries and exact proof, except that C69 lands the source before C60 runs its post-release check. Treat these as delivery readiness checks, separate from the leaf's own code prerequisites. Issue roles do not supply permission to dispatch.

### 1. Core records and reducers

| Child | Disposition | Hours | Required prerequisites |
| --- | --- | ---: | --- |
| [C01 / #3](core-implementation-plan.md#c01-package-foundation-and-command-result-contract) | Retain scope | 3.5 | #83 |
| [C02 / #4](core-implementation-plan.md#c02-event-envelopes-and-reducer-dispatch-invariants) | Retain scope | 2.5 | C01 |
| [C03 / #5](core-implementation-plan.md#c03-canonical-authored-content-and-metadata-ownership) | Retain scope | 3.5 | C01 |
| [C54 / #6](core-implementation-plan.md#c54-lifecycle-relationships-and-document-state-reducers) | Revise scope | 3.5 | C02, C03 |
| [C55 / #7](core-implementation-plan.md#c55-attempt-execution-and-clock-boundary-reducers) | Revise scope | 3.5 | C02 |
| [C56 / #8](core-implementation-plan.md#c56-evidence-action-and-provenance-reducers-with-composition) | Revise scope · Integration owner | 3.5 | C02, C54, C55 |

### 2. Trusted Git story store

| Child | Disposition | Hours | Required prerequisites |
| --- | --- | ---: | --- |
| [C04 / #9](core-implementation-plan.md#c04-typed-operations-and-memorybackend-semantics) | Retain scope | 4 | C02, C54, C55, C56 |
| [C05 / #10](core-implementation-plan.md#c05-git-snapshot-reads-and-atomic-operation-commits) | Retain scope | 4 | C04 |
| [C06 / #11](core-implementation-plan.md#c06-planning-history-validation-and-worktree-exclusion) | Retain scope | 3.5 | C05, C01 |
| [C07 / #12](core-implementation-plan.md#c07-committed-configuration-and-routing-anchors) | Revise scope | 3.5 | C03, C06 |
| [C08 / #13](core-implementation-plan.md#c08-candidate-fetch-and-shared-history-continuity) | Retain scope · Integration owner | 4 | C06, C07 |

### 3. Extension contracts and owned ingress

| Child | Disposition | Hours | Required prerequisites |
| --- | --- | ---: | --- |
| [C13 / #14](core-implementation-plan.md#c13-extension-and-provider-registration-contracts) | Revise scope | 4 | C02, C07 |
| [C14 / #15](core-implementation-plan.md#c14-constrained-extension-writes-and-retained-unknown-data) | Retain scope · Integration owner | 3.5 | C04, C13, C08 |
| [C23 / #28](core-implementation-plan.md#c23-activity-eligibility-and-implementation-clock-fold) | Retain scope | 3.5 | C02, C13 |
| [C80 / #233](2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c80) | Retain scope | 3.5 | C13 |
| C90 | New · Pinned workflow document and ordered graph | 3.5 | C07, C13 |
| C92 | New · Versioned Markdown directive resolution | 3.5 | C90, C13 |

### 4. Store readback and publication recovery

| Child | Disposition | Hours | Required prerequisites |
| --- | --- | ---: | --- |
| [C15 / #16](core-implementation-plan.md#c15-deterministic-views-and-structured-descriptions) | Retain scope | 2.5 | C02, C03, C04 |
| [C18 / #23](core-implementation-plan.md#c18-snapshot-index-and-read-only-queries) | Retain scope · Integration owner | 4 | C02, C08 |
| [C09 / #17](core-implementation-plan.md#c09-publication-replay-and-conflict-recovery) | Retain scope | 4 | C04, C08, C15, C14 |
| [C10 / #18](core-implementation-plan.md#c10-forward-repair-from-maximal-valid-prefix) | Retain scope | 4 | C08, C09, C06 |

### 5. Installation and worktree binding

| Child | Disposition | Hours | Required prerequisites |
| --- | --- | ---: | --- |
| [C11 / #19](core-implementation-plan.md#c11-crash-resumable-init-and-reconfiguration) | Revise scope | 4 | C07, C09, C10 |
| [C12 / #20](core-implementation-plan.md#c12-hook-chaining-and-readiness-diagnostics) | Retain scope | 3 | C06, C11 |
| [C16 / #21](core-implementation-plan.md#c16-authoring-and-implementation-bindings) | Retain scope | 4 | C06, C07, C15 |
| [C17 / #22](core-implementation-plan.md#c17-allowlisted-sync-and-authored-conflict-resolution) | Retain scope | 4 | C09, C14, C16, C12 |
| C104 | New · Integrate installed setup and binding on trunk · Integration owner | 2 | C17, C12 |

### 6. Intake, numbering and graduation

| Child | Disposition | Hours | Required prerequisites |
| --- | --- | ---: | --- |
| [C19 / #24](core-implementation-plan.md#c19-ideas-drafts-and-atomic-discard) | Retain scope | 2.5 | C09, C15 |
| [C74 / #74](core-implementation-plan.md#c74-entity-scoped-editing-and-graduation-handoff) | Retain scope | 3.5 | C16, C17, C19 |
| [C20 / #25](core-implementation-plan.md#c20-semantic-identity-reservations-and-uncertain-dispatch) | Revise scope | 4 | C09, C13, C19, C74 |
| [C22 / #26](core-implementation-plan.md#c22-graduation-and-atomic-relationships) | Revise scope | 4 | C15, C20, C74 |
| [C21 / #27](core-implementation-plan.md#c21-shared-local-number-allocation) | Retain scope · Integration owner | 4 | C22, C17, C74 |

### 7. Design and plan review evidence

| Child | Disposition | Hours | Required prerequisites |
| --- | --- | ---: | --- |
| [C24 / #29](core-implementation-plan.md#c24-portable-review-schemas-and-patch-reconstruction) | Retain scope | 3 | C02, C03, C56 |
| [C57 / #32](core-implementation-plan.md#c57-review-finding-closure-topology-and-policy-assurance) | Retain scope | 2.5 | C24 |
| [C58 / #33](core-implementation-plan.md#c58-native-review-lineage-and-timing-anchor-adapters) | Retain scope | 2.5 | C57 |
| [C25 / #34](core-implementation-plan.md#c25-live-review-capsules-and-qualified-turn-timing) | Retain scope | 3 | C09, C23, C58 |
| [C26 / #35](core-implementation-plan.md#c26-cas-review-import-and-exact-content-acceptance) | Retain scope · Integration owner | 4 | C14, C17, C25, C58 |

### 8. Planning and pickup evidence

| Child | Disposition | Hours | Required prerequisites |
| --- | --- | ---: | --- |
| [C27 / #36](core-implementation-plan.md#c27-attempts-jit-coverage-and-estimates) | Revise scope | 3.5 | C16, C23, C26 |
| [C72 / #75](core-implementation-plan.md#c72-typed-decomposition-descriptors-and-applicability) | Revise scope | 4 | C03, C07, C20, C26, C27 |
| C93 | New · Standalone, epic and child-JIT basis evaluator | 3.5 | C27, C72, C26 |
| C94 | New · Material child-JIT change reconciliation · Integration owner | 4 | C93, C26 |

### 9. Configured state transitions

| Child | Disposition | Hours | Required prerequisites |
| --- | --- | ---: | --- |
| C91 | New · Typed obligation placement and structural validation | 4 | C90, C13 |
| [C28 / #37](core-implementation-plan.md#c28-state-transitions-and-atomic-guard-outcomes) | Revise scope | 4 | C15, C22, C26, C27, C17, C21, C09, C72, C91, C92, C94 |
| [C71 / #76](core-implementation-plan.md#c71-bounded-refine-split-and-kind-invalidation) | Revise scope | 3.5 | C28, C22, C26, C27 |
| [C29 / #38](core-implementation-plan.md#c29-kind-specific-guards-and-terminal-dispositions) | Revise scope | 4 | C28, C71 |
| C105 | New · Integrate configured state transitions on trunk · Integration owner | 2 | C29, C71, C91 |

### 10. Attempt control and verification preparation

| Child | Disposition | Hours | Required prerequisites |
| --- | --- | ---: | --- |
| [C30 / #39](core-implementation-plan.md#c30-expansion-reservation-and-resolution) | Retain scope | 4 | C20, C21, C22, C23, C28, C29 |
| [C31 / #40](core-implementation-plan.md#c31-trip-ordering-replan-decisions-and-human-pivots) | Revise scope | 4 | C23, C27, C28, C30, C14, C17, C71, C74, C29 |
| [C32 / #41](core-implementation-plan.md#c32-single-use-execution-admission-and-cancellation) | Revise scope | 3.5 | C09, C16, C31 |
| [C33 / #30](core-implementation-plan.md#c33-private-immutable-input-capture) | Retain scope | 3 | C07, C16 |
| [C34 / #31](core-implementation-plan.md#c34-offline-environment-provisioning-and-cache-identity) | Retain scope · Integration owner | 3.5 | C33 |

### 11. Managed local verification

| Child | Disposition | Hours | Required prerequisites |
| --- | --- | ---: | --- |
| [C35 / #42](core-implementation-plan.md#c35-captured-export-test-execution-and-receipts) | Revise scope | 3.5 | C12, C32, C34, C31 |
| [C36 / #43](core-implementation-plan.md#c36-macos-contained-lane-probe-and-profile) | Retain scope | 3.5 | C35 |
| [C37 / #44](core-implementation-plan.md#c37-linux-contained-lane-probe-and-profile) | Retain scope | 3.5 | C35 |
| C95 | New · Test selection policy and execution receipt · Integration owner | 4 | C13, C35 |

### 12. Source review, delivery and sign-off evidence

| Child | Disposition | Hours | Required prerequisites |
| --- | --- | ---: | --- |
| [C73 / #77](core-implementation-plan.md#c73-source-review-envelope-and-independence-validation) | Retain scope | 3 | C07, C16, C56, C57 |
| [C38 / #45](core-implementation-plan.md#c38-source-review-evidence-and-effective-pass-activation) | Revise scope | 4 | C29, C35, C73 |
| [C39 / #46](core-implementation-plan.md#c39-positive-delivery-observation-and-archival-proof) | Retain scope | 3.5 | C38 |
| [C40 / #47](core-implementation-plan.md#c40-reviewed-squash-and-rebase-transformation-plans) | Revise scope | 3 | C39 |
| [C41 / #48](core-implementation-plan.md#c41-admitted-target-mutation-and-exact-result-recovery) | Revise scope · Integration owner | 4 | C32, C40, C06, C39 |
| [C42 / #49](core-implementation-plan.md#c42-atomic-sign-off-and-retained-evidence-reconstruction) | Revise scope | 4 | C29, C38, C39 |

### 13. Durable actions and installed extension composition

| Child | Disposition | Hours | Required prerequisites |
| --- | --- | ---: | --- |
| [C43 / #50](core-implementation-plan.md#c43-durable-resident-action-queue-and-replay) | Revise scope | 4 | C09, C13, C17, C28, C35, C31, C74 |
| [C62 / #63](core-implementation-plan.md#c62-epic-aggregation-and-scope-resolution-checkpoint) | Revise scope | 4 | C22, C29, C38, C42, C43 |
| [C63 / #64](core-implementation-plan.md#c63-installed-extension-discovery-and-commandinit-composition) | Revise scope | 3.5 | C12, C13, C14, C43, C01, C62 |
| [C64 / #58](core-implementation-plan.md#c64-deterministic-two-clone-qualification-fixtures) | Retain scope · Integration owner | 3 | C09, C10, C21, C43 |

### 14. Installed lifecycle guards and recovery

| Child | Disposition | Hours | Required prerequisites |
| --- | --- | ---: | --- |
| [C76 / #79](core-implementation-plan.md#c76-source-commit-guard-and-retained-source-evidence) | Revise scope | 3 | C28, C29, C31, C35, C38, C39, C40, C41, C42, C62, C63 |
| [C79 / #80](core-implementation-plan.md#c79-test-and-review-exit-composites-with-atomic-signoff) | Revise scope | 4 | C76, C35, C38, C39, C42, C62, C91, C102, C103 |
| [C78 / #81](core-implementation-plan.md#c78-installed-transition-explanation-and-unknown-guards) | Revise scope · Integration owner | 4 | C18, C28, C29, C62, C76, C79, C92 |
| [C75 / #82](core-implementation-plan.md#c75-plan-entry-graduation-and-provenance-reconciliation) | Revise scope | 3.5 | C72, C21, C22, C28, C31, C64, C63, C76, C79 |
| C102 | New · Same-attempt Review to Dev rework | 3.5 | C28, C31, C38 |
| C103 | New · Uncertain-merge and post-delivery recovery fence | 3.5 | C39, C31, C29 |

### 15. Managed branch and draft resources

| Child | Disposition | Hours | Required prerequisites |
| --- | --- | ---: | --- |
| [C81 / #234](2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c81) | Revise scope | 4 | C16, C20, C22, C43, C64, C80 |
| [C82 / #235](2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c82) | Revise scope | 3 | C75, C81 |
| [C84 / #236](2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c84) | Retain scope | 3.5 | C81 |
| [C83 / #237](2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c83) | Revise scope | 4 | C82, C84, C97, C94 |
| C96 | New · Provision an integration resource in Plan · Integration owner | 4 | C83, C62, C94 |
| C97 | New · Durable transition preparation and repin | 3.5 | C28, C43, C91 |

### 16. Legacy adoption and workflow cutover

| Child | Disposition | Hours | Required prerequisites |
| --- | --- | ---: | --- |
| [C77 / #78](core-implementation-plan.md#c77-legacy-kind-normalization-and-unresolved-inventory) | Retain scope | 2.5 | C03, C54 |
| [C46 / #53](core-implementation-plan.md#c46-legacy-inventory-and-deterministic-v0-adapters) | Revise scope | 4 | C03, C06, C25, C58, C72, C77 |
| [C47 / #54](core-implementation-plan.md#c47-stable-legacy-adoption-preparation) | Revise scope | 3 | C07, C11, C46 |
| [C48 / #55](core-implementation-plan.md#c48-atomic-migration-apply-and-accepted-snapshot-binding) | Revise scope | 3.5 | C09, C17, C26, C47, C10 |
| [C51 / #56](core-implementation-plan.md#c51-real-reviewmigration-and-second-clone-qualification) | Revise scope · Integration owner | 4 | C48, C18 |
| C98 | New · Versioned workflow cutover and reconciliation | 4 | C48, C29, C79, C83, C11 |

### 17. Installed local lifecycle and evidence

| Child | Disposition | Hours | Required prerequisites |
| --- | --- | ---: | --- |
| [C44 / #51](core-implementation-plan.md#c44-estimate-lineage-usage-and-learning-outcomes) | Revise scope | 3 | C23, C27, C42, C14 |
| [C45 / #52](core-implementation-plan.md#c45-spike-deliverable-binding-and-validation-walk) | Retain scope | 3 | C29, C33, C35, C38, C39, C42, C16 |
| [C61 / #57](core-implementation-plan.md#c61-scoped-evidence-only-recovery-and-real-rerun) | Retain scope | 3 | C16, C27, C32, C35, C38, C42, C45 |
| [C49 / #65](core-implementation-plan.md#c49-core-only-nominal-lifecycle-qualification) | Revise scope | 4 | C12, C18, C19, C22, C26, C27, C31, C35, C38, C39, C42, C43, C44, C45, C61, C62, C21, C10, C41, C48, C63, C76, C78, C79, C91, C92, C95, C102, C103 |
| [C68 / #67](core-implementation-plan.md#c68-lifecycle-reconciliation-and-limited-rerun-qualification) | Revise scope | 3 | C49, C61 |
| [C67 / #66](core-implementation-plan.md#c67-complete-installed-cli-surface-audit) | Revise scope · Integration owner | 3 | C49, C51, C63, C44, C71, C74, C75, C76, C78, C79 |

### 18. Concurrency and recovery qualification

| Child | Disposition | Hours | Required prerequisites |
| --- | --- | ---: | --- |
| [C65 / #61](core-implementation-plan.md#c65-execution-fences-and-clock-rebuild-qualification) | Retain scope | 3.5 | C64, C30, C31, C32, C35, C38, C42, C61, C76, C79 |
| [C66 / #62](core-implementation-plan.md#c66-managed-delivery-race-and-recovery-qualification) | Retain scope · Integration owner | 3.5 | C64, C41, C42, C76, C79 |
| [C70 / #59](core-implementation-plan.md#c70-post-preflight-consumer-integration-qualification) | Retain scope | 3 | C31, C64, C27, C28, C30 |
| [C50 / #60](core-implementation-plan.md#c50-shared-store-conflicts-and-publication-recovery-qualification) | Retain scope | 3 | C64, C17, C30 |

### 19. Governed PR delivery decisions

| Child | Disposition | Hours | Required prerequisites |
| --- | --- | ---: | --- |
| [C85 / #238](2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c85) | Revise scope | 4 | C79, C83 |
| [C86 / #239](2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c86) | Revise scope | 4 | C79, C83 |
| C99 | New · Target-tip CI refresh and review equivalence | 4 | C38, C73, C80 |
| [C88 / #241](2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c88) | Revise scope | 4 | C41, C84, C86, C95, C99, C103 |
| C106 | New · Integrate governed PR decisions on trunk · Integration owner | 2 | C85, C88 |

### 20. Installed hosted delivery composition

| Child | Disposition | Hours | Required prerequisites |
| --- | --- | ---: | --- |
| [C87 / #240](2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c87) | Revise scope | 4 | C67, C82, C85, C96, C97 |
| [C89 / #242](2026-11-11-2-governed-pr-lifecycle-reconciliation.md#c89) | Revise scope | 3.5 | C87, C88, C92 |
| C100 | New · Installed configured hosted rework and closeout walk | 4 | C89, C96, C97, C99, C102, C103 |
| C101 | New · CLI/MCP parity and hosted restart refusals · Integration owner | 4 | C89, C78, C92, C100 |

### 21. Core packaging and release qualification

| Child | Disposition | Hours | Required prerequisites |
| --- | --- | ---: | --- |
| [C52 / #68](core-implementation-plan.md#c52-entrypoint-performance-and-unit-isolation-budgets) | Retain scope | 3 | C18, C49, C50, C51, C65, C66, C67, C68, C70 |
| [C59 / #69](core-implementation-plan.md#c59-cross-platform-wheel-and-ci-qualification) | Retain scope | 3 | C36, C37, C49, C50, C51, C52, C63, C65, C66, C67, C68, C70, C75 |
| [C53 / #70](core-implementation-plan.md#c53-release-workflow-tutorials-and-candidate-handoff) | Retain scope | 3.5 | C59, C03 |
| [C69 / #71](core-implementation-plan.md#c69-read-only-release-checker-and-dual-platform-workflow) | Retain scope · Integration owner | 3.5 | C53 |
| [C60 / #72](core-implementation-plan.md#c60-publish-and-qualify-the-exact-released-core) | Retain scope | 2.5 | C53, C69 |


## Optional packages and post-M1 qualification

These delivery epics use their own release authority and compatible Core API version; their publication is independent of the Core M1 release. Use the same four-to-six-child structure. Package authors can land a tested package candidate once ready. Follow-up runtime qualifications can consume a published wheel or compatible delivered producer under their owning stories.

### TIA package (four children, 15 h proposed)

| Child | Hours | Deliverable and proof |
| --- | ---: | --- |
| Extract portable input and inventory configuration | 4 | Extract the selector from AITM-specific paths and pytest assumptions. Exercise two distinct repository layouts against pinned tree and inventory inputs. |
| Preserve selected/full/fallback policy evidence | 4 | Use #423 pinned fixtures. Verify obligation selection identity and safe full fallback for unknown, stale, dynamic, and unsupported input. |
| Expose installed selector and advisory command | 3.5 | Consume Core C95's typed selection contract using a compatible fixture. Prove enabled selection and disabled or missing baseline behavior with no authority over the required hosted verifier. |
| Qualify wheel and publish independently | 3.5 | Install the exact wheel in an empty environment, replay advisory fixtures and integration contract, record provenance and compatibility, and land the package under its own release authority. |

### Agent effort and cost interoperability (five children, 18.25 h proposed)

| Child | Hours | Deliverable and proof |
| --- | ---: | --- |
| Package session-owned capture as a Core extension | 4 | Reuse existing effort capture, sanitized receipt and report paths, register compatible Core API/namespace, and verify prior standalone commands with private data retained locally. |
| Qualify the optional wheel and receipt replay | 3.5 | Install and release the compatible wheel independently. Verify explicit enablement, baseline Core without the wheel, sanitized replay, unavailable/partial coverage, and optional closeout reporting. Consume #51's supported ingress and #459's producer contract. |
| [#228](https://github.com/kburson/aitm/issues/228) | 3.75 | Retain post-release legacy timing replay and existing prerequisites. |
| [#229](https://github.com/kburson/aitm/issues/229) | 3.75 | Retain post-release native Actual qualification and existing prerequisites. |
| [#230](https://github.com/kburson/aitm/issues/230) | 3.25 | Retain live Cost qualification outside M1. Preserve #51 and #459 and qualify the installed plugin if selected in that path. |

Separately validate independent install and release boundaries against the accepted Core design. Any changed release order or scope that crosses the current #228/#229/#230 commitments returns to planning review before pickup.
