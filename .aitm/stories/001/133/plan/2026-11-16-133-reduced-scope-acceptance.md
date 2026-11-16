# #133 reduced-scope acceptance

Accepted November 16, 2026 by Codex as the closure operator, acting on the owner's direction to close the reduced plan after decomposition. The governing scope is the [PR feedback replacement](2026-11-16-133-pr-feedback-replacement.md) and [decomposition](2026-11-16-133-decomposition.md). The delivered target is ordinary pull-request validation on `trunk`.

| Acceptance | Verified result |
| --- | --- |
| Use a trusted path map for the live PR validation workflow | #340 shipped a base-owned map. #344 narrowed audited fixture and direct source changes to 33 and 30 tests with exact selection and execution records. The explicit documentation rule selected checks only. [#340 delivery](../../../003/340/retro/2026-11-16-delivery.md) · [#344 hosted cases](../../../003/344/plan/tia-evidence.md) |
| Run the full suite for uncertain impact and control changes | The shared Ledger change went full on its own. The control, unknown executable, fixture move and runtime-data case also went full. Both exact trees passed 1,517 tests. [Ledger run](https://github.com/kburson/aitm/actions/runs/43878780064) · [Control and uncertainty run](https://github.com/kburson/aitm/actions/runs/43878789073) |
| Run the short check on each push, reuse successful full evidence for the same selection, and cancel a superseded run | #341 shipped the policy. #344 verified attested same-selection reuse, a fresh full run after a changed selection, and the cancellation of a superseded attempt that produced no successful stamp. [#341 delivery](../../../003/341/retro/2026-11-16-delivery.md) · [Reuse run](https://github.com/kburson/aitm/actions/runs/43880030738) · [Changed selection](https://github.com/kburson/aitm/actions/runs/43882437964/attempts/2) |
| Catch a regression on the short mapped path after a prior full pass | The mapped fixture run restored the earlier full stamp and caught the seeded failure. The independent full run on the same tree caught the same assertion. The governed verifier refused the red candidate. [Red run](https://github.com/kburson/aitm/actions/runs/43881192348) · [Receipt](../../../003/344/plan/tia-proof/receipt.json) |
| Verify independent review, delivery and trunk full validation | #340 and #341 landed in [PR #342](https://github.com/kburson/aitm/pull/342), merge `625b5407978675ac3b906990c8bb0713dcae18fd`. #344 landed in [PR #346](https://github.com/kburson/aitm/pull/346), merge `8799c5a445dd4b51d499132e9a314b64796ae918`, on reviewed and tested tree `456a155fbe7d10cb7daafd2bf46f134be78366a8`. Independent source and live-proof reviews passed. The [delivered trunk run](https://github.com/kburson/aitm/actions/runs/43878715343) passed 1,517 tests. |

Closeout rechecked GitHub attempt outcomes and heads for all eight hosted cases and the hashes of all four retained test inventories. The live evidence establishes the governed PR workflow and verifier. The active trunk rules require pull requests and protect against deletion and non-fast-forward updates. Native required status checks are absent. [Trunk rules](https://github.com/kburson/aitm/rules/26821811).

## Disposition of the original scope

- [#351](https://github.com/kburson/aitm/issues/351) owns trusted local selection for uncommitted changes and pre-commit execution.
- [#356](https://github.com/kburson/aitm/issues/356) owns execution-category shards through a scheduled full sweep.
- [#362](https://github.com/kburson/aitm/issues/362) owns an advisory scheduled-failure flag. It carries no merge-hold or repair-owner authority.
- A generalized dependency-graph proof, production Stop the Line enforcement and rollback, and the former scale and shadow cutover qualification are outside the reduced acceptance. The earlier measurements, rehearsals and no-go review stay historical evidence. [Prior cutover review](../../../002/294/plan/readiness-review.md).

GitHub showed 62 closed direct children, 28 Completed and 34 Not Planned. #133 had no blockers or dependents. The three follow-on epics were open, had no parent, and had no dependency edges blocking them. Epic closure is scoped to the delivered PR validation.

[Signed epic retrospective](../retro/2026-11-16-133-delivery.md).
