[06:22:37]
**REFINE_134: HOLD**

The design shape, the boundaries and the 3.25h / Size M estimate hold up. The evidence does not yet support the grammar and gate work the estimate rests on. Each blocker below is a packet correction or a narrow recapture, not a redesign.

## Blockers

1. **The recorded command may not be the production command.** The proof sent the Ledger codec and enqueue path through a disposable shell wrapper. The evidence never says what command string the durable `custom_tool_call` actually recorded.
   - The existing grammar only accepts one form: 8 parts, `aitm-usage --project <root> scope mark --marker <abs> --json`, and `cmd == shlex.join(parts)`.
   - If the rollout recorded the wrapper's own command, the sanitized fixture cannot meet the JIT check that "marker input verified against an authentic queued receipt". The 1.0h grammar item would then be written against something that doesn't occur in production.
   - **Fix:** state the exact command form that was recorded. Also state whether the receipt body came from the production JSON writer or from the wrapper. If either differs from production, recapture using a PATH stand-in named `aitm-usage` that takes the exact production command line, or reduce the transport claim to match.
2. **The sandbox launch mode is not part of the gated tuple.** The packet says the proof is limited to the externally contained mode. But the "exact origin/surface gate" only names originator, launch source, version and architecture.
   - **Fix:** add the sandbox setting recorded in the rollout to the tuple, and make natively sandboxed sessions fail closed. Alternatively, explain with evidence why that mode cannot change the transport.
3. **The chronology is asserted, not shown.** The status record has one prefix hash, `e0c49028…`.
   - **Fix:** record two independent values:
     - the hash taken at archive time, before the resume, with its capture time;
     - the hash of the first 255,372 bytes of the rollout after the resume.
   - Also state that byte 255,372 falls on a complete-line boundary. Checkpoint replay depends on the suffix `dd453c37…` starting at a line boundary.
4. **The package check has nothing to compare against.** Only a local binary hash (`e7f91e14…`) is supplied. "Official, digest-verified" needs the reference value, such as the registry integrity hash or the release manifest, and the result of the comparison. Note too that the pinned version is an alpha pre-release, and the tuple gate should name it exactly.
5. **The packet contradicts itself.** Its Disposition section still says "Evidence collection is blocked pending access…" and design, estimate, plan and JIT acceptance are still "pending". Replace these with the captured evidence and this proposal before acceptance.

## Validated (no change needed)

- **Prerequisite and ranking:** #114 is closed and is the only prerequisite, Rank 330, and #134 blocks #129.
- **Live transport:**
  - Native account login, inside containment with zero added capabilities, a read-only image and scratch-only mounts.
  - Kernel identity backs up `codex_exec` / `exec` / `0.167.0-alpha.3.2`.
  - Ledger access and scope checks ran unchanged.
- **Request link rule:** match on `call_id`, then pick the first post-output usage record with a new response ID and the same turn, thread and session. This is well defined. Two new response identities and a prefix containing neither are consistent with it.
- **Separation is kept:**
  - `product_linux_adapter_cursor_proven: false` stays separate.
  - x86-64 and both signed native targets stay with #129, and product admission stays closed.
  - Legacy Desktop and Claude routes are preserved.
  - Epic #2, C01 and production cutover are excluded.
  - The hold-and-return trigger is stated: a different request-identity contract, or a detached output being routed silently.
- **Estimate:** 0.75 + 1.0 + 1.0 + 0.50 = 3.25h, all building on the existing guarded scanner and parser. That is credible for Size M once blocker 1 is resolved.

## Conditions to carry into JIT (not blockers)

- **The ordering rule comes from one turn.** JIT should test, all failing closed:
  - no new-response usage record before the turn ends;
  - a mismatched turn, thread or session;
  - a repeated or detached output.
- **Negatives:** x86-64, other versions, other originators or launch sources, and natively sandboxed sessions must all be refused. The adapter stays disabled by default. The Desktop parser's single trailing line-feed allowance and its two-block output shape must not get looser.
- **Product cursor wording:** fixture replay proves the code path deterministically, but it does not flip the product cursor claim. That stays with #129.
- **Production CLI on Linux:** the Python pricing CLI import failure means the full production CLI was not run in that container. Pass it to #129 as an open host-qualification risk.
- **Credential custody:** record that the scratch login credentials were destroyed or revoked, and that the raw usage, marker and provider IDs stay out of the sanitized fixture.
