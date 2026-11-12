# #147 independent exact-source reassessment for owner disposition

**Reviewer** Codex / story141, independent of author Codex / story147.
**Reviewed at** 2026-11-12 02:32:20 UTC.

**Verdict** The replacement source addresses both prior findings. No
blocking source findings for owner disposition on the exact replacement
when bound to its authenticated hosted tested tree. Formal independent
post-verifier Review has its own evidence.

| Identity | Observed value |
| --- | --- |
| Target base | `71aa5c880fc6a1db1cf676dfc663373f02ef7b16` |
| Replacement head and tree | `0d8f8ea353d71ab19802e882ceecbd105e6837ae`, `9699130f9be8411cb2a5646197e803956b1ef1b3` |
| Immediate parent | `a9f97f937369192b6f565f6d5cec1e26340358ab` |
| Added source | `tools/ci/tia/controls.py` blob `b89aff93e93323749946ec5c2b40a72af9a21203`, raw SHA-256 `7283e2dcb149adba06ab1fd992d39f643c5b217c06d141dd1ef4a5578b541001` |
| Added tests | `tools/ci/tests/test_tia_controls.py` blob `4c8d0e7bce5c75cbe86abcecf4d68ba4b440db62`, raw SHA-256 `a33ca2a3c3ad7befc485c11b45adfdd357e5b1516eddaa793ffa58543d4bebbc` |
| Accepted Plan and JIT | Planning `4a56ad67541ae17d9b90fd05d633124711ed210a`; same accepted Plan and JIT as the original assessment. |

- The full-scope correction at `tools/ci/tia/controls.py:336` compares
  SHA-256 of both trusted T02 policy inputs against the declared
  scope, matches the T02 workload and complete set of reviewed
  profile/platform pairs, and checks owner, runner identity and
  capabilities before binding any decision. Exact approvals attached
  to missing helper, wrong platform, or wrong owner evidence yield
  `invalid_scope`, with full required and no approved references.
  The added secondary-platform case proves the complete lane check
  follows the reviewed policy. A separately named comparison workload
  retains the full trigger and its approval cannot clear a full scope.
- The reference correction at `tools/ci/tia/controls.py:711` requires
  proper observer and receipt digests and a nonempty named map of Git
  control identities before accepting a lane as collected. Tests
  hold the exact raw digest fixed to the received bytes and exercise
  null, malformed and empty provenance. The accepted T02 fixture
  continues through the genuine classifier and existing replay.
- Both public T10 function signatures and output schemas are unchanged.
  `ControlCandidate` adds a typed field for the independently reviewed
  T02 `SuitePolicy` bytes needed to establish scope. An absent,
  incompatible or digest-mismatched policy fails closed. This implements
  the accepted plan's caller-supplied trusted workload boundary without
  obtaining policy from candidate execution or adding an authority
  source. No upstream file, workflow or live policy changed.

The exact target range adds only the two owned paths and passes Git
whitespace checks. With locked CPython 3.13.9, an independent focused
selection ran all 14 new cases and passed in 4.25s, with 41 older cases
deselected. The author branch was clean and on the exact reviewed tree
before and after those checks. The remote branch still pointed to the
earlier attempt at initial readback. Bind any owner decision to the
replacement's actual PR head, applicable base, tested tree and hosted
attempt after separate read-back.
