# #370 Size, Estimate, and engagement backfill

Project 24 estimates are in agent-hours. The three delivered stories have retrospective scope estimates. #398 has a prospective estimate for the remaining qualification. No lifecycle status changes or inferred Refinement pass accompany this backfill.

| Story | Size | Estimate hours | Actual hours | Observed ms | Evidence through UTC | Source |
| --- | --- | ---: | ---: | ---: | --- | --- |
| [#383](https://github.com/kburson/aitm/issues/383) | M | 4.0 | 0.5355 | 1,927,886 | 2026-11-19T15:03:21.473Z | [Receipt](../../383/attachments/timing/370-native-engagement-backfill-20261119-383.json) |
| [#385](https://github.com/kburson/aitm/issues/385) | M | 4.0 | 0.0877 | 315,712 | 2026-11-19T16:05:38.411Z | [Receipt](../../385/attachments/timing/370-native-engagement-backfill-20261119-385.json) |
| [#393](https://github.com/kburson/aitm/issues/393) | S | 3.0 | 0.0551 | 198,498 | 2026-11-19T18:37:56.750Z | [Receipt](../../393/attachments/timing/370-native-engagement-backfill-20261119-393.json) |
| [#398](https://github.com/kburson/aitm/issues/398) | M | 3.5 | 0.0020 | 7,136 | 2026-11-19T21:12:30.572Z | [Receipt](../../398/attachments/timing/370-native-engagement-backfill-20261119-398.json) |

Total observed engagement across the four stories was **0.6803 agent-hours** (2,449,232 ms). All four Actual values have partial coverage. #398 covers attributable scoping and filing so far.

Actual is the union of attributable completed Codex reasoning, progress and command intervals per agent. Independent agents contribute separately. The #383 total includes the coordinator, snapshot implementer, cross-platform qualifier, and source reviewer. Shared handoff work was counted only where an action could be assigned to one story. Explicit waits, passive hosted run watches, owner wait, unbound gaps, and lifecycle dates were excluded. Local execution and bounded tool calls count when attributable. Raw sessions and unverified work are outside the receipts. Calculate hours from the exact milliseconds and round once to four decimal places. These partial observations cannot calibrate the estimates.

## Sizing basis

- #383. Three Git input adapters, advisory CLI, cross-platform qualification and review.
- #385. A new hosted comparison harness, seven PR cases and retained evidence.
- #393. One existing suite and a bounded four-case qualification using the earlier harness.
- #398. Prospective estimate for a production dependency audit and matched hosted runs.
