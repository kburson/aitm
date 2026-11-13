[22:16:26]
# HOLD

The recovery plan does change real things, but the B boundary still doesn't come from the existing capture model. It comes from rewriting fields on the observation. The first HOLD set the rule for this case: if unchanged code doesn't produce a boundary at 10, the work needs parent-plan re-acceptance, not #270. Unchanged code still doesn't produce one.

## Live negative vs diagnostic mocks

- **Live result is still negative.** The live preflight and the exact replay agree. Unmodified `_native_delta`/`_verify_next` advances the cursor, finds 0 boundaries, refuses, and creates no epoch. The cause is now known: the child observations fail the `boundary.stream_ref == locator.stream_ref` filter.
- **The mocks prove only that the types fit together.** They patch `read_delta`, and the parent mock also patches `_approved_candidate`. They show the downstream types accept the injected inputs. They prove no authority.
- **The child mock rewrote two fields, not one.** It changed `boundary.stream_ref` and also `project_context` (to `frame.anchor_ref`). The recovery text mentions only the stream. `project_context` decides `anchor_project` and therefore the route. Without that rewrite the child likely resolves UNASSIGNED or HELD.

## Do existing types fix the first HOLD, or add capture authority?

They add capture authority.

- **The relabeling is a capture-model change.** The stream filter is the isolation guard, and the stream decides the capture key. Calling the gap "the isolation stream, not a new boundary type" still means changing which stream owns these native requests. That is M07.
- **It creates a second issuer of `VerifiedBoundary`.** Plan item 2 writes the projected proof straight into `_verified`, skipping the armed-frontier identity check in `verify_boundary`. `_require_direct_proof` trusts anything in `_verified`. The stop boundary excludes this kind of parallel registry authority.
- **The projection is needed on every read, not just at issuance.** The diagnostic needed it during `read_source` as well. So every later read of B's epoch (reopen, #204) needs the qualifier too, which makes the qualifier or receipt standing read authority. That contradicts "do not treat the receipt as permission".
- **Expiry leaves an orphan epoch.** After the 5-minute expiry, the B epoch stays durable and enabled, but the ordinary path can't read it.

## Is the private issue/revalidation path safe?

- **Issuance is fine.** It is named and gated. Ordinary reads keep the uniqueness refusal. `_stream` includes `source_id`.
- **Revalidation is not.** `view(*batches)` can be called again later, outside the private entry, and it only runs `_recheck_batch`. That recheck covers the registry view, the root, each file's own cursor and the checkout. It does not recheck the pair:
  - that B holds exactly the transcript and its metadata;
  - that no new sidecar has appeared under A;
  - that the receipt is still live;
  - possibly, appends past a terminal prefix (that depends on whether `fixed=` rejects growth).

  So the plan's promise to recheck "before issuing or reissuing" doesn't hold. Fixing it needs either a pair-aware `_recheck_batch` (a change to shared code) or pair batches that can be used only once.

## Can native evidence and replay fit in four hours?

No.

- **No live positive exists yet.** Every positive so far comes from a mock. The live run depends on the model calling Agent exactly once.
- **The input mode isn't pinned.** Pausing between turns needs a specific input mode. It has to be pinned and shown to produce the approved `native_surface`, because `_native_delta` filters on it.
- **The workload is too large.** A projection on every read, a pair-aware recheck, the receipt, the 14-case matrix, both suites and source review don't fit inside the cap.

## Concrete missing proof

1. **Stream and context values.** Take these from the saved artifacts:
   - B's locator `stream_ref` under the live `subagents` root, not the replay root;
   - the A-root sidecar's `stream_ref`;
   - the adapter's emitted `boundary.stream_ref` and `project_context` for rows 10 and 19.

   Together they show which stream the existing model assigns child requests to.
2. **An unpatched read of B after a B epoch exists.** Run `read_source(B, …)` and record whether it routes. If it doesn't, the projection is permanent read authority.
3. **The child route with only the stream projection.** Run it without the `project_context` rewrite and record the result.

## Smallest slice

- **The model question goes to parent-plan re-acceptance.** Hold #270 and keep #204 → #119 unchanged. Proofs 1–3 are the inputs that decision needs.
- **270a can be done now inside the current gates.** It is the native qualifier and closure trace only:
  - process ownership, pause and arm;
  - exactly one Agent call;
  - B contents exactly the transcript and metadata;
  - closed prefixes and late-append detection.

  It issues no registry or scope authority: no `_verified` writes, no epoch and no receipt.
- **270b and 270c wait for the accepted model.** 270b is registry and scope; 270c is receipt, restart and the refusal matrix.
