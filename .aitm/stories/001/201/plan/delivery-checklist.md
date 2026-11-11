# #201 manual delivery checklist

## Accepted pickup and Develop checkpoint

[#199](https://github.com/kburson/aitm/issues/199) is Closed Completed and Done. [PR #205](https://github.com/kburson/aitm/pull/205) delivered literal trunk `2eebb3b7f6b262d3ed4951ffde0cbcb5d3a5ade3`, tree `9899ff4990510ebc9de09566fb08efcb33f9d112`. A fresh clean locked detached baseline passed 948 product and CLI, 182 helper, Ruff, whitespace and raw 10,236/11,175 product and 778/821 helper lines. The review's baseline readback condition was verified before setting Start Date.

[Round one](2026-11-10-201-pickup-review-r1.md) held the initial artifact. [Round two](2026-11-10-201-pickup-review-r2.md) passed the [exact revised JIT](2026-11-10-201-durable-revision-succession-plan.md) at SHA-256 `302b2220f9f887e7ea55526ee043d667682b3df65f84eb357735ff8a74d3a67f`. The delivered `ScopeState.read_source` authenticates a supplied cursor and calls the provider with a cold read from the same current fixed capture limit. The real journal-level earlier-cursor fixture remains a hard gate. #201 still directly blocks #119 and #202.

Codex owns the isolated branch `codex/aitm-201-durable-revision-succession` and Close. Project Rank 226, Size M, Estimate 3.75 implementation agent-hours, Start Date November 10. At the 2.25-hour checkpoint the migration lane must be GREEN and committed and both required RED fixtures must exist. Any required split keeps a direct #119 gate.
