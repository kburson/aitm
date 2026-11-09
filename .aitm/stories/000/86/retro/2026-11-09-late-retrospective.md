# #86 U13 · Draft aliases, ancestry and direct/inclusive rollups · Late retrospective

Written November 9, 2026 (America/Chicago), after historical closure.

**Author** Codex follow-up agent in the #83 retrospective chat.

**Status** Evidence-based reconstruction. Original implementer `/root/implement_u13` was identified from the original dispatch and retained implementation records. The original agent was inaccessible from this chat. Original implementer sign-off remains missing.

## Design, plan and delivery

The design called for canonical draft graduation, distinct-descendant rollups and immutable history. The amended plan put relationship admission and publication order behind the shared inbox and ledger guards. The installed CLI and restart tests exercised ordered partial drain and preserved earlier as-of views. Exact head `981a1e41593c` passed 141 locked tests. The later exact accounting head `424d8a3140f1` passed 360. Both landed in PR #97. [Leaf design](../design/design.md) · [Implementation plan](../plan/implementation-plan.md) · [Protected source delivery](../../83/attachments/source-delivery.md).

## What worked and what needed repair

Initial review demonstrated that a generic write could bypass relationship admission and UUID order could reverse publish order. Later integration exposed ambient Decimal precision rounding valid prices. The exact follow-up verified direct, inclusive and unassigned totals with wider rates, low precision, reversed order and caller traps. [Relationship replan](../../83/plan/usage-capture-relationship-replan.md) · [Independent review](../plan/source-review.md) · [Accounting review](../plan/accounting-integration-source-review.md).

## Lesson and confidence

Assign ownership at shared admission boundaries and test ordering independently of generated identifiers. Test the real pricing representation across the rollup boundary. Confidence is high for the tested typed graph and exact totals, with coverage bounded by upstream evidence. GitHub lists zero CI checks and zero submitted reviews on the applicable source PRs. The locked runs and independent source reviews were recorded separately in planning.

## Timing

The source record reports 18m 01s of implementation-to-commit intervals for the first candidate and relationship repair. The accounting handoff adds 2m 37s to its commit. Planning first recorded Review at 10:48:48 CST and the final return to Review at 13:11:37 CST. It recorded Done at 17:17:20 CST. The observed spans are wall-clock evidence. Total agent engagement is Unknown. [Planning events](../events.jsonl) · [GitHub issue](https://github.com/kburson/aitm/issues/86).
