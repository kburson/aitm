[06:27:03]
**REFINE_134: PASS**

All five earlier blockers are now closed by the evidence you supplied:

1. **Recorded command:** The durable input holds the exact eight-token production command, which `shlex.join` reproduces as-is. The `aitm-usage` PATH stand-in used the real Ledger/session validator, command codec and `enqueue_command`. It does not claim to validate the production CLI. Its receipt is the two-field `{"command_id","status":"queued"}\n`, forwarded into the native tool result in two blocks. The run that did not forward the receipt is kept as a negative.
2. **Sandbox mode:** The rollout records `sandbox_policy.type=danger-full-access` and `permission_profile.type=disabled`, and both are now part of the tuple. Natively sandboxed sessions are refused. The full tuple is exact: `0.167.0-alpha.3.2`, aarch64, `codex_exec`, `exec`, and the contained mode.
3. **Chronology:** The archive was made at 12:15:49.885Z, before the capture at 12:16:25.345Z. Its hash `e0c49028…` matches the post-resume prefix hash, and the boundary falls on a complete line. A second check also passed. At 12:25:16Z the 267,207-byte file hashed to `5b7b06b3…`. After the later benign resumed turn, the same prefix gave the same hash, again on a line boundary, with exactly 1 new native usage record.
4. **Package check:** The sha512 integrity value for `@openai/codex@0.167.0-alpha.3.2-linux-arm64` matches the reference, and the gate names the exact alpha version.
5. **Contradictory packet:** The new authenticated sample replaces the old "blocked pending access" disposition. Design, estimate (M / 3.25h) and JIT scope are now stated.

**Conditions to carry into JIT (not blockers):**
- **Grammar:** Pin the exact recorded script: one `tools.exec_command` call with `cmd` and `max_output_tokens`, followed by `text(result.output)`. Reject scripts with extra statements or different arguments. Keep Desktop's two-block output shape and its single trailing line-feed allowance unchanged.
- **Request link and negatives:** All of these must fail closed:
  - no follow-on usage record with a new response ID;
  - a different turn, thread or session;
  - a repeated or detached output;
  - a receipt that was not forwarded;
  - any neighbouring tuple (x86-64, other versions, other originators or launch sources, native sandbox).
- **Package evidence:** Label which sha512 line is the registry value and which is the local tarball. Tie the binary hash `e7f91e14…` to the verified tarball.
- **Product cursor and #129:** `product_linux_adapter_cursor_proven` stays false. The production CLI import failure on the build image goes to #129 as an open host-qualification risk. The accepted #129 target qualifications are unchanged.
- **Credential custody:** At the custody boundary, record that the scratch provider credential was retired. Confirm that no live credentials or raw production IDs are in the fixture or CI.
- **Exclusions:** Epic #2, C01 and production cutover stay out of scope.
