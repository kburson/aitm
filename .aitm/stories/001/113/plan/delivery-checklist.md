# #113 delivery · November 10, 2026

## Attempt 1

Implementing agent and closure owner Codex. [Accepted pickup](jit.md) and [two independent review rounds](jit-review.md). Required predecessor #112 is closed and Done. Target trunk, exact base `338ff3382fd1757ae150fabfe93df98df5338e2a`, branch `codex/aitm-113-versioned-persistence`. The untouched base passed 116 focused tests and [trunk CI](https://github.com/kburson/aitm/actions/runs/42839139388). Built the exact base wheel and used it to generate a private v1 ledger, backup and export for the old/new compatibility rehearsal. Required validation is the plan's focused and locked package suites, both raw coverage floors, Ruff, installed old/new wheel rehearsal, the six-job exact hosted lane and independent source review.

- [x] Verify prerequisites and review pickup.
- [x] Record local validation and push the exact candidate for Test.
- [x] Record exact hosted run and independent source review.
- [x] Verify delivery, publish signed retrospective and close as Done.

### Test checkpoint

[PR #132](https://github.com/kburson/aitm/pull/132) read back as trunk at base `338ff3382fd1757ae150fabfe93df98df5338e2a` and candidate head `83fe253ed2a979bb23b52f0a3280591d662112a6`, tree `3e4d46feb9a8c7890937b089e486824cb308b93d`. The canonical hosted run is pending.

Test-first verification produced five expected interface and CLI failures and two passes for schema mismatches already refused by v1. All seven new cases passed after implementation. An additional test assertion exposed acceptance of JSON boolean `true` as v1 via Python numeric equality. The probe now compares exact JSON types and refuses it. The focused package pass covered 123 cases. The final locked product run passed 571 tests including CLI and child coverage. The helper suite passed 182. Raw line floors passed at 6,487/7,106 product and 778/821 helpers. Ruff and whitespace checks passed. [Exact isolated old and new wheel rehearsal](../attachments/versioned-persistence-compatibility.md).

### Review checkpoint

[Canonical run 42841994451 attempt 1](https://github.com/kburson/aitm/actions/runs/42841994451/attempts/1) passed all six jobs. GitHub reported tested merge `7531f5d7d6b3ecf89c4fa42ad2854c3eedbde4e2` with the expected tree and ordered base/head parents. The signed subject records 563 base tests, 571 candidate tests, product coverage 6,487/7,106 and helper coverage 778/821.

| Job | Outcome |
| --- | --- |
| [file-checks](https://github.com/kburson/aitm/actions/runs/42841994451/job/129919363523) | Success |
| [python-base](https://github.com/kburson/aitm/actions/runs/42841994451/job/129919364044) | Success |
| [python](https://github.com/kburson/aitm/actions/runs/42841994451/job/129919364045) | Success |
| [quality](https://github.com/kburson/aitm/actions/runs/42841994451/job/129919364129) | Success |
| [collect-evidence](https://github.com/kburson/aitm/actions/runs/42841994451/job/129921264289) | Success |
| [aitm-ci](https://github.com/kburson/aitm/actions/runs/42841994451/job/129921367895) | Success |

The [independent off-platform review](post-ci-source-review.md) passed for the exact source and additive test control. No native GitHub review was submitted or required. The authenticated raw inventories retained every baseline test and added seven M03 cases plus the candidate-only CLI case. The delivered gate replay matched the signed result.

### Delivery and sign-off

The delivered verifier passed at `2026-11-10T15:20:16.330766Z` for the exact reviewed tree. It verified all six jobs and the signature on artifact `13776951909`, archive SHA-256 `9bed9f90d228fb2d850794395b5bd4752274fa71b1f04b6bdeaf6e488e07fb6e` and subject SHA-256 `01ca9b360b3bc84233942edf142280fc28cc111ef576497f838cb37b61259c71`.

[PR #132](https://github.com/kburson/aitm/pull/132) merged by merge commit into trunk at `dc037364ba617b97244c93670d12358d0b5cbba7` at `2026-11-10T15:20:42Z`. The fetched target had exact reviewed tree `3e4d46feb9a8c7890937b089e486824cb308b93d` and ordered parents `338ff3382fd1757ae150fabfe93df98df5338e2a` and `83fe253ed2a979bb23b52f0a3280591d662112a6`. Head ancestry and zero source diff were verified. [Signed retrospective](../retro/2026-11-10-versioned-project-persistence.md).

The last gate was the implementing-agent sign-off at `2026-11-10T15:21:29Z`.

GitHub readback confirmed Completed closure at `2026-11-10T15:21:32Z` and Project status Done. #114 may enter its own leaf preparation. [Issue #113](https://github.com/kburson/aitm/issues/113).
