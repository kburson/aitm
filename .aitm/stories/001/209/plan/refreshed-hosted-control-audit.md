# #209 independent refreshed CI-control audit

**PASS** for the exact reviewed tree `b4a757f106b89086a24d0e909bc259d7b5b93c88`, literal trunk `56266ed30bbc572b7e56bc64777e802be264c23f`, and candidate `dab76d25ffdce10d5782e14b5b1ea02f617b235c`.

Independent Codex reviewer `capture_workflow_review` applied the literal-base verifier's `gate_controls` to both trees. Each tree has 67 control entries. Only the two existing journal test blobs differ, with both endpoints matching the prior independently audited changes. The exact binary test diff has SHA-256 `a39f3bdc728605cc1916980ccfc8012536d412a7d0347dd83a841deadfdbbdce`. Prior head `0bcb00c69cbf5d38431480b90260d013a6f09e3e` resolves to the previous audited tree.

The candidate inherits the workflow, observer, verifier, policy, gate, lock and configuration byte-for-byte from trunk. The candidate runs the full package and CLI-evidence suite with three workers. Exact worker receipt, collection and phase reconciliation feed the full baseline retention and no-deterioration checks, raw 90 percent line floors, child evidence, APFS capability, artifact custody and signing. The delivered TIA inventory adds no CI selector. The two retained test changes require the explicit exact reviewed-tree input to the trusted verifier.

This audit covers the transported test controls and exact current tree. The hosted verifier must still authenticate the current merge tree and ordered parents, and independent source acceptance follows signed validation.
