# Story #459 exact-source approval

Claude Sonnet 5.5 approved the replacement source independently. The original review requested more evidence for ambiguous scope, unpriced usage, foreign pins and receiver readback. Sixteen focused producer and fixture tests passed after the additional cases. The existing coverage and receipt guards prevent ambiguous timing joins from attributing a receiver row. The replacement production source matches the original reviewed diff.

- Base `0f8c6ff70b5112bd3a17af3a2ab5665e347a416c`
- Approved head `51d19ac11c8c515abf95664058b577e5bc2a7452`
- Approved tree `1fbe3c6012ada44431ea6d6d75646bab9533a1ca`

The exact local full rerun passed 1,780 tests with one skip. An earlier intermittent failure in the unchanged macOS watcher passed in its isolated run and the full rerun. The authenticated trusted verifier passed on GitHub's exact merge tree. Hosted Ubuntu and Windows wheel jobs passed. The supplemental local macOS installed wheel passed all 236 fixtures.

GitHub cancelled both hosted macOS jobs before assigning a runner. Story #459 remains in Test. The source approval and local evidence are available for the next hosted attempt on the same tree. [Trusted CI](459-trusted-ci.json) · [Local macOS evidence](459-local-portability.json) · [Hosted macOS attempts](459-hosted-macos-hold.json) · [Premerge #461 rehearsal](459-fixture-rehearsal.json).
