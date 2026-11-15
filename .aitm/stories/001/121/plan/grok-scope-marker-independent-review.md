[16:59:09]
AMEND_121_GROK_MARKER: PASS

This passes as a proposed upstream ownership decision only. It does not pass, waive or pre-clear #121 JIT, and M11f still needs independent Refine and exact JIT.

## Verified against literal source

| Claim | Evidence |
|---|---|
| Missing owner-scope-to-prompt receipt | `MarkRequest` holds `{command_id, grant_id, scope, destination_binding}`. `_ScopeBody` holds `{request, generation, format}`. `ScopeEnvelope` holds `{body, seal}`. None of them has a Grok session, prompt or hook event field. |
| `monitor_scope.py:2894` and `:2968` | Both excerpts read `iter_verified` and accept only `type(request) is DispositionRequest` matching project, hold and release. They make no Grok join. This settles the prior H1 caveat about unshown source. |
| Pilot is not authority | The HMAC body is `{event, session, prompt, nonce, started, pid}`, with no command, grant or digest. Its receipt namespace is `isolated-grok-prompt-v1`. `isolated_grok_pilot.py:372` is the only `GrokAdapter(` construction. The amendment correctly refuses to promote it. |
| Two-stage native join | The pilot hook seals only session and prompt. `_completed_carrier` later requires exactly one `hook_execution` before exactly one `turn_completed`, a matching `prompt_id`, single-run `success`, `end_turn` and time ordering, and only then takes `hook.event_id` from the observed row. The `verify_receipt(session_id, prompt, hook.event_id)` seam is called from `verified_boundary` with the observed hook. `start_hook` already enforces `OVERLAP_UNVERIFIED` and single-run success. So "the hook cannot invent the later event ID, the reader takes it from the observed row" matches the native shape. |
| Exact prior repair | It repairs H1 with a narrow upstream producer and verifier leaf. It correctly drops my prior option 2's "registry-backed `WakeResolver` for park", because the park premise was wrong (next row). |
| PARK bypasses `WakeResolver` | `_admit` checks `WakeKind.PARK`, then `return self.park(request.session)` before `resolver.resolve`. `serve_once` checks socket identity, mode `0600` and `_peer_uid == geteuid` before `_admit`. `park` validates the ref and walks only `self._records` by `facts.session`. |
| CHANGE and STOP ownership at #121 | `_admit` rejects any non-`RESOLVED` result or invalid facts. It also rejects a Stop unless `current_stop` is set and `turn` is not `None`. A Stop that lacks verified current-turn proof therefore fails closed in shipped code, which supports "no new #320 or M10b edge". |
| Qualifier and scope control | The amendment requires: a qualified `UserPromptSubmit`, the owned producer context, the source, project and checkout binding, one-use, and binding to command ID, digest and grant generation. Changed, revoked, stale or competing attempts are held. There is no cross-prompt replay. Retention is allowlisted keyed evidence only. |
| Narrowest dependency graph | M11f depends on #182 and #329, both closed. #115 and #304 are closed, and #117 is reached transitively through #329. #330 and #331 remain #121's own edges, which is correct because M11f does not use journal delivery. Rank 249.75 sits between 249.5 and 250. 3.75 h is at or under 4.0, size M. All existing edges remain. |
| Coverage and gates | Qualified marked and project-only hookless coverage are preserved. The full gate chain is restated, nothing is waived, and there is no downgrade. Epic #2, C01, cutover and #204 stay excluded. |
| Constraints | The amendment does not assume the publisher knows the event ID. It prefers retained evidence and offline fixtures. Paid live turns return to the authorization boundary. |

## Conditions carried to M11f Refine and JIT (not holds)

1. **Hook entry file.** The supplied product hook `main()` parses a `HookEvent` frame, not Grok's raw `hookEventName/sessionId/promptId` row. Refine must name the exact module that receives the Grok row before `sources/hooks.py` is accepted as owner.
2. **Native selection mechanism.** Refine must state concretely how the publisher identifies the single pending owner proposal at hook time. Any ambiguity holds, as the amendment already requires.
3. **Estimate.** The 3.75 h figure needs exact Refine and JIT validation against the three-file map, or against the bounded edit map the amendment names as a fallback.

## Conditions carried to #121 JIT recovery

1. **Resolver bound.** Confirm that the concrete CHANGE and Stop resolver, and the listener that `_WakeListener.resolver` requires, fit `monitor.py`, `service.py` and the test file within 3.5 h.
2. **Inventory binding.** The prior `inventory=` binding condition on `_grok_capture_evidence` still applies.
