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
