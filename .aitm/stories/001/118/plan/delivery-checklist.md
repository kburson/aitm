# #118 manual delivery checklist

## Accepted split and Development checkpoint

[#117](https://github.com/kburson/aitm/issues/117), [#182](https://github.com/kburson/aitm/issues/182) and [#194](https://github.com/kburson/aitm/issues/194) are Closed and Done. The exact literal trunk `c4ea6b0d6c548830a3ad05d0bb76ec48625d1ca2` is the delivered tree from [PR #198](https://github.com/kburson/aitm/pull/198). The fresh locked baseline passed 877 product and CLI tests, 182 helpers, Ruff, whitespace and coverage of 9,649/10,549 product and 778/821 helper lines.

The [first independent review](2026-11-10-118-pickup-review-r1.md) held both initial artifacts. The [second review](2026-11-10-118-pickup-review-r2.md) passed the pickup and held the split for explicit incomparable-content ownership. The [third review](2026-11-10-118-pickup-review-r3.md) passed the exact [M08a pickup](2026-11-10-118-routing-journal-plan.md) and [M08b split](2026-11-10-118-m08b-revision-disposition-split.md). The [native split receipt](2026-11-10-118-m08b-split-receipt.json) binds #199 after #118 and before #119 at rank 225. The direct #118 prerequisite of #119 remains.

Codex owns the isolated branch `codex/aitm-118-routing-journal` and closure. The estimate is M, 3.75 agent-hours, with the reviewed 2.25-hour checkpoint. Project 24 Dev start is November 10 and rank 220. #199 is Backlog. M08a retains only private transactional claims and replay, and #199 owns causal ordering and dispositions.

## Test checkpoint

The [literal trunk refresh](2026-11-10-118-target-refresh.md) and its [independent review](2026-11-10-118-target-refresh-review.md) retain the exact approved pickup and split bytes. The detached refreshed baseline matched all 877 product and CLI tests, 182 helper tests, and both raw coverage counts.

[PR #200](https://github.com/kburson/aitm/pull/200) read back exact head `db814e9e8d37e08860e822baed72f917132541a6`, tree `cb6ff8ce8506abc2a4bda4da3ddad93a35c33aad` and literal trunk `679c328204ab797aabdc9a9f93fbf1085d03bb65`. [Hosted run 42922357862](https://github.com/kburson/aitm/actions/runs/42922357862) is pending. Required jobs are file-checks, quality, python-base, python, collect-evidence and aitm-ci.

The locked frozen gate passed 920 product and CLI tests, 182 helper tests, Ruff, whitespace and coverage of 10,101/11,029 product and 778/821 helper lines. It adds 30 physical-store and 13 native-routing regressions over the exact baseline. An intermediate parallel run had four integration failures while the source fixtures were being corrected. The integrated source preflight held four causality checks, including a visible scope rename followed by a failed directory sync. The new native fault fixture reproduced the custody bug and now proves the journal rolls back before a fresh replay can settle the receipt. A second independent preflight passed all four repaired source paths.

The two original implementation lanes independently signed their source and fixture handoffs. Formal sign-offs follow verified delivery.

## Review checkpoint

[All six required jobs](https://github.com/kburson/aitm/actions/runs/42922357862/attempts/1) passed on exact head `db814e9e8d37e08860e822baed72f917132541a6`. The [authenticated receipt](hosted-ci-receipt.json) verified tested merge `cd0fd26ce52f8909f663d1f9003695c324c6cb72`, exact tree `cb6ff8ce8506abc2a4bda4da3ddad93a35c33aad`, artifact `13812986424`, and signed subject SHA-256 `aeae1ddbbc543f9a25c6efd832c26778cc6a794e74b8a507c9f24128df310258`. The first verifier held because a GitHub commit read failed. The same endpoint read then succeeded, and the same trusted verifier passed the same run and tree without policy or source changes. [Initial verifier result](hosted-verifier-initial-read-hold.json)

The trusted raw replay retained 876 baseline package test identities and passed all 920 candidate tests. The locked local baseline includes the fixed CLI evidence test for 877. Raw coverage passed at 10,101/11,029 product and 778/821 helper lines. Independent exact source review is pending.

The [independent exact source verdict](post-ci-source-review.md) passed `db814e9e8d37e08860e822baed72f917132541a6` and tree `cb6ff8ce8506abc2a4bda4da3ddad93a35c33aad`. The hosted run completed successfully before review. The raw replay retains 876 package test identities. The locked local baseline adds the fixed CLI evidence control test for 877, and 43 journal regressions bring the candidate to 920.

The third source seam is the private `ScopeState.view(..., _confirm_publication=True)` option. It defaults to the existing behavior and makes the journal confirm the parent sync and current registry on both sides of staging. The native RED and GREEN prove that a visible scope replacement after a failed sync cannot commit journal progress. Scope disagreement on copied usage stays held, and both owner and rival frontiers remain replayable after an ownership dispute. #199 must independently gate the release of both. The native PR review is absent. The exact source verdict is off-platform.

### Verified delivery

[PR #200](https://github.com/kburson/aitm/pull/200) merged into trunk at `2026-11-10T23:30:24Z` as `1452999b2f0f5a90161e39862458029c0084772c`. Fetched trunk contains that merge with ordered parents `679c328204ab797aabdc9a9f93fbf1085d03bb65` and `db814e9e8d37e08860e822baed72f917132541a6`, exact tree `cb6ff8ce8506abc2a4bda4da3ddad93a35c33aad`, candidate ancestry and zero source diff. Branch rules permitted an ordinary merge with zero required native approvals. All six exact checks and the off-platform verdict passed.

The original [native fixture author](../retro/2026-11-10-118-journal-native-implementer-retrospective.md), [storage author](../retro/2026-11-10-118-journal-store-implementer-retrospective.md), [routing implementer and coordinator](../retro/2026-11-10-118-routing-journal-implementer-retrospective.md) each signed their retrospective. All three signatures were read back at `2026-11-10T23:32:53+00:00`. Original implementer sign-off was the last required delivery gate.
