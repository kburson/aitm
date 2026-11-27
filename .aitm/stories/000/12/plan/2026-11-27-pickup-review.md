# #12 pickup review

Independent Grok 4.7 Build Fast review on integration base `cce0cb2b033be027f695e3d8f9896edca40de765`. [First findings](2026-11-27-pickup-review-r1.md).

PASS

The owned paths match C07 exactly: `config.py`, `models/config.py`, `store/installation.py`, `services.py`, and `packages/aitm-core/tests/integration/test_c07.py`. The implementation prerequisites are C03 and C06, with C06 as the shared-file predecessor. C01 supplies `StoreAnchor` and `RefreshResult` as an input port. C08 retains network refresh and stale/unknown freshness.

`resolve_policy(anchor: Installation, refresh: RefreshResult) -> PolicySnapshot` and `classify_change(old, new) -> PolicyChange` match the producer contract, including `services.policy` wired to the committed resolver. Policy and configured workflow bytes come from the same anchored default commit. C90 retains parsing and C98 retains cutover. Story-worktree substitution cannot change authority. Anchored code, default, store, and issuer changes require reconfigure. A delivered issuer or anchor change fences both modes. Tip-effective fields apply at the next pin, and tip-effective Git host configuration cannot redirect the anchored store.

`review.documents.design_coverage=own-document` and the separate `review.source` schema, independence, and assurance fields stay explicit. Missing or unsupported inherited coverage stays unavailable. Missing, ambiguous, or unsupported policy reports unavailable. Labeled fixtures supply no product defaults.

The verification gate is `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c07.py -q`, plus the affected contract suites and Ruff, after tests first via `test_policy_authority`. Exact repository CI and separate Core hosted CI precede draft removal. A fresh Grok 4.7 source SAR and the trusted verifier precede exact merge, followed by integration landing, closeout, and #12 Done. The C110 trunk fixture remains the gate citation, and the accepted amendment’s state flow, JIT review threshold, and host authority stay intact.
