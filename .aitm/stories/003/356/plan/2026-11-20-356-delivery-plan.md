# #356 Delivery plan

**Goal**

Coordinate the research, local, hosted and scheduled full-sweep work.

**Scope**

[Refined story](../story.md) and [epic delivery plan](../../356/plan/2026-11-20-356-delivery-plan.md).

## Sequence and release evidence

Move the parent epic into Dev before moving any child into Dev.

| Child | Prerequisite | Evidence handed forward |
| --- | --- | --- |
| [#357](../../357/story.md) | Owner pickup | Exact category register, timing provenance, exception and platform inventory |
| [#358](../../358/story.md) | Accepted #357 | Serial and concurrent comparison, runner and isolation matrix |
| [#359](../../359/story.md) | Accepted #357 and #358 | Local command, exact coverage of test IDs, outcome parity and failure controls |
| [#411](../../../004/411/story.md) | Before #360 acceptance | Requested Ubuntu runner label and signed receipts for both observed builds |
| [#360](../../360/story.md) | Delivered #359 | Hosted manual run, parallel-job receipts and aggregate checks |
| [#361](../../361/story.md) | Delivered #360 | Verified default-branch scheduled run and operating instructions |

- [x] Refine child scope and write each plan. Mark receipt-dependent decisions at their owning child.
- [x] Start the #357 classification spike on the pinned trunk collection.
- [x] Independently accept both spike findings before authorizing source implementation.
- [x] Verify child delivery in dependency order, including the actual schedule event and receipt reconciliation.
- [x] Record aggregate acceptance, epic sign-off and closure after the last required child.

## Evidence informing the design

- [#285 audit](../../../002/285/plan/2026-11-14-285-behavior-audit.md) supplies 42 historical families and names fixture-cost questions. [#286 standard](../../../002/286/plan/2026-11-14-286-core-behavior-test-standard.md) distinguishes API, temporary Git/filesystem, subprocess and provider boundaries.
- [#148](https://github.com/kburson/aitm/issues/148) delivered advisory grouping and exact-union checks in `tools/ci/tia/shards.py`. Reuse them only if they fit the accepted category and runner contract.
- [#290 benchmark](../../../002/290/plan/2026-11-15-290-benchmark-results.md) saw 2.64× in a private local worker experiment. Its 3,020 assignments included repeats, and the native scheduled attempt registered 7h 43m late. Measure both runtime and queue in this epic.
- [#292](../../../002/292/plan/2026-11-15-292-hosted-shadow-results.md) and [#293](../../../002/293/plan/2026-11-15-293-hosted-validation-results.md) show exact-input identity, child evidence and cache isolation needs. [#294](../../../002/294/plan/readiness-review.md) records a no-go for gate cutover. [#337](../../337/plan/2026-11-15-337-full-pr-and-rollback-results.md) records queue, retry, evidence freshness and rollback observations. This epic delivers a full sweep alongside the governed path.

## Epic acceptance

All six children were verified closed before the epic closeout. The [epic sign-off](../retro/2026-11-21-356-sign-off.md) ties the accepted serial, manual and scheduled evidence together.
