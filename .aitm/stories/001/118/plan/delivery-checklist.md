# #118 manual delivery checklist

## Accepted split and Development checkpoint

[#117](https://github.com/kburson/aitm/issues/117), [#182](https://github.com/kburson/aitm/issues/182) and [#194](https://github.com/kburson/aitm/issues/194) are Closed and Done. The exact literal trunk `c4ea6b0d6c548830a3ad05d0bb76ec48625d1ca2` is the delivered tree from [PR #198](https://github.com/kburson/aitm/pull/198). The fresh locked baseline passed 877 product and CLI tests, 182 helpers, Ruff, whitespace and coverage of 9,649/10,549 product and 778/821 helper lines.

The [first independent review](2026-11-10-118-pickup-review-r1.md) held both initial artifacts. The [second review](2026-11-10-118-pickup-review-r2.md) passed the pickup and held the split for explicit incomparable-content ownership. The [third review](2026-11-10-118-pickup-review-r3.md) passed the exact [M08a pickup](2026-11-10-118-routing-journal-plan.md) and [M08b split](2026-11-10-118-m08b-revision-disposition-split.md). The [native split receipt](2026-11-10-118-m08b-split-receipt.json) binds #199 after #118 and before #119 at rank 225. The direct #118 prerequisite of #119 remains.

Codex owns the isolated branch `codex/aitm-118-routing-journal` and closure. The estimate is M, 3.75 agent-hours, with the reviewed 2.25-hour checkpoint. Project 24 Dev start is November 10 and rank 220. #199 is Backlog. M08a retains only private transactional claims and replay, and #199 owns causal ordering and dispositions.

## Test checkpoint

The [literal trunk refresh](2026-11-10-118-target-refresh.md) and its [independent review](2026-11-10-118-target-refresh-review.md) retain the exact approved pickup and split bytes. The detached refreshed baseline matched all 877 product and CLI tests, 182 helper tests, and both raw coverage counts.

[PR #200](https://github.com/kburson/aitm/pull/200) read back exact head , tree  and literal trunk . [Hosted run 42922357862](https://github.com/kburson/aitm/actions/runs/42922357862) is pending. Required jobs are file-checks, quality, python-base, python, collect-evidence and aitm-ci.

The locked frozen gate passed 920 product and CLI tests, 182 helper tests, Ruff, whitespace and coverage of 10,101/11,029 product and 778/821 helper lines. It adds 30 physical-store and 13 native-routing regressions over the exact baseline. An intermediate parallel run had four integration failures while the source fixtures were being corrected. The integrated source preflight held four causality checks, including a visible scope rename followed by a failed directory sync. The new native fault fixture reproduced the custody bug and now proves the journal rolls back before a fresh replay can settle the receipt. A second independent preflight passed all four repaired source paths.

The two original implementation lanes independently signed their source and fixture handoffs. Formal sign-offs follow verified delivery.
