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
