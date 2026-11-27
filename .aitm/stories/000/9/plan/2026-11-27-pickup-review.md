# #9 pickup review

Independent Grok 4.7 Build Fast review on integration base `44ca79c17f80a657d6278cfd82cb988e8a19820a`. [First findings](2026-11-27-pickup-review-r1.md) · [Second findings](2026-11-27-pickup-review-r2.md).

PASS

The current #9 pickup matches the accepted C04 contract and closes every item from the second review. Owned paths are the four exact package files. `Backend.read` and `transact` stay fully typed. `RelatedWriteSet`, `FinalizationIntent`, `WriteAuthorizer`, `PendingActionRunner`, and `AttemptPreflight` match the contract fields. `OperationCategory` keeps `normal`, `authored_sync`, `stop_reconciliation`, and `recovery`.

`test_operation_cas` still covers pinned reads, identical retry, changed-payload error, stale read-set conflict, and atomic related-story updates, and those cases stay reusable for Git. Refusal records guards with no transition and no related writes. Memory and Git share pinned reads, immutable prior snapshots, CAS, append order, and atomic related-story writes. Mutations stay on the typed transaction route. A blind file-map API stays out.

A missing `WriteAuthorizer` refuses production writes before C14. C04–C08 use explicit fixture authority. The shipped composition has no allow-all. Absent-capability tests unregister the named slot so they stay valid after a production registration. No attempt in the pinned read-set is explicit not-applicable. Attempt-bearing mutation without `AttemptPreflight` is unavailable. `authored_sync`, `stop_reconciliation`, and `recovery` stay on their declared operations and are not a preflight bypass. Attempt reconcile and expand stay `normal`, require preflight, and cannot skip trip checks. Category and request identity hold across retries. C27, C28, and C30 use test-only injected preflight. Production stays unavailable when required preflight is absent.

Verification is tests first, then `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c04.py -q` to PASS, plus affected contract suites and Ruff. Draft exit still requires exact-repo and Core hosted CI. Merge still requires Grok 4.7 source SAR and the trusted verifier.
