# #96 U11 · Project Mac activation and dogfood proof · Late retrospective

Written November 9, 2026 (America/Chicago), after historical closure.

**Author** Codex follow-up agent in the #83 retrospective chat.

**Status** Evidence-based reconstruction. Original implementer `/root/implement_u11` was identified from the original dispatch and retained implementation records. The original agent was inaccessible from this chat. Original implementer sign-off remains missing.

## Design, plan and delivery

The amended plan assigned #96 the live gate. The exact PR #99 release qualified at 17:16:19 CST. The operator and an independent verifier both obtained `qualified`. The receipts record both arrival orders for both providers, isolated launchd recovery, production workflow, real stopped-window catch-up and a byte-identical 42-row replay. The final release used the same durable project identity and ledger. The source PRs belong to integration and the two repair leaves. #96's deliverable was the independently verified installed activation and sanitized receipt. [Leaf design](../design/design.md) · [Implementation plan](../plan/implementation-plan.md) · [Protected source delivery](../../83/attachments/source-delivery.md).

## What worked and what needed repair

Live qualification stopped twice for separately reviewed replans. PR #97 rejected the actual Desktop marker carrier and PR #98 still held Claude startup bookkeeping ahead of the target request. Neither isolated failure touched production. A later runtime check refused unexpected Finder metadata, which the operator preserved outside the runtime before rechecking. The first Codex catch-up lacked durable turn context. A new turn in the same stream during a confirmed stop supplied valid evidence without changing scope or relationships. [Activation plan](../plan/implementation-plan.md) · [Desktop diagnostic](../attachments/desktop-marker-diagnostic.md) · [Claude diagnostic](../attachments/claude-startup-diagnostic.md) · [Activation summary](../attachments/activation-summary.md) · [Receipt](../../83/attachments/activation-receipt.json).

## Lesson and confidence

Run provider-native proof early, restart from the exact repaired release and refresh the heartbeats and watermarks near final verification. Split activation ownership from closure of source leaves. Confidence is high for the observed release and proof window. A request crossing a restart can still lack attributable turn context. GitHub lists zero CI checks and zero submitted reviews on the source PRs. Local locked runs, independent off-platform review and the installed activation receipt are separate evidence.

## Timing

The activation implementer start at 16:03:15 CST to qualifying at 17:16:19 CST spans about 73 minutes, including both pauses. The receipt's 1,315.425-second conservative bound measures controlled workload against its 1,800-second budget. Planning recorded Test, Review and Done together at 17:17:20 CST. The observed spans are wall-clock evidence. Total agent engagement is Unknown. [Planning events](../events.jsonl) · [GitHub issue](https://github.com/kburson/aitm/issues/96).
