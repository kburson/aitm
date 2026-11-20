# #411 Delivery plan

1. Deliver a backward-compatible reader before enabling the new signed receipt. The old trunk verifier must be able to authorize the reader PR using existing CI evidence. The new reader validates versioned Ubuntu labels against authenticated job labels and preserves the legacy Darwin and exact-build contracts.
2. Enable the new receipt in canonical CI. Source each label from the same workflow matrix value used by its job's `runs-on`. Capture each actual build and pinned runtime, keep the trusted source digests exact, and retain both builds in the signed receipt. Update consumers of the raw and signed receipts.
3. Prove same-label mixed and equal builds, another versioned Ubuntu label, and refusal of missing, inconsistent or invalid evidence. Get independent Grok review before each merge, run canonical CI and the trusted verifier, then verify the new receipt on GitHub before closing #411 and releasing #360.

## Reader candidate

[PR #412](https://github.com/kburson/aitm/pull/412) contains the new reader. All 160 gate and verifier tests passed. [Grok passed the exact head](https://github.com/kburson/aitm/pull/412#pullrequestreview-5999767888). The unchanged canonical producer and current trunk verifier must accept this PR before introduction of v3.

## Producer rehearsal

The separate producer candidate passed 227 related tests and workflow lint. In a local replay of #410 attempt 6, the new gate accepted the downloaded test evidence after adding each requested label obtained from the corresponding authenticated GitHub job record. The two observed images were `ubuntu24:20261116.376.1` and `ubuntu24:20261116.133.1`, both for `ubuntu-24.04` and Python 3.13.9. This replay exercised the gate. A live signed receipt and current trusted verifier are required for delivery.

[Draft PR #413](https://github.com/kburson/aitm/pull/413) exercises the new producer in Actions before rollout. The first run showed that GitHub appended the matrix value to static job names. An explicit job name from the one-row matrix restored `python-base` and `python` in the [next Actions run](https://github.com/kburson/aitm/actions/runs/44822847471). The authenticated job records preserve the `ubuntu-24.04` label for both lanes. [Grok accepted that draft revision](https://github.com/kburson/aitm/pull/413#pullrequestreview-5999817940).

The [reader's first attempt](https://github.com/kburson/aitm/actions/runs/44821288070/attempts/1) passed both Python jobs and was rejected by the old same-image comparison. [Attempt 2](https://github.com/kburson/aitm/actions/runs/44821288070/attempts/2) failed in the existing monitor coverage fixture before evidence collection. The reader remains subject to the current trusted gate.

The corrected draft passed all six canonical jobs. Its [attestation-verified mixed-build receipt](../attachments/2026-11-20-411-hosted-mixed-build-draft.json) records `ubuntu24:20261116.133.1` for the base and `ubuntu24:20261116.376.1` for the candidate, with `ubuntu-24.04` and Python 3.13.9 on both. This establishes hosted producer behavior before rollout. The staged reader and final target verification still gate delivery.
