# U13 accounting integration verification

Integration base `b08e49b1a1afc3bd491376f7f32621fb42f8e7a4`. Independently accepted exact head `424d8a3140f1633ac40fb185212f677934d8d36b`. [Original source review](source-review.md) retained.

The locked package suite passed 360 tests on the exact integration source. Ruff and diff checks passed.

Independent exact spec PASS and quality PASS. The original low-context and wider-rate reproductions return exact USD. Five focused reviewer cases verified deterministic direct, inclusive and unassigned totals with durable U06 accounting, ambient precision/traps and reversed order. The fresh explicit accumulator covers the typed U06 amount and ledger count bounds. Source changes are limited to rollup implementation and tests. Scope and relationship logic remain intact.
