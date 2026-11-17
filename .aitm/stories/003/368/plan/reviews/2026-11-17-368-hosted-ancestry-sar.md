# #368 ancestry single-agent review

Opus 5.5 at high effort performed standalone SAR. The reviewer considered the supplied plan and exact packet text and test
output. The author independently verified the reported Git and file hashes. The final check resolved the timed guard finding.

- The policy adds three literal metadata grants and preserves the existing protection boundaries. The initial run’s failure is
  reproduced by the real pinned ledger ancestry check. The revised local predicate returned the full physical chain.
- The protected hosted gate compares full worker and controller readbacks, matches the pinned owner, mode and ACL predicate,
  and requires EPERM for known-existing protected targets.
- The final packet binds plan acceptance plus 1252 seconds as a canonical UTC deadline. Red/green tests cover equality,
  expiration, malformed and absent data, and the controller reads its decision immediately before product dispatch.

**PASS** on the accepted plan and its exact execution packet. Plan SHA-256 `361618e5244f2c64aaffb98a31a3ea291ee62797f27c700304f41bc7b225885f`.
Packet SHA-256 `d16be608871c267227c3ed63d3ebcfab9049f68a9abcb0056069885359b1e7e8`.
[Exact plan](../2026-11-17-368-hosted-ancestry-implementation-plan.md) · [Execution packet](../2026-11-17-368-hosted-ancestry-execution-packet.md) · [Plan XPR](hosted-ancestry/plan/2026-11-17-2026-11-17-368-hosted-ancestry-implementation-plan-review-84fdbdfe0dd75c4a33ae32978465093a/review-84fdbdfe0dd75c4a33ae32978465093a-review-manifest.md).

The first broker review returned without submitting its draft response. Its evidence was preserved. The accepted XPR is a
fresh review of the revised plan with the resulting worker-predicate and budget findings incorporated.
