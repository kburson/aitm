# #112 delivery · November 10, 2026

## Attempt 1

Codex is the implementing agent and closure owner. [Reviewed pickup](jit.md) and [independent verdict](jit-review.md). Predecessor #111 is closed and Done. Target trunk, base `c0371cc2363c1e95892fdcad75aa20181abeba20`, branch `codex/aitm-112-atomic-filesystem`. The untouched baseline passed 96 focused tests on macOS. Required validation is the locked package suite and Ruff, raw product and helper line floors, native candidate proof on Darwin and disposable Linux arm64 ext4, exact six-job hosted CI and independent exact-source review.

- [x] Verify prerequisites and review pickup.
- [x] Record local validation and push the exact candidate for Test.
- [ ] Record exact hosted run and independent source review.
- [ ] Verify delivery, publish the signed retrospective and close as Done.

### Test checkpoint

[PR #131](https://github.com/kburson/aitm/pull/131) read back as trunk at base `c0371cc2363c1e95892fdcad75aa20181abeba20` and candidate head `b04b01162a967ee1eed5cc557d4f2398a5fe44a1`, tree `29d903cebbe75e9a1f963682be77b9c219bdeafd`. The [canonical hosted run](https://github.com/kburson/aitm/actions/runs/42837579428/attempts/1) is pending.

The new host tests passed 16 cases. The scoped suites passed 126 cases, including installer backup and restore, service publication and both export races. The serial full suite passed 564 tests with child evidence enabled. Raw product line coverage was 6,364/6,981 and helper coverage was 778/821, each above 90%. The locally built wheel installed into a fresh environment and the console help ran. Ruff and whitespace checks passed.

The first overlapping product run had five Codex-reader failures that returned empty observations. All 84 reader tests then passed in isolation. The final full pass ran serially with a dedicated temporary directory. A separate initial helper invocation omitted the workflow's Python module path and failed to collect. The same helper suite passed all 182 cases with the workflow's module path.

[Exact candidate ext4 receipt and baseline runtime observation](../attachments/ext4-publication-proof.md).
