# #194 independent pickup review, round 1

Reviewer **Claude Opus 5.5, high**. Off-platform exact pickup on November 10, 2026.

# HOLD: #194 M07c pickup review

I reviewed only the packet and used no tools. I did not check the stated SHA-256 values.

The design is sound: selecting the variant from the receipt, the quoting, the unset/empty handling and the scope are all right. Three gaps in the pickup could force a scope decision during Develop or weaken verification. Each can be fixed by editing the text, with no new estimate.

## Blockers

1. **The installed upgrade fixture can't be built as written.**
   - **No old starting state.** Every new preparation pins the new launcher. The pickup doesn't say how the test gets a genuine old exact receipt. Recommend preparing through the normal path with only the generator swapped to the retained old one in the test. Don't hand-write the receipt.
   - **No second wheel digest.** `_wheel(parent, …)` embeds `parent/'control'` and the same package bytes. Two builds from one parent likely give the same digest, so `_prepare` would reuse the old runtime instead of upgrading. That conflicts with "fixture changes only its test-only root redirection." State how the second approved digest is made (an existing variant flag, a separate parent, or similar) and confirm the installer accepts another 0.1.0 wheel with a different digest.
2. **Verification order is a security regression risk.** To build both launcher variants, `_read_runtime` needs `_site(environment, _interpreter(base))`, and `_interpreter(base)` runs the interpreter. Today `interpreter_sha256` is checked before anything runs `base`. When `interpreter=None`, the new code could run an interpreter that hasn't been checked. Require this order:
   - check the private receipt and schema;
   - check `interpreter_sha256`;
   - only then compute the version and site;
   - select the variant;
   - compare the whole launcher against the selected bytes.
3. **One pinning site isn't covered.** The accepted split says the generated launcher bytes are pinned "during both wheel verification and installation." The pickup only covers launcher generation and `_read_runtime`/`_prepare`. List every place that uses `_launcher` or the console digest, including any wheel verification or `_probe_runtime` comparison. Each must use the receipt-selected variant, or old installs will fail verification there.

## Checked and adequate

- **Receipt-bound selection:** pick the variant whose digest equals the receipt, then require an exact byte match. Never fall back to the other variant, and reject an unknown hash even if it matches the mutated file. Correct, and the wire schema and `console_sha256` field are unchanged.
- **Quoting:** the unquoted `${CODEX_THREAD_ID+"CODEX_THREAD_ID=$CODEX_THREAD_ID"}` gives zero fields when unset and exactly one field when set. That field is not split or globbed, so newlines, `$()`, backticks and quotes stay data.
  - A leading hyphen is harmless because the argument starts with `CODEX_THREAD_ID=`.
  - Putting it before the Python path is right for `env -i`.
- **Unset vs empty:** the launcher keeps them distinct and the CLI refuses both. The CLI check against the authenticated marker remains the only authorization.
- **Scope:** limited to `install.py`, its tests and the installed fixture. No CLI changes, no production install, migration or cutover. #118 waits until #194 closes, and M11/M16 keep coordination.

## Non-blocking amendments (recommended)

- Pin the old launcher with a literal golden byte string and digest for fixed paths, so the test doesn't just compare the retained function with itself. Freeze `_ENVIRONMENT` and `_RUN_CONSOLE` for the old variant.
- Same wheel prepared again over an old receipt: assert the launcher and receipt bytes are unchanged (no rewrite in place).
- Failed or rolled-back upgrade: assert the old runtime still verifies under its old receipt.
- Codex runs with `CODEX_THREAD_ID` already set in its environment. Every shell, installed and existing test must build its subprocess environment explicitly, or the unset case and the clean-environment assertions will behave differently locally than in hosted CI.
- In the probe, check key-absent and key-present-with-empty-value separately. Add an unrelated test variable and assert it doesn't get through.
- Use a `--request` file path containing a space so `"$@"` is exercised.
- Hosted Linux `/bin/sh` (likely dash) and macOS `/bin/sh` (bash in POSIX mode) both need to pass the shell fixture. Say so explicitly.

## Estimate

- **1.75 h:** believable but at the top of the split's 1.25–1.75 range, and the allocations sum exactly to 1.75. That holds only if blocker 1 is solved with existing fixture support; if a new wheel variant is needed, the 0.35 reserve is the likely cost.
- **0.9 h checkpoint:** the arithmetic works (0.45 + about 0.25 + about 0.2). But it gates the lower-risk pieces and leaves out the riskiest one. Add: "a genuine old-receipt installed runtime and a distinct approved wheel digest are buildable in the isolated root."
- The four-hour reopen cap is appropriate.

**Resolution:** fix blockers 1–3 in the pickup, re-hash it, and the verdict becomes PASS without a new estimate. The fresh locked baseline remains a separate prerequisite before Develop.
