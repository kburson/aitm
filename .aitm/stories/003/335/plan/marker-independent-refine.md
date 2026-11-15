[17:03:47]
REFINE_335: PASS

The three-file design can meet the accepted scope at 3.75 h, within the 4.0 h limit, with no change to core, install or gates. This passes Refine only. It does not pre-clear JIT, and the conditions below are binding on JIT and Develop.

## Verified against the supplied literal trunk `4ba4354f`

| Area | Finding |
|---|---|
| Entry shape | `sources/hooks.py:main()` reads a `_parse_frame` `HookEvent`, not Grok's raw `{hookEventName, sessionId, promptId, workspaceRoot}` row. So a separate module is required. `sources/` is already a package, since `hooks.py` runs as `__main__`. `uv_build` ships everything under `src/aitm_usage`, so `python -m aitm_usage.sources.grok_scope_hook` needs no `[project.scripts]` or config change. |
| Hook-side capability | `ControlInbox.enqueue_scope` already runs as a non-writer producer. It takes `publication()`, `open_grant`, `require_witness` and `seal_request`. So the hook side can take the publication lock, re-verify the grant and seal, and recheck the witness without new authority. |
| Envelope re-verification without the lock | `verify_again` shows the read-only pattern: `_read_private(dir, _filename(command_id))`, then `seal_request(current, request) == envelope` under `open_grant`, then `require_witness`. The lookup can reuse this pattern without `publication()`. |
| Process identity | `install._process_identity` gives `(pid, started, executable)`, checks UID and refuses zombies. `_BSDProcessInfo.parent_pid` and `_libproc()` are importable as they are. Ancestry is not in `install.py`. The pilot's `_under_process` is qualification-only. |
| Adapter callback | `GrokAdapter(origin_cb, verify_receipt)`. `start_hook` requires `user_prompt_submit`, refuses overlap and records the hook only on a single successful run. `verified_boundary` requires `hook.time <= update.time` and calls `verify_receipt(origin.session_id, prompt, hook.event_id)`. It then requires `validate_source_ref(receipt)`, and binds `event_id` into `boundary_ref` (`grok-marker-boundary`). |
| Core join | `_verified_boundary` requires `boundary.receipt_ref == command.receipt_ref` and the first unique receipt-linked target in the batch, then `_development_proof` for Mark. |
| Scope-receipt domain | **It is not enforced for Grok.** The `pseudonymize("scope-receipt", command_id)` check is skipped when `surface is GROK_BUILD_MACOS`. |
| Product construction | The only `GrokAdapter(` is `isolated_grok_pilot.py:372`. The product wiring stays with the qualified runtime integration (#121), consistent with the leaf being dormant. |

## Conditions carried to JIT and Develop

1. **Receipt domain by construction.** The lookup must return exactly `evidence.pseudonymize("scope-receipt", str(command_id))`. JIT must read the `MarkRequest`→`Mark` conversion and confirm `Mark.receipt_ref` equals that value. Do not edit the Grok exemption line, which is out of the map and would be a gate change. Test that a pilot-domain ref (`isolated-grok-prompt-v1`) for the same command fails the core equality check.
2. **Event-ID binding is non-durable by design.** The lookup is pure and keyed only on `(session, prompt)` plus the persisted receipt. The observed `event_id` is bound in two ways:
   - by the adapter's ordered single-hook, `end_turn` rule;
   - by `_verified_boundary`'s first-unique-ordinal rule.

   Tests must show both of these, through the real `GrokAdapter` and `verify_boundary` (`monitor_scope.py`):
   - a second `hook_execution` for the same prompt is refused;
   - a substituted `event_id` row is refused.

   The lookup must take no lock and do no writes.
3. **Ancestry.** The ancestry walk lives in `grok_scope_hook.py`. It uses `_libproc()` and `_BSDProcessInfo` with a before/after incarnation double read at each hop, mirroring `_process_identity`. It must terminate at the staged `(pid, started, executable)` and fail closed at PID 1 or after a bounded depth. `install.py` stays unchanged.
4. **Storage namespace.** Attempts and receipts must not be files that `ScopeInboxReader.iter_verified` enumerates. Otherwise they risk failing every disposition route. Before Develop, JIT must name the private directory and its creator. The creator is the staging writer under lease, using existing private-write helpers with no edit to `monitor_control.py` or `scopes.py`. If neither is possible, return to Refine.
5. **Checkout match.** Compare `workspaceRoot` to the staged checkout by pinned directory identity (the `_directory` or stat identity), not by persisted raw path. The durable receipt holds only pseudonymized session, prompt and command refs. Confirm the hook can obtain `source_evidence` for pseudonymization without the writer lease. If it cannot, store only a keyed digest computed at staging.
6. **Selector is not authority.** The env selector only picks the staged attempt. Authority comes from the staged record plus ancestry plus the sealed envelope. Forged-descendant tests must cover:
   - a model-spawned tool calling the module with a different prompt;
   - a replay after the first bind;
   - a missing or mismatched `GROK_HOOK_EVENT` or `GROK_SESSION_ID`.
7. **File map.** The #329 fixtures must be imported as they are. Any `conftest.py` or fixture edit is a fourth file and returns to Refine.
8. **Platform and coverage.** Physical libproc custody tests are gated to macOS. The deterministic identity and ancestry control branches must run everywhere, so that branch coverage of the new module holds on the signed hosted Test.

## Estimate

3.75 h is accepted, with about 0.25 h of headroom. Checkpoint at about 1.9 h: show a valid attempt, a conflicting same-session attempt and a wrong-owner attempt, all proven end to end through the actual `GrokAdapter` callback and `verify_boundary`. If condition 1 or 4 needs a fourth product file, or the projection exceeds 4.0 h, return to Refine.

No missing authorities. Mark application stays with #121, and project-only hookless and socket/wake behavior stay unchanged. Exclusions remain: no live provider run, installation, Epic #2, C01, cutover or #204.
