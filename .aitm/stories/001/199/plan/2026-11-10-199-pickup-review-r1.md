# #199 independent pickup and split review, round 1

Claude Opus 5.5, high effort. Off-platform review of the full exact pickup and split on the literal trunk baseline. November 10, 2026.

# Independent review: #199 JIT/refine and the proposed M08b split

I used only the packet. I made no tool calls, edits or GitHub changes. Neither verdict authorizes a provider run, a later leaf Develop, or a change to the parent order.

## Verdict 1: #199 JIT/refine (`ec1bc8a1…84187`) — **HOLD**

The plan does not change any original obligation. The obligations that matter are scope switch, disabled span, re-enrollment, copy, untimed ordinal and legacy byte equivalence. It also keeps the journal, ledger and coordinator unchanged, and it states that quota metadata releases nothing. Three seams are not exact enough to meet the four-hour cap.

**H1. The witness carrier into `VerifiedScopeBatch` is not specified.** (*Interfaces*; *Task 2*; `sources/adapter.py` `read_delta`/`AdapterBatch`; `monitor_scope.py`)
- The plan names both ends: the producer callback and `ScopeState.verified_revision(batch, observation)`.
- It does not name what connects them. `ScopeState` only receives the public four-field `AdapterBatch` from `ProviderAdapter().read_delta(...)`, and `VerifiedScopeBatch` is built positionally.
- Adding a field to either one may be the "shared public data shape" change that the plan says sends it back to planning.
- Required fixes:
  - Name the private carrier. It should be either a field with `compare=False, repr=False` (the `SourceFrame._prefix` pattern) or a table held by the issuer and keyed by identity.
  - State that this carrier is not a shape change.
  - State that `verified_revision` trusts only batches in `self._batches`, so a caller-built `AdapterBatch` that carries a witness gets nothing.
- Name the key used for the "service-keyed" fingerprints and the keyed prefix. The adapter has `source._ledger`, and `ScopeState` validates through `registry.source_evidence()`. Say which key derives the witness and which one verifies it.

**H2. The list of emission sites is incomplete.** (*Task 1*, bullet 2; `sources/claude.py`)
- `publish()` is called from five places:
  1. the accept path
  2. the issue branch `publish(key, replace(record, processing_tier=revised_tier), previous)`
  3. `withdraw_overlapping_report`
  4. `report`
  5. `terminal`
- Site 2 publishes a real revision alongside a MALFORMED_USAGE, COUNTER_REGRESSION or UNRECONCILED_USAGE diagnostic. "Parser diagnostics" does not clearly cover it. State that this tier-invalidation revision gets no witness, and add it as a RED negative.
- `terminal()` receives `event.timed_ordinal` and `location`, not the frame that commits the revision. The plan must change that internal signature so the untimed witness carries `SidebandFrame.ordinal`.
- One terminal row can complete several requests, and those requests then share one later row. The phrase "ordered distinct later spans" in *Review focus* needs to say it applies to successive revisions of one request. Add a fixture where one terminal row completes multiple requests.

**H3. The quota-only seam is undefined, and it is the main risk to the cap.** (*Interfaces*, last paragraph; *Task 1*, bullet 4)
- "Before deduplication" and "identical diagnostic" are not defined. The plan needs to say where deduplication happens and which fields count for equality (code, location or ordinal, provider, stream, observation key).
- It must also classify three cases:
  - the end-of-run `not self.quota_checked` gap at `self.latest`
  - a rate-limit row that is present but malformed while an account is verified
  - a non-success `result` gap at the same frame as the quota gap
- M08b1 never uses this metadata, so it adds no standalone value to #199. With only 0.25 h of margin, either move it to M08b2 (and re-estimate M08b2) or keep it with the definitions above and justify the 3.75 h.

Two notes, not blockers:
- `read_delta` returns UNSUPPORTED_FORMAT on anything other than Darwin/arm64. RED "through the actual adapter" has to name how it runs on the Linux hosted jobs (the existing platform fixture pattern).
- Add the inverse cost-state case: the timed context is disabled and the untimed ordinal is re-enabled.

## Verdict 2: the native split (`91623a43…a57a80`) — **HOLD**

These parts survive the split:
- Parent and #118 bytes are pinned by hash.
- M09 keeps the actual write ACK and atomic child replacement.
- M12 and M13 keep fencing and visibility.
- Linux carriers and release qualification stay outside these leaves.
- M11 still runs after #119 and #120.
- The provider run stays conditional and is not authorized.
- A child relation, equal sums, call counts and session totals are all declared insufficient.
- Every leaf directly gates #119.
- Copied or stale evidence cannot lift a dispute.
- The scope-switch and disabled-span tests are placed in M08b2.

The following blockers remain.

**S1. Nothing makes the native edges exist before #199 closes.** (*Native ordering*; #199 *Delivery*)
- #119's only direct prerequisites today are #118 (Closed) and #199. If #199 closes before M08b2–M08b5 exist with native blocked-by edges on #119, #119 becomes unblocked natively.
- Require that M08b2–M08b5 are created, along with the #199→b2→b3→b4→b5 chain and each leaf's direct block on #119, and verified natively before #199 enters Develop. At the latest, this must happen before #199 Project Close.

**S2. M08b5 has no closure rule when the evidence fails.** (*M08b5* paragraph)
- "Keep #119 blocked, and record the exact failing proof gate" is not enough. If b5 closes as Done after a failed qualification, the native edge releases #119 even though no folded intent was delivered.
- State that b5 can close only in one of two ways:
  - it delivers the folded intent, or
  - a native blocker on #119 replaces it until an independently re-accepted parent change exists.

**S3. The exact #118 contract has no named owner.** (*Accepted #118 split*, M08b bullet; parent *M08 Contract*)
- No leaf is named as the one that introduces `RoutingJournal.record_disposition(change: VerifiedRouteDisposition) -> JournalChange`. M08b4 only says "atomic local JournalChange", and M08b5 says "one exact journal folded intent".
- The parent rule "a superseding covering representation and the withdrawal of its children must share a single publication change" is also not carried.
- Assign the exact signature to one leaf (probably M08b4). State that M08b5 extends it so the folded replacement and the child withdrawal happen in one `JournalChange`.

**S4. Only M08b2 gets a schema version review.** (*M08b2* paragraph versus *M08b3*, *M08b4* and *M08b5*)
- #118 requires an independent version review for any new private schema in a successor.
- M08b3 (durable disputes), M08b4 (scope persistence and disposition receipts) and M08b5 (folded intent) will probably each add state.
- Each leaf that adds state needs the same obligation: exact admission from the old version, atomic schema change and retry, explicit treatment of old rows, no rewrite of history, and rejection of unknown schemas.

**S5. M08b2 has no rule for applying a successor to the journal head.** (*M08b2*)
- The b1 proof covers only the immediate native predecessor. If an intermediate revision was held (for example, during a disabled span), the durable head is an earlier revision. Applying the successor to it would bring in the held change.
- Require that b2 applies a successor only when the proof's predecessor material fingerprint equals the durable head. Proofs must not chain through a revision that had no proof. #199's witness must expose that fingerprint.

**S6. Quota and aggregate settlement in M08b2 are not bounded.** (*Authority and evidence*, para 2; *M08b2* row)
- "Inapplicable to progress" combined with "usage-vs-quota cursor settlement" could move the cursor past quota rows that are still unattributed. After that, a later account verification can no longer replay them.
- State that a quota-only release must not drop the quota replay obligation unless another component keeps it (and name that component), and that same-code and mixed cases still replay.
- State that OVERLAP_UNVERIFIED and any other aggregate diagnostic are never settled before M08b5.

**S7. M08b5's Grok option conflicts with the accepted order.** (*M08b5* paragraph; `monitor_scope.py` `_eligible`; parent M10 and M11)
- `_eligible` returns an empty set for `GROK_BUILD_MACOS`. Grok scope admission belongs to M10 and M11, which come after #119.
- So "qualified Grok carrier" can never meet "exact original eligible ownership" inside the accepted order.
- State that before M11 the only path is the Claude carrier, and that any Grok-based positive fold is a parent-order change that needs re-acceptance.

One unverified point: the packet does not show that ranks 226–229 are unoccupied.
