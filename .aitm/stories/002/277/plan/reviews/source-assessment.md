# #277 signed independent source assessment

**Source verdict: no material findings.** The exact candidate meets the reviewed read-only canonical push intake scope. Formal review admission is pending the complete exact-head #103 evidence.

Signed by OpenAI Codex, independent review agent `/root/review148`. I reviewed both changed files and ran validation in a separate exact-head archive. I independently read the GitHub PR, push, attempt, job and artifact identities.

- Repository and pull request: [kburson/aitm #281](https://github.com/kburson/aitm/pull/281)
- Literal target: `trunk`
- Base: `342b64314ff0966199f23b8efc77519febbad335`
- Candidate head: `10ea993c55baa4d2671cf4259e995caeeab252fd`
- Synthetic merge: `262f68eef7aa4d21085039f7d4b48e427a87a60c`
- Candidate and tested tree: `9c796de3b1b2405a4f8a85caaf91250457a5ee10`
- Reviewed plan SHA-256: `8ddce43eb6c263a530d9302abffa32b4feb91c03f3f302efdd6ddda3dc2cd631`
- Independent plan review SHA-256: `ebcc295d881880f7c03af4c6bcef5fc35e7e0b34c018ff6355b591d8ab26f3e4`
- Live green receipt SHA-256: `7af086e0146f3be1f6347e82b09b9c76038ad59a027a9ae9d1ecb6c00b153204`
- Saved shadow and stale controls SHA-256: `4afa36ba98d8c7bbd26d61e89209f72d5a5c643343b77704607c6954acfa4d08`

## Source assessment

The candidate adds `tools/ci/ci_advisory.py` and its tests. It uses the existing bounded, GET-only GitHub transport. It pins repository and head-repository IDs, workflow ID and path, protected literal `trunk`, run number, latest attempt, Actions suite and exact-attempt job/check identity. It treats the three policy push jobs and the collector as required. A known failure retains its job ID alongside a missing or malformed sibling or unavailable final freshness read. A confirmed branch or attempt change yields a stale decision. The final branch, workflow, run and exact-attempt readback determines `current_verified` independently of the observed job result.

Green requires successful run and suite plus all four authenticated successful jobs. The code validates exact-attempt archive custody, size, SHA-256 and bounded member structure before JSON parsing. It binds workflow, evaluator and policy to exact protected-tree blobs and checks the product inventory against that tree before invoking the existing push evaluator. Live and shadow decisions carry distinct provenance. #103 remains the merge gate. [#103](https://github.com/kburson/aitm/issues/103)

The final source incorporates fixes for preservation of verified failure when readback is unavailable, exact-attempt re-read, malformed sibling evidence, explicit provenance and GitHub's actual rerun creation timestamp behavior.

## Independent evidence

- The exact-head export under CPython 3.13.9 and a locked uv 0.10.6 environment passed 158 tests across the advisory, policy and verifier suites. Ruff lint and formatting and exact-range Git whitespace checks passed.
- I ran the exact candidate CLI on current protected `trunk`, run `43404405270` number 145 attempt 1. It returned live, current-verified green. The existing push evaluator passed on 1,216 tests from artifact `14027075991`, SHA-256 `e45f97966ce5b4a3ced682832a0b1aa26256daba7a5bd8406c1f39a5a4f2803c`. [Push run](https://github.com/kburson/aitm/actions/runs/43404405270/attempts/1)
- I reproduced the historical red and forced missing-artifact incomplete decisions offline from saved provider responses, using the same reducer. Historical push `43250904624` attempt 1 retained authenticated `collect-evidence:failure` with no artifact. Delayed delivery of that attempt against live trunk yielded stale. [Historical push](https://github.com/kburson/aitm/actions/runs/43250904624/attempts/1)
- I independently shadowed real provider metadata for historical push rerun `42940157251` attempt 2. The reducer verified the four exact-attempt jobs and readback even though GitHub recorded attempt creation one second after the attempt began. It withheld green because the historical protected workflow bytes differ from the current trusted checkout. [Historical rerun](https://github.com/kburson/aitm/actions/runs/42940157251/attempts/2)

GitHub showed the story in Test and PR #281 open in draft during this assessment. The first three attempts of the final candidate's hosted CI each completed the candidate Python, quality and file checks successfully and cancelled the required base lane at its time limit. Attempt 4 is in progress. Formal SAR requires successful current CI, a trusted verifier pass and Review admission. [Exact CI run](https://github.com/kburson/aitm/actions/runs/43409093456)
