# #411 Delivery plan

1. Deliver a backward-compatible reader before enabling the new signed receipt. The old trunk verifier must be able to authorize the reader PR using existing CI evidence. The new reader validates versioned Ubuntu labels against authenticated job labels and preserves the legacy Darwin and exact-build contracts.
2. Enable the new receipt in canonical CI. Source each label from the same workflow matrix value used by its job's `runs-on`. Capture each actual build and pinned runtime, keep the trusted source digests exact, and retain both builds in the signed receipt. Update consumers of the raw and signed receipts.
3. Prove same-label mixed and equal builds, another versioned Ubuntu label, and refusal of missing, inconsistent or invalid evidence. Get independent Grok review before each merge, run canonical CI and the trusted verifier, then verify the new receipt on GitHub before closing #411 and releasing #360.

## Reader candidate

[PR #412](https://github.com/kburson/aitm/pull/412) contains the new reader. All 160 gate and verifier tests passed. [Grok passed the exact head](https://github.com/kburson/aitm/pull/412#pullrequestreview-5999767888). The unchanged canonical producer and current trunk verifier must accept this PR before introduction of v3.

## Producer rehearsal

The separate producer candidate passed 227 related tests and workflow lint. In a local replay of #410 attempt 6, the new gate accepted the downloaded test evidence after adding each requested label obtained from the corresponding authenticated GitHub job record. The two observed images were `ubuntu24:20261116.376.1` and `ubuntu24:20261116.133.1`, both for `ubuntu-24.04` and Python 3.13.9. This replay exercised the gate. A live signed receipt and current trusted verifier are required for delivery.
