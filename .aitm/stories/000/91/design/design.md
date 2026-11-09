# As-of export and C44 compatibility proof design

[Reviewed parent design](../../83/design/usage-capture-design.md) at raw SHA-256 `d716e3bb03ed4622935df0af39fb87891feb4132c1278441ddc3db7fbf0ee8ee`. The scope below implements U07 for #91. [Accepted amendment](../../83/plan/usage-capture-replan.md) at raw SHA-256 `7df41b26c4b4f9ce786807832ba544862560eac1e297a22c497fb31791f5c239` also governs this pickup. [Accepted relationship amendment](../../83/plan/usage-capture-relationship-replan.md) at raw SHA-256 `55eb9f5a6edf6e0d8a63d9bce64979a1d397d5defc7608395511ae13127930c8` also remains in force.

Produce deterministic fixed-view usage snapshots with an explicit rate basis and exact scope provenance, and prove replay and reconciliation against a temporary immutable receiver. The existing local ledger stays authoritative. The fixture exercises the future C44 seam.

The collector is maintained for the life of AITM. This leaf contributes the scoped deliverable in the parent plan. Work belongs to #83.
