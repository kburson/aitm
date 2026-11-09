# #92 U08 · Collector service, live commands and status · Late retrospective

Written November 9, 2026 (America/Chicago), after historical closure.

**Author** Codex follow-up agent in the #83 retrospective chat.

**Status** Evidence-based reconstruction. Original implementer `/root/implement_u08` was identified from the original dispatch and retained implementation records. The original agent was inaccessible from this chat. Original implementer sign-off remains missing.

## Design, plan and delivery

The collector plan joined registration, the inbox and both adapters with atomic scope, observation and checkpoint progress. Exact head `a6a69bce45e9` passed 409 locked tests and installed-wheel smoke. The later producer witness `f720ae48c896` passed 418 locked tests and the existing U12 process test. Both landed in PR #97. [Leaf design](../design/design.md) · [Implementation plan](../plan/implementation-plan.md) · [Protected source delivery](../../83/attachments/source-delivery.md).

## What worked and what needed repair

Two repairs addressed the commit ceiling and false or proof-lost receipts. A preexisting Claude fixture failed on one locked run and passed both an isolated run and a full rerun. U09 later reproduced false launch readiness from a different process. The replan assigned U08 the status producer mode and PID. Independent probes verified that a real continuous service and one-shot collector reported distinct origins, while legacy producer identity stayed Unknown. [Collector review](../plan/source-review.md) · [Launch-health replan](../../83/plan/usage-capture-launch-health-replan.md) · [Producer review](../plan/launch-health-source-review.md).

## Lesson and confidence

Treat status as an observation by a specific producer and prove it across separate processes. Confidence is high for verified replay and producer attribution. Installation readiness also depends on the live process matching the witness, which U09 owns. GitHub lists zero CI checks and zero submitted reviews on the applicable source PRs. The locked runs and independent source reviews were recorded separately in planning.

## Timing

The first local implementation and verification handoff covers 17m 41s. The launch-health follow-up covers 3m 30s. These windows omit intervening independent review and other repair work. Planning first recorded Review at 14:01:57 CST and the final return to Review at 14:58:06 CST. It recorded Done at 17:17:20 CST. The observed spans are wall-clock evidence. Total agent engagement is Unknown. [Planning events](../events.jsonl) · [GitHub issue](https://github.com/kburson/aitm/issues/92).
