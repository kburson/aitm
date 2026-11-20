# #411 Delivery plan

1. Deliver a backward-compatible reader before enabling the new signed receipt. The old trunk verifier must be able to authorize the reader PR using existing CI evidence. The new reader validates versioned Ubuntu labels against authenticated job labels and preserves the legacy Darwin and exact-build contracts.
2. Enable the new receipt in canonical CI. Source each label from the same workflow matrix value used by its job's `runs-on`. Capture each actual build and pinned runtime, keep the trusted source digests exact, and retain both builds in the signed receipt. Update consumers of the raw and signed receipts.
3. Prove same-label mixed and equal builds, another versioned Ubuntu label, and refusal of missing, inconsistent or invalid evidence. Get independent Grok review before each merge, run canonical CI and the trusted verifier, then verify the new receipt on GitHub before closing #411 and releasing #360.
