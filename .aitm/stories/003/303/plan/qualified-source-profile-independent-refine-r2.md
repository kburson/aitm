[20:41:04]
**REFINE_303_R2: PASS**

This verdict means the revised leaf is ready for exact JIT. It does not approve implementation, and development waits for an independent JIT. I used only the evidence you supplied and did not recompute the SHA.

## Prior holds

| Finding | R2 disposition | Status |
|---|---|---|
| **H1:** no source proves which provider executable produced the stream | #303 defines no issuer anywhere in the product and adds no release grant path. Proving the executable against the real admitted stream is left to the accepted issuer (#304) and the target gates. | Resolved by assigning it to #304, not by dropping it |
| **H2:** no source for external policy generation or revocation | #303's currentness check uses only the in-writer versioned generation, lease, physical root and exact tuple. External currentness inside reserve belongs to the issuer. A missing verifier, lease, root, capability or active check fails closed. | Resolved. This matches the currentness definition the amendment accepted. |
| **H3:** the parent plan had to re-accept the scope change | ISSUER_303 passed. The native record shows edges 303 → 304 and 304 → {121, 125, 128, 129}. Rank 229.065 checks out and the protected relations match. | Resolved |

## Fit with trunk and the accepted boundaries

- **Approval check.** The check in `_approve` runs before the early-return and replay path, as the original Refine required.
- **Payload checks.** R2 fixes a gap in my first Refine. In the supplied excerpt, `ScopeState._read_grok` does its own `_source(...)` lookup and its own checks, and does not call `_approved_candidate`. Naming it as a separate gate is correct.
- **Reserve recheck.** The first recheck in `_reserve` runs after the route validation and before `sequence`, `_claim` and `_write_progress`. The second runs after `final_view`, before `return outcomes` and inside the transaction, so it happens before commit. Because the return path is shared, this also covers the `current == read.progress` branch.
- **Historical reads and history boundaries.** Sanctioned history stays readable without granting live ingress. #300 alone owns persistence. #121 and #125 get verified authority through the issuer. #128 and #129 own final native host proof and the signed catalogs. Epic #2, Claude and production cutover stay excluded.
- **Sizing.** 0.7 + 0.6 + 0.5 + 0.9 = 2.7h, under the 4h cap with 1.3h headroom. Estimate entry is gated after acceptance, and Actual is measured progress.

## Conditions JIT must meet (none of these block the PASS)

1. **Re-verify the new trunk.** The trunk moved from `a85d088` to `8d794c5`, and "no project usage source difference" is asserted, not shown. JIT must pin `8d794c5` and re-confirm every named call site. If any of them changed, return to Refine.
2. **Sentence to tighten: "Existing authorizations remain unchanged by the exclusion".** It must mean stored approvals are not mutated or revoked. It must not mean they still admit live traffic, because that would be the legacy fallback the split forbids. JIT should state this explicitly and add a test proving a pre-existing approval is refused live.
3. **Audit the other payload paths.** Capture/delta, replay, the control inbox and adopted historical paths each need an exact call site and a disposition: either gated, or historical-only. If the audit finds an ungated live payload path that pushes the estimate past the 4h cap, return to Refine.
4. **Keep the issuer hook inert.** The private guarded currentness contract must be non-issuing and unreachable from the product. JIT must show where it fits inside the 0.7h types line (issuer condition 2).
5. **Fill test gaps.** Add tests for:
   - Codex and Grok payload refusal, each on its own path;
   - lease loss, and a verifier being unavailable;
   - writer-local supersede and revoke;
   - the test-tree shim being unreachable from package import.
6. **Name the issuer.** Refer to the issuer dependency as #304 in the issue scope, not as "the new issuer dependency".
