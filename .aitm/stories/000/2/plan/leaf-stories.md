# Core leaf stories

Current accepted [implementation plan](core-implementation-plan.md): publication `bd4adf06c90fcf02bf0930bbdec5d477aa951740`, raw SHA-256 `19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8`. **79 leaves / 257.5 implementation agent-hours**, all ≤4 h, P1/S. Initial Refine remains 180 h/XL/P1; prior accepted Plan was 220.5 h/70 leaves. These estimates include verification/source review, not measured throughput. [Current reconciliation receipt](leaf-reconciliation-receipt.json) and [original creation receipt](leaf-issue-receipt.json).

Separate design and plan full-file validation is complete, with complete actual fresh input retrieval verified in every round. [Design retrospective](../design/reviews/xpr-2026-11-09-core-design-fullfile/retrospective.md) and [plan retrospective](reviews/xpr-2026-11-09-core-plan-fullfile/retrospective.md). Historical reviews and their procedure audit remain unchanged in meaning; the new validations fulfill the later owner instruction.

Rows are the accepted topological order. Numeric C-key order is not execution order. Start only after predecessors' required interfaces/evidence are delivered; issue closure alone is insufficient. Every issue remains open and record Backlog. Parent decomposition is not a leaf's own Design/Plan/JIT acceptance. No implementation is authorized.

| Order | Key | Issue / record | Hours | Required predecessors |
| --- | --- | --- | --- | --- |
| 1 | [C01](core-implementation-plan.md#c01-package-foundation-and-command-result-contract) | [#3](https://github.com/kburson/aitm/issues/3) / [story](../../3/story.md) | 3.5 | — |
| 2 | [C02](core-implementation-plan.md#c02-event-envelopes-and-reducer-dispatch-invariants) | [#4](https://github.com/kburson/aitm/issues/4) / [story](../../4/story.md) | 2.5 | C01 / #3 |
| 3 | [C03](core-implementation-plan.md#c03-canonical-authored-content-and-metadata-ownership) | [#5](https://github.com/kburson/aitm/issues/5) / [story](../../5/story.md) | 3.5 | C01 / #3 |
| 4 | [C54](core-implementation-plan.md#c54-lifecycle-relationships-and-document-state-reducers) | [#6](https://github.com/kburson/aitm/issues/6) / [story](../../6/story.md) | 3.5 | C02 / #4, C03 / #5 |
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
| 17 | [C11](core-implementation-plan.md#c11-crash-resumable-init-and-reconfiguration) | [#19](https://github.com/kburson/aitm/issues/19) / [story](../../19/story.md) | 4 | C07 / #12, C09 / #17, C10 / #18 |
| 18 | [C12](core-implementation-plan.md#c12-hook-chaining-and-readiness-diagnostics) | [#20](https://github.com/kburson/aitm/issues/20) / [story](../../20/story.md) | 3 | C06 / #11, C11 / #19 |
| 19 | [C16](core-implementation-plan.md#c16-authoring-and-implementation-bindings) | [#21](https://github.com/kburson/aitm/issues/21) / [story](../../21/story.md) | 4 | C06 / #11, C07 / #12, C15 / #16 |
| 20 | [C17](core-implementation-plan.md#c17-allowlisted-sync-and-authored-conflict-resolution) | [#22](https://github.com/kburson/aitm/issues/22) / [story](../../22/story.md) | 4 | C09 / #17, C14 / #15, C16 / #21, C12 / #20 |
| 21 | [C18](core-implementation-plan.md#c18-snapshot-index-and-read-only-queries) | [#23](https://github.com/kburson/aitm/issues/23) / [story](../../23/story.md) | 3.5 | C02 / #4, C08 / #13 |
| 22 | [C19](core-implementation-plan.md#c19-ideas-drafts-and-atomic-discard) | [#24](https://github.com/kburson/aitm/issues/24) / [story](../../24/story.md) | 2.5 | C09 / #17, C15 / #16 |
| 23 | [C74](core-implementation-plan.md#c74-entity-scoped-editing-and-graduation-handoff) | [#74](https://github.com/kburson/aitm/issues/74) / [story](../../74/story.md) | 3.5 | C16 / #21, C17 / #22, C19 / #24 |
| 24 | [C20](core-implementation-plan.md#c20-semantic-identity-reservations-and-uncertain-dispatch) | [#25](https://github.com/kburson/aitm/issues/25) / [story](../../25/story.md) | 3.5 | C09 / #17, C13 / #14, C19 / #24, C74 / #74 |
| 25 | [C22](core-implementation-plan.md#c22-graduation-and-atomic-relationships) | [#26](https://github.com/kburson/aitm/issues/26) / [story](../../26/story.md) | 3.5 | C15 / #16, C20 / #25, C74 / #74 |
| 26 | [C21](core-implementation-plan.md#c21-shared-local-number-allocation) | [#27](https://github.com/kburson/aitm/issues/27) / [story](../../27/story.md) | 3.5 | C22 / #26, C17 / #22, C74 / #74 |
| 27 | [C23](core-implementation-plan.md#c23-activity-eligibility-and-implementation-clock-fold) | [#28](https://github.com/kburson/aitm/issues/28) / [story](../../28/story.md) | 3.5 | C02 / #4, C13 / #14 |
| 28 | [C24](core-implementation-plan.md#c24-portable-review-schemas-and-patch-reconstruction) | [#29](https://github.com/kburson/aitm/issues/29) / [story](../../29/story.md) | 3 | C02 / #4, C03 / #5, C56 / #8 |
| 29 | [C33](core-implementation-plan.md#c33-private-immutable-input-capture) | [#30](https://github.com/kburson/aitm/issues/30) / [story](../../30/story.md) | 3 | C07 / #12, C16 / #21 |
| 30 | [C34](core-implementation-plan.md#c34-offline-environment-provisioning-and-cache-identity) | [#31](https://github.com/kburson/aitm/issues/31) / [story](../../31/story.md) | 3 | C33 / #30 |
| 31 | [C57](core-implementation-plan.md#c57-review-finding-closure-topology-and-policy-assurance) | [#32](https://github.com/kburson/aitm/issues/32) / [story](../../32/story.md) | 2.5 | C24 / #29 |
| 32 | [C58](core-implementation-plan.md#c58-native-review-lineage-and-timing-anchor-adapters) | [#33](https://github.com/kburson/aitm/issues/33) / [story](../../33/story.md) | 2.5 | C57 / #32 |
| 33 | [C25](core-implementation-plan.md#c25-live-review-capsules-and-qualified-turn-timing) | [#34](https://github.com/kburson/aitm/issues/34) / [story](../../34/story.md) | 3 | C09 / #17, C23 / #28, C58 / #33 |
| 34 | [C26](core-implementation-plan.md#c26-cas-review-import-and-exact-content-acceptance) | [#35](https://github.com/kburson/aitm/issues/35) / [story](../../35/story.md) | 3.5 | C14 / #15, C17 / #22, C25 / #34, C58 / #33 |
| 35 | [C27](core-implementation-plan.md#c27-attempts-jit-coverage-and-estimates) | [#36](https://github.com/kburson/aitm/issues/36) / [story](../../36/story.md) | 3 | C16 / #21, C23 / #28, C26 / #35 |
| 36 | [C72](core-implementation-plan.md#c72-typed-decomposition-descriptors-and-applicability) | [#75](https://github.com/kburson/aitm/issues/75) / [story](../../75/story.md) | 3.5 | C03 / #5, C07 / #12, C20 / #25, C26 / #35, C27 / #36 |
| 37 | [C28](core-implementation-plan.md#c28-state-transitions-and-atomic-guard-outcomes) | [#37](https://github.com/kburson/aitm/issues/37) / [story](../../37/story.md) | 4 | C15 / #16, C22 / #26, C26 / #35, C27 / #36, C17 / #22, C21 / #27, C09 / #17, C72 / #75 |
| 38 | [C71](core-implementation-plan.md#c71-bounded-refine-split-and-kind-invalidation) | [#76](https://github.com/kburson/aitm/issues/76) / [story](../../76/story.md) | 3.5 | C28 / #37, C22 / #26, C26 / #35, C27 / #36 |
| 39 | [C29](core-implementation-plan.md#c29-kind-specific-guards-and-terminal-dispositions) | [#38](https://github.com/kburson/aitm/issues/38) / [story](../../38/story.md) | 4 | C28 / #37, C71 / #76 |
| 40 | [C30](core-implementation-plan.md#c30-expansion-reservation-and-resolution) | [#39](https://github.com/kburson/aitm/issues/39) / [story](../../39/story.md) | 4 | C20 / #25, C21 / #27, C22 / #26, C23 / #28, C28 / #37, C29 / #38 |
| 41 | [C31](core-implementation-plan.md#c31-trip-ordering-replan-decisions-and-human-pivots) | [#40](https://github.com/kburson/aitm/issues/40) / [story](../../40/story.md) | 4 | C23 / #28, C27 / #36, C28 / #37, C30 / #39, C14 / #15, C17 / #22, C71 / #76, C74 / #74, C29 / #38 |
| 42 | [C32](core-implementation-plan.md#c32-single-use-execution-admission-and-cancellation) | [#41](https://github.com/kburson/aitm/issues/41) / [story](../../41/story.md) | 3.5 | C09 / #17, C16 / #21, C31 / #40 |
| 43 | [C35](core-implementation-plan.md#c35-captured-export-test-execution-and-receipts) | [#42](https://github.com/kburson/aitm/issues/42) / [story](../../42/story.md) | 3 | C12 / #20, C32 / #41, C34 / #31, C31 / #40 |
| 44 | [C73](core-implementation-plan.md#c73-source-review-envelope-and-independence-validation) | [#77](https://github.com/kburson/aitm/issues/77) / [story](../../77/story.md) | 3 | C07 / #12, C16 / #21, C56 / #8, C57 / #32 |
| 45 | [C36](core-implementation-plan.md#c36-macos-contained-lane-probe-and-profile) | [#43](https://github.com/kburson/aitm/issues/43) / [story](../../43/story.md) | 3.5 | C35 / #42 |
| 46 | [C37](core-implementation-plan.md#c37-linux-contained-lane-probe-and-profile) | [#44](https://github.com/kburson/aitm/issues/44) / [story](../../44/story.md) | 3.5 | C35 / #42 |
| 47 | [C38](core-implementation-plan.md#c38-source-review-evidence-and-effective-pass-activation) | [#45](https://github.com/kburson/aitm/issues/45) / [story](../../45/story.md) | 3.5 | C29 / #38, C35 / #42, C73 / #77 |
| 48 | [C39](core-implementation-plan.md#c39-positive-delivery-observation-and-archival-proof) | [#46](https://github.com/kburson/aitm/issues/46) / [story](../../46/story.md) | 3.5 | C38 / #45 |
| 49 | [C40](core-implementation-plan.md#c40-reviewed-squash-and-rebase-transformation-plans) | [#47](https://github.com/kburson/aitm/issues/47) / [story](../../47/story.md) | 3 | C39 / #46 |
| 50 | [C41](core-implementation-plan.md#c41-admitted-target-mutation-and-exact-result-recovery) | [#48](https://github.com/kburson/aitm/issues/48) / [story](../../48/story.md) | 3.5 | C32 / #41, C40 / #47, C06 / #11, C39 / #46 |
| 51 | [C42](core-implementation-plan.md#c42-atomic-sign-off-and-retained-evidence-reconstruction) | [#49](https://github.com/kburson/aitm/issues/49) / [story](../../49/story.md) | 3.5 | C29 / #38, C38 / #45, C39 / #46 |
| 52 | [C43](core-implementation-plan.md#c43-durable-resident-action-queue-and-replay) | [#50](https://github.com/kburson/aitm/issues/50) / [story](../../50/story.md) | 3 | C09 / #17, C13 / #14, C17 / #22, C28 / #37, C35 / #42, C31 / #40, C74 / #74 |
| 53 | [C44](core-implementation-plan.md#c44-estimate-lineage-usage-and-learning-outcomes) | [#51](https://github.com/kburson/aitm/issues/51) / [story](../../51/story.md) | 2.5 | C23 / #28, C27 / #36, C42 / #49 |
| 54 | [C45](core-implementation-plan.md#c45-spike-deliverable-binding-and-validation-walk) | [#52](https://github.com/kburson/aitm/issues/52) / [story](../../52/story.md) | 3 | C29 / #38, C33 / #30, C35 / #42, C38 / #45, C39 / #46, C42 / #49, C16 / #21 |
| 55 | [C77](core-implementation-plan.md#c77-legacy-kind-normalization-and-unresolved-inventory) | [#78](https://github.com/kburson/aitm/issues/78) / [story](../../78/story.md) | 2.5 | C03 / #5, C54 / #6 |
| 56 | [C46](core-implementation-plan.md#c46-legacy-inventory-and-deterministic-v0-adapters) | [#53](https://github.com/kburson/aitm/issues/53) / [story](../../53/story.md) | 4 | C03 / #5, C06 / #11, C25 / #34, C58 / #33, C72 / #75, C77 / #78 |
| 57 | [C47](core-implementation-plan.md#c47-stable-legacy-adoption-preparation) | [#54](https://github.com/kburson/aitm/issues/54) / [story](../../54/story.md) | 3 | C07 / #12, C11 / #19, C46 / #53 |
| 58 | [C48](core-implementation-plan.md#c48-atomic-migration-apply-and-accepted-snapshot-binding) | [#55](https://github.com/kburson/aitm/issues/55) / [story](../../55/story.md) | 3.5 | C09 / #17, C17 / #22, C26 / #35, C47 / #54, C10 / #18 |
| 59 | [C51](core-implementation-plan.md#c51-real-reviewmigration-and-second-clone-qualification) | [#56](https://github.com/kburson/aitm/issues/56) / [story](../../56/story.md) | 3.5 | C48 / #55, C18 / #23 |
| 60 | [C61](core-implementation-plan.md#c61-scoped-evidence-only-recovery-and-real-rerun) | [#57](https://github.com/kburson/aitm/issues/57) / [story](../../57/story.md) | 3 | C16 / #21, C27 / #36, C32 / #41, C35 / #42, C38 / #45, C42 / #49, C45 / #52 |
| 61 | [C64](core-implementation-plan.md#c64-deterministic-two-clone-qualification-fixtures) | [#58](https://github.com/kburson/aitm/issues/58) / [story](../../58/story.md) | 2.5 | C09 / #17, C10 / #18, C21 / #27, C43 / #50 |
| 62 | [C70](core-implementation-plan.md#c70-post-preflight-consumer-integration-qualification) | [#59](https://github.com/kburson/aitm/issues/59) / [story](../../59/story.md) | 3 | C31 / #40, C64 / #58, C27 / #36, C28 / #37, C30 / #39 |
| 63 | [C50](core-implementation-plan.md#c50-shared-store-conflicts-and-publication-recovery-qualification) | [#60](https://github.com/kburson/aitm/issues/60) / [story](../../60/story.md) | 3 | C64 / #58, C17 / #22, C30 / #39 |
| 64 | [C62](core-implementation-plan.md#c62-epic-aggregation-and-scope-resolution-checkpoint) | [#63](https://github.com/kburson/aitm/issues/63) / [story](../../63/story.md) | 3 | C22 / #26, C29 / #38, C38 / #45, C42 / #49, C43 / #50 |
| 65 | [C63](core-implementation-plan.md#c63-installed-extension-discovery-and-commandinit-composition) | [#64](https://github.com/kburson/aitm/issues/64) / [story](../../64/story.md) | 3 | C12 / #20, C13 / #14, C14 / #15, C43 / #50, C01 / #3, C62 / #63 |
| 66 | [C76](core-implementation-plan.md#c76-source-commit-guard-and-retained-source-evidence) | [#79](https://github.com/kburson/aitm/issues/79) / [story](../../79/story.md) | 3 | C28 / #37, C29 / #38, C31 / #40, C35 / #42, C38 / #45, C39 / #46, C40 / #47, C41 / #48, C42 / #49, C62 / #63, C63 / #64 |
| 67 | [C79](core-implementation-plan.md#c79-test-and-review-exit-composites-with-atomic-signoff) | [#80](https://github.com/kburson/aitm/issues/80) / [story](../../80/story.md) | 3 | C76 / #79, C35 / #42, C38 / #45, C39 / #46, C42 / #49, C62 / #63 |
| 68 | [C65](core-implementation-plan.md#c65-execution-fences-and-clock-rebuild-qualification) | [#61](https://github.com/kburson/aitm/issues/61) / [story](../../61/story.md) | 3.5 | C64 / #58, C30 / #39, C31 / #40, C32 / #41, C35 / #42, C38 / #45, C42 / #49, C61 / #57, C76 / #79, C79 / #80 |
| 69 | [C66](core-implementation-plan.md#c66-managed-delivery-race-and-recovery-qualification) | [#62](https://github.com/kburson/aitm/issues/62) / [story](../../62/story.md) | 3 | C64 / #58, C41 / #48, C42 / #49, C76 / #79, C79 / #80 |
| 70 | [C78](core-implementation-plan.md#c78-installed-transition-explanation-and-unknown-guards) | [#81](https://github.com/kburson/aitm/issues/81) / [story](../../81/story.md) | 3 | C18 / #23, C28 / #37, C29 / #38, C62 / #63, C76 / #79, C79 / #80 |
| 71 | [C49](core-implementation-plan.md#c49-core-only-nominal-lifecycle-qualification) | [#65](https://github.com/kburson/aitm/issues/65) / [story](../../65/story.md) | 3 | C12 / #20, C18 / #23, C19 / #24, C22 / #26, C26 / #35, C27 / #36, C31 / #40, C35 / #42, C38 / #45, C39 / #46, C42 / #49, C43 / #50, C44 / #51, C45 / #52, C61 / #57, C62 / #63, C21 / #27, C10 / #18, C41 / #48, C48 / #55, C63 / #64, C76 / #79, C78 / #81, C79 / #80 |
| 72 | [C75](core-implementation-plan.md#c75-plan-entry-graduation-and-provenance-reconciliation) | [#82](https://github.com/kburson/aitm/issues/82) / [story](../../82/story.md) | 3.5 | C72 / #75, C21 / #27, C22 / #26, C28 / #37, C31 / #40, C64 / #58, C63 / #64, C76 / #79, C79 / #80 |
| 73 | [C67](core-implementation-plan.md#c67-complete-installed-cli-surface-audit) | [#66](https://github.com/kburson/aitm/issues/66) / [story](../../66/story.md) | 2.5 | C49 / #65, C51 / #56, C63 / #64, C44 / #51, C71 / #76, C74 / #74, C75 / #82, C76 / #79, C78 / #81, C79 / #80 |
| 74 | [C68](core-implementation-plan.md#c68-lifecycle-reconciliation-and-limited-rerun-qualification) | [#67](https://github.com/kburson/aitm/issues/67) / [story](../../67/story.md) | 3 | C49 / #65, C61 / #57 |
| 75 | [C52](core-implementation-plan.md#c52-entrypoint-performance-and-unit-isolation-budgets) | [#68](https://github.com/kburson/aitm/issues/68) / [story](../../68/story.md) | 3 | C18 / #23, C49 / #65, C50 / #60, C51 / #56, C65 / #61, C66 / #62, C67 / #66, C68 / #67, C70 / #59 |
| 76 | [C59](core-implementation-plan.md#c59-cross-platform-wheel-and-ci-qualification) | [#69](https://github.com/kburson/aitm/issues/69) / [story](../../69/story.md) | 3 | C36 / #43, C37 / #44, C49 / #65, C50 / #60, C51 / #56, C52 / #68, C63 / #64, C65 / #61, C66 / #62, C67 / #66, C68 / #67, C70 / #59, C75 / #82 |
| 77 | [C53](core-implementation-plan.md#c53-release-workflow-tutorials-and-candidate-handoff) | [#70](https://github.com/kburson/aitm/issues/70) / [story](../../70/story.md) | 3.5 | C59 / #69, C03 / #5 |
| 78 | [C69](core-implementation-plan.md#c69-read-only-release-checker-and-dual-platform-workflow) | [#71](https://github.com/kburson/aitm/issues/71) / [story](../../71/story.md) | 3 | C53 / #70 |
| 79 | [C60](core-implementation-plan.md#c60-publish-and-qualify-the-exact-released-core) | [#72](https://github.com/kburson/aitm/issues/72) / [story](../../72/story.md) | 2.5 | C53 / #70, C69 / #71 |

## Dependency waves and independent work

Earliest-ready waves reflect dependency and shared-file ordering, not promised calendar concurrency. Platform/release capability and actual delivery evidence remain prerequisites.

- Wave 1: C01 / #3.
- Wave 2: C02 / #4, C03 / #5.
- Wave 3: C54 / #6, C55 / #7.
- Wave 4: C56 / #8, C77 / #78.
- Wave 5: C04 / #9, C24 / #29.
- Wave 6: C05 / #10, C15 / #16, C57 / #32.
- Wave 7: C06 / #11, C58 / #33.
- Wave 8: C07 / #12.
- Wave 9: C08 / #13, C13 / #14, C16 / #21.
- Wave 10: C14 / #15, C18 / #23, C23 / #28, C33 / #30, C73 / #77.
- Wave 11: C09 / #17, C34 / #31.
- Wave 12: C10 / #18, C19 / #24, C25 / #34.
- Wave 13: C11 / #19.
- Wave 14: C12 / #20.
- Wave 15: C17 / #22.
- Wave 16: C74 / #74, C26 / #35.
- Wave 17: C20 / #25, C27 / #36.
- Wave 18: C22 / #26, C72 / #75.
- Wave 19: C21 / #27, C46 / #53.
- Wave 20: C28 / #37, C47 / #54.
- Wave 21: C71 / #76, C48 / #55.
- Wave 22: C29 / #38, C51 / #56.
- Wave 23: C30 / #39.
- Wave 24: C31 / #40.
- Wave 25: C32 / #41.
- Wave 26: C35 / #42.
- Wave 27: C36 / #43, C37 / #44, C38 / #45, C43 / #50.
- Wave 28: C39 / #46, C64 / #58.
- Wave 29: C40 / #47, C42 / #49, C70 / #59, C50 / #60.
- Wave 30: C41 / #48, C44 / #51, C45 / #52, C62 / #63.
- Wave 31: C61 / #57, C63 / #64.
- Wave 32: C76 / #79.
- Wave 33: C79 / #80.
- Wave 34: C65 / #61, C66 / #62, C78 / #81, C75 / #82.
- Wave 35: C49 / #65.
- Wave 36: C67 / #66, C68 / #67.
- Wave 37: C52 / #68.
- Wave 38: C59 / #69.
- Wave 39: C53 / #70.
- Wave 40: C69 / #71.
- Wave 41: C60 / #72.

## Release, migration and owner choices

C53 prepares release, C69 delivers the read-only observer, and C60 needs separate release authority and exact released-wheel evidence for master C5. Production C6 requires M2 GitHub identity-provider readiness, explicit supported production review policy, bounded declaration/freeze, released checkout ownership, forward recovery, fresh-clone/index parity and real issuer reconciliation. Bootstrap remains in use until verified cutover. No release, adoption or epic closure is claimed.

Global review depth/sequence, expansion completion interpretation, second-trip cap, hosted every-push audit, later provider/harness details and full-install name remain owner-open. Each child still needs its own applicable Design/Plan/JIT and execution authority. New requirements or implausible ≤4 h bounds require replan/review, not acceptance relaxation.
