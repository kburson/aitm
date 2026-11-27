# #12 initial pickup review

Independent Grok 4.7 Build Fast review.

CHANGES REQUIRED

The owned paths match C07 (`config.py`, `models/config.py`, `store/installation.py`, `services.py`, `packages/aitm-core/tests/integration/test_c07.py`). The producer signatures, `services.policy` wiring, same-commit workflow bytes with parsing left to C90 and cutover left to C98, `review.documents.design_coverage=own-document`, separate `review.source` schema/independence/assurance fields, and the C110/#497 gate citation are intact. Tip-effective Git host configuration stays unable to redirect the anchored store.

Required corrections:

1. **Prerequisites.** Carry C03 and C06, plus C01 `StoreAnchor`/`RefreshResult` as structural input types only. `RefreshResult` is an input port. C08 stays the owner of network refresh and stale/unknown freshness, and is not a C07 implementation dependency. Drop “consume typed fetched observations from C01/C08” as a dependency.

2. **Reconfigure vs fence.** Anchored code, default, store, and issuer changes require reconfigure. A delivered issuer/anchor change fences both enforcement modes. Keep “related routing” out of that fence.

3. **Authority tests.** `test_policy_authority` must show story-edited limits, mode, and commands are ignored, and story-worktree substitution cannot change authority. Tip-effective fields apply on the next pinned evaluation. Missing or unsupported policy, including inherited coverage, stays unavailable. Labeled fixture values stay fixtures and are not product defaults.

4. **Verify gate.** Keep the leaf command `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c07.py -q`, plus affected contract suites and Ruff. Exact repository CI and separate Core hosted CI precede draft removal. A fresh Grok 4.7 source SAR and the trusted verifier precede exact merge, then integration landing, closeout, and #12 Done. Preserve the accepted amendment’s state flow, JIT review threshold, and host authority in `0945941c6c024b6dd621202b2456696ae1df0154`.
