# Post-cutover verification of the parallel macOS base job

**Recorded November 15, 2026.** [PR #319](https://github.com/kburson/aitm/pull/319) enabled three workers for the literal-base job in merge `75d4bc06657f93f77d6b07e3ae2605cb1c9a269f`. [PR #313](https://github.com/kburson/aitm/pull/313) supplied the first ordinary PR run against that trunk revision and a later run against the updated trunk.

## Full-suite and timing readback

Both runs completed the full literal-base Python suite with zero deselected tests. Times run from the GitHub job's start through completion, including setup and artifact upload. Both jobs stayed below the eight-minute limit.

| PR #313 run | Literal base | Tests passed | Phase outcomes | Pytest elapsed | Base job elapsed |
| --- | --- | ---: | ---: | ---: | ---: |
| [First post-cutover run](https://github.com/kburson/aitm/actions/runs/43728770575/attempts/1) · [base job](https://github.com/kburson/aitm/actions/runs/43728770575/job/132856371656) | `75d4bc06657f93f77d6b07e3ae2605cb1c9a269f` | 1,294 | 3,882 | 213.63s | **3m57s** |
| [Later run on updated trunk](https://github.com/kburson/aitm/actions/runs/43733098637/attempts/1) · [base job](https://github.com/kburson/aitm/actions/runs/43733098637/job/132869683517) | `ab9db80098849e323d5122eb47bf48f377107058` | 1,311 | 3,933 | 180.51s | **3m18s** |

The first run matched every test ID and phase outcome in the [serial qualification](https://github.com/kburson/aitm/actions/runs/43726916730/attempts/1). The later run matched a fresh locked pytest collection from its exact base commit and had one passing report for each test phase.

## Signed CI evidence

Both downloaded archives matched GitHub's SHA-256 digests. Sigstore verification bound each signed candidate to its GitHub-hosted `ci.yml` invocation and exact synthetic merge. Each signed report also bound the downloaded base-test record by SHA-256. The ordered merge parents matched the base and head in the corresponding planning receipt.

| Run | PR head | Tested merge | Base artifact | Signed artifact | Planning receipt |
| --- | --- | --- | ---: | ---: | --- |
| 43728770575 attempt 1 | `f3848b9d5635a21d30f666a7a9077857d1f20b5d` | `fe4aee7f79e88498511cb0471ee24d605cb88a8f` | `14167288031` | `14167088993` | [Round 2 signed CI receipt](../../134/plan/carrier-signed-hosted-r2.json) |
| 43733098637 attempt 1 | `91fd55832ae4d9cf7daa79d56138050b63495092` | `12cdcfe64c0a97d27b956c4bfe77b982a99edd51` | `14169630250` | `14169019994` | [Round 3 signed CI receipt](../../134/plan/carrier-signed-hosted-r3.json) |

| Run | Signed archive SHA-256 | Signed candidate SHA-256 |
| --- | --- | --- |
| 43728770575 attempt 1 | `3e1983b2b0319cbb4b5aadf8df94adf2a5cd6acf06ea1f0bf9bfba13d6fee847` | `8cac0d7d013aaabdd5550c40dcc634ffcf6ad8d04d2e11f2327d136a63e11c74` |
| 43733098637 attempt 1 | `e48e6b1f9a5da890085f9b76cef6e7f152e5588570dc08071e07b955f0ab1c5b` | `95d62bd42c0bca52ec904220f204bf8429fb2490dc534b273716ab3442d1a940` |

The round 2 source review recorded a separate [HOLD](../../134/plan/carrier-independent-source-r2-receipt.json). The delivered round 3 revision had an [independent source PASS](../../134/plan/carrier-independent-source-r3-receipt.json).
