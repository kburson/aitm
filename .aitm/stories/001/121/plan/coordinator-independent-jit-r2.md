[00:11:11]
**JIT_121: PASS**

This verdict rests only on the supplied packet and source excerpts. I executed nothing. No true hold remains. The items under "Develop conditions" are entry checks and required tests inside the three files. They are not blockers.

## Binding facts

| Check | Evidence |
|---|---|
| Trunk | `755fa2ec` / tree `2ffe0024` is the PR #336 merge. Its literal base `4ba4354f` is #331's merge. Ordered parents and zero diff are verified in `marker-verified-delivery.json`. |
| Graph | All eight Blocked-By issues are CLOSED/COMPLETED and Done: #115, #120, #304, #325, #326, #330, #331, #335. #123 and #125 are open and downstream. |
| Size | Rank 250, M, 3.5 h, against the 4.0 h cap. Reserves are 1.25 + 1.15 + 1.1 = 3.5. |
| Writable files | `service.py` is blob `08e79cf2`, unchanged since attempt 1. `monitor.py` is absent from the tree, so it is new. |

## 1. Prior holds and Stop

**H1 is closed by #335.**
- `bind_grok_prompt` binds the prompt to exactly one staged attempt. That attempt carries the command ID, `proposal_digest`, source, profile, checkout, session, process and image. The binding happens under `ControlInbox.publication()`, and the first prompt wins.
- `grok_receipt_lookup` returns `scope_receipt_ref` only when exactly one attempt matches on `(session_ref, prompt_ref)`. That attempt must also match the current source, profile generation, checkout and digest.
- The lookup ignores `_event_id`. `GrokAdapter.verified_boundary` takes the event ID from the observed hook row instead, so the hook never supplies it.
- `grok_mark` re-acquires publication and re-verifies the original sealed proposal and receipt. It then yields `Mark(command_id, scope, scope_receipt_ref, destination_binding)` for `verify_boundary` and `apply_mark`.
- This is a product authority, not the pilot namespace. It sits entirely outside #121's files.

**PARK bypasses the resolver.** `Scheduler._admit` returns `self.park(request.session)` before calling `resolver.resolve`. `serve_once` checks socket identity, mode `0600` and peer UID first.

**CHANGE is buildable in `monitor.py` from existing seams.** The facts it must supply are:
- **Approval:** `_approved_candidate(..., inventory=)` or `_grok_admission`.
- **Stream:** `locator.stream_ref`.
- **Provider:** `MonitorProvider`, which must equal `request.provider`.
- **Session:** a keyed session. For Grok this is the `grok-session` pseudonym. For Codex and Claude it is the origin `session_ref`.
- **Turn:** may be `None` for CHANGE.
- **Fact:** a service-keyed, scheduling-only fact.
- **Project:** a project ref, or `None`.
- **Cursor:** none. The cursor stays in the `RoutingJournal` custody.

**Refusing Stop satisfies the accepted conditional requirement.**
- The #121 plan says only that a native Stop "must be joined to the exact current … turn before it can settle".
- The proof list requires no positive Stop.
- Accepted M10 defines `STOP_WITHOUT_CURRENT_TURN` as a closed variant and states that a lost or refused wake costs latency, not correctness.
- The v1 `_frame` carries only kind, provider and locator. A fresh Stop and a late Stop for different turns produce identical bytes. No delivered interface binds a frame to a turn, and the last completed turn in the stream proves nothing about which Stop arrived.
- `completion_witness` is gated on `Disposition` and is limited to Codex Desktop. The Grok receipt proves a marker only, not a Stop.
- **Required behavior:** the resolver returns `STOP_WITHOUT_CURRENT_TURN` for every Stop, before any read and with no durable write. Settling still happens through explicit PARK. Coverage still comes from watch, timer and catch-up.

**Transport is not scheduling.** `SENT` and `_park_session` exit 0 report transport only. Admission is decided solely by the boolean from `serve_once` / `_admit`.

**Offline controls are not native proof.**
- The Stop probe's positive case uses the synthetic resolver fixture. It proves the scheduler contract and nothing about native provenance.
- The Grok delivery probe uses #335's product functions with synthetic ancestry. It is a valid retained Develop fixture.
- Native hook-ancestry proof belongs to #335's delivered Test. #121 must claim neither of these as native proof.

**A positive native Stop is not required here.** If it is ever mandated, it needs two things, both outside these three files:
- A producer-issued completion identity in a v2 frame. That means changes to `sources/hooks.py` (`_frame`/`_parse_frame`, which reject unknown keys and `v≠1`), the ingress in `monitor_control.py`, and the hook producer.
- An adapter verifier that joins that identity to the exact turn, in `sources/adapter.py` and/or `sources/grok.py`.

That would be a new Refine leaf. Do not assign it to #320 or #125 on the strength of the probe alone.

## 2. Custody and resource conditions

These were confirmed from source:
- `apply_pending` holds publication for its whole loop. `enroll_grok` takes publication itself, so step 1 must return before step 2.
- Armed and `BoundaryUnavailable` edges are held. `grok_enrollment_gaps()` yields sanitized gaps.
- `reserve_batch` accepts only a `PreparedRouting` that this journal issued.
- `ack` re-checks digest, identity and durable readback, and is idempotent.
- `finish` accepts only the exact unexpired lease and backs off up to 8 s.
- `take_due` is limited to 64 or fewer and round-robins by project and stream.
- `_InventoryCycle` rejects physical aliases and holds a root that fails.
- `_origin_for` reuses cached origins without opening the payload.

## Develop conditions (not holds)

1. **Inventory binding entry check.** The body of `Registry._apply` was not supplied. Bind `inventory=` as a keyword into `_grok_capture_evidence`. Let the first RED confirm there is no duplicate keyword or arity conflict. If a fix would require editing the Registry, return to Refine.
2. **One active cycle; inventory before publication.**
   - `_inventory_cycle` and `_OriginCache._use` are non-blocking and non-reentrant.
   - `RoutingJournal.prepare` and `read_source` pass no inventory. They depend on `_current_inventory(None)` returning `_active_inventory`.
   - Outside an active cycle, Codex/Claude fall back to `ProviderAdapter.discover`, which reopens every parked origin. The Grok fallback in `_current_grok` is unshown.
   - Therefore run the resolver, `apply_pending`, `enroll_grok`, `prepare` and the mark reads inside the cycle.
   - The payload-open counter must also cover `prepare` for both providers.
3. **Publication discipline.**
   - Read `iter_verified` under its own publication, release it, then enter `grok_mark`.
   - Inside `grok_mark`, read only the one selected stream.
   - `bind_grok_prompt`, the native hook, contends for the same lock. A long hold fails closed but loses the binding.
4. **Mark/journal race.**
   - Once the hook binds, any Grok read sees the receipt boundary, including the read inside step-4 `prepare`.
   - Test the case where a turn completes between step 3 and step 4. Its unapplied mark must not be reserved project-only before it.
   - If the existing journal does not already hold it, `monitor.py` must skip `reserve_batch` for a prepared read that carries an unapplied receipt boundary.
   - If that guard needs a journal or scope edit, return to Refine.
5. **Grok binding scope.**
   - `grok_receipt_lookup` and `grok_mark` are bound to one `(source_id, checkout)` pair. `verify_receipt` receives only `(session, prompt, event_id)`.
   - Use one adapter or `ScopeState` per caller-supplied qualified context, and hold the others. Do not dispatch by trial.
   - Call `stage_grok_attempt` only when the caller supplies an attested pid and session.
   - A full receipt store (1 MiB) means the mark is held.
6. **Resolver side effects.**
   - Validate the locator under an approved root without following symlinks.
   - Require exactly one inventory match.
   - Call with `observed=False`, and never call `_record_live_exclusion`.
   - Release any `_grok_admissions` entry, as the `finally` in `prepare` does.
   - Derive the fact from the keyed stream plus the snapshot identity, with no raw path, session or turn.
   - Excluded or unknown locators return `UNKNOWN_LOCATOR` or `WRONG_SOURCE_TYPE` and leave no durable wake state. Use the mixed-root test to prove this.
7. **Watch and fallback work.**
   - `Scheduler.notify` refuses hints without the issuer capability.
   - Route watch, fallback and restart discoveries through `scheduler._admit(HookEvent(CHANGE, …), resolver)` using the same resolver, or catch up directly.
   - Never construct a `WakeHint`.
8. **Root loss.**
   - `WatchSet._check` deletes the root and `_lost` suppresses it. There is no API to add it back.
   - Revalidate, then recreate the `WatchSet` or use timed reconcile.
   - Group approvals by physical identity before building `WatchRoot` values.
   - Exceeding `_INVENTORY_MAX_ROOTS` holds the cycle rather than running it partially.
9. **Clock and lease.**
   - Take `now` for `take_due` from the scheduler's clock, because `finish` compares against `self._clock()`.
   - Catch-up must fit inside the TTL (default 5.0 s), or the work repeats idempotently.
   - Set `caught_up=True` only after `reserve_batch` commits at the read frontier.
   - Retries for owed claims stay in journal custody.
10. **Park test.** Assert scheduler state independently of the exit code. Parking an unknown session gives exit 0 with no admission.
11. **Test file.** `test_monitor_watches.py` is not in the supplied listing; confirm it is new. Confirm the locked pytest import mode resolves cross-module fixture imports, since the probe needed `PYTHONPATH`, without editing other test files.

## 3. Estimate and exclusions

**Estimate.** The CHANGE resolver, listener wiring and constant Stop refusal fit within the 1.25 h cycle/scheduler reserve. Everything else integrates existing seams. Keep the checkpoint at about 1.75 h. Return to Refine on any fourth file or a projected total over 4.0 h.

**Gates and exclusions.**
- Keep locked local Test, signed hosted Test, independent source review, protected merge and verified native Close.
- Keep the old `run_service` entry. The new entry stays dormant, with no installer or console-script change.
- Epic #2, C01, production cutover and #204 stay out of scope.
- #320's installer and #125's rehearsal are not dependencies.
- No new live model turn is needed.
- Receipt retention and scale remain a separate follow-up.

**Record note.** The recovery packet names planning baseline `46145d6c`, while this review's evidence snapshot is `dcee3efe`. Pin `dcee3efe` in the JIT record. This does not affect product readiness.
