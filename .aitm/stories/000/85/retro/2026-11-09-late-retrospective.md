# #85 U02 · Scope inbox and provider-session binding · Late retrospective

Written November 9, 2026 (America/Chicago), after historical closure.

**Author** Codex follow-up agent in the #83 retrospective chat.

**Status** Evidence-based reconstruction. Original implementer `/root/implement_u02` was identified from the original dispatch and retained implementation records. The original agent was inaccessible from this chat. Original implementer sign-off remains missing.

## Design, plan and delivery

The amended plan assigned atomic inbox publication, typed dispatch and durable pending/final dispositions. The implementer verified real CLI publication under a writer lease, concurrent publication and acknowledgment, owner reassignment and replay against prior as-of history. Exact head `67e888d720e6` passed 101 locked tests and landed in PR #97. The retained evidence also includes RED/GREEN for 32 focused scope cases. [Leaf design](../design/design.md) · [Implementation plan](../plan/implementation-plan.md) · [Protected source delivery](../../83/attachments/source-delivery.md).

## What worked and what needed repair

Review exposed unqualified development defaults, cross-stream generation ordering, lost pending locations and scope-only dispatch. A second pass found late-arriving request or message IDs could disturb lineage. The final repair preserves already admitted pre-rebind observations by immutable key and leaves fresh old-stream or ambiguous work Unknown. [Inbox ownership amendment](../../83/plan/usage-capture-replan.md) · [Independent review](../plan/source-review.md).

## Lesson and confidence

Test ownership switches across streams, including sparse provider IDs and delayed replay. Confidence is high for the typed inbox and fixture-proven scope order. Native-provider ordering and real process crashes were later verification gates. GitHub lists zero CI checks and zero submitted reviews on the applicable source PRs. The locked runs and independent source reviews were recorded separately in planning.

## Timing

The original observed local interval was 18m 37s. Initial work and two repair intervals total 24m 24s in the source review. First planning Review was 10:12:30 CST and the planning Done checkpoint was 17:17:20 CST. The observed spans are wall-clock evidence. Total agent engagement is Unknown. [Planning events](../events.jsonl) · [GitHub issue](https://github.com/kburson/aitm/issues/85).
