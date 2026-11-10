# #138 delivery evidence

Attempt 1. Implementation owner `codex-collaboration:/root/impl138`.
Closure coordinator Codex. Literal parent `trunk`. Follow the
[manual delivery checklist](../../../../manual-delivery-checklist.md)
and [#103 verification contract](../../103/design/github-ci-quality-gates-design.md).
The owner's stop is before merge.

## Candidate `28db19ee8415` · Test

[Open PR](https://github.com/kburson/aitm/pull/183) · base `d769b3169724eeb9ef4b4aee47d3ab4c4489072d` · head `28db19ee841567bdab9f0c4624fb30ed18a7047e` · local tree `cbda78ce605593be91611a02c06d51edd7ff9c87`.

- Locked Python 3.13.9 and uv 0.10.6 on the isolated source checkout.
- Exact-head focused pytest result `49 passed in 0.13s`.
- Exact-head full local package and CI test result `945 passed in 99.03s (0:01:39)`.
- Ruff check, Ruff format and source diff whitespace passed.
- Focused collection and execution are separate from the hosted #103
  test list and helper denominator.
- Hosted validation and independent review apply to this exact candidate.

### Prior local observations

The first broad run on the original candidate ended with 11 failures,
928 passes and 5 setup errors. The repeat ended with 7 failures, 936
passes and 1 setup error. Both involved unchanged native monitor and
scan tests. A targeted comparison of the 22 distinct nodes passed on
both frozen trunk and the original candidate. The complete original
candidate then passed with a dedicated pytest temporary directory
(`944 passed in 97.11s (0:01:37)`). Retain the failed logs separately. The
exact replacement uses that isolated directory approach and retains
the full inventory. A precise cause of the transient failures was
not established.

The [first independent review](source-review-attempt-1.md) found a
stable error-category gap for malformed helper command quoting. The
[replacement review](source-review-attempt-2.md) verifies its
resolution at `28db19ee841567bdab9f0c4624fb30ed18a7047e`. No unresolved source
findings remain. The [sanitized historical report](../attachments/serial-baseline.md)
reconciles the same canonical baseline bytes across the correction.

## Authenticated hosted Test

All six required jobs passed on the [exact attempt](https://github.com/kburson/aitm/actions/runs/42898241656/attempts/1).
The signed verifier components and independent raw replay agree on the
tested merge `c7efd9d46034905ea08a0ff0cabeb697b13f58f7`, ordered base/head, and exact tree
`cbda78ce605593be91611a02c06d51edd7ff9c87`. The hosted result retained 713
trusted base outcomes and verified 714 product
and CLI outcomes. Product line coverage was 8404/9229
and helper coverage was 778/821,
both above the 90% floor. [Exact evidence](hosted-test-28db19ee8415.json).

GitHub's rules were unchanged. The verifier classifies the two new
files under `tools/ci/` as gate-defining. The workflow, policy,
trusted verifier, lock and required test list and helper coverage
denominator are unchanged. The existing #103 owner disposition
applies separately to these exact additions.

The [superseded hosted run](https://github.com/kburson/aitm/actions/runs/42897701333) was cancelled after the correction push. Its results carry no authority for the replacement.

The owner’s exact-tree disposition is pending. The [trusted verifier hold](verifier-hold-28db19ee8415.json) leaves the story in Test while the independent source verdict is retained. The PR remains open and unmerged.
