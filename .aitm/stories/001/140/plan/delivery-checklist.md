# #140 delivery evidence

Attempt 1. Implementation owner `codex-collaboration:/root/impl140`.
Closure coordinator Codex. Literal parent `trunk`. Follow the
[manual delivery checklist](../../../../manual-delivery-checklist.md)
and [#103 verification contract](../../103/design/github-ci-quality-gates-design.md).
The owner's stop is before merge.

## Candidate `6397dd9a5ff7` · Test

[Open PR](https://github.com/kburson/aitm/pull/184) · base `d769b3169724eeb9ef4b4aee47d3ab4c4489072d` · head `6397dd9a5ff7e26a3711651f871f846cb3ef60f1` · local tree `e89faf081d000fd8749430edd8ce47328e6703bb`.

- Locked Python 3.13.9 and uv 0.10.6 on the isolated source checkout.
- Exact-head focused pytest result `38 passed in 24.45s`.
- Exact-head full local package and CI test result `934 passed in 127.84s (0:02:07)`.
- Ruff check, Ruff format and source diff whitespace passed.
- Focused collection and execution are separate from the hosted #103
  test list and helper denominator.
- Hosted validation and independent review apply to this exact candidate.

### Independent source review

The [intermediate hosted review](hosted-task-review.md) identified four
refusal gaps. The [whole-branch SPR](source-review-attempt-1.md)
confirmed the regressions and fixes on the exact candidate and
accepted the source without actionable findings. The source verdict
and authenticated hosted checks are separate.

## Authenticated hosted Test

All six required jobs passed on the [exact attempt](https://github.com/kburson/aitm/actions/runs/42897870711/attempts/1).
The signed verifier components and independent raw replay agree on the
tested merge `01b54fa474830dbd70915a4556f359b0b21f4a35`, ordered base/head, and exact tree
`e89faf081d000fd8749430edd8ce47328e6703bb`. The hosted result retained 713
trusted base outcomes and verified 714 product
and CLI outcomes. Product line coverage was 8404/9229
and helper coverage was 778/821,
both above the 90% floor. [Exact evidence](hosted-test-6397dd9a5ff7.json).

GitHub's rules were unchanged. The verifier classifies the two new
files under `tools/ci/` as gate-defining. The workflow, policy,
trusted verifier, lock and required test list and helper coverage
denominator are unchanged. The existing #103 owner disposition
applies separately to these exact additions.

The owner’s exact-tree disposition is pending. The [trusted verifier hold](verifier-hold-6397dd9a5ff7.json) leaves the story in Test while the independent source verdict is retained. The PR remains open and unmerged.

The owner approved the exact tree `e89faf081d000fd8749430edd8ce47328e6703bb` for the existing #103 disposition in the implementation conversation. The [trusted verifier](verifier-pass-6397dd9a5ff7.json) passed for that tree. The independent source review is retained and the story enters In review. The PR remains open and unmerged.

[Exact-tree owner disposition](owner-disposition-6397dd9a5ff7.json).

## Candidate `62c248b9ab53` · Test

[Open PR](https://github.com/kburson/aitm/pull/184) · base `0175e77c398dc97c59db166fa64e2e9a673b4b40` · head `62c248b9ab534f55565d7c1ec636bfe5b460b0dd` · local tree `4296f0b010776d754c39cdc9605e01e2b76e6805`.

- Locked Python 3.13.9 and uv 0.10.6 on the isolated source checkout.
- Exact-head focused pytest result `38 passed in 24.46s`.
- Exact-head full local package and CI test result `983 passed in 108.57s (0:01:48)`.
- Ruff check, Ruff format and source diff whitespace passed.
- Focused collection and execution are separate from the hosted #103
  test list and helper denominator.
- Hosted validation and independent review apply to this exact candidate.

## Refreshed candidate after #183 delivery

The earlier review remains evidence for its original base. The same
PR received a normal merge of verified trunk `0175e77c398dc97c59db166fa64e2e9a673b4b40` into the story
branch. Refreshed head is `62c248b9ab534f55565d7c1ec636bfe5b460b0dd`, exact tree `4296f0b010776d754c39cdc9605e01e2b76e6805`. Compared to
the refreshed base, only the two original snapshot files are added,
and both are byte-identical to the initial reviewed source.

The refreshed local focused result was `38 passed in 24.46s`.
The complete combined local suite returned
`983 passed in 108.57s (0:01:48)`. Ruff and source whitespace passed.
All six required jobs passed on the [exact refreshed attempt](https://github.com/kburson/aitm/actions/runs/42902200360/attempts/1).
Signed CI and raw replay matched. [Hosted receipt](hosted-test-62c248b9ab53.json).
The [independent refresh review](source-review-attempt-2.md) accepted the exact
refreshed candidate.

[Owner disposition](owner-disposition-62c248b9ab53.json) and the [trusted verifier](verifier-pass-62c248b9ab53.json) bind the exact refreshed tree. The independent review is effective on that candidate.
