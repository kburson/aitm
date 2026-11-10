# #113 delivery · November 10, 2026

## Attempt 1

Implementing agent and closure owner Codex. [Accepted pickup](jit.md) and [two independent review rounds](jit-review.md). Required predecessor #112 is closed and Done. Target trunk, exact base `338ff3382fd1757ae150fabfe93df98df5338e2a`, branch `codex/aitm-113-versioned-persistence`. The untouched base passed 116 focused tests and [trunk CI](https://github.com/kburson/aitm/actions/runs/42839139388). Built the exact base wheel and used it to generate a private v1 ledger, backup and export for the old/new compatibility rehearsal. Required validation is the plan's focused and locked package suites, both raw coverage floors, Ruff, installed old/new wheel rehearsal, the six-job exact hosted lane and independent source review.

- [x] Verify prerequisites and review pickup.
- [x] Record local validation and push the exact candidate for Test.
- [ ] Record exact hosted run and independent source review.
- [ ] Verify delivery, publish signed retrospective and close as Done.

### Test checkpoint

[PR #132](https://github.com/kburson/aitm/pull/132) read back as trunk at base `338ff3382fd1757ae150fabfe93df98df5338e2a` and candidate head `83fe253ed2a979bb23b52f0a3280591d662112a6`, tree `3e4d46feb9a8c7890937b089e486824cb308b93d`. The canonical hosted run is pending.

Test-first verification produced five expected interface and CLI failures and two passes for schema mismatches already refused by v1. All seven new cases passed after implementation. An additional test assertion exposed acceptance of JSON boolean `true` as v1 via Python numeric equality. The probe now compares exact JSON types and refuses it. The focused package pass covered 123 cases. The final locked product run passed 571 tests including CLI and child coverage. The helper suite passed 182. Raw line floors passed at 6,487/7,106 product and 778/821 helpers. Ruff and whitespace checks passed. [Exact isolated old and new wheel rehearsal](../attachments/versioned-persistence-compatibility.md).
