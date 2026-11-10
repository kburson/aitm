# #118 M08a native journal test implementer retrospective

I wrote the 12 original native journal integration cases in `packages/aitm-usage/tests/test_monitor_journal.py` on `codex/aitm-118-routing-journal`, from the accepted pickup base `c4ea6b0d6c548830a3ad05d0bb76ec48625d1ca2`. The tests exercise real Codex Desktop adapter, capture, and scope paths with synthetic transcript rows. I owned the native fixture lane and signed its implementation handoff before source freeze. [Accepted pickup](../plan/2026-11-10-118-routing-journal-plan.md) · [Independent pickup verdict](../plan/2026-11-10-118-pickup-review-r3.md)

## Alignment and evidence

The first-claim, replay, competing-owner, and changed-content cases check that one logical key has one pending owner and that later disputes and holds preserve the original payload. The copy case admits two physical source roots against matching prefixes, because capture verifies each locator and incarnation. It proves that byte-exact transcripts deduplicate one logical key while keeping independent cursors, and that a distinct native response with equal token counts receives its own key. The negative cases cover cloned proof and cursor objects, stale prior, replaced incarnation, a missing cursor, a scanner fallback without a verified session, and an adapter-issued identity conflict that remains visible through the scope reader.

My `test_reservation_and_cursor_commit_together` performs the real cursor write and then injects an error before commit. It verifies rollback across reopen before retrying successfully. A separate test stages one observation, reopens with the earlier cursor, and settles the full native batch. The terminal receipt fixture stages preceding usage and holds progress until the exact native turn receipt has a durable scope event. A subsequent observation proves that the explicit scope survives reopening. The coordinator subsequently added `test_journal_reconfirms_visible_scope_replacement_before_durable_progress` to exercise a different fault, a visible scope replacement followed by failed directory sync. [Delivery checklist](../plan/delivery-checklist.md) · [Independent source review](../plan/post-ci-source-review.md)

## Misses, repair, and timing

The first RED reached the native setup and failed on import because the parallel storage module was still absent. That run provides integration evidence for the missing feature, with limited evidence about which individual assertions would catch a regression. I wrote the other cases while production work continued. My first terminal receipt probe closed an empty turn and emitted a coverage gap, which could independently block progress. I used a delayed pre-cutoff counter to close the turn structurally and asserted that the real adapter produced a full cursor, zero diagnostics, and a receipt beyond all admitted usage. That made the receipt's effect observable independently of diagnostics.

The locked journal lane passed all 12 tests in 4.01 seconds. The related journal, scope, adapter, registry, and ledger run passed 192 tests in 14.01 seconds. Ruff lint, formatting, and whitespace checks passed. Those are test execution times. Active authoring and debugging time, and idle time between checkpoints, are Unknown.

## Delivery and confidence

The locked delivery gate passed 920 product and CLI tests and 182 helper tests. The signed hosted run 42922357862 attempt 1 and the independent Claude Opus 5.5 medium PASS both cover reviewed head `db814e9e8d37e08860e822baed72f917132541a6` and exact tree `cb6ff8ce8506abc2a4bda4da3ddad93a35c33aad`. PR #200 merged to literal trunk as `1452999b2f0f5a90161e39862458029c0084772c` at `2026-11-10T23:30:24Z`. I verified locally that the reviewed head and delivered merge have the same tree. [Signed hosted receipt](../plan/hosted-ci-receipt.json) · [Independent source review](../plan/post-ci-source-review.md) · [PR #200](https://github.com/kburson/aitm/pull/200)

**Confidence 4/5** in the native journal fixtures. Their assertions use real admission and scope authority, and the terminal-receipt and rollback cases check durable state after reopening. The original lane used Codex Desktop fixtures, so its direct provider-specific evidence is limited to that adapter.

Signed at `2026-11-10T23:31:58Z` by **Codex `/root/journal_native_tests`**, original #118 native journal test author.
