# Actual backfill evidence · November 10, 2026

Evidence cutoff **13:35:05 CST**. Ten numeric Actual fields and their companion Actual coverage fields were read back on [AITM-PY Backlog](https://github.com/users/kburson/projects/24). This receipt records that historical snapshot. All values are partial. The [machine-readable receipt](2026-11-10-actual-backfill.json) retains the unrounded milliseconds, pseudonymous interval evidence, and board readback fields used to verify the rollups.

| Story | Estimate on board (h) | Recovered time | Actual (agent-hours) |
| --- | ---: | ---: | ---: |
| [#100 Usage monitor](https://github.com/kburson/aitm/issues/100) | — | 8:27:31 | 8.4586 |
| [#111 Host path security](https://github.com/kburson/aitm/issues/111) | 2.5 | 0:36:27 | 0.6074 |
| [#112 Atomic filesystem operations](https://github.com/kburson/aitm/issues/112) | 2.5 | 0:23:59 | 0.3996 |
| [#113 Versioned project persistence](https://github.com/kburson/aitm/issues/113) | 3.75 | 0:29:24 | 0.4901 |
| [#114 Provider adapters](https://github.com/kburson/aitm/issues/114) | 3.75 | 1:09:09 | 1.1524 |
| [#115 Grok evidence adapter](https://github.com/kburson/aitm/issues/115) | 3.75 | 1:23:00 | 1.3834 |
| [#116 Registry and capture epochs](https://github.com/kburson/aitm/issues/116) | 4 | 3:07:34 | 3.1262 |
| [#133 Test impact analysis](https://github.com/kburson/aitm/issues/133) | 146.5 | 2:11:54 | 2.1983 |
| [#138 Pin the serial baseline](https://github.com/kburson/aitm/issues/138) | 2.5 | 0:17:50 | 0.2972 |
| [#140 Resolve exact Git changes](https://github.com/kburson/aitm/issues/140) | 3 | 0:11:23 | 0.1897 |

## Reconstruction and coverage

- #100 includes **1:17:58** of direct epic work and #111–#116. #133 includes **1:42:41** of direct epic work and #138/#140. Compute the rollups from unrounded intervals and round the final board value. #101 and #102 are separate research prerequisites. #134, #135 and #137 have no separately attributed turns in this reconstruction.
- Completed and interrupted Codex turns use retained native duration. Specific progress and action timestamps were used to split mixed-scope turns. #116's open turn was bounded by the observed Test checkpoint. Dedicated Claude reviews use retained result duration or an evidenced SDK prompt and terminal response. Result receipt completion anchors use the observed receipt write. These are historical attribution decisions and can omit or approximate intervals.
- Count qualified in-turn tool time once per actor and sum independent agents. Gaps between turns, owner waits and ambiguous intervals contribute no observed effort. Missing evidence stays partial or Unknown. The historical readback had no Cost values for these rows.
- #111's separately reviewed [pickup](../../111/plan/jit.md) estimated **2.5 implementation agent-hours**. The board value spans pickup through closure across the coordinator, implementer and reviewer. The observed Develop-to-review-pass subtotal is **0:28:31** across participants, the dedicated implementer turn is **0:12:24**, and Develop-to-Done wall time is **0:12:54**. Retain all these observations for analysis and exclude the partial record from calibration.

The earlier provisional sums that included owner waits were cleared and replaced by the Actual values above. The [coordination brief](timing-and-usage-coordination.md) records the metric and calibration boundaries.
