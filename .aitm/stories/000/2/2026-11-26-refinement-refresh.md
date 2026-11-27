# Core #2 refinement refresh

Recorded November 26, 2026. **Size XL. Estimate 386.5 implementation agent-hours. Project Rank 10.**

## Scope and estimate

#2 coordinates the accepted Core scope. The estimate is a rollup of the **22 Core delivery mini-epics and 110 bounded children** in the accepted ledger, including implementation, verification, source review, and integration. Count the underlying work once. Each mini-epic delivers its own verified trunk result and each child has an estimate of at most four hours. The multi-subsystem Core scope warrants XL at the coordination level.

| Estimate basis | Agent-hours |
| --- | ---: |
| Initial top-down Refine estimate, retained as history | 180 |
| Prior accepted baseline, 89 leaves | 297.25 |
| Accepted configured-workflow delivery plan, 110 leaves | 386.5 |
| Difference from prior accepted baseline | +89.25 |

The updated basis includes the configured workflow and managed handoff changes, legacy-rule qualification, and independent trunk integration. TIA (#492), Agent Cost Capture (#493, including #230), and post-release timing work (#228/#229) keep their separate estimates. Observed planning time and Cost are recorded separately in the [planning effort receipt](attachments/2026-11-26-core-planning-effort.md).

## Admission and first delivery slice

- The configured-workflow amendment and implementation plan have accepted XPR records. The accepted implementation estimate is reused for this refinement because the full reconciled child ledger is available.
- Native parent #1 and open downstream dependency #247 were verified. The only native blocker, #456, is closed, so the verified issue graph shows no open native blocker for planning.
- Rank 10 puts #2 in the first planning slot in this delivery sequence. The first implementation slice is [#470](https://github.com/kburson/aitm/issues/470), also ranked 10, beginning with [#3](https://github.com/kburson/aitm/issues/3) at child rank 10. Applicable slice and child pickup gates govern actual start.
- This record places #2 in **Refine** on Project #24. The next decision is admission to Ready for Planning and Plan under the applicable planning policy. The Refine entry and estimate are recorded through the current manual-bootstrap process.

[Accepted plan](plan/2026-11-26-configured-workflow-implementation-plan.md) · [Delivery ledger](plan/2026-11-26-core-mini-epic-ledger.md) · [Verified implementation ranks](plan/2026-11-26-core-implementation-ranks.md) · [Historical refinement](refinement.md) · [Verified Project #24 readback](plan/2026-11-26-refine-board.json).
