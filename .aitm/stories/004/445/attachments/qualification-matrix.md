# Portable agent effort release qualification

The tested merge is `9e062e22f296adb6ad91fafd9cbe2ab3fd2f1d09`, tree `5f75b556cb3cf508a9e38308a0155a174acd3efc`. [Ordinary CI](https://github.com/kburson/aitm/actions/runs/45634555848/attempts/1) passed six jobs and [trusted verification](trusted-pr-454.json). The [portability matrix](https://github.com/kburson/aitm/actions/runs/45634556081/attempts/1) checked the same merge SHA and tree.

| Host | Installed wheel and fixture result | Attempt-one artifact SHA-256 |
| --- | --- | --- |
| Linux x64, Ubuntu 24.04 | 122 passed | `e76a708f2756573b85880d1be24ea2cec755afd5e1c3dc357ce66acd85b32327` |
| macOS arm64, macos-15 | 122 passed | `62bc6f46e0b1f3af5ab71ef097bed610ac448b79fd757b6eb1a4b32010bbfa` |
| Windows x64, Windows 2025 | 122 passed | `adcba0a69ae493b5db4326d23a528fb8b9e9ed6297bac26e4c8789c45a48e116` |

Each host built and installed the dependency-free Python wheel, exercised the installed `aitm-effort` console and verified the portable import path. The same wheel passed all 122 fixtures locally on macOS 26.6.2 arm64. The pilot used package Git tree `d9ef80a6a750a531a2e7affd93618e7fe8d5e838` from the tested merge and wheel SHA-256 `e36ad20efd6b0f1c7114b280381ba07ca424c8221943f3353ab6e59c9cecffbb`. The [coordinator-measured pilot receipt](445-live-portable-effort-pilot.json) has SHA-256 `ef7d54306f8c0145ffe82430b8bf659af2593e57b87762086c4c012eb22b73d0` and used a private disposable project with existing provider sign-in and permissions. [Independent evidence review](pr-454-source-review.md).

| Provider on macOS | Qualified live path | Coverage limits |
| --- | --- | --- |
| Codex 0.171.0-alpha.13 | Fresh and resumed headless capture, exact retained recovery, configured TUI notify | Interrupted counters may be unavailable. Codex AIPR sealed-review admission remains unqualified. [Native evidence](../../439/attachments/codex-native-qualification.json) · [#434 findings](../../434/attachments/codex-review-lock-results.md) |
| Claude Code 2.1.331 | Fresh and resumed headless capture, exact retained recovery, configured Stop; live AIPR companion reconciliation | Interrupted terminal evidence can exceed exact retained coverage. [Native evidence](../../440/attachments/claude-native-qualification.json) · [AIPR pilot](../../444/attachments/444-live-aipr-companions.json) |
| Grok Build 1.0.92 | Fresh and resumed headless capture, configured exact ordinal recovery; live AIPR companion reconciliation | Cancellation can leave usage unknown. Native reported USD ticks and verified billing remain distinct. [Native evidence](../../441/attachments/grok-native-qualification.json) · [AIPR pilot](../../444/attachments/444-live-aipr-companions.json) |

Hosted Linux and Windows coverage is installed-wheel and fixture coverage. Live provider qualification on those hosts remains a follow-on when the configured provider surfaces can be exercised. Interactive coverage applies to configured routes with exact native authority. Verified billed amounts remain unknown. The release scope is the portable package on trunk. Existing #100 production activation follows its own gates.

The [pilot results](pilot-results.md) record exact rollup parity, zero duplicates, explicit gaps, restart and replay, private raw custody, and observed overhead.
