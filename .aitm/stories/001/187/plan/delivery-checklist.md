# #187 delivery checklist

Attempt 1. Implementer and closure owner are Codex. Target branch `trunk`. Prerequisite #186 is delivered and closed. Only the two attribution paths and #187's own planning records are in scope.

- [x] [Design, Plan and JIT](jit.md) reviewed and accepted in the [independent verdict](jit-review.md).
- [ ] Exact candidate, focused dashboard verification and hosted CI.
- [ ] Independent source review, merge readback, retrospective and closure.

## Candidate 1

[PR #208](https://github.com/kburson/aitm/pull/208) targets trunk base `1282538954dc5a7e7f7b27da4e3ab096892e3add`, head `a35a6c2b99bde7c19c179a1c93060e5d66e04229`, tree `0f285f7cd50587f18dae78304c1b12fa731620f1`. The two-path diff is confined to the attribution module and its tests. The clean candidate passed the dashboard suite, Ruff and both real planning pins with all 114 direct intervals and ten exact direct subtotals.

[Candidate 1 CI](https://github.com/kburson/aitm/actions/runs/42945752556) was canceled after the replacement pushed. Its trusted-base, quality and file checks had passed on the superseded head.

The independent preliminary review reproduced two defects on candidate 1. A boundary with neither endpoint supplied no missing-evidence gap. A same-scope replay in a different receipt could bypass an unsupported revision's hold. Both cases were reproduced in regression tests before correction. The fix keeps one-ended boundaries and unrelated scopes available. This precheck is separate from the required final signed-candidate review.

## Candidate 2

[PR #208](https://github.com/kburson/aitm/pull/208) targets trunk base `1282538954dc5a7e7f7b27da4e3ab096892e3add`, head `68ab81db38f90dca2167ffe0e71b0d8789ce3b3a`, tree `f62fbd48047f73baf52f65f86b33d475328b2f1f`. The two-path diff is confined to the attribution module and its tests. The clean candidate passed the dashboard suite, Ruff and both real planning pins with all 114 direct intervals and ten exact direct subtotals.

[Candidate 2 CI](https://github.com/kburson/aitm/actions/runs/42946132032/attempts/1) passed trusted base, quality and file checks. The [candidate Python job](https://github.com/kburson/aitm/actions/runs/42946132032/job/130279377837) failed in two existing Codex monitor tests. Evidence collection failed and signing was skipped.

Monitor failure evidence: `test_lookahead_receipt_enrolls_exact_request_and_aggregate_stays_unassigned[reasoning-True-]` found no candidate, and `test_activation_frontier_requires_exact_first_eligible_delta[warm-True]` returned no expected observation. The other 994 cases passed. The monitor, CI policy and verifier are unchanged relative to the base. Trigger a fresh first attempt, because the verifier's GitHub rerun timestamp check is a known hold.
Both named monitor failures passed on a focused local rerun using the same source.

## Candidate 3

[PR #208](https://github.com/kburson/aitm/pull/208) targets trunk base `1282538954dc5a7e7f7b27da4e3ab096892e3add`, head `27abd178ce3e0b1e076e2c94c3a4a3f863179254`, tree `f62fbd48047f73baf52f65f86b33d475328b2f1f`. The two-path diff is confined to the attribution module and its tests. The clean candidate passed the dashboard suite, Ruff and both real planning pins with all 114 direct intervals and ten exact direct subtotals.

- [x] [Hosted CI](https://github.com/kburson/aitm/actions/runs/42946905299/attempts/1) and [delivered verifier](hosted-verification-r3.json) passed.
- [x] [Independent source review](post-ci-source-review.md) accepted the exact signed tree. Off-platform review. No native review was submitted.

The tested merge `ecf070613b90ad20f8a833134477bbd615065150` has the ordered base and head parents above and the same tree as the local candidate. The trusted verifier checked the signed evidence for all six jobs. Dashboard tests remain separate local proof.
