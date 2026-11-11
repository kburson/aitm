# #201 manual delivery checklist

## Accepted pickup and Develop checkpoint

[#199](https://github.com/kburson/aitm/issues/199) is Closed Completed and Done. [PR #205](https://github.com/kburson/aitm/pull/205) delivered literal trunk `2eebb3b7f6b262d3ed4951ffde0cbcb5d3a5ade3`, tree `9899ff4990510ebc9de09566fb08efcb33f9d112`. A fresh clean locked detached baseline passed 948 product and CLI, 182 helper, Ruff, whitespace and raw 10,236/11,175 product and 778/821 helper lines. The review's baseline readback condition was verified before setting Start Date.

[Round one](2026-11-10-201-pickup-review-r1.md) held the initial artifact. [Round two](2026-11-10-201-pickup-review-r2.md) passed the [exact revised JIT](2026-11-10-201-durable-revision-succession-plan.md) at SHA-256 `302b2220f9f887e7ea55526ee043d667682b3df65f84eb357735ff8a74d3a67f`. The delivered `ScopeState.read_source` authenticates a supplied cursor and calls the provider with a cold read from the same current fixed capture limit. The real journal-level earlier-cursor fixture remains a hard gate. #201 still directly blocks #119 and #202.

Codex owns the isolated branch `codex/aitm-201-durable-revision-succession` and Close. Project Rank 226, Size M, Estimate 3.75 implementation agent-hours, Start Date November 10. At the 2.25-hour checkpoint the migration lane must be GREEN and committed and both required RED fixtures must exist. Any required split keeps a direct #119 gate.

## Test checkpoint

[PR #206](https://github.com/kburson/aitm/pull/206) read back exact head `8887c7142617014c9e3712c8b3eba22f21331cf1`, tree `eb1145db4bd3f7ab88c832c40e0ca180d335d798` and literal trunk `2eebb3b7f6b262d3ed4951ffde0cbcb5d3a5ade3`. [Hosted run 42937140018](https://github.com/kburson/aitm/actions/runs/42937140018) is pending. Required jobs are file-checks, quality, python-base, python, collect-evidence and aitm-ci.

The exact frozen local gate passed 970 product and CLI tests and 182 helpers, Ruff, whitespace and raw coverage of 10,360/11,301 product and 778/821 helper lines. All 948 local baseline test IDs remain. The two-file migration commit `272c51484de88bb5e7f0a748c210479fd05f56e3` passed 959 product and CLI tests, 182 helpers and strict v1 compatibility. Both required native RED fixtures existed and the migration was GREEN and committed before proceeding past the reviewed checkpoint. The final integrated related suite passed 273 tests.

The full terminal fixture verifies an earlier real persisted cursor through the normal cold reread and reserves the whole batch. Every observation and native receipt settles, the exact original replays, both later edges stage, and quota is the sole remaining diagnostic keeping the earlier cursor. Other fixtures verify same-batch revision order and historic view, restart, exact archive replay without physical succession, changed original scope, disabled intermediate, transaction rollback, changed predecessor with equal successor material, two unchanged-material prefix rewrites, and a stored first-claim digest mismatch. The initial preflight held on a weak singular-reserve fixture. The full-batch replacement and additional negatives passed independent source preflight.

The v1-layout first claim authenticates the historical capture prefix and exact normalized material. It cannot prove raw observation bytes beyond that old prefix when progress stayed held. A named fixture preserves this limit. The v2 path additionally matches the durable predecessor's exact keyed whole-row prefix, and v2 replay matches the whole edge.
