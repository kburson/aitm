# #112 delivery · November 10, 2026

## Attempt 1

Codex is the implementing agent and closure owner. [Reviewed pickup](jit.md) and [independent verdict](jit-review.md). Predecessor #111 is closed and Done. Target trunk, base `c0371cc2363c1e95892fdcad75aa20181abeba20`, branch `codex/aitm-112-atomic-filesystem`. The untouched baseline passed 96 focused tests on macOS. Required validation is the locked package suite and Ruff, raw product and helper line floors, native candidate proof on Darwin and disposable Linux arm64 ext4, exact six-job hosted CI and independent exact-source review.

- [x] Verify prerequisites and review pickup.
- [x] Record local validation and push the exact candidate for Test.
- [x] Record exact hosted run and independent source review.
- [x] Verify delivery, publish the signed retrospective and close as Done.

### Test checkpoint

[PR #131](https://github.com/kburson/aitm/pull/131) read back as trunk at base `c0371cc2363c1e95892fdcad75aa20181abeba20` and candidate head `b04b01162a967ee1eed5cc557d4f2398a5fe44a1`, tree `29d903cebbe75e9a1f963682be77b9c219bdeafd`. The [canonical hosted run](https://github.com/kburson/aitm/actions/runs/42837579428/attempts/1) is pending.

The new host tests passed 16 cases. The scoped suites passed 126 cases, including installer backup and restore, service publication and both export races. The serial full suite passed 564 tests with child evidence enabled. Raw product line coverage was 6,364/6,981 and helper coverage was 778/821, each above 90%. The locally built wheel installed into a fresh environment and the console help ran. Ruff and whitespace checks passed.

The first overlapping product run had five Codex-reader failures that returned empty observations. All 84 reader tests then passed in isolation. The final full pass ran serially with a dedicated temporary directory. A separate initial helper invocation omitted the workflow's Python module path and failed to collect. The same helper suite passed all 182 cases with the workflow's module path.

[Exact candidate ext4 receipt and baseline runtime observation](../attachments/ext4-publication-proof.md).

### Review checkpoint

[Canonical run 42837579428 attempt 1](https://github.com/kburson/aitm/actions/runs/42837579428/attempts/1) passed all six jobs. GitHub read back tested merge `7ae7beace1ae0af2cc0054769e2320b53f89559c` with the expected tree and ordered base/head parents. The signed subject records 547 base tests, 564 candidate tests, product coverage 6,364/6,981 and helper coverage 778/821. Independent review of the source and test-control changes is next.

| Job | Outcome |
| --- | --- |
| [python-base](https://github.com/kburson/aitm/actions/runs/42837579428/job/129903789797) | Success |
| [python](https://github.com/kburson/aitm/actions/runs/42837579428/job/129903790328) | Success |
| [quality](https://github.com/kburson/aitm/actions/runs/42837579428/job/129903790399) | Success |
| [file-checks](https://github.com/kburson/aitm/actions/runs/42837579428/job/129903790454) | Success |
| [collect-evidence](https://github.com/kburson/aitm/actions/runs/42837579428/job/129905743545) | Success |
| [aitm-ci](https://github.com/kburson/aitm/actions/runs/42837579428/job/129905841601) | Success |

The [independent off-platform review](post-ci-source-review.md) passed for the exact six-file source diff and both changed test files. The review record resolves the 17-test inventory difference, records the expected red run and scopes the native Linux proof. No native GitHub review was submitted or required by the current trunk rules.

### Delivery and sign-off

The delivered verifier passed at `2026-11-10T14:55:34.076486Z` for the exact reviewed tree. It verified the six jobs, attestation and subject on artifact `13773529284` with archive digest `sha256:b057eddc659c7007b258d2f7ffa702c113f0a70751b75b68ed27e97fa5176877` and subject SHA-256 `ced441506e7d74325befb40a391e128dcc35c9df3b2ea801635771e5dfda52ab`.

[PR #131](https://github.com/kburson/aitm/pull/131) merged by merge commit into trunk at `338ff3382fd1757ae150fabfe93df98df5338e2a` at `2026-11-10T14:56:02Z`. The fetched remote target matched the PR merge SHA and exact reviewed tree `29d903cebbe75e9a1f963682be77b9c219bdeafd`, with ordered parents `c0371cc2363c1e95892fdcad75aa20181abeba20` and `b04b01162a967ee1eed5cc557d4f2398a5fe44a1`. Head ancestry and zero content diff were verified. Both proof volumes were removed. [Signed implementing-agent retrospective](../retro/2026-11-10-atomic-filesystem-operations.md).

The last gate was the implementing-agent sign-off at `2026-11-10T14:56:38Z`.

GitHub readback confirmed Completed closure at `2026-11-10T14:56:41Z` and Project status Done. #113 may enter its own leaf preparation. [Issue #112](https://github.com/kburson/aitm/issues/112).
