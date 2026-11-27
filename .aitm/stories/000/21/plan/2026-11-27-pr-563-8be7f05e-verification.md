# PR #563 exact hosted verification

- Target `codex/core-475-integration`
- Base `d79dae51c3223d90f8c1241c159631c5f0e60cf3`
- Head `8be7f05e57dd16db42aaf5212c1353d8e07d8e83`
- GitHub synthetic merge `b41e5a0b6afaec9b0522b8e31e0880585e10ccb5`
- Verified tree `ae464a3069a626109f83be1724b1f37c2a1f85ff`

Both hosted workflows passed on the exact draft candidate. The synthetic merge has the
ordered expected parents. The trusted verifier passed for this repository CI run and tree.

| Hosted collection | Unit | Integration | Total |
| --- | ---: | ---: | ---: |
| Core | 834 | 72 | 906 |
| aitm-usage product and CLI | 1644 | 142 | 1786 |

Both full unique pytest collections clear 92%.

[Repository CI](https://github.com/kburson/aitm/actions/runs/46076866754/attempts/1) · [Core CI](https://github.com/kburson/aitm/actions/runs/46076866696/attempts/1) · [Trusted verifier](2026-11-27-pr-563-8be7f05e-verification.json).
