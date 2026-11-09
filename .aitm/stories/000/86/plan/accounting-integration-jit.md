# U13 accounting integration pickup

Accepted [scoped follow-up](../../83/plan/usage-capture-accounting-integration-supplement.md) at raw SHA-256 `b7bc937e48a5f7105b47740904a18abad6e0b52a2694f7ad1b6b916cd901f6d7` and [independent exact review](../../83/plan/usage-capture-accounting-integration-supplement-review.md).

Integration base `b08e49b1a1afc3bd491376f7f32621fb42f8e7a4`. Reuse the clean dedicated branch `codex/aitm-usage-u13` and retain the original source receipt.

Rollup addition inherits the caller's Decimal context. It rounded an ordinary rate under a low-precision context and a schema-valid wider custom price at default precision. Sum exact U06-bounded amounts deterministically across direct, inclusive and unattributed totals. Keep the current projection and relation behavior. Use only rollup implementation and tests.

Original cap 3 agent-hours. Retain RED and GREEN, full locked tests and independent exact source review.
