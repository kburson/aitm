[22:42:54]
# HOLD

The plan addresses most of the earlier HOLD, but it leaves one core design decision unresolved: what authorizes B's projection after the process exits. The fix is wording only and needs no new evidence. Once correction 1 is added, along with the two small additions below, this plan should PASS without another evidence round.

## Blocking gap: the plan permits B's projection only during the live process, but it's needed after exit

The plan allows the private adapter projection "only under a writer-owned process window". That window covers the boundary step: arming, ordinal 10, then `verify_boundary`/`enroll_stream`. But B's scope evidence for its spans has to be read after the process exits, because it depends on terminal extents and the durable Agent result. #204's consumers will read it later still, in their own transaction.

The controls show that without the projection, B's scope evidence fails:
- Projecting only the stream routes `unassigned`.
- An unmodified read after the epoch exists returns `held` with 0 proofs.

So each post-exit B scope read needs both projections, the stream and the project context. The plan never says what authorizes them once the process has exited. Read literally, it forbids them. This is the "standing read authority" issue from the earlier HOLD, now unstated rather than resolved.

**Minimal correction:** split the authority in two.
- **(a) Boundary projection:** allowed only inside the live writer-owned process window, as written. This is the only route into `_verified`.
- **(b) Post-exit scope projection of B:** allowed only under the authenticated admission record, as a read-only step under the lease and inbox lock. Each use rechecks everything the plan already lists. It feeds only the paired `VerifiedScopeBatch`, never capture, `_verified`, epochs or permission. The checkout comes only from B's own verified frame rows, never from A.
- State explicitly that the record is a read qualifier for this one pair. Re-accepting the parent plan is the right place to admit that.

## Required additions (not blocking on their own)

1. **Late-append and extra-sibling refusals:** add both to #272's minimum refusal set, checked at the consumption recheck rather than only at issuance. The plan's recheck promises exact terminal extents. It is still unproven whether `_capture_position(fixed=)` rejects growth, and #271 showed it only as a diagnostic. If it doesn't reject growth, the extent-equality check has to be new code, and #272 has to prove it.
2. **Fresh live run, with #271's ordinals as reference only:** wording like "Retained positive is [37, 47)" and "ordinal 10" must not read as reusing #271's artifacts. #271 is closure evidence only and issued no child epoch. A genuine boundary needs a live arm, so the acceptance criterion should be the shape of the run:
   - an origin prefix with no requests, armed before the first child request;
   - exactly two B requests, both after that boundary;
   - one A prompt-to-result span after A's epoch.

   If the arm lands after the first request, that request is an earlier unadmitted request. The run is then a refusal, not a positive with shifted spans.

## Accepted as written

- **Single issuer:** the armed-frontier identity check and `_verified` publication stay inside the existing `verify_boundary` path. This removes the second-issuer problem.
- **Separate ordinal spaces:** these hold because the source ID is in both `_capture_key` (via `CaptureChange`) and the scope `_stream`. One unrecorded detail: the controls record only booleans. Record the actual parent and sidecar locator `stream_ref` values, so it's shown that "B locator stream" and "pinned native session stream ID" are the same value.
- **Consent and transitions:**
  - B is enabled before the prompt through the ordered inbox, as prospective consent with no epoch.
  - A's own epoch is established before the covering prompt.
  - Qualification is refused while either edge is pending, disabled or revoked.
  - Ordinary disable of B must be proven to fence correctly before the positive.
  - A's ambiguity-pending disable already exists today; #272 doesn't introduce it, so refusing qualification in that state is enough.
- **Exact-pair resolver for A:** it is adapter-specific, accepts only the enrolled parent and the authenticated B sidecar, and leaves ordinary uniqueness refusal in place. This fits M06.
- **Batch and receipt rechecks:**
  - No consumable `ScopeView` or `VerifiedScopeBatch` is returned, which closes the earlier reuse of `view(*batches)`.
  - The extension to the shared recheck is typed to the paired context.
  - Every consumer rechecks under the lease and lock, and nothing is cached.
  - Checking every scope event boundary is stricter than the endpoint-only check in `resolve_route`.
  - Requiring both spans to have the same original route fails closed when A's scope events don't reach B's timeline.
- **Record and epoch order:** publishing the record after the epoch is durable is safe because the record grants nothing alone. Each use refuses on a pending command or a changed epoch. The B epoch left behind if publication fails is acceptable only because ordinary reads have no effect. Assert in #272 that after the B epoch exists, an ordinary scan of A and B creates no holds, gaps, journal entries or totals.
- **Gates and order:** M06/M07 consent, the prospective boundary, the original-scope and first-owner gates, and #204 → #119 are all unchanged. Restart, faults, disable/re-enable controls and the wider refusal matrix are correctly left to #273. #204 already depends on #273, so the record's behaviour across disable and re-enable does not need to be settled in #272.
- **Four-hour slice:** this is plausible now that restart and the matrix have moved to #273. Treat the 2.75-hour checkpoint as a hard stop. If there is no genuine B boundary through `verify_boundary`/`enroll_stream` and no paired `ScopeState` resolution by then, nothing is delivered from #272, the failing gate is recorded, and #204 and #119 stay blocked.
