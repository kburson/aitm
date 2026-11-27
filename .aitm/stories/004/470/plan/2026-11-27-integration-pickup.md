# #470 Core records and reducers integration pickup

The [accepted ledger](../../../000/2/plan/2026-11-26-core-mini-epic-ledger.md#1-core-records-and-reducers) defines the slice and its sibling delivery requirements. The [reviewed kickoff](../../../000/2/plan/2026-11-27-core-kickoff/kickoff.md) applies them to manual delivery.

## Integration resource

The coordinator created `codex/core-470-integration` from trunk `a5ad6965c1c5b8817c0503dedbf55f576b5ddc67` and verified the remote ref at the same commit. Each story branches from that ref at its own pickup and records the observed base. [#83 activation](../../../000/83/attachments/activation-receipt.json) supplies the upstream prerequisite. The first draft is [#526](https://github.com/kburson/aitm/pull/526) for #3.

## Delivery and acceptance

Pick up #3, #4, #5, #6, #7 and #8 in that order. After each story clears local verification, exact hosted CI and Grok 4.7 source SAR, verify that its reviewed change landed on the integration ref and publish its individual closeout.

The slice owner #8 verifies the exact #3–#7 deliveries, binds its own reviewed change and demonstrates replay of typed records into deterministic state from a fixture using the installed package. The upstream trunk PR requires a real integration diff. Close #470 after the composed-tree test and applicable CI and review pass, the trunk landing is verified, and the required child dispositions are recorded.
