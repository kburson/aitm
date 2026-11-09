# #91 U07 · As-of export and C44 compatibility proof · Late retrospective

Written November 9, 2026 (America/Chicago), after historical closure.

**Author** Codex follow-up agent in the #83 retrospective chat.

**Status** Evidence-based reconstruction. Original implementer `/root/implement_u07` was identified from the original dispatch and retained implementation records. The original agent was inaccessible from this chat. Original implementer sign-off remains missing.

## Design, plan and delivery

The plan delivered deterministic exports at a fixed ledger sequence and a receiver fixture for C44-compatible data. The repinned pickup used the repaired U13 accounting base. Exact head `304a52aab095` passed 386 locked tests, 26 export cases and installed-wheel replay before landing in PR #97. [Leaf design](../design/design.md) · [Implementation plan](../plan/implementation-plan.md) · [Protected source delivery](../../83/attachments/source-delivery.md).

## What worked and what needed repair

Independent review required three focused repairs. Disposable Darwin and SQLite cases covered substituted staging wrappers, identical and conflicting destination writers, retry of directory sync, and conflicting observation, scope and price provenance. [Independent review](../plan/source-review.md) · [Accounting prerequisites](../../83/plan/usage-capture-accounting-integration-supplement.md).

## Lesson and confidence

Verify concurrent export finalization and retry behavior at the real filesystem boundary. Confidence is high for byte stability and the tested receiver contract. The receiver fixture assumes a producer-supplied cutoff, and native C44 adoption remains separate. GitHub lists zero CI checks and zero submitted reviews on the applicable source PRs. The locked runs and independent source reviews were recorded separately in planning.

## Timing

The implementer records 9m 19s to the initial candidate and 4m 26s for the repair interval. First planning Review was 13:29:20 CST and the planning Done checkpoint was 17:17:20 CST. The observed spans are wall-clock evidence. Total agent engagement is Unknown. [Planning events](../events.jsonl) · [GitHub issue](https://github.com/kburson/aitm/issues/91).
