# #190 delivery checklist

Attempt 1. Implementer is the assigned Codex agent. Closure owner is the coordinating Codex agent. Target trunk. Pickup base `72ca2d2535248844b164014d7817bffec0e9fb7e`. Predecessors #188, #189 are delivered. File ownership is defined by the exact pickup.

- [x] [Design, Plan and JIT](jit.md) and [independent acceptance](jit-review.md).
- [x] Local verification, applicable hosted CI and independent source acceptance.
- [x] Verified merge, implementing-agent sign-off, and issue/Project closure.

## Candidate 2

[Source PR #219](https://github.com/kburson/aitm/pull/219) targets trunk base `72ca2d2535248844b164014d7817bffec0e9fb7e`. Exact head `577ba9382cd8298922a83803aa3e66abdc853fa3` and tree `4d0144095980203ca7833e3581adac0e32cee6a4` contain only the reviewed story paths. Focused dashboard tests, the full dashboard suite, Ruff, and whitespace checks passed on the clean checkout.

- [x] [Hosted CI](https://github.com/kburson/aitm/actions/runs/42959980651/attempts/1) and [delivered verifier](hosted-verification-2.json) passed.
- [x] [Independent source review](post-ci-source-review.md) accepted the exact signed tree. Off-platform review, with native approval absent.

# #190 snapshot readback

Python 3.13.9 ran 56 dashboard tests, including the real planning pin, with Ruff lint/format and Git whitespace checks passing. Two distinct Git readers with the same as-of 2026-11-11T04:23:16Z produced byte-identical snapshot and validation pairs.

- Historical planning `17761cc1928fd916cf32a9c078d4a742bfcb32b8`, 169 stories. Snapshot `e46da18999caf132dcc451e9ae8e7b12dd5517a49113f85931c48d93c5e3772a`. Validation `3497de8b8d908759aa0e62bd313de3bced70e4fba6bd82e6aaa2dfa227821ab6`. All ten legacy direct and inclusive Actual values match the accepted readback, with partial coverage. #111 implementation elapsed is 774000 ms and all-phase elapsed is Unknown.
- Later planning `200bae51aa458152f98b98a34a29fdc176c4f6d1`, 179 stories. Snapshot `bcd22bdb3a9150cdd85bdf9c8ba4b723240768dfc630db3371c80fa8b5391b5a`. Validation `4f3a8a69369f4a5dd113dd19da04f27388c252f11676f6cb40692d3932774fec`. Direct agent work is attributable to #186–#189. #111 preserves the same elapsed scope and coverage.
- Each validation artifact binds the exact snapshot digest. Direct and inclusive Cost remain Unknown across both views without a verified report selector. A separate focused fixture resolves and preserves an exact Decimal cost and independent usage cutoff.

Precheck found a missing estimate basis, malformed events that displaced progress, and a directory substitution race. The revised candidate includes tests for all three. The initial hosted run [42959652223](https://github.com/kburson/aitm/actions/runs/42959652223) on head `4698428af832024651c54b2fc53a5b580485140b` was superseded before Test.

The signed candidate matches tested merge `d7e93ca475bbfb2e54870ddb348fc8e355073dd3`, with the ordered base/head parents and the exact tree above.

## Verified delivery

[PR #219](https://github.com/kburson/aitm/pull/219) merged to trunk at `2026-11-11T04:41:45Z` as `5cc77ab5f66e98d9d2777d7816f662e71a8804e9`. The exact reviewed tree `4d0144095980203ca7833e3581adac0e32cee6a4` is reachable from remote trunk `5cc77ab5f66e98d9d2777d7816f662e71a8804e9`. Ordered merge parents `72ca2d2535248844b164014d7817bffec0e9fb7e` and `577ba9382cd8298922a83803aa3e66abdc853fa3` match the tested candidate. [Implementing-agent sign-off](../retro/2026-11-10-implementer-signoff.md) passed at `2026-11-11T04:41:48Z`. The issue closed Completed at `2026-11-11T04:41:51Z` and the project item read back Done.
