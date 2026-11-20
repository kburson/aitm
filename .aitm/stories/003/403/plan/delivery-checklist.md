# #403 delivery checklist

Codex is the implementing agent. The target is `trunk`. This checkpoint covers implementation and hosted advisory qualification.

- [x] Owner-approved implementation and qualifications per the [Astra-reviewed plan](../../370/plan/2026-11-19-370-import-chain-list.md).
- [x] Published branch `codex/403-import-chain` for [PR #406](https://github.com/kburson/aitm/pull/406).
- [x] Verified literal base `f2ff2b6f073fa769261b44fb0c05a055da7eb1c9`, exact implementation head `9b5f22c2f49250fe5c9208ccb13df9fc7bccba6e`, and head tree `89d057850bbfeb8263243c15c18c65a6add9e430`.
- [x] Verified both advisory shadow cases on that tool revision. [Hosted shadow run](https://github.com/kburson/aitm/actions/runs/44663963730).
- [x] Validated the unchanged required CI on PR #406. [CI run](https://github.com/kburson/aitm/actions/runs/44663966017).

Earlier shadow results were superseded as independent implementation review identified unsupported loader escapes and a missing transitive shared-input rule. The required quality job identified an import order difference. The current candidate incorporates those corrections. [Superseded CI](https://github.com/kburson/aitm/actions/runs/44663809686).

[Advisory qualification findings](../../370/plan/2026-11-20-370-import-chain-shadow-findings.md) and [archived evidence](../../370/plan/2026-11-20-370-import-chain-shadow-evidence.json).

[Independent source review](reviews/2026-11-20-403-source-review.md) and [required CI verifier receipt](2026-11-20-403-required-ci.json). The implementation PR remains open for review.
