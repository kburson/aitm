# #89 U05 · Claude Code request usage adapter · Late retrospective

Written November 9, 2026 (America/Chicago), after historical closure.

**Author** Codex follow-up agent in the #83 retrospective chat.

**Status** Evidence-based reconstruction. Original implementer `/root/implement_u05` was identified from the original dispatch and retained implementation records. The original agent was inaccessible from this chat. Original implementer sign-off remains missing.

## Design, plan and delivery

The accepted plan called for request reconciliation, separately attributed child evidence and qualified quota evidence. Exact head `d081f954f9c1` passed 305 locked tests and reconciled 19 and 26 complete native requests in field-only probes. Exact accounting follow-up `296c6c314453` passed 351 tests. Both landed in PR #97. [Leaf design](../design/design.md) · [Implementation plan](../plan/implementation-plan.md) · [Protected source delivery](../../83/attachments/source-delivery.md).

## What worked and what needed repair

The first review found four defects involving account ownership, late excluded child evidence, tool linkage and malformed terminal cache fields. The later accounting check also found that a Standard/global first row could survive explicit contradictory processing evidence. The repair kept the original scope and measured tokens, revised the current tier to Unknown, and preserved earlier as-of pricing. [Adapter review](../plan/source-review.md) · [Accounting amendment](../../83/plan/usage-capture-accounting-integration-supplement.md) · [Accounting review](../plan/accounting-integration-source-review.md).

## Lesson and confidence

Include contradictory late evidence and excluded linked children in split-commit and restart fixtures. Confidence is high for the verified formats and the accounting revision. Unsupported nested work and absent account proof retain their coverage limits. GitHub lists zero CI checks and zero submitted reviews on the applicable source PRs. The locked runs and independent source reviews were recorded separately in planning.

## Timing

The handoffs record 17m 52s to the first candidate, 2m 13s for the initial review repair, and 3m 25s for the accounting repair. Planning first recorded Review at 12:42:31 CST and the final return to Review at 13:02:28 CST. It recorded Done at 17:17:20 CST. The observed spans are wall-clock evidence. Total agent engagement is Unknown. [Planning events](../events.jsonl) · [GitHub issue](https://github.com/kburson/aitm/issues/89).
