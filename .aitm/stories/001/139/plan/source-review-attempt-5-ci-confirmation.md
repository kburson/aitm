# #139 source review confirmation for hosted attempt 3

| Field | Verified value |
| --- | --- |
| Reviewer | `codex-collaboration:/root/review197` |
| Pull request | [kburson/aitm #197](https://github.com/kburson/aitm/pull/197) |
| Literal `trunk` base | `b0f8ac79b8bd3f178b1d47dc2e66650f1f54e0d5` |
| Reviewed PR head | `dbbc729574c9b078658af310b2efa2945020224f` |
| GitHub test merge commit | `59a03a1942401d2f462c11e548ad74b1d73beeaf` |
| Reviewed and tested tree | `7d93353e06c8177c19bc1f918217e2f8ccf75da7` |
| Hosted run | [43058239273, attempt 3](https://github.com/kburson/aitm/actions/runs/43058239273/attempts/3) |
| Check suite | `116603413479` |

**The accepted source review applies to this exact hosted candidate.**
Authenticated GitHub reads confirmed the PR remains open, the literal
`trunk` and PR merge refs match the tuple, and the GitHub-verified test
commit has the expected base and head as parents and the reviewed tree.
The source review at `source-review-attempt-5.md` has SHA-256
`b0df50fdb6ef69573bb30b8e6e078565b3227a43eb3c9dac3917ad115427065d`.

## Hosted jobs and evidence

The attempt and all six required jobs completed successfully. I
verified each job on the attempt-specific GitHub endpoint.

| Job | GitHub job ID |
| --- | --- |
| `python-base` | `130663105348` |
| `python` | `130663105319` |
| `quality` | `130663104955` |
| `file-checks` | `130663105346` |
| `collect-evidence` | `130667401182` |
| `aitm-ci` | `130667537799` |

The local archive for GitHub artifact `13874037440` matches the
authenticated artifact SHA-256
`b1ae8d1c86f1384ae7b1300a19e6c3fc2605c3725cc70a3a0997a5d0074098c2`.
I independently verified the GitHub attestation for `candidate.json`.
Its SHA-256 is
`6305f2154c7f9724b95fce802e13048d59b43b7727bd459d8d43204391c95ab7`.
The verified certificate binds the GitHub-hosted signer workflow and
source digest to the tested merge commit and ref `refs/pull/197/merge`,
and its invocation URI names this exact run attempt.

I read the coordinator's signed-subject and raw-replay diagnostic,
`hosted-artifact-diagnostic-dbbc729574c9-a3.json`, SHA-256
`052d7bdc9826cb9d141a2c63992774f7581743300823615d943928addf2b7645`.
I independently matched the three raw archive digests and the
collector subject to the diagnostic and attested archive, and checked
the base and candidate phase reports and coverage. The candidate has
1,071 passing outcomes, the base has 1,070, and both have zero
failures. The candidate ID set equals the exact trunk push set. The
base ID set differs only by the candidate's CLI help test. Both
required child processes passed. Product coverage is 10,655/11,604
lines and helper coverage is 778/821 lines.

## Trusted verifier and owner disposition

The trusted verifier held attempt 3 with `selected attempt identity
or outcome disagrees`. I reproduced the field discrepancy using the
authenticated endpoints. The canonical workflow list and run record
return `created_at=2026-11-11T16:25:48Z`, while the attempt record
returns `created_at=2026-11-11T16:42:30Z`. The verifier requires those
values to be equal at `tools/ci/verify_pr.py:403`. The recorded hold
SHA-256 is
`e33097a08872f055f19447221e0626e13e9df4d3f01ec4b53ea88e60d487d9c7`.

The separate #103 owner disposition for the three added gate-control
paths and exact tree `7d93353e06c8177c19bc1f918217e2f8ccf75da7`
remains pending. Delivery requires the owner's explicit disposition
and a trusted-target verification pass. This confirmation binds the
existing source verdict to the successful hosted attempt and replay.

Signed `codex-collaboration:/root/review197` for the tuple above.
