[20:27:11]
# SPLIT_300: PASS

**Basis:** I used only the supplied evidence: the split plan, the #300 Refine HOLD, the R2 amendment and the NA-1 JSON. I did not recompute either SHA. Several things were not supplied: the M09–M19 milestone prose, #300's current native body, and where #121 and #125 sit in the graph. This PASS accepts the parent plan for this exact split only. It is not a Refine, JIT or code approval, and it does not authorize development for either leaf.

## How the split answers each Refine finding

| Refine finding | How the split resolves it | Verdict |
|---|---|---|
| 1. Profile default and activation authority | The default is closed. There is no open flag in any command, constructor or configuration. Regression tests get a profile only through test-owned fixtures. Only a qualified issuer can bind policy, and raw profile dicts are refused. Leaf JIT must name the issuer, attestation input and root binding, or HOLD. | Resolved for plan purposes |
| 2. No source for build or executable identity | The producer consumes an authenticated installation identity. #128/#129 own binary inspection and signed catalogs. The release catalog is empty until receipts exist. | Resolved; this matches R2's exact-build receipt rule |
| 3. Approval behavior vs the coverage key | New and repeated approvals are both refused. The registry encoding is unchanged. An excluded installation gets no source ID. A refused install in an already-approved root records only a broad status with unknown extent. | Resolved; consistent with R2's fallback to a broader authorized status |
| 4. Where policy changes come from and when they are rechecked | Recheck happens before reserve and on the `current == read.progress` retry path. Capabilities are immutable, and a superseded or revoked one fails the final check. | Recheck points resolved; source deferred (condition 2) |
| 5. Sequence and schema details | One transaction writes both the event and its `commits` row, so `_tip` covers it. A lazy upgrade takes v4/v5 to v6 with both tables. v4/v5 reads return empty without upgrading. Unknown schemas are rejected. The refusal is written before `prepare` raises. Rollback is noted for #126. | Resolved |
| 6. Estimate | Two leaves of about 2.7h and 2.5h, each capped at 4h and re-estimated in its own Refine/JIT. Fixture churn is timeboxed. | Resolved; each leaf can be scoped on its own |

## What is preserved

- **Dependencies:**
  - The producer's only incoming edge is closed #210. Its outgoing edges are {300, 119, 129}.
  - #300 keeps #210, adds the producer and still blocks #119 and #129.
  - No existing edge is removed, so a partial insertion still leaves every gate closed.
- **Endpoints:** The procedure requires #300's, #119's and #129's prerequisite sets to equal the old set plus the producer. It also requires the #301 and #297 relations to stay unchanged.
- **Epic #100:** The producer is a direct child, so closure still requires every included child to deliver. Epic #2, C01 and cutover stay excluded.
- **Release rules:**
  - Neither profile mode admits Claude.
  - Isolated qualification is limited to non-Claude tuples inside the matrix.
  - The release allowlist is empty before receipts.
  - History stays readable without live authorization.
  - Plain refusal, native diagnostics and healthy independent progress are kept.
  - No receipt, cursor or ACK is fabricated.
- **Handoff between the leaves:**
  - The producer returns a private decision derived by the writer, carrying the policy generation. It writes no coverage records.
  - #300 consumes that decision only through the writer. It never accepts a caller-supplied exclusion claim.
  - Service, signing, reporting and installation stay downstream.

## Conditions for leaf Refine/JIT and graph execution

These do not block this PASS, but each leaf's Refine/JIT must meet them.

1. **R2's tests stay owned.** R2's three named tests remain #300's end-to-end obligations unless a leaf JIT explicitly moves a sub-case to the producer. That includes these R2 items, which the split never mentions:
   - archived-replay bypass
   - late writes
   - existing hold and disposition replay/expiry behavior
   - unrelated failures staying independent
   - no unauthorized cross-project coverage
2. **Name the revocation source.** The producer's JIT must name the existing authenticated source of the current policy generation and of supersession or revocation that the final check reads inside the write transaction. The leaf adds no persistence, so if no existing source can supply this, the leaf must HOLD.
3. **Keep fixtures out of the product.** Test shims must live only in the test tree and be unreachable from package import or any product path.
4. **Name the release-issuer owner.** The plan says to "pass explicit issuer contracts to the later scope owner" but never names that owner. If the producer holds on the issuer, the split returns for parent re-acceptance; no downstream leaf takes it over implicitly.
5. **Order #300 after the producer.** #300's Refine/JIT must bind the producer's decision type as delivered at its exact merged head, not as planned.
6. **Graph execution:**
   - Explicitly re-verify the R2 endpoints: #100 incoming {101,102} and outgoing {2}; #297's children; #204 outgoing {296}; #119 outgoing {120,122,296}; the #295/#298/#135 edges; and #301 having no parent and no edges.
   - If a step fails partway, reconcile before proceeding.
   - Add a note to #300's native issue pointing to the split so its policy ownership isn't stated twice.
   - Record this artifact's SHA alongside the producer body. The body's link points to the `planning` branch, which can change.

## Not verifiable from the supplied evidence

- Either SHA.
- The NA-1 edges not shown in the JSON. As in the Refine, I accepted these on your statement.
- Whether #121 and #125 are native dependents of the producer or of #300.
- Whether the R2 M11/M15/M18/M19 text already covers the duties this split assigns to #121, #125, #128 and #129.
