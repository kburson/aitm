# PR #561 exact verification

Verified live `codex/core-475-integration` base `8e4def51deb2fa3ba79fdef1671712aec1fb9977`, head `d5e9127293ab07ce1f59a479c65c5f86be58179f`, GitHub synthetic merge `70373f753bcb2e1472b0e62a138005e8161d0fb3`, and synthetic tree `c78419dd204adb23449d6021a267b92c7ad7e7dd`. The synthetic commit has the ordered expected parents. Both hosted workflows passed while the PR was draft. The live candidate remained exact when the PR was marked ready.

| Lane | Unit | Integration | Full unique collection |
| --- | ---: | ---: | ---: |
| Hosted Linux Core | 807 | 70 | 877 |
| Hosted Linux aitm-usage product and CLI | 1,644 | 142 | 1,786 |
| Local macOS Core | 807 | 70 | 877 |
| Local macOS aitm-usage product | 1,642 | 138 | 1,780 |

The hosted Core product suite passed 877 tests, the tooling suite passed one, and Ruff check and formatting passed. The repository workflow passed its coverage and branch checks. The local Core run built a fresh installed wheel in an isolated environment. It passed 57 C11 cases, then 878 Core and tooling tests, and Ruff check and formatting. The Core and usage floors remain 92%.

[Repository CI](https://github.com/kburson/aitm/actions/runs/46066744789/attempts/1) · [Core CI](https://github.com/kburson/aitm/actions/runs/46066744769/attempts/1) · [Trusted verifier](2026-11-27-pr-561-verifier.json).

C11 splits the setup producer into its bootstrap, journal and explicit adoption modules. The accepted scope and dependencies remain the C11 entry. The real Git proofs cover local and hosted init, resume without repeating arguments, no publication before landed policy, original-history recovery and replacement proposal, branch deletion fencing, non-default publication and normal mutation, and reconfiguration with immutable issuer history.
