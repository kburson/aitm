[06:39:23]
**JIT_134: PASS**

I checked this against the excerpts and evidence pasted into the message. I did not read the files at the pinned blobs directly.

## The six prior blockers

1. **Package evidence: resolved.** The JIT now requires `package-provenance.json` as a gate before delivery. That record carries the registry value and the local tarball value as two separately labelled sha512 lines. They are equal, as expected. It ties the archive entry `package/vendor/aarch64-unknown-linux-musl/bin/codex` to binary `e7f91e14…`, with a byte-for-byte comparison set to true.

2. **Host binding: resolved.** The gate is now explicit in both directions:
   - `CODEX_CLI_LINUX` is admitted only on Linux/aarch64.
   - The Codex Desktop and Claude Code macOS surfaces are admitted only on Darwin/arm64.
   - Unknown surfaces refuse.
   - Wrong-host negatives are required in each direction, including a macOS Codex CLI source in a Linux-like file.
   - The old `surface is None or host != Darwin/arm64` check can no longer let a Linux-classified source through on Darwin.

3. **Typed surface and client pin: resolved.**
   - `NativeSurface.CODEX_CLI_LINUX` already exists, and `_SURFACE_PROVIDER` maps it to `CODEX`.
   - `normalize_client_version` is an exact `StrEnum` lookup, so `"0.167.0-alpha.3.2"` gives `CODEX_0_167_0_ALPHA_3_2`, which is the same value as `_SUPPORTED_CLIENTS[Provider.CODEX]` and `_CLIENT`.
   - The raw `cli_version` string is compared exactly before normalization.
   - The `monitor_types.py` and `types.py` blobs are pinned as unchanged, and no new type or client is added.

4. **Row order: resolved.** The JIT now pins the order from `verified-row-order.json`:
   - 7: `custom_tool_call`
   - 8: `token_usage_record` (this sets `response_seen`)
   - 9: `item_completed`
   - 10: `custom_tool_call_output`
   - 11: `token_count` (it can summarize the earlier request but cannot own it)
   - 12: `item_completed`
   - 13: `message`
   - 14: the following, distinct `token_usage_record`

   The JIT says neither side of the pairing is loosened, and returns to Refine if the order doesn't fit.

5. **Replay contract: resolved.**
   - Replay of the actual bytes runs locally, under private custody, before the scratch acquisition closes.
   - `e0c49028…` and `5b7b06b3…` are provenance only. They are never a fixture's expected hash and are never in CI.
   - The sanitized fixture gets its own digests and line boundaries, and those are what the hosted test checks.

   The word "Bind" in the Replay section is now covered by this precedence clause.

6. **Dropped negatives and conditions: resolved.**
   - A thread-mismatch negative independent of turn and session.
   - A non-`exec` source negative.
   - A `permission_profile` negative independent of `sandbox_policy`.
   - Product live Linux cursor qualification stays false until #129.
   - The staged tracked files and the hosted fixture and test inputs are checked for login cache, live credentials, raw provider IDs and user paths.

## Rechecked and unchanged

- The command still has 8 tokens and round-trips through `shlex.join`.
- The output is still the bounded header plus a queued receipt with two fields and one LF.
- The wrapper's literal form, with two LFs, and the reuse of the Desktop parser are unchanged.
- Scope, size M / 3.25 hours, #114, #129, Epic #2, C01 and the cutover exclusions are unchanged.

## Not blocking

- The JIT states the cursor condition in prose. You could name the flag `product_linux_adapter_cursor_proven` literally in the test assertion.
- The pasted code doesn't show whether the existing Codex walk ignores `item_completed` between the call and its output (row 9). The red/green run will show this, and the JIT already sends any mismatch back to Refine.
