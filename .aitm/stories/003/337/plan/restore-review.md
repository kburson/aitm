# Independent review of the refreshed #337 disposable restore

Verdict: ACCEPTED

I accept the exact refreshed forward restore in [disposable PR #2](https://github.com/kburson/aitm-rollback-337/pull/2), repository ID `1459345121`, for the simulated operator's expected-head merge into `trunk` under the active update hold. This acceptance applies to the identities below. I exercised read-only provider and source checks in a separate session and reran the delivered verifier from a clean detached checkout of the protected lab base.

| Input | Exact identity |
| --- | --- |
| Literal base `trunk` | `0cc6c0c9fabe47efb36972d6aa0af0ec56f6bd15` |
| Refreshed candidate head `probe/restore` | `d43d94a7dcf0ab1932092ee135ea142b9b21ef18` |
| GitHub synthetic merge, ordered parents base then head | `37d2c271233584fe98c97ca7b8a646f28f4b4f5b` |
| Reviewed tree | `6dcdc52b7dd0e582b0a5e555ea45af44dda65fa1` |
| Pinned production source | `4ba4354f603ad861c897111dcaaf2342fc68da86` |
| Reviewed rehearsal plan SHA-256 | `ccdca1f606d6142b472769eee74adc96a29b1926d1bbdab89fc34a45bf341a80` |

The lab base adds `.github/workflows/rollback-pilot.yml` and `.rollback-lab-mode.json` to the production pin. The restore changes only the latter's mode from `pilot` to `full-only`. The empty synchronization commit preserved tree `6dcdc52b7dd0e582b0a5e555ea45af44dda65fa1`. I checked the new synthetic merge's ordered parents and exact tree. The canonical workflow, trusted verifier, gate, observer, policy, lockfile, package configuration and test inputs match the production pin byte for byte. The public lab uses its own canonical `ci.yml` workflow ID `419574482`.

GitHub rebuilt the original test merge `37f507b7b4cf94d42eb0b20d169bc549207c1f15` as `f0c55072985f9346b76e0b2d7ae9f021f2b37d76` after the ordinary actor's denied attempt with a green full check. The parent order and tree remained the same. The SHA-bound signature still identified the first test merge. The author and I separately ran the trusted verifier and received `hold` before a restore merge. The first source disposition, provider readbacks and failed verifier receipt are retained in `records/restore-superseded/`. The refreshed candidate has a new head, synthetic merge, run and signed archive.

The new GitHub Actions run `43777508613` attempt `1` passed all six required jobs. Authenticated check IDs are `133007047741` for `python-base`, `133007047920` for `python`, `133007048164` for `quality`, `133007047958` for `file-checks`, `133008767807` for `collect-evidence` and `133008836815` for `aitm-ci`. The signed report records 1,486 baseline and 1,487 candidate tests, both line-coverage gates, required child witnesses and exact installed-wheel evidence. My independent `tools/ci/verify_pr.py` run with pinned `gh` 2.97.0 returned `pass` at `2026-11-16T00:03:54.008800+00:00`. Its fields agree with the retained author receipt apart from the independent verification timestamp. SHA-256 of `records/restore/trusted-verifier.json` is `c605650f6de7d8e7d42c79467b3cc4beeedde3251ed48e5e5c35bf52055ffb7c`. Signed artifact `14186817835` has archive digest `sha256:5488e6b75bd4a2905488a12ab929865dd832c837f3e28315127e6ba9effdc443` and subject digest `e8a71418312c8e4835270c39329e92a3adab412898ddefe82db225e9cc729be4`. [Exact run attempt](https://github.com/kburson/aitm-rollback-337/actions/runs/43777508613/attempts/1)

The copied normal trunk ruleset `27339225` matches the production rule parameters and grants zero bypasses. The distinct strict full-check ruleset `27339233` requires all six canonical contexts from GitHub Actions app `15368` and grants zero bypasses. The active update hold `27339262` grants only user `1082467` a PR-only bypass. The native contexts enforce expected check outcomes. The delivered trusted verifier remains mandatory and authenticates the exact base, head, merge, tree, workflow, attempt and signed jobs. The administrative account acts as the designated operator in the disposable rehearsal. Production #103 retains its existing authority. [Protection](https://github.com/kburson/aitm-rollback-337/rules/27339225) · [Required checks](https://github.com/kburson/aitm-rollback-337/rules/27339233) · [Update hold](https://github.com/kburson/aitm-rollback-337/rules/27339262)

This disposition covers the refreshed restore source and premerge evidence. The completion decision additionally requires the exact landed tree, fresh restored-trunk and ordinary-candidate evidence, distinct simulated operator acknowledgment and release of only the hold.

Signed by the independent Codex reviewer `/root/review337`.
