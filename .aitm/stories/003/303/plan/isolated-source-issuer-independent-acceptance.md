[20:36:55]
**ISSUER_303: PASS**

I reviewed only the evidence you supplied. I didn't recompute the SHA. This verdict accepts the parent plan only. It doesn't authorize any development, and the issuer leaf still needs its own Refine and JIT before implementation.

## Basis

- **R2 proof and gates are kept.** The R2 carrier matrix, the release receipt requirement, #83, #297/#301 and #204 are all unchanged. Epic #2, C01 and cutover stay excluded. The issuer has to run Linux and macOS qualification on the exact existing R2 hosts and carriers before anyone claims release support. It also has to go through its own Refine, JIT, signed Test, source review, merge and Close. If a host identity or currentness channel can't be built, the leaf must name the gap and keep the gate closed. It may not weaken the gate.
- **Both HOLD findings now have a named owner.**
  - H1 (no proof of which provider binary produced the stream): the issuer owns proving it on a real controlled installation and binding it to the owner, root, writer and tuple. The amendment explicitly rejects a release receipt, user flag, transcript metadata, stdout, version string, a caller-supplied object or a detached hash as proof. A missing host link fails closed.
  - H2 (no source for policy generation or revocation): the issuer owns the authenticated versioned generation. Expiry and revocation are enforced under the writer's protected authority. A changed generation is rejected before the final write or a retry return, and an old capability can't be committed after revocation.
  - This matches resolution option 2 from the Refine HOLD: the requirement moves to a named owner and is not dropped.
- **There are no cycles, checked against the native endpoints.** The issuer's only dependency is #303, and #303's only incoming edge is #210, which is closed. None of #121, #125, #128 or #129 can reach #303 or the issuer, so adding issuer → {121, 125, 128, 129} can't create a loop. All existing edges are kept, including #303 → {119, 129, 300} and #300 → {119, 129}. Rank 229.065 sits between #300 (229.06) and #295 (229.1), ahead of #119 (230).
- **#303 is ready to return to Refine.** Its scope is now bounded:
  - closed default, no issuer reachable from the product, no release-grant path, no legacy fallback, and test-tree shims only;
  - live approval (including repeats), payload read and reserve/retry each require a present, current capability;
  - generation, lease, root, grant and installation-evidence identity are checked inside the write transaction;
  - it freezes or refuses when the proof or verifier is missing;
  - it returns only the private exclusion decision.

  The Refine already found the 2.7h estimate viable at this boundary, because #303 no longer has to build a new authenticated source. #300 keeps its #303 edge and its test-tree proofs, and the real carriers stay behind the issuer.

## Conditions to carry (they don't block acceptance)

1. **Tighten the issue body.** The exact body leaves out several requirements that only appear in the prose:
   - production and installed readiness must not be able to invoke the issuer;
   - an unavailable host link fails closed;
   - the Linux/macOS R2 host requirement;
   - the 3.5h estimate and the 4h cap.

   Either add them to the body or cite this amendment by SHA in it.
2. **Keep #303's hook for the issuer's currentness proof non-issuing and unreachable from the product.** #303's JIT needs to confirm that hook still fits in 2.7h.
3. **Settle the boundary with #128 when the issue scopes are rewritten.** The issuer now owns proving the provider executable during the controlled run. #128 keeps final native installation and target qualification. Make sure neither issue's scope claims the other's part.
4. **Justification for two new edges is asserted, not evidenced.** The claim that #121 and #125 consume verified policy is the amendment's own. Extra blocking edges only strengthen the gates, so this is acceptable. Issuer → #125 and issuer → #129 are already implied through #121 and #128, but stating them is harmless.
5. **Re-check the graph at insertion time.** The cycle check above uses the endpoint data you supplied. Confirm the endpoints and protected relations again when the issue is actually inserted.
