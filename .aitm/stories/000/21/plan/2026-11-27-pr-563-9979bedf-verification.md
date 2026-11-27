# PR #563 exact hosted verification

- Target `codex/core-475-integration`
- Base `d79dae51c3223d90f8c1241c159631c5f0e60cf3`
- Head `9979bedf63059ca35e844c1f9404f8864fe9d39f`
- GitHub synthetic merge `414e0698c4148269c040f474a4a9965a6da8c435`
- Verified tree `d9af931eb9c3f932d6e0809ea9bc5c02ee5516ac`

Both hosted workflows passed on the exact draft candidate. The synthetic merge has the
ordered expected parents. The trusted verifier passed for this repository CI run and tree.

| Hosted collection | Unit | Integration | Total |
| --- | ---: | ---: | ---: |
| Core | 834 | 72 | 906 |
| aitm-usage product and CLI | 1644 | 142 | 1786 |

Both full unique pytest collections clear 92%.

[Repository CI](https://github.com/kburson/aitm/actions/runs/46078242137/attempts/1) · [Core CI](https://github.com/kburson/aitm/actions/runs/46078242223/attempts/1) · [Trusted verifier](2026-11-27-pr-563-9979bedf-verification.json).
