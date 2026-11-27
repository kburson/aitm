# #10 pickup review

Independent Grok 4.7 Build Fast review on integration base `48666e85daf2bd3f42a3e09849603d0329e61cf8`.

PASS

The #10 pickup matches the accepted C05 contract and the C04 prerequisite at `48666e85daf2bd3f42a3e09849603d0329e61cf8`.

- Paths are the package-qualified forms of the contract files: `packages/aitm-core/src/aitm_core/store/git_backend.py`, `packages/aitm-core/src/aitm_core/store/objects.py`, and `packages/aitm-core/tests/integration/test_c05.py`.
- `GitBackend(Repository, ValidationGate).transact(op, expected) -> OperationResult` and `read_tree(oid) -> Snapshot` are the produced contract. The gate is required for the literal target, production registration stays in C06, and the shipped backend has no allow-all default. Temporary Git tests use explicit fixtures.
- Snapshot reads pin one immutable tree and read it only through `git cat-file --batch`, keeping C04 `read(snapshot, paths)`. CAS uses a temporary index plus `hash-object`, `commit-tree`, and `update-ref` against the expected old ref, with the caller index and working tree left isolated. One commit stores the operation outcome, guard results, events, related writes, and pending action identifiers.
- Recovery is by operation ID after interruption both before and after ref CAS. `test_git_transaction` starts the work and reruns the C04 contract on real temporary Git, including typed read-set, operation outcomes, and service authority.
- Verification is `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c05.py -q`, the affected suite, and Ruff. Delivery is a draft PR, exact-repo Core hosted CI before ready, then a fresh Grok 4.7 source SAR and the trusted verifier before the exact merge, followed by integration closeout and #10 Done.
