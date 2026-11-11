# #2 governed PR and working-branch lifecycle SAR author disposition

The independent review examined both source artifacts at
`54f9f08b44096e44a9465dfeae80b60d455f0227` and requested five changes.
The revised artifact commit is `ff09e06bdc96619ac13eb11e15aafb4495056432`.

| Artifact | Input SHA-256 | Revised SHA-256 |
| --- | --- | --- |
| [Specification](../../../design/2026-11-11-2-governed-pr-and-branch-lifecycle-design.md) | `5bf6605f0366d878b5f3c88e3019bcef6c8ba97da48ca555148be62712481027` | `11ea2e95327da0834648447721eec72430e3606ea9e54252cd7a3b45e9b69c4c` |
| [Plan](../../2026-11-11-2-governed-pr-and-branch-lifecycle.md) | `57e0a0972aeeaa4e47d02f41df09267246c4a0b17543b879600a292e03dd870b` | `55642beeeed874ddf990f87d557186581b021c26f3253b13069e46abf4605db6` |

| Finding | Author disposition |
| --- | --- |
| SAR-PR-01 | Add an incarnation-scoped retirement fence in the same authority order as dependent admission and retain the ref until winning dependents and ambiguous effects are resolved. Include uncontrolled provider routes in the hold predicate. |
| SAR-PR-02 | Separate stable resource incarnation from current C16 session authority. Publish stage-specific claims, require positive effect attribution and safe replay proof, and verify durable retained source before deleting the old working ref on scrap. |
| SAR-PR-03 | Designate an ordinary integration delivery story for an epic branch. Provision its draft early in Backlog, then require its own attempt, review, CI and C41 authority. Preserve C62 aggregation. |
| SAR-PR-04 | Order readiness at the exact provider transition with PR, head, target and applicable flag binding. Defer unqualified routes, reconcile ambiguous effects, and retain merge denial after an earlier valid readiness transition. |
| SAR-PR-05 | Add proof entry points, prerequisites and receipts for local and hosted boundaries. Separate non-default qualification from the #158-gated default delivery and record an unavailable result as denial evidence. |

All five are returned for independent SAR closure. The changes are
planning obligations. This disposition records no provider qualification.
