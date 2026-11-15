# #289 formal independent SAR

**Verdict: ACCEPTED for shadow deployment.** No blocking findings for the reviewed PR. Completing #289 still requires genuine scheduled hosted evidence and separate review.

Signed by OpenAI Codex, independent review agent `/root/review148`. I reviewed the full change, ran independent exact-source tests and reconciled the hosted evidence. This approval covers the reviewed shadow workflow only.

## Exact candidate and hosted evidence

- Repository and pull request: [kburson/aitm #305](https://github.com/kburson/aitm/pull/305)
- Literal target: `trunk`
- Base: `ea73031baedfb37e9e6336b064ac34a1f57059a6`
- Candidate head: `2ca9aa063dcc6b19c1395c853615ffa19d0860b6`
- Tested synthetic merge: `62de115dc1132374ea6cf54761211fb8c658914a`
- Reviewed candidate and tested tree: `30044a43e6ecd8f529d2fc94ca6296d24fdc6fd8`
- CI: [run 43669342596, attempt 1](https://github.com/kburson/aitm/actions/runs/43669342596/attempts/1)
- Trusted #103 verifier pass SHA-256: `adb6a7660ecb9af60f118b77b893144cd72af74e2567314a3408e12325799a81`
- Exact tree disposition SHA-256: `71e50e4cd1b797f06e1131865a409b68c537d4510f2c293c0249d81a5a1be61c`

I independently verified #289 In review and PR #305 open in draft. GitHub confirms the tested synthetic commit has those exact ordered parents and the candidate tree. The six successful hosted jobs match the trusted verifier: `python-base` 132675742456, `python` 132675742401, `quality` 132675742244, `file-checks` 132675742542, `collect-evidence` 132677387188 and `aitm-ci` 132677421555.

The trusted verifier, artifact metadata and signer log agree on artifact `14143786798`, archive digest `sha256:0f109aa91da89d705b619c9ca931a0292527490f0a9a189569a9c0b720d9dd31` and subject digest `404dabd5aee4d9e5de09820ea111919c3440f7cfae9c3a4febd5b6e54b3171c1`. The trusted verifier performed cryptographic verification. [#103](https://github.com/kburson/aitm/issues/103)

## Source and validation scope

The reviewed plan SHA-256 is `5a0c9d578a37b98a1dff3c516fba900b726215f8fed0ec4f894d316781268be1`. The independent plan review SHA-256 is `d3fa644d733ad07f30b223c4206fc904dc1e4a161d788617937c5a4e6c3e8598`. The independent source assessment SHA-256 is `6e642ec460ad29c35d0bb898fab9025140adee1283c78d14874d849e0dc65059`.

The four added files implement a standalone protected-default-trunk schedule and diagnostic dispatch. The runner uses exact checkout, pinned tools and private fixture roots for product and CI-helper collection and execution. The consumer checks provider run, attempt, suite and job identity, selected artifact custody and digest, protected control bytes, matching collection and execution inventories, per-test phases and native child evidence. A provider-authenticated failure remains observable with missing artifact. Current slot eligibility uses the original run creation time and the 45-minute missing-slot grace. Timely registered active jobs remain pending. Scheduled and dispatch evidence remain separate, and the shadow warning/recovery flow retains scheduled provenance without changing #103.

An independent exact Git export passed **200 tests** across scheduled, advisory, incident, recovery, policy and verifier suites. Ruff lint and formatting, Bash syntax and exact-range Git whitespace checks passed. Each of two broader coordinator local runner trials retained one native product setup error, with distinct tracebacks. I independently reran both identified nodes three times with fresh private fixtures and all six passed. The full local observations are diagnostic and give no complete scheduled receipt.

Deployment exposes the workflow for protected default-trunk observation. A genuine scheduled run from the expected slot, successful exact full receipt and separately reviewed qualification remain required before #289 can close. The diagnostic dispatch cannot satisfy that condition. The verdict binds these exact candidate identities. [#289](https://github.com/kburson/aitm/issues/289)
