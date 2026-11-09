# #93 U12 · Integrated restart, enrollment and privacy proof · Late retrospective

Written November 9, 2026 (America/Chicago), after historical closure.

**Author** Codex follow-up agent in the #83 retrospective chat.

**Status** Evidence-based reconstruction. Original implementer `/root/implement_u12` was identified from the original dispatch and retained implementation records. The original agent was inaccessible from this chat. Original implementer sign-off remains missing.

## Design, plan and delivery

The plan required real subprocess interruption and privacy proof over the production entry points. Independent review of `05318125f9d0` verified three SIGKILL boundaries, both marker orders, first-child attribution and restart replay. Canary scans included a real nonempty WAL and a fixed export. The exact installed-wheel proof and 410 locked tests passed before PR #97. [Leaf design](../design/design.md) · [Implementation plan](../plan/implementation-plan.md) · [Protected source delivery](../../83/attachments/source-delivery.md).

## What worked and what needed repair

The process harness exposed an abandoned temporary inbox stage that needed to be counted under the real publication mutex. The narrow production repair avoided reading or retiring abandoned stages. The U08 launch-health follow-up reran the unchanged U12 test at the new exact head. [Independent process review](../plan/source-review.md) · [Exact rerun after U08 repair](../../92/plan/launch-health-source-review.md).

## Lesson and confidence

Keep subprocess crash and privacy tests on the same installed wheel and real filesystem paths as the supported entry points. Confidence is high for the three verified crash boundaries and inspected durable surfaces. Live provider recovery remained #96's gate. GitHub lists zero CI checks and zero submitted reviews on the applicable source PRs. The locked runs and independent source reviews were recorded separately in planning.

## Timing

The handoff reports a 9m 18s local implementation and verification interval, from 14:02:40 to 14:11:58 CST. First planning Review was 14:13:56 CST and the planning Done checkpoint was 17:17:20 CST. The observed spans are wall-clock evidence. Total agent engagement is Unknown. [Planning events](../events.jsonl) · [GitHub issue](https://github.com/kburson/aitm/issues/93).
