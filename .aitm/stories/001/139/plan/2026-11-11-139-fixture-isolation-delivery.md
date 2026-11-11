# #139 Hosted Python fixture isolation delivery

The owner directed delivery of the fixture isolation from #231 and
qualification of the full hosted Python job within the existing
eight-minute limit. This work holds #197 until both prerequisites pass
and retains #159's blockers #157 and #158.

## Candidate

[PR #245](https://github.com/kburson/aitm/pull/245) extracts only
[`d1916b81`](https://github.com/kburson/aitm/commit/d1916b81fc05417c6ff709beb59890d22369243b)
from #231. The fixture patch changes `.github/workflows/ci.yml` by giving
each Python job a fresh private pytest base directory, separate from
evidence output. The resulting workflow blob matches the source patch
exactly. Both job limits and the test, coverage, and signing requirements
retain their previous values.

The first PR candidate has base `b0f8ac79b8bd3f178b1d47dc2e66650f1f54e0d5`,
head `65a9d70e01def9b81307773975ae8ea7ec86da98`, and GitHub test merge
`ebd6341b9d5b1f52c836ab5199565dec45199a4f`. Its tested tree is
`1b4859c42c61b379e68a5bd20af5d077a54f209b`. GitHub returned those exact
base and head commits as ordered test-merge parents.

Actionlint passed at the workflow's pinned version. Four local fixture
probes passed, exercising both capture errors under controlled ancestor
metadata churn and their successful private-directory counterparts.

## Hosted qualification

[Run 43085566452, attempt 1](https://github.com/kburson/aitm/actions/runs/43085566452/attempts/1)
passed all six required jobs. The candidate Python job finished in
374 seconds through wheel smoke and artifact upload. The isolated base
job finished in 171 seconds. The signed candidate evidence records
1,071 candidate tests, 1,070 base tests, both required subprocess
records, 10,655 of 11,604 product lines, and 778 of 821 helper lines.
The signature and payload for archive `13886472350` were verified
against the exact test merge, tree and attempt. The initial trusted
verifier held at its reviewed-tree check while independent review ran.

## Exact-candidate review and disposition

Claude Opus 5.5 medium gave an independent off-platform **PASS** after
hosted validation. The reviewer bound the base, head, test merge, and
tree above, and reported no blocking findings. [Review response](fixture-isolation-pr245-review.md).
Review input SHA-256
`fee9f9c4e738fbdaef0d6a35c5b1cf727c2881729313914bea2f25dbc997c8fd`.
The reviewer confirmed scope, fixture and artifact separation, test
inputs, coverage, and signing. No native GitHub review was submitted.

The signed payload and local tested tree both bind workflow blob
`7314705a5054920b885a3445c75ecf4fd7bf29c6`, replacing base workflow blob
`96424d880798d78e1eae93fba4d748d4fe985792`. The signed timing records
374 hosted seconds and a warm cache. This was one qualifying PR sample.
The base remained pinned for the final check. The extra candidate test
is the existing CLI proof. The separate CI-helper invocation retains
its original fixture placement, within the scope of the source patch.

The owner instruction to deliver the fixture isolation from #231
applies to this exact extracted workflow change. The reviewed tree
above is the resulting #103 disposition scope. The
[trusted verifier receipt](fixture-isolation-pr245-verifier.json) passed
for the exact tree and signed attempt.

## Delivery

PR #245 merged through GitHub with the reviewed head pinned. The
delivered trunk commit is `21b06b2b8be47adcf4c3c747ba7c0a6469196f79`.
GitHub readback verified the reviewed base and head as ordered parents
and the reviewed tree `1b4859c42c61b379e68a5bd20af5d077a54f209b`.

The [exact trunk push](https://github.com/kburson/aitm/actions/runs/43087210117/attempts/1)
passed. The complete Python job took 462 seconds, leaving 18 seconds
under the unchanged 480-second limit. Wheel smoke, artifact upload and
the push collector passed. The base lane and attestation signer are
PR-only. The [trunk receipt](fixture-isolation-trunk-qualification.json)
binds the push SHA, artifact digest, 1,071 test IDs and coverage totals.
Both qualifying samples used a warm cache.

Fixture delivery and separate hosted qualification satisfy the #197
hold prerequisites. #197's head remains
`dbbc729574c9b078658af310b2efa2945020224f`. Its old failed attempt is
still the latest run for that head. A refresh to current trunk and
fresh exact-candidate validation are the next #139 steps. #159 remains
blocked by open issues #157 and #158.
