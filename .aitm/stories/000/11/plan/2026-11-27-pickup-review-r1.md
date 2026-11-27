# #11 first pickup review

Independent Grok 4.7 Build Fast verdict.

CHANGES REQUIRED

The pickup matches the owned paths, the C05 pin plus the C01/#3 predecessor, the three produced signatures, distinct review refs, planning-versus-delivery validation, the unregistered `ForwardRepairVerifier` slot that must stay refused after C10, `test_store_gate` first, `test_c06.py` with affected suites and Ruff, and exact-repository plus separate Core hosted CI before draft removal and before the Grok 4.7 source SAR and trusted verifier.

Three contract obligations are still loose:

1. **Rejection set.** State empty-root, single-parent, authorized data paths, and code-ancestry isolation, and reject symlinks, submodules, path traversal, code or executable payloads, and outside-path writes.
2. **Entry points.** A real `planning validate` and a normal `GitBackend` transaction through `services.backend` must each reject an outside-path write. No caller can omit `ValidationGate`.
3. **Checkout gate.** One clone lock must serialize supported ref mutations and branch-binding or checkout operations, including fetch-view advancement, retries, init, repair, and migration, while checking only the literal target. Supported operations must not check out that ref. Refuse an already checked-out target. On an external checkout between pre and post checks, keep both refs, the index, and unsynced bytes, fence publication, and require explicit reconciliation without reset or automatic index repair. Diagnostics must state the cooperative-exclusion limit.
