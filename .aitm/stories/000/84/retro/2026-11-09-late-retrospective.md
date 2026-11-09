# #84 U01 · Package and private durable ledger · Late retrospective

Written November 9, 2026 (America/Chicago), after historical closure.

**Author** Codex follow-up agent in the #83 retrospective chat.

**Status** Evidence-based reconstruction. Original implementer `/root/implement_u01` was identified from the original dispatch and retained implementation records. The original agent was inaccessible from this chat. Original implementer sign-off remains missing.

## Design, plan and delivery

The leaf design and amended plan delivered a standalone package, a process-held writer lease, explicit initialization, atomic observation and checkpoint commits, and reproducible as-of reads. The original handoff recorded a fresh wheel CLI smoke test and exercised real rollback and writer death. The final reviewed head `0df428e4fa5d` passed 69 locked tests and landed in PR #97. [Leaf design](../design/design.md) · [Implementation plan](../plan/implementation-plan.md) · [Protected source delivery](../../83/attachments/source-delivery.md).

## What worked and what needed repair

Initial review reproduced ACL exposure, lock replacement, stale writes and weak validation of schema, private fields and references. The ownership amendment assigned shared contracts before repair. The first repaired candidate still let APFS firmlink aliases acquire a second writer. The final independent overlap matrix rejected equal and nested physical roots in both directions and preserved legitimate alias use. [Initial replan](../../83/plan/usage-capture-replan.md) · [Independent review](../plan/source-review.md).

## Lesson and confidence

Test physical identity and negative privacy cases at pickup. Include a real competing process and both path-ancestry directions. Confidence is high for the exact reviewed ledger and the tested Darwin paths, with provider behavior covered by later leaves. GitHub lists zero CI checks and zero submitted reviews on the applicable source PRs. The locked runs and independent source reviews were recorded separately in planning.

## Timing

The original local interval was 12m 15s. The source review reports 24m 54s of observed implementer intervals across the initial build and both repairs. First planning Review was 09:35:15 CST and the planning Done checkpoint was 17:17:20 CST. The observed spans are wall-clock evidence. Total agent engagement is Unknown. [Planning events](../events.jsonl) · [GitHub issue](https://github.com/kburson/aitm/issues/84).
