[20:33:37]
**REFINE_303: HOLD**

I used only the supplied evidence: the Refine artifact, the accepted split and its PASS conditions, the NA-1 native JSON and the trunk excerpts. I did not recompute the SHA. This verdict does not claim that any implementation or delivery has happened.

## Viable as a bounded plan (concrete details can stay JIT work)

- **Gate placement fits the trunk.**
  - `_approve` returns early on the matching-`source_id` replay path, so the check must come before that loop.
  - Payload checks fit in `_approved_candidate`, which is the shared choke point for the native Codex, Grok and delta/boundary paths.
  - In `RoutingJournal._reserve`, the `current == read.progress` path skips `_write_progress` but still returns `outcomes`. A check inside the transaction, before the first `_claim` and before the return, covers every reserve path.
  - None of this needs a change to the journal format, cursors, ACK or reports.
- **Closed default and release mode work.** A new writer starts closed and the release catalog has zero entries. That means release mode needs no receipt consumer in this leaf. One condition: no release-grant path should be written at all, rather than left waiting for future receipt wiring.
- **The custody primitives exist.** The lease (`Registry.lease`), the source key checked against `source_key_id`, `ScopeState` operator authority and the root identity in `_approved_candidate` are all in the trunk. The artifact correctly says these prove custody, not executable identity.
- **The private exclusion decision and the estimate fit 2.7h**, as long as no new authenticated source has to be built.

## HOLD findings (known missing source or authority, not JIT detail)

**H1. No provider-executable attestation source exists.**
- The accepted contract requires a grant to carry a "verifier-produced exact installation identity" for isolated qualification.
- The only verifier in the supplied evidence is `ActivationReceipt`. Its own docstring says it has "No private provider or host identity fields". `validate_activation_receipt` deliberately does not open project files.
- `_approved_candidate` checks only the platform/machine/surface/provider tuple, which is request metadata. The artifact itself says that is insufficient.
- #128/#129 own host executable inspection, but per NA-1 #303's only incoming edge is #210. #129 is downstream of #303, and #128 is not a prerequisite. So #303 cannot consume their output.
- The accepted split's own rule applies: "If no existing authenticated input can supply one of these fields, hold rather than synthesize it."

**H2. No authenticated source exists for policy generation or external revocation.**
- PASS condition 2 requires the JIT to name the existing source that the final check reads inside the write transaction.
- The supplied trunk has only lease loss and root change, and the artifact concedes these cannot prove external revocation. The leaf also forbids policy persistence.
- A writer-local keyed slot can enforce supersession within one writer. It cannot satisfy the "current external authorization" part of the final check.

**H3. Only a scope change can resolve H1/H2, so the parent plan must re-accept it.**
- The only ways to supply H1/H2 are a new authenticated input or a new producer. Both are outside the accepted leaf.
- PASS condition 4 says that if the producer holds on the issuer, the split goes back for parent re-acceptance. No downstream leaf may take the issuer over implicitly.

## Smallest resolution

Either of these would resolve the hold:

1. **Evidence amendment (no scope change).** Cite, at trunk `a85d088`, an existing authenticated:
   - provider-executable installation attestation;
   - policy generation and supersession/revocation source.

   Give the exact paths and functions. If both exist, this becomes a PASS with no other change.

2. **Scope amendment (preferred if option 1 is unavailable).** Amend the split and re-accept it at the parent level:
   - **#303 keeps:**
     - closed enforcement at approval, payload read and reserve/retry
     - the empty release catalog
     - the typed issuer and capability contract, with **zero product-reachable issuers**
     - writer-local slot supersession and revocation
     - the private exclusion decision
     - hosted tests whose grants come only from a test-tree issuer that cannot be reached from package import
   - **#303's currentness** is defined as: the writer-local slot generation, the active lease, the bound root and the installation-evidence object identity.
   - **The real isolated qualification issuer moves to a named new leaf.** That covers the host attestation input, the disposable-root binding and the external generation/revocation source. The new leaf must:
     - depend on #303;
     - block #128 and #129, plus #121 and #125 if they consume verified policy;
     - be added without removing any existing edge.

   This moves the accepted "real isolated authority boundary" condition to a named owner instead of removing it. It also keeps #303 within its 2.7h estimate and #300's dependency on the decision type intact.

Until one of these is accepted, #303 must not enter JIT.
