# Draft aliases, ancestry and direct/inclusive rollups implementation plan

[Leaf design](../design/design.md) · [Accepted parent plan](../../83/plan/usage-capture-implementation-plan.md) at raw SHA-256 `07919dde4475310b7fe277791206f611ce5cd615eeaed491d3a619e61142daf5`. [Accepted amendment](../../83/plan/usage-capture-replan.md) at raw SHA-256 `7df41b26c4b4f9ce786807832ba544862560eac1e297a22c497fb31791f5c239` also governs this pickup.

**Estimate** 3 agent-hours including source review and verification. Stop and return to planning if the estimate ceases to fit.

**Files** `src/aitm_usage/{rollup,cli}.py`, `tests/test_rollup.py`.

**Contract** `rollup(root: ItemKey, view: LedgerView) -> UsageRollup`. Queue alias and parent commands through U02's inbox. Preserve revisions of ancestry and graduation aliases and compute inclusive totals from distinct canonical descendants. Represent known Decimal price and a separate Unknown count.

- [ ] Write `test_graduation_and_inclusive_rollup` with an epic, two children, an alias from draft to issue, epic batch usage and per-child usage. Assert each observation contributes once, previous as-of results remain intact and cycles or contradictory aliases are refused. Exercise real CLI publication of alias and parent commands. Use price fixtures until U06 supplies accounting.
- [ ] Run `test_rollup.py` to show failure, implement the rollup and alias/ancestry commands, then pass leaf verification.

## Pickup detail

Use U02 queue publication, typed digest and disposition, and the guarded commit unit that accepts a typed revision tuple. Extend the static command and record unions in types.py for alias and parent only. Add only their order and evaluation dispatch cases in scopes.py. Resolve shared project identity in cli.py by validating the existing private state root, database and sidecars with U01 path checks, then reading the project UUID from the SQLite identity row through the existing lease-free read-only connection. Call Ledger.open for full guard, UUID, key and schema verification before enqueue. Do not copy the private key or initialize new state. Reject a wrong or malformed identity and unsafe state before publication with a sanitized error. Test arbitrary ordinary state-directory paths and actual CLI submissions while the writer is active. If this requires an unassigned ledger.py edit, return to planning. Keep one entrypoint for later commands. Avoid a new storage engine, registry or alternate command path.

For rollup, use verified current UsageObservation records and resolve_scope from the same fixed LedgerView. Canonicalize draft and issue identities before selecting direct and inclusive sets. Verify valid alias and parent updates, exact replay, contradictory aliases, and cycles created through canonicalization. Reopen the ledger and repeat direct/inclusive parity. Retain earlier as-of attribution after a later alias or parent change. Each observation contributes once and unknown scope is not attributed to an item.

The narrow price projection used by the rollup reads only matching current typed records from the supplied fixed LedgerView, including in-memory fixtures for the interface. It requires the observation SourceRef key, matching revision number, versioned rate basis, and Decimal USD or unavailable. Define it in rollup.py without persisting fixture-only records. U06 supplies the concrete typed durable accounting record with the same fields and cannot modify rollup.py. Use a unique qualifying price basis for the observation in that snapshot. If more than one distinct basis is present and no basis is selected, keep price Unknown, as with mismatch or missing evidence. Test that pricing recorded at a later sequence leaves the older rollup unchanged. Show known-price and Unknown counts with preserved token quantities in the same test. Keep billing and quota out of the price projection.

Pin the independently accepted exact U02 predecessor and stop for changed ownership or a forecast above three agent-hours. Retain TDD RED/GREEN, full suite, Ruff, and independent source verification.
