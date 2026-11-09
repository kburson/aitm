# U04 accounting integration verification

Integration base `296c6c314453c9682df62f1174d5a999d81795c9`. Independently accepted exact head `b08e49b1a1afc3bd491376f7f32621fb42f8e7a4`. [Original source review](source-review.md) retained.

The locked package suite passed 357 tests on the exact integration source. Ruff and diff checks passed.

Independent exact spec PASS and quality PASS. Thirteen targeted reviewer cases verified valid account windows, genuine inline signals with no verified account, malformed envelope and foreign limit ID coverage, absent and credits-only signals, and held/excluded paths. The source uses an existing sanitized diagnostic and preserves known usage. It never creates a task debit. Only Codex adapter and tests changed.
