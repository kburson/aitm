# #377 Linux runner transition

The current required gate runs the literal PR base and checks that its test outcomes carry forward. The delivered verifier expects Darwin APFS evidence. The macOS runner switch therefore uses two ordered pull requests. Both use the canonical CI gate and exact-tree source review.

1. [PR #378](https://github.com/kburson/aitm/pull/378) makes the literal base testable on Linux and adds Linux evidence to the verifier while retaining legacy evidence validation. Test IDs in the required product baseline carry forward. The Linux install path retains the strictly inspected runtime layout.
2. [PR #379](https://github.com/kburson/aitm/pull/379) switches the two required Python jobs to Ubuntu 24.04 and exercises public watch events. Its initial hosted runs target the bridge branch for early qualification. Retarget to trunk after the bridge merges and require a fresh canonical run on the live base, head, and merge tree.

A non-root Ubuntu 24.04 replay of the bridge passed 1,524 tests using CPython 3.13.9 and three workers. The first hosted cutover attempt stopped because it probed Python before the locked environment installed it. The next attempt hit the runner-home ACL ancestry and was refused by the existing ledger checks. The next candidate uses private scratch for the pinned interpreter and test fixtures. Hosted CI remains the delivery gate.
