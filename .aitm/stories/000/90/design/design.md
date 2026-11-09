# Pricing and quota availability design

[Reviewed parent design](../../83/design/usage-capture-design.md) at raw SHA-256 `d716e3bb03ed4622935df0af39fb87891feb4132c1278441ddc3db7fbf0ee8ee`. The scope below implements U06 for #90. [Accepted amendment](../../83/plan/usage-capture-replan.md) at raw SHA-256 `7df41b26c4b4f9ce786807832ba544862560eac1e297a22c497fb31791f5c239` also governs this pickup. [Accepted relationship amendment](../../83/plan/usage-capture-relationship-replan.md) at raw SHA-256 `55eb9f5a6edf6e0d8a63d9bce64979a1d397d5defc7608395511ae13127930c8` also remains in force.

Normalize independent API-equivalent prices, provider account-window observations and separately unavailable billed spend. Reuse each provider adapter's measured request categories and the existing as-of ledger and fixed-view rollup. Only exact known Standard comparisons receive prices, with explicit Unknown and retained coverage otherwise.

The collector is maintained for the life of AITM. This leaf contributes the scoped deliverable in the parent plan. Work belongs to #83.
