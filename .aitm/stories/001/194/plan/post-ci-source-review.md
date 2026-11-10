# #194 independent exact source review

Reviewer **Claude Opus 5.5, medium**. Off-platform packet verdict, November 10, 2026 at 22:40 UTC. Exact head `915a9a8ddb4a3d2ef82d490ee699dc7ba84471db`, tree `978272c4242736049ee6531b8afd9c8d3b329b9f`, base `49865245d175ce6c52913738f2c9a42c0abea632`. Signed hosted run 42915596021 attempt 1.

# Verdict: PASS for #194 M07c, exact head `915a9a8`, tree `978272c`

I found no source-backed blockers. As instructed, I used only the packet and no tools. I accepted the signed CI evidence and the stated diff SHA-256 as provided and didn't recompute either.

## Checks

1. **The legacy variant is byte-exact.** `shlex.join(a) + " " + shlex.join(b)` gives the same bytes as `shlex.join(a + b)`. With `legacy=True` the inserted text is `""`, so the output matches the old generator exactly. The golden test pins this with literal bytes and digest `272cbc70…045c`, using paths that contain spaces.

2. **Selection uses the receipt digest and never falls back.**
   - `_read_runtime` loops over (new, old) and stops at the first variant whose SHA-256 equals `console_sha256`. If neither matches it raises `unknown launcher`.
   - The selected bytes go through `_probe_runtime` to `_inspect_surface`, which compares the full file. No site regenerates the launcher after selection, and nothing retries the other variant.
   - The tests show:
     - If the launcher is swapped to the opposite variant, the early hash check refuses it and `_probe_runtime` is never reached.
     - If the receipt digest is rewritten to match a mutated launcher, the read still refuses it as unknown.
   - `_prepare` pins the new launcher and passes those same bytes to the probe.

3. **The interpreter digest is checked before the interpreter runs.** The read path checks, in order:
   - the receipt and its schema
   - the layout
   - custody of the retained wheel
   - the executable hash
   - the interpreter hash

   Only then does it call `_interpreter(base)`, derive the site path and select the variant. The test patches `_interpreter` to fail if called and confirms that a bad interpreter digest is refused first.

4. **The candidate forwarding is correct.**
   - The launcher uses the unquoted `${CODEX_THREAD_ID+"CODEX_THREAD_ID=$CODEX_THREAD_ID"}` form, which sits outside both `shlex.join` calls.
   - When the variable is unset, the expansion disappears completely, with no empty argument left behind.
   - When it is set, it becomes exactly one quoted field. Because the operator is `+` and not `:+`, a set-but-empty value is forwarded as `CODEX_THREAD_ID=`.
   - The expanded text is never re-parsed, so `$()`, backticks, quotes and newlines stay as plain data.
   - A value with a leading hyphen is safe because the argument itself starts with `CODEX_THREAD_ID=`.
   - The fixture covers matching, wrong, unset, empty and hostile values. It asserts that presence and value come through byte for byte, that an unrelated variable is dropped, and that no side-effect file is created.

5. **No unrelated environment is forwarded.** `env -i` and the fixed entries are unchanged. Subprocess environments in the tests are built explicitly. The fake LaunchControl children now use `install._ENVIRONMENT`, which matches how launchd starts services and keeps the invoking shell's `CODEX_THREAD_ID` from leaking in.

6. **Reinstalling the same wheel is idempotent.** The old runtime is built through the real `service install` path, with only the generator swapped, inside `monkeypatch.context()`. The test then restores the default generator, and a second install returns `already-active`. The receipt and launcher bytes are unchanged.

7. **Rollback and the real upgrade both work.**
   - The two wheel digests differ and the wheel filenames are identical, so both wheels are version 0.1.0.
   - A failed upgrade returns `activation-rolled-back`. The old program stays loaded and its runtime still passes `_read_runtime` with the original receipt bytes.
   - A successful upgrade returns `upgraded` and installs a different executable.

8. **The installed commands are tested and isolated from the account's real root.**
   - The old launcher refuses even the correct thread. That reproduces the original #103 defect.
   - The new launcher refuses no candidate, an empty candidate and a wrong one, and writes no inbox file in those cases.
   - With the correct thread it returns exact `queued` bytes and creates the inbox file.
   - `monitor scope mark --request '<path with space>' --json` queues against a real `ScopeInboxReader` witness. The test checks that the envelope equals the proposal, `command_status` is `None`, and no `scope-v1.json` is written.
   - The wheel fixture now redirects `monitor_registry._control_root` as well. The envelope being found in the temporary inbox is positive evidence that the write stayed isolated.

9. **No source activation or production operations.** The diff has no workflow, migration, cutover or production install changes.

10. **The gates pass.**
    - All 877 tests pass, which is 867 plus the 10 new cases.
    - Product coverage is 9,649/10,549. The baseline had 11 fewer statements and 11 fewer covered lines, so every new statement is covered.
    - Helper coverage is unchanged at 778/821.
    - All six hosted jobs pass with signed verification, and the tree matches.

## Non-blocking notes for the record

- **Baseline count mismatch.** The raw replay reports `baseline_tests: 866`, but the pickup recorded 867. Since 877 equals 867 + 10, the replay's baseline figure looks like it counts differently. Reconcile it in the delivery evidence.
- **`_prepare` still runs the interpreter first.** On the same-wheel install path, `_prepare` still runs `_interpreter(interpreter)` before reading the existing receipt. This is the operator-supplied path that predates this change and is outside the read-path contract. Note it if #118 tightens custody.
- **The environment check uses one sentinel variable.** The fixture asserts that a single unrelated variable is dropped rather than comparing the whole environment. That is acceptable because `env -i` guarantees it structurally, and a full comparison could be flaky on Darwin.
- **No launchctl check after the installed commands.** Service non-activation after the installed CLI subprocesses is inferred from their command semantics, not asserted. Those subprocesses are outside the fake's monkeypatch, so the fake could not see a real launchctl call anyway.
- **Darwin `/bin/sh` only.** The shell fixture ran only under Darwin's `/bin/sh`, so dash is still unproven until the separate Linux carrier and host gates run. This risk was accepted at pickup.
