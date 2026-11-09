# Core leaf stories

Accepted decomposition: [core-implementation-plan.md](core-implementation-plan.md), XPR publication `55b94bbe77a19002ff077c122560cf185652d25c`, raw SHA-256 `2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd`. **70 leaves, 220.5 implementation agent-hours; every leaf ≤4 h.** Initial Refine remains 180 h / XL / P1. Leaf size S and priority P1 are scoped planning labels with rationale in each record.

Rows are the accepted topological execution order. Numeric C-key order is not execution order. All native issue dependencies below include required shared-file predecessors. Start a leaf only after its predecessors' required interfaces/evidence are delivered; issue closure alone is insufficient. Planning acceptance does not authorize implementation.

| Order | Plan key | Issue / record | Hours | Required predecessors |
| --- | --- | --- | --- | --- |
| 1 | [C01](core-implementation-plan.md#c01-package-foundation-and-command-result-contract) | [#3](https://github.com/kburson/aitm/issues/3) / [story](../../3/story.md) | 3.5 | — |
| 2 | [C02](core-implementation-plan.md#c02-event-envelopes-and-reducer-dispatch-invariants) | [#4](https://github.com/kburson/aitm/issues/4) / [story](../../4/story.md) | 2.5 | C01 / #3 |
| 3 | [C03](core-implementation-plan.md#c03-canonical-authored-content-and-metadata-ownership) | [#5](https://github.com/kburson/aitm/issues/5) / [story](../../5/story.md) | 3 | C01 / #3 |
| 4 | [C54](core-implementation-plan.md#c54-lifecycle-relationships-and-document-state-reducers) | [#6](https://github.com/kburson/aitm/issues/6) / [story](../../6/story.md) | 3 | C02 / #4, C03 / #5 |
| 5 | [C55](core-implementation-plan.md#c55-attempt-execution-and-clock-boundary-reducers) | [#7](https://github.com/kburson/aitm/issues/7) / [story](../../7/story.md) | 3.5 | C02 / #4 |
| 6 | [C56](core-implementation-plan.md#c56-evidence-action-and-provenance-reducers-with-composition) | [#8](https://github.com/kburson/aitm/issues/8) / [story](../../8/story.md) | 3 | C02 / #4, C54 / #6, C55 / #7 |
| 7 | [C04](core-implementation-plan.md#c04-typed-operations-and-memorybackend-semantics) | [#9](https://github.com/kburson/aitm/issues/9) / [story](../../9/story.md) | 4 | C02 / #4, C54 / #6, C55 / #7, C56 / #8 |
| 8 | [C05](core-implementation-plan.md#c05-git-snapshot-reads-and-atomic-operation-commits) | [#10](https://github.com/kburson/aitm/issues/10) / [story](../../10/story.md) | 4 | C04 / #9 |
| 9 | [C06](core-implementation-plan.md#c06-planning-history-validation-and-worktree-exclusion) | [#11](https://github.com/kburson/aitm/issues/11) / [story](../../11/story.md) | 3.5 | C05 / #10, C01 / #3 |
| 10 | [C07](core-implementation-plan.md#c07-committed-configuration-and-routing-anchors) | [#12](https://github.com/kburson/aitm/issues/12) / [story](../../12/story.md) | 3 | C03 / #5, C06 / #11 |
| 11 | [C08](core-implementation-plan.md#c08-candidate-fetch-and-shared-history-continuity) | [#13](https://github.com/kburson/aitm/issues/13) / [story](../../13/story.md) | 3.5 | C06 / #11, C07 / #12 |
| 12 | [C13](core-implementation-plan.md#c13-extension-and-provider-registration-contracts) | [#14](https://github.com/kburson/aitm/issues/14) / [story](../../14/story.md) | 3 | C02 / #4, C07 / #12 |
| 13 | [C14](core-implementation-plan.md#c14-constrained-extension-writes-and-retained-unknown-data) | [#15](https://github.com/kburson/aitm/issues/15) / [story](../../15/story.md) | 3 | C04 / #9, C13 / #14, C08 / #13 |
| 14 | [C15](core-implementation-plan.md#c15-deterministic-views-and-structured-descriptions) | [#16](https://github.com/kburson/aitm/issues/16) / [story](../../16/story.md) | 2.5 | C02 / #4, C03 / #5, C04 / #9 |
| 15 | [C09](core-implementation-plan.md#c09-publication-replay-and-conflict-recovery) | [#17](https://github.com/kburson/aitm/issues/17) / [story](../../17/story.md) | 4 | C04 / #9, C08 / #13, C15 / #16, C14 / #15 |
| 16 | [C10](core-implementation-plan.md#c10-forward-repair-from-maximal-valid-prefix) | [#18](https://github.com/kburson/aitm/issues/18) / [story](../../18/story.md) | 4 | C08 / #13, C09 / #17, C06 / #11 |
| 17 | [C11](core-implementation-plan.md#c11-crash-resumable-init-and-reconfiguration) | [#19](https://github.com/kburson/aitm/issues/19) / [story](../../19/story.md) | 3.5 | C07 / #12, C09 / #17, C10 / #18 |
| 18 | [C12](core-implementation-plan.md#c12-hook-chaining-and-readiness-diagnostics) | [#20](https://github.com/kburson/aitm/issues/20) / [story](../../20/story.md) | 3 | C06 / #11, C11 / #19 |
| 19 | [C16](core-implementation-plan.md#c16-authoring-and-implementation-bindings) | [#21](https://github.com/kburson/aitm/issues/21) / [story](../../21/story.md) | 3.5 | C06 / #11, C07 / #12, C15 / #16 |
| 20 | [C17](core-implementation-plan.md#c17-allowlisted-sync-and-authored-conflict-resolution) | [#22](https://github.com/kburson/aitm/issues/22) / [story](../../22/story.md) | 3 | C09 / #17, C14 / #15, C16 / #21, C12 / #20 |
| 21 | [C18](core-implementation-plan.md#c18-snapshot-index-and-read-only-queries) | [#23](https://github.com/kburson/aitm/issues/23) / [story](../../23/story.md) | 3.5 | C02 / #4, C08 / #13 |
| 22 | [C19](core-implementation-plan.md#c19-ideas-drafts-and-atomic-discard) | [#24](https://github.com/kburson/aitm/issues/24) / [story](../../24/story.md) | 2.5 | C09 / #17, C15 / #16 |
| 23 | [C20](core-implementation-plan.md#c20-semantic-identity-reservations-and-uncertain-dispatch) | [#25](https://github.com/kburson/aitm/issues/25) / [story](../../25/story.md) | 3.5 | C09 / #17, C13 / #14, C19 / #24 |
| 24 | [C22](core-implementation-plan.md#c22-graduation-and-atomic-relationships) | [#26](https://github.com/kburson/aitm/issues/26) / [story](../../26/story.md) | 3 | C15 / #16, C20 / #25 |
| 25 | [C21](core-implementation-plan.md#c21-shared-local-number-allocation) | [#27](https://github.com/kburson/aitm/issues/27) / [story](../../27/story.md) | 3.5 | C22 / #26, C17 / #22 |
| 26 | [C23](core-implementation-plan.md#c23-activity-eligibility-and-implementation-clock-fold) | [#28](https://github.com/kburson/aitm/issues/28) / [story](../../28/story.md) | 3.5 | C02 / #4, C13 / #14 |
| 27 | [C24](core-implementation-plan.md#c24-portable-review-schemas-and-patch-reconstruction) | [#29](https://github.com/kburson/aitm/issues/29) / [story](../../29/story.md) | 3 | C02 / #4, C03 / #5, C56 / #8 |
| 28 | [C33](core-implementation-plan.md#c33-private-immutable-input-capture) | [#30](https://github.com/kburson/aitm/issues/30) / [story](../../30/story.md) | 3 | C07 / #12, C16 / #21 |
| 29 | [C34](core-implementation-plan.md#c34-offline-environment-provisioning-and-cache-identity) | [#31](https://github.com/kburson/aitm/issues/31) / [story](../../31/story.md) | 3 | C33 / #30 |
| 30 | [C57](core-implementation-plan.md#c57-review-finding-closure-topology-and-policy-assurance) | [#32](https://github.com/kburson/aitm/issues/32) / [story](../../32/story.md) | 2.5 | C24 / #29 |
| 31 | [C58](core-implementation-plan.md#c58-native-review-lineage-and-timing-anchor-adapters) | [#33](https://github.com/kburson/aitm/issues/33) / [story](../../33/story.md) | 2.5 | C57 / #32 |
| 32 | [C25](core-implementation-plan.md#c25-live-review-capsules-and-qualified-turn-timing) | [#34](https://github.com/kburson/aitm/issues/34) / [story](../../34/story.md) | 3 | C09 / #17, C23 / #28, C58 / #33 |
| 33 | [C26](core-implementation-plan.md#c26-cas-review-import-and-exact-content-acceptance) | [#35](https://github.com/kburson/aitm/issues/35) / [story](../../35/story.md) | 3.5 | C14 / #15, C17 / #22, C25 / #34, C58 / #33 |
| 34 | [C27](core-implementation-plan.md#c27-attempts-jit-coverage-and-estimates) | [#36](https://github.com/kburson/aitm/issues/36) / [story](../../36/story.md) | 3 | C16 / #21, C23 / #28, C26 / #35 |
| 35 | [C28](core-implementation-plan.md#c28-state-transitions-and-atomic-guard-outcomes) | [#37](https://github.com/kburson/aitm/issues/37) / [story](../../37/story.md) | 3.5 | C15 / #16, C22 / #26, C26 / #35, C27 / #36, C17 / #22, C21 / #27, C09 / #17 |
| 36 | [C29](core-implementation-plan.md#c29-kind-specific-guards-and-terminal-dispositions) | [#38](https://github.com/kburson/aitm/issues/38) / [story](../../38/story.md) | 3 | C28 / #37 |
| 37 | [C30](core-implementation-plan.md#c30-expansion-reservation-and-resolution) | [#39](https://github.com/kburson/aitm/issues/39) / [story](../../39/story.md) | 3.5 | C20 / #25, C21 / #27, C22 / #26, C23 / #28, C28 / #37 |
| 38 | [C31](core-implementation-plan.md#c31-trip-ordering-replan-decisions-and-human-pivots) | [#40](https://github.com/kburson/aitm/issues/40) / [story](../../40/story.md) | 3.5 | C23 / #28, C27 / #36, C28 / #37, C30 / #39, C14 / #15, C17 / #22 |
| 39 | [C32](core-implementation-plan.md#c32-single-use-execution-admission-and-cancellation) | [#41](https://github.com/kburson/aitm/issues/41) / [story](../../41/story.md) | 3.5 | C09 / #17, C16 / #21, C31 / #40 |
| 40 | [C35](core-implementation-plan.md#c35-captured-export-test-execution-and-receipts) | [#42](https://github.com/kburson/aitm/issues/42) / [story](../../42/story.md) | 3 | C12 / #20, C32 / #41, C34 / #31, C31 / #40 |
| 41 | [C36](core-implementation-plan.md#c36-macos-contained-lane-probe-and-profile) | [#43](https://github.com/kburson/aitm/issues/43) / [story](../../43/story.md) | 3.5 | C35 / #42 |
| 42 | [C37](core-implementation-plan.md#c37-linux-contained-lane-probe-and-profile) | [#44](https://github.com/kburson/aitm/issues/44) / [story](../../44/story.md) | 3.5 | C35 / #42 |
| 43 | [C38](core-implementation-plan.md#c38-source-review-evidence-and-effective-pass-activation) | [#45](https://github.com/kburson/aitm/issues/45) / [story](../../45/story.md) | 3 | C29 / #38, C35 / #42 |
| 44 | [C39](core-implementation-plan.md#c39-positive-delivery-observation-and-archival-proof) | [#46](https://github.com/kburson/aitm/issues/46) / [story](../../46/story.md) | 3.5 | C38 / #45 |
| 45 | [C40](core-implementation-plan.md#c40-reviewed-squash-and-rebase-transformation-plans) | [#47](https://github.com/kburson/aitm/issues/47) / [story](../../47/story.md) | 3 | C39 / #46 |
| 46 | [C41](core-implementation-plan.md#c41-admitted-target-mutation-and-exact-result-recovery) | [#48](https://github.com/kburson/aitm/issues/48) / [story](../../48/story.md) | 3.5 | C32 / #41, C40 / #47, C06 / #11, C39 / #46 |
| 47 | [C42](core-implementation-plan.md#c42-atomic-sign-off-and-retained-evidence-reconstruction) | [#49](https://github.com/kburson/aitm/issues/49) / [story](../../49/story.md) | 3.5 | C29 / #38, C38 / #45, C39 / #46 |
| 48 | [C43](core-implementation-plan.md#c43-durable-resident-action-queue-and-replay) | [#50](https://github.com/kburson/aitm/issues/50) / [story](../../50/story.md) | 3 | C09 / #17, C13 / #14, C17 / #22, C28 / #37, C35 / #42, C31 / #40 |
| 49 | [C44](core-implementation-plan.md#c44-estimate-lineage-usage-and-learning-outcomes) | [#51](https://github.com/kburson/aitm/issues/51) / [story](../../51/story.md) | 2.5 | C23 / #28, C27 / #36, C42 / #49 |
| 50 | [C45](core-implementation-plan.md#c45-spike-deliverable-binding-and-validation-walk) | [#52](https://github.com/kburson/aitm/issues/52) / [story](../../52/story.md) | 3 | C29 / #38, C33 / #30, C35 / #42, C38 / #45, C39 / #46, C42 / #49, C16 / #21 |
| 51 | [C46](core-implementation-plan.md#c46-legacy-inventory-and-deterministic-v0-adapters) | [#53](https://github.com/kburson/aitm/issues/53) / [story](../../53/story.md) | 3 | C03 / #5, C06 / #11, C25 / #34, C58 / #33 |
| 52 | [C47](core-implementation-plan.md#c47-stable-legacy-adoption-preparation) | [#54](https://github.com/kburson/aitm/issues/54) / [story](../../54/story.md) | 3 | C07 / #12, C11 / #19, C46 / #53 |
| 53 | [C48](core-implementation-plan.md#c48-atomic-migration-apply-and-accepted-snapshot-binding) | [#55](https://github.com/kburson/aitm/issues/55) / [story](../../55/story.md) | 3.5 | C09 / #17, C17 / #22, C26 / #35, C47 / #54, C10 / #18 |
| 54 | [C51](core-implementation-plan.md#c51-real-reviewmigration-and-second-clone-qualification) | [#56](https://github.com/kburson/aitm/issues/56) / [story](../../56/story.md) | 3 | C48 / #55, C18 / #23 |
| 55 | [C61](core-implementation-plan.md#c61-scoped-evidence-only-recovery-and-real-rerun) | [#57](https://github.com/kburson/aitm/issues/57) / [story](../../57/story.md) | 3 | C16 / #21, C27 / #36, C32 / #41, C35 / #42, C38 / #45, C42 / #49, C45 / #52 |
| 56 | [C64](core-implementation-plan.md#c64-deterministic-two-clone-qualification-fixtures) | [#58](https://github.com/kburson/aitm/issues/58) / [story](../../58/story.md) | 2.5 | C09 / #17, C10 / #18, C21 / #27, C43 / #50 |
| 57 | [C70](core-implementation-plan.md#c70-post-preflight-consumer-integration-qualification) | [#59](https://github.com/kburson/aitm/issues/59) / [story](../../59/story.md) | 3 | C31 / #40, C64 / #58, C27 / #36, C28 / #37, C30 / #39 |
| 58 | [C50](core-implementation-plan.md#c50-shared-store-conflicts-and-publication-recovery-qualification) | [#60](https://github.com/kburson/aitm/issues/60) / [story](../../60/story.md) | 3 | C64 / #58, C17 / #22, C30 / #39 |
| 59 | [C65](core-implementation-plan.md#c65-execution-fences-and-clock-rebuild-qualification) | [#61](https://github.com/kburson/aitm/issues/61) / [story](../../61/story.md) | 3.5 | C64 / #58, C30 / #39, C31 / #40, C32 / #41, C35 / #42, C38 / #45, C42 / #49, C61 / #57 |
| 60 | [C66](core-implementation-plan.md#c66-managed-delivery-race-and-recovery-qualification) | [#62](https://github.com/kburson/aitm/issues/62) / [story](../../62/story.md) | 3 | C64 / #58, C41 / #48, C42 / #49 |
| 61 | [C62](core-implementation-plan.md#c62-epic-aggregation-and-scope-resolution-checkpoint) | [#63](https://github.com/kburson/aitm/issues/63) / [story](../../63/story.md) | 2.5 | C22 / #26, C29 / #38, C38 / #45, C42 / #49 |
| 62 | [C63](core-implementation-plan.md#c63-installed-extension-discovery-and-commandinit-composition) | [#64](https://github.com/kburson/aitm/issues/64) / [story](../../64/story.md) | 3 | C12 / #20, C13 / #14, C14 / #15, C43 / #50, C01 / #3 |
| 63 | [C49](core-implementation-plan.md#c49-core-only-nominal-lifecycle-qualification) | [#65](https://github.com/kburson/aitm/issues/65) / [story](../../65/story.md) | 3 | C12 / #20, C18 / #23, C19 / #24, C22 / #26, C26 / #35, C27 / #36, C31 / #40, C35 / #42, C38 / #45, C39 / #46, C42 / #49, C43 / #50, C44 / #51, C45 / #52, C61 / #57, C62 / #63, C21 / #27, C10 / #18, C41 / #48, C48 / #55, C63 / #64 |
| 64 | [C67](core-implementation-plan.md#c67-complete-installed-cli-surface-audit) | [#66](https://github.com/kburson/aitm/issues/66) / [story](../../66/story.md) | 2.5 | C49 / #65, C51 / #56, C63 / #64, C44 / #51 |
| 65 | [C68](core-implementation-plan.md#c68-lifecycle-reconciliation-and-limited-rerun-qualification) | [#67](https://github.com/kburson/aitm/issues/67) / [story](../../67/story.md) | 3 | C49 / #65, C61 / #57 |
| 66 | [C52](core-implementation-plan.md#c52-entrypoint-performance-and-unit-isolation-budgets) | [#68](https://github.com/kburson/aitm/issues/68) / [story](../../68/story.md) | 3 | C18 / #23, C49 / #65, C50 / #60, C51 / #56, C65 / #61, C66 / #62, C67 / #66, C68 / #67, C70 / #59 |
| 67 | [C59](core-implementation-plan.md#c59-cross-platform-wheel-and-ci-qualification) | [#69](https://github.com/kburson/aitm/issues/69) / [story](../../69/story.md) | 3 | C36 / #43, C37 / #44, C49 / #65, C50 / #60, C51 / #56, C52 / #68, C63 / #64, C65 / #61, C66 / #62, C67 / #66, C68 / #67, C70 / #59 |
| 68 | [C53](core-implementation-plan.md#c53-release-workflow-tutorials-and-candidate-handoff) | [#70](https://github.com/kburson/aitm/issues/70) / [story](../../70/story.md) | 3.5 | C59 / #69, C03 / #5 |
| 69 | [C69](core-implementation-plan.md#c69-read-only-release-checker-and-dual-platform-workflow) | [#71](https://github.com/kburson/aitm/issues/71) / [story](../../71/story.md) | 3 | C53 / #70 |
| 70 | [C60](core-implementation-plan.md#c60-publish-and-qualify-the-exact-released-core) | [#72](https://github.com/kburson/aitm/issues/72) / [story](../../72/story.md) | 2.5 | C53 / #70, C69 / #71 |

## Dependency waves and independent work

These are earliest-ready DAG waves, not promised calendar concurrency. Within a wave all prerequisites must actually be delivered; shared touched paths are serialized by the accepted graph. Platform and release credentials/capabilities remain real execution prerequisites.

- Wave 1: C01 / #3.
- Wave 2: C02 / #4, C03 / #5.
- Wave 3: C54 / #6, C55 / #7.
- Wave 4: C56 / #8.
- Wave 5: C04 / #9, C24 / #29.
- Wave 6: C05 / #10, C15 / #16, C57 / #32.
- Wave 7: C06 / #11, C58 / #33.
- Wave 8: C07 / #12.
- Wave 9: C08 / #13, C13 / #14, C16 / #21.
- Wave 10: C14 / #15, C18 / #23, C23 / #28, C33 / #30.
- Wave 11: C09 / #17, C34 / #31.
- Wave 12: C10 / #18, C19 / #24, C25 / #34.
- Wave 13: C11 / #19, C20 / #25, C46 / #53.
- Wave 14: C12 / #20, C22 / #26, C47 / #54.
- Wave 15: C17 / #22.
- Wave 16: C21 / #27, C26 / #35.
- Wave 17: C27 / #36, C48 / #55.
- Wave 18: C28 / #37, C51 / #56.
- Wave 19: C29 / #38, C30 / #39.
- Wave 20: C31 / #40.
- Wave 21: C32 / #41.
- Wave 22: C35 / #42.
- Wave 23: C36 / #43, C37 / #44, C38 / #45, C43 / #50.
- Wave 24: C39 / #46, C64 / #58, C63 / #64.
- Wave 25: C40 / #47, C42 / #49, C70 / #59, C50 / #60.
- Wave 26: C41 / #48, C44 / #51, C45 / #52, C62 / #63.
- Wave 27: C61 / #57, C66 / #62.
- Wave 28: C65 / #61, C49 / #65.
- Wave 29: C67 / #66, C68 / #67.
- Wave 30: C52 / #68.
- Wave 31: C59 / #69.
- Wave 32: C53 / #70.
- Wave 33: C69 / #71.
- Wave 34: C60 / #72.

## Review reminders

- C25 / #34: Own available live/completion interfaces here; C51 composes the later C26 final importer. Earlier SAR optional reminder; do not invent a dependency cycle.
- C28 / #37: Use the declared typed preflight fixture until C31 supplies the production implementation; production attempt-bearing mutations remain unavailable meanwhile. C31 proves the representative real pipeline; C70 qualifies reconcile/provisional/expansion consumers with actual preflight and C64 fixtures.
- C59 / #69: All nested suites reuse the same prepared consumer and exact supplied wheel. Smoke must not rebuild/reinstall another candidate.
- C60 / #72: Use the delivered C69 observer and C59 isolated runner against the exact released wheel. Fixture PASS alone is not released C5 acceptance.

## Release, migration and owner decisions

C53 prepares release, C69 supplies the separately delivered read-only observer, and C60 needs later explicit release authority and complete exact released-wheel proof for master C5. Production C6 adoption remains later: GitHub identity-provider readiness, explicit supported production review policy, bounded declaration/freeze, safe checkout handoff, forward recovery, fresh-clone/index parity and actual issuer reconciliation. Bootstrap continues until that boundary. Global review depth/sequence, expansion completion interpretation, second-trip cap, hosted every-push audit, later provider/harness details and full-install name remain owner-open. None blocks completion of this authorized planning task.

The epic plan supplies parent decomposition only. Each child still needs the Design/Plan/JIT/review policy explicitly applicable when its work is authorized. All issues remain open and records Backlog; no expansion, implementation clock, runtime acceptance or product delivery is inferred.
