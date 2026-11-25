# #442 Trail rollup implementation plan

The [portable effort plan](../../426/plan/2026-11-24-agent-effort-cost-implementation-plan.md) defines the scope. This story exercises the [published #433 trail fixture](../../433/attachments/epic-trail-receipt.json) through the portable receipt store.

1. Persist caller-verified start and end evidence against one enrolled attempt and exact native turn. Record detach and attach as a replayable link between sessions under the same assignment. Exercise marker conflicts, mixed turns, delayed delivery, and database reopen.
2. Roll up effective receipts by story, epic, provider, and role. Count bounded usage once. Retain inclusive parent evidence and verified independent engagement while excluding its overlapping tokens and price from additive subtotals. Expose unknown values, unassigned observations, and unsettled attempts.
3. Require clock-domain evidence per observation before unioning intervals. Sum the interval union within each session for agent engagement and union comparable sessions for working wall time. Compute elapsed workflow from a separately verified window. Leave contradictory scope crossings uncredited.
4. Reconcile the published epic and each child, including totals before and after late attribution. Require independent source review, authenticated CI, trusted verification, and merge-tree parity for delivery.
