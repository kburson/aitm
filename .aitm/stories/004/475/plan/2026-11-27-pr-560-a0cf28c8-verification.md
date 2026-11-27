# PR #560 exact hosted verification

- Target `trunk`
- Base `2f5a1f7bf5d33b54cc24dd376d9ee1f377568699`
- Head `a0cf28c88c4315b478343e4b557ee3b21e0771c4`
- GitHub synthetic merge `857e6bb8c26830c9d178b3853327bac14c97effe`
- Verified tree `d6b2490cefa6f70edbb458564795ab67af3c7ddf`

Both hosted workflows passed on the exact draft candidate. The synthetic merge has the
ordered expected parents. The trusted verifier passed for this repository CI run and tree.

| Hosted collection | Unit | Integration | Total |
| --- | ---: | ---: | ---: |
| Core | 850 | 73 | 923 |
| aitm-usage product and CLI | 1644 | 142 | 1786 |

Both full unique pytest collections clear 92%.

[Repository CI](https://github.com/kburson/aitm/actions/runs/46082012497/attempts/1) · [Core CI](https://github.com/kburson/aitm/actions/runs/46082012489/attempts/1) · [Trusted verifier](2026-11-27-pr-560-a0cf28c8-verification.json).

## Local macOS full collections

```text
Composed head a0cf28c88c4315b478343e4b557ee3b21e0771c4
Tree d6b2490cefa6f70edbb458564795ab67af3c7ddf
aitm-core (darwin) full collection: 850 unit, 73 integration, 923 total. Unit floor: 92%.
aitm-usage (darwin) full collection: 1642 unit, 138 integration, 1780 total. Unit floor: 92%.
```
