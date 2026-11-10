# #104 design · Bootstrap Actions and Python validation

## Scope

CI1 establishes the initial same-repository GitHub Actions route to trunk. The parent design governs this leaf at SHA-256 `d48fc2bd0b1973c48a39b4b197a9ab7e97d77db7bdd34980e58022037d4c1ed0`. [Accepted parent design](../../103/design/github-ci-quality-gates-design.md).

The first PR begins with a standalone read-only diagnostic on a hosted macOS runner. It identifies the event and runner for comparison with authenticated GitHub evidence. The closure owner must establish the tested merge's immutable association with the specific Actions run and attempt, independently of the diagnostic output. The exact Git commit's ordered parents must corroborate the event base and head, and match the live target and PR head. A matching current PR merge ref can corroborate the object but does not establish that association. If the provider linkage is missing, return to Planning before building CI.

## Delivery when the diagnostic clears

On that same PR, add the first complete collector and executable CI helper tests, trusted exact-base inventory, locked wheel smoke and stable `aitm-ci` aggregate. Use the unrounded 90% line floor separately for the Python source and executable CI helpers. Coverage improvements must verify observable behavior, failure dispositions or invariants. Keep the required Darwin tests serial and explicitly account for subprocess measurement and outcomes.

The real bootstrap PR must pass every required gate and independent source review. Verify the trunk merge and push workflow and prove the integration route on the named disposable PR. Close this leaf on its own final gate and sign-off. Later verifier and file-lint source belong to #105 and #106.
