# #11 pickup review

Independent Grok 4.7 Build Fast review on integration base `25b0657dccf471820387402053f1efd1e00c3b52`. [First findings](2026-11-27-pickup-review-r1.md).

PASS

The revised pickup closes all three prior gaps and stays inside the accepted C06 leaf.

1. **Rejection set.** It requires an empty anchored root, single-parent continuation, authorized data paths, and isolation from the anchored code ancestry, and it rejects symlinks, submodules, path traversal, code or executable payloads, and outside-path writes.
2. **Entry points.** A real installed `planning validate` and a normal `GitBackend` transaction through `services.backend` must each reject an outside-path write, and every transaction requires the injected `ValidationGate`.
3. **Checkout gate.** One cooperative clone lock covers supported ref mutations and branch-binding or checkout operations, including fetch-view advancement, retries, init, repair, and migration, and the inventory check is limited to the literal target. Supported operations must not check out that ref. An already checked-out target is refused, and distinct review refs stay allowed. An out-of-band checkout between the pre- and post-CAS checks keeps both ref versions, the affected index, and unsynced bytes, fences publication and further writes, and requires explicit checkout reconciliation while leaving the index and workspace in their observed state. Diagnostics state the cooperative-exclusion limit for arbitrary external Git operations.

The owned paths, the C05 pin and C01/#3 predecessor, the three produced signatures, the planning-versus-delivery split, the unregistered `ForwardRepairVerifier` slot that stays refused after C10, `test_store_gate` first, `test_c06.py` with affected suites and Ruff, and exact-repository plus separate Core hosted CI before draft removal, the Grok 4.7 source SAR, and the trusted verifier all remain in place.
