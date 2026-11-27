# #9 second pickup review

Grok 4.7 Build Fast verdict.

CHANGES REQUIRED

The revised pickup still drops contract constraints that change what #9 is allowed to ship. The branch pin, dependency set, category values, CAS retry and conflict cases, Git-reusable tests, fixture authority, slot unregister, normal-category preflight for reconcile and expand, and the C27/C28/C30 test-only injection are aligned with C04.

Required changes:

1. Name the owned paths exactly: `packages/aitm-core/src/aitm_core/models/operations.py`, `packages/aitm-core/src/aitm_core/store/backend.py`, `packages/aitm-core/src/aitm_core/store/memory_backend.py`, and `packages/aitm-core/tests/unit/test_c04.py`. Scoping `models/` and `store/` only as siblings of `tests/` under `packages/aitm-core` points at the wrong tree.

2. Keep the port signatures typed: `Backend.read(snapshot: Snapshot, paths: Sequence[str]) -> Blobs` and `transact(op: Operation, expected: Snapshot) -> OperationResult`. Field lists for `RelatedWriteSet`, `FinalizationIntent`, `WriteAuthorizer`, `PendingActionRunner`, and `AttemptPreflight` already match.

3. State that a missing `WriteAuthorizer` refuses production writes before C14, and that C04–C08 must not rely on a shipped allow-all. “Missing registration refuses” is satisfied by registering an allow-all. Keep the unregister-the-slot rule, and state that those negative tests must not treat permanent absence as the production default.

4. State that `stop_reconciliation` and `recovery` are narrow capabilities for their declared operations and are not a blanket preflight bypass. State that attempt reconcile and expand stay `normal`, require preflight, and must not borrow `stop_reconciliation` or `recovery` to skip trips. `authored_sync` stays on its own declared operations. It is not a bypass category.

5. Restate the boundary: no blind file-map API and no MemoryBackend with weaker semantics than pinned reads, immutable prior snapshots, CAS, append order, and atomic related-story updates. Refusal must record guards with no transition and no related writes.

6. Name the verify gate: `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c04.py -q` to PASS, plus the affected contract suites and Ruff. Tests come first. The draft, hosted CI, source SAR, and verifier steps can stay as delivery gates around that.
