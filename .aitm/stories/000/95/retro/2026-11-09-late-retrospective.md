# #95 U10 · Qualification validator and on-host runbook · Late retrospective

Written November 9, 2026 (America/Chicago), after historical closure.

**Author** Codex follow-up agent in the #83 retrospective chat.

**Status** Evidence-based reconstruction. Original implementer `/root/implement_u10` was identified from the original dispatch and retained implementation records. The original agent was inaccessible from this chat. Original implementer sign-off remains missing.

## Design, plan and delivery

The leaf delivered a read-only installed qualifier and a runbook requiring authenticated native, runtime and restart evidence. Exact `00ccef89e1e0` passed 491 serial locked tests, offline installed-wheel verification and independent review. This head also became the PR #97 integration head. [Leaf design](../design/design.md) · [Implementation plan](../plan/implementation-plan.md) · [Protected source delivery](../../83/attachments/source-delivery.md).

## What worked and what needed repair

Review found that held data could masquerade as an observation-first case and that alias or ancestry changes could move raw approved scopes into disallowed canonical scopes. The two repairs required a distinct immutable pre-poll capture, explicit allowed identities, and canonical graph agreement across fixed, settled and live views. The trusted local operator still has to capture from the actual selected source. [Independent qualifier review](../plan/source-review.md) · [Live activation](../../96/attachments/activation-summary.md).

## Lesson and confidence

Make historical proof contemporaneous and bound to the first status and source prefix. Verify authority at each relevant view. Confidence is high for the exact qualifier under its reviewed evidence model. The installed host had to produce its own fresh evidence under #96. GitHub lists zero CI checks and zero submitted reviews on the applicable source PRs. The locked runs and independent source reviews were recorded separately in planning.

## Timing

The first handoff records 24m 47s to commit and local verification ending at 15:46:49 CST. Independent acceptance of the repaired head was recorded at 16:02:31 CST. First planning Review was 16:02:31 CST and the planning Done checkpoint was 17:17:20 CST. The observed spans are wall-clock evidence. Total agent engagement is Unknown. [Planning events](../events.jsonl) · [GitHub issue](https://github.com/kburson/aitm/issues/95).
