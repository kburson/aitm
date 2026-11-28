# First source review and coordinator disposition for #580

Grok 4.7 returned FAIL after reviewing the complete pinned packet in one call with zero tools. Returned the PR to draft. The replacement head is `f7743f4438038f03db305d15dec9d4f737629c1f`.

The coordinator reproduced malformed and empty coverage behavior and the skipped preflight on repeat observations. The revision returns typed applicability, keeps partial coverage in history, refuses stale or closed attempt identities, and routes repeats through normal preflight. The in-process CLI proof uses MemoryBackend with injected boundaries and no Git or subprocess. Repository CI, Core CI and trusted verification must qualify the replacement before a fresh independent review.

FAIL

base 33516757c6bb3ee2397a5827dc249184d6bfc835
source head 233a916d6e9b41796ca58661d8196322d231806f
synthetic merge b79151c3e9393f7d400872650c832fd50b1b5c90
tree af01ac355b75fd8913706a47e2813a201aaa60b0

The packet is complete through `END OF COMPLETE REVIEW PACKET`. Pinned base, source head, synthetic merge, and tree match the hosted-gate and trusted-verifier receipts. `reviewed_tree` is null. Unit count 1034, Ruff, and hosted run attempt 1 are recorded. Those receipts do not clear the contract holes below.

Same-attempt attachment keeps generation, start, clocks, used time, and allowance, and the attempt reducer replays `core.attempt.reconciled` through that same check. Legacy attempt streams still resolve `source` from `started` when `reconciliation` is absent. Refine observations stay a separate phase, keep decomposition proposal identity, and refuse refine before design acceptance. Epic refine hours are unrestricted. Cross-child descriptor files stay out of this diff.

Acceptance is held for these defects:

1. Dependency coverage is wrong for an empty complete set. `assess_jit` returns true for a descendant whenever `complete` is true and `paths` is empty, because no changed path can intersect the tracked set. Incomplete coverage is therefore treated as applicable. `record_jit` / `run_jit` never call `assess_jit`. Partial coverage is stored as `lifecycle.jit` with outcome `hold`, so the current JIT slot can hold non-accepted coverage. A closed current attempt skips the stale attempt/generation check, so a JIT row can name another attempt.

2. Transaction preflight is skipped on the retained-evidence path. `run_reconcile` and `run_jit` return `LocalOutcome.COMPLETED` when the folded fact already matches, before `publish`. A later blocked preflight cannot refuse that call. The mandated producer shapes `reconcile_attempt(...) -> OperationResult`, `record_jit(request) -> OperationResult`, and `assess_jit(...) -> JitResult` are absent. The write path returns `CommandResult` under other names.

3. The unit lane introduces Git. `cli/plan.py` resolves the JIT baseline with `workspace.repo._git` `rev-parse`. The accepted C27 lane forbids subprocess/Git. `test_c27.py` never calls `handle` or `_run`, so the implementation-binding purpose check, attempt-id match, baseline object-id checks, and injected CLI preflight are unproven. The MemoryBackend test calls `run_reconcile` / `run_jit` directly.

4. Malformed descendant paths raise from `repository_path` inside `assess_jit` instead of a typed non-applicable result. CLI `ValueError` is collapsed to `REFUSED`, including integrity failures that `_error` would classify as `INTEGRITY_ERROR` on the service path.

REVIEW COMPLETE
