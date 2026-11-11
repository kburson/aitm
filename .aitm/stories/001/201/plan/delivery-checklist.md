# #201 manual delivery checklist

## Accepted pickup and Develop checkpoint

[#199](https://github.com/kburson/aitm/issues/199) is Closed Completed and Done. [PR #205](https://github.com/kburson/aitm/pull/205) delivered literal trunk `2eebb3b7f6b262d3ed4951ffde0cbcb5d3a5ade3`, tree `9899ff4990510ebc9de09566fb08efcb33f9d112`. A fresh clean locked detached baseline passed 948 product and CLI, 182 helper, Ruff, whitespace and raw 10,236/11,175 product and 778/821 helper lines. The review's baseline readback condition was verified before setting Start Date.

[Round one](2026-11-10-201-pickup-review-r1.md) held the initial artifact. [Round two](2026-11-10-201-pickup-review-r2.md) passed the [exact revised JIT](2026-11-10-201-durable-revision-succession-plan.md) at SHA-256 `302b2220f9f887e7ea55526ee043d667682b3df65f84eb357735ff8a74d3a67f`. The delivered `ScopeState.read_source` authenticates a supplied cursor and calls the provider with a cold read from the same current fixed capture limit. The real journal-level earlier-cursor fixture remains a hard gate. #201 still directly blocks #119 and #202.

Codex owns the isolated branch `codex/aitm-201-durable-revision-succession` and Close. Project Rank 226, Size M, Estimate 3.75 implementation agent-hours, Start Date November 10. At the 2.25-hour checkpoint the migration lane must be GREEN and committed and both required RED fixtures must exist. Any required split keeps a direct #119 gate.

## Test checkpoint

[PR #206](https://github.com/kburson/aitm/pull/206) read back exact head `8887c7142617014c9e3712c8b3eba22f21331cf1`, tree `eb1145db4bd3f7ab88c832c40e0ca180d335d798` and literal trunk `2eebb3b7f6b262d3ed4951ffde0cbcb5d3a5ade3`. [Hosted run 42937140018](https://github.com/kburson/aitm/actions/runs/42937140018) passed before the first source review and is retained below. Required jobs are file-checks, quality, python-base, python, collect-evidence and aitm-ci.

The exact frozen local gate passed 970 product and CLI tests and 182 helpers, Ruff, whitespace and raw coverage of 10,360/11,301 product and 778/821 helper lines. All 948 local baseline test IDs remain. The two-file migration commit `272c51484de88bb5e7f0a748c210479fd05f56e3` passed 959 product and CLI tests, 182 helpers and strict v1 compatibility. Both required native RED fixtures existed and the migration was GREEN and committed before proceeding past the reviewed checkpoint. The final integrated related suite passed 273 tests.

The full terminal fixture verifies an earlier real persisted cursor through the normal cold reread and reserves the whole batch. Every observation and native receipt settles, the exact original replays, both later edges stage, and quota is the sole remaining diagnostic keeping the earlier cursor. Other fixtures verify same-batch revision order and historic view, restart, exact archive replay without physical succession, changed original scope, disabled intermediate, transaction rollback, changed predecessor with equal successor material, two unchanged-material prefix rewrites, and a stored first-claim digest mismatch. The initial preflight held on a weak singular-reserve fixture. The full-batch replacement and additional negatives passed independent source preflight.

The v1-layout first claim authenticates the historical capture prefix and exact normalized material. It cannot prove raw observation bytes beyond that old prefix when progress stayed held. A named fixture preserves this limit. The v2 path additionally matches the durable predecessor's exact keyed whole-row prefix, and v2 replay matches the whole edge.

## Review checkpoint

[All six required jobs](https://github.com/kburson/aitm/actions/runs/42937140018/attempts/1) passed on exact head `8887c7142617014c9e3712c8b3eba22f21331cf1`. The [authenticated receipt](hosted-ci-receipt.json) verified tested merge `1090446b073e7277cae0f5e6b41995dd30e9b47c`, tree `eb1145db4bd3f7ab88c832c40e0ca180d335d798`, artifact `13819571030` and signed subject SHA-256 `09293ae8b92afbeb13656b45ee3f4c2fb4612ec46b3a52ec3f43490098725a86`. The trusted raw replay retained 947 baseline package test identities and passed all 970 candidate tests. The locked local baseline includes the fixed CLI control for 948. Raw coverage passed at 10,360/11,301 product and 778/821 helpers. Independent exact source review is pending.

### Independent source HOLD and return to Develop

The [first exact independent source review](post-ci-source-review-held-r1.md) held the successful hosted candidate for changed behavior on an already disputed first-owner key. The current candidate returned DISPUTED for same-owner changed and unrecorded material. Prior behavior returned HELD for that material. Both statuses already keep the cursor replayable, but the unplanned disposition change must be removed. Exact recorded first material remains DISPUTED. Add a real native fixture for changed material on the existing disputed key and retain the [first signed CI receipt](hosted-ci-receipt.json).

## Replacement Test checkpoint

[PR #206](https://github.com/kburson/aitm/pull/206) read back replacement head `ae0e3a774e242af35210e57eeee499b789214afe`, tree `d34be057faf72d4c157c0dbf4e43003ccf40612d` and the unchanged literal trunk `2eebb3b7f6b262d3ed4951ffde0cbcb5d3a5ade3`. [Hosted run 42938964526](https://github.com/kburson/aitm/actions/runs/42938964526) passed and was authenticated below. The changed material on the actual disputed key returned DISPUTED in RED and now returns HELD. Exact recorded first material still returns DISPUTED. Neither cursor nor view changed, and all 24 related journal tests passed. Only that classification and its fixture differ from the earlier published candidate.

The fresh locked full gate again passed 970 product and CLI, 182 helpers, Ruff, whitespace and raw coverage of 10,360/11,301 product and 778/821 helper lines. All 948 local baseline IDs remain. No schema, gate controls or routing producer changed in the replacement.

## Replacement Review checkpoint

[All six hosted jobs](https://github.com/kburson/aitm/actions/runs/42938964526/attempts/1) passed on exact replacement head `ae0e3a774e242af35210e57eeee499b789214afe`. The [authenticated receipt](hosted-ci-replacement-receipt.json) verified tested merge `d2967c1f8a6887fda0fe1f2d3cacea5c087315b5`, tree `d34be057faf72d4c157c0dbf4e43003ccf40612d`, artifact `13819413267`, and signed subject SHA-256 `a98a23398b08ab0f7fe68a2811d042462c5b9f8fd533d209a55763e5880c4ea9`. The raw replay retained all 947 package baseline identities and passed all 970 candidate tests with both raw coverage floors. The [earlier signed receipt](hosted-ci-receipt.json) and [independent HOLD](post-ci-source-review-held-r1.md) remain intact. Exact replacement source review is pending.

The [independent exact source verdict](post-ci-source-review.md) passed replacement head `ae0e3a774e242af35210e57eeee499b789214afe`, tree `d34be057faf72d4c157c0dbf4e43003ccf40612d` and the literal trunk base. The tested changed-material fixture uses the existing real Codex Desktop `NativeJournalFixture`, even though the reviewer described that fixture as Claude in a nonblocking note. The restored classification applies uniformly. Exact recorded first material stays disputed and unrecorded material stays held. The earlier source HOLD and signed run are separately retained.

The first-claim payload/digest consistency check is intentional fail-closed hardening across the existing supported surfaces. The v1-layout initial raw-prefix limit is documented in the PR and remains explicitly tested. Native GitHub review is absent. The exact independent verdict is off-platform.

### Verified delivery

[PR #206](https://github.com/kburson/aitm/pull/206) merged into literal trunk at `2026-11-11T01:36:15Z` as `5324a80bad7730b2bdb4a2b87acf00f7171305c0`. Fetched trunk contains the merge with ordered parents `2eebb3b7f6b262d3ed4951ffde0cbcb5d3a5ade3` and `ae0e3a774e242af35210e57eeee499b789214afe`, exact tree `d34be057faf72d4c157c0dbf4e43003ccf40612d`, candidate ancestry and zero source diff. All six required checks and the exact off-platform verdict passed. Branch rules permitted an ordinary merge with zero required native approvals.

The original [SQLite migration author](../retro/2026-11-10-201-store-migration-implementer-retrospective.md) and [journal adjudication implementer](../retro/2026-11-10-201-journal-adjudication-implementer-retrospective.md) personally signed. Both signatures and the [fresh native dependency readback](close-dependency-readback.json) were verified at `2026-11-11T01:38:45+00:00`, clearing the final Close prerequisites.
