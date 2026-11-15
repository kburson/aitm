[16:54:35]
JIT_121: HOLD

The scope, estimate, ordering and custody contracts all bind. The hold is that no delivered product source authenticates the join between an owner's sealed scope proposal and the Grok prompt that carried it. The proof requirements make that join mandatory, and the three-file bound cannot add it.

## Binding conditions that pass

| Condition | Evidence |
|---|---|
| Literal trunk and prerequisites | `4ba4354f` is #331's merge (PR #334). #331's literal base `8be6d460` is #330's merge (PR #333). Both records show ordered parents and zero diff verified. #115, #120, #304, #325, #326, #330 and #331 are closed. #123 and #125 stay open and downstream. The #330 record still lists #331 as `open`, but that is a snapshot taken at #330's close and #331's own record supersedes it. |
| Estimate | 3.5 h, size M, under the 4.0 h cap. Reservations sum exactly: 1.25 + 1.15 + 1.1 = 3.5. Actual so far is 0.0107 h. |
| Three-file bound | `monitor.py` is absent from the trunk tree, so it is a new file. `service.py` is blob `08e79cf2`. The test file is not in the supplied src listing and needs an existence check. |
| Control publication and enrollment lock | `Registry.apply_pending` holds `inbox.publication()` for the whole pending loop. `ScopeState.enroll_grok` takes `inbox.publication()` itself and documents "call outside publication()". Because the lock is non-reentrant, the order is forced: step 1 must return before step 2 runs. |
| Pending-disable ordering | `enroll_grok` reads `inbox.iter_pending(locked)` at call time and checks `_GrokPending` rows. Either raises `BoundaryUnavailable`, so pending disables block (Amend condition 3). |
| Armed or pending edges held | In `apply_pending`, `_CaptureArmed` saves the armed view and adds the edge to `held_edges`. `BoundaryUnavailable` also holds the edge. Other edges keep running. |
| Enrollment waits for the turn | With no cut, `enroll_grok` commits the arm witness, then raises "Waiting for the enrolled Grok turn to finish". |
| Pre-witness gaps | `grok_enrollment_gaps()` derives sanitized `GrokEnrollmentGap` values from durable `_GrokGrant.witnesses`. It reports the span `[0, cut.offset)` for a frozen cut and `(None, None)` for an inactive arm. |
| Scope envelope authentication | `ScopeInboxReader.iter_verified` re-runs `seal_request(record, request)` under `open_grant` and `pinned_destination`. |
| Guarded delivery | `reserve_batch` accepts only a `PreparedRouting` issued by this writer. `_stored_ack` checks the HMAC seal, project, destination, revision and sequence ordering. Owed work is retired only on exact ACK. |
| Bounded retry | `Scheduler.finish` accepts only the current, unexpired `WorkItem`. A failed catch-up backs off up to 8.0 s, and `SETTLING` becomes `PARKED` only on catch-up. `take_due` enforces a limit of 64 or less with project and stream round-robin. |
| Park route | `_park_session` sends a `HookEvent(WakeKind.PARK)` through `HookSender`. It fails closed to `UNAVAILABLE` and never touches `ControlInbox`. |

**Condition carried to Develop (not a hold):** `apply_pending` has no `inventory` parameter. The shared `_InventoryCycle` must reach the callback by binding `inventory=` into `_grok_capture_evidence`. Confirm that `Registry._apply` does not already pass `inventory`, or the binding conflicts.

## Holds

**H1. The Grok marker receipt has no authenticated product producer.**
- `GrokAdapter.verified_boundary` (`sources/grok.py`) accepts any `verify_receipt(session_id, prompt, hook.event_id)` result that passes `validate_source_ref`. That check confirms the value is shaped like a source ref. It does not authenticate it.
- The only `GrokAdapter(` construction at trunk is `tools/qualification/isolated_grok_pilot.py:372`. Its receipt is `pseudonymize("isolated-grok-prompt-v1", receipt_sha256)`, computed over the pilot HMAC body `{event, session, prompt, nonce, started, pid}`. That body carries no grant, `command_id`, envelope digest or project.
- So the pilot receipt proves that a pilot child's hook ran for that prompt. It does not prove that this owner's `ScopeEnvelope` was carried by that prompt.
- The pilot is also a disposable capability with its own receipt namespace. Using it as the owner join would be test-only authority, which the scope forbids.
- `seal_request` and `iter_verified` reference no Grok prompt or receipt.
- The required proof ("one authorized Grok marked turn joins a real authenticated owner receipt to the native completion") therefore has no existing way to authenticate the join. Any mapping written in `monitor.py` would be invented authority.
- The real producer would be a Grok `user_prompt_submit` issuer plus a product `verify_receipt`, likely in `sources/hooks.py` and/or `monitor_scope.py`. That is a third-file incompatibility.
- One caveat: the bodies of the call sites at `monitor_scope.py:2894` and `:2968` were not supplied. If they already bind this join, H1 dissolves. Exact JIT cannot pass on unshown source.

**H2. No concrete `WakeResolver` is identified.**
- Only the `WakeResolver` Protocol and `WakeIngress` are supplied.
- The accepted test list includes "park in the existing CLI paths". `_park_session` returns 0 only when it gets `SENT`, which needs a listening ingress with a real resolver that maps a session ref to registry streams.
- Codex and Claude Stop additionally need the verified current-turn origin from M10b, which is held and shared with #125.
- A test-supplied resolver would be test-only authority.

## Resolution options

1. **Supply missing source.** Provide the excerpts of `monitor_scope.py:2880–2990` and `sources/hooks.py`, plus any concrete `WakeResolver`, so I can re-run JIT on that evidence. This works if they already contain the join.
2. **Add a narrow producer story before #121.** Rank it between 249.5 and 250. It would own:
   - an authenticated Grok prompt-marker receipt that binds the envelope `command_id` and digest to the session, prompt and hook event;
   - the product `verify_receipt`;
   - a registry-backed `WakeResolver` for park.

   #121 would add that story as a Blocked-By and keep its three-file bound and 3.5 h estimate.
3. **Return #121 to Refine.** Its proof would then cover a coordinator that holds every Grok mark at `BoundaryUnavailable`. The park ingress would stay closed, so CLI park returns `UNAVAILABLE` and reconciliation covers it. The marked-turn proof would be deferred to a named later story.

Reply 1, 2, or 3.
