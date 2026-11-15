[08:41:44]
SOURCE_134: HOLD. The code follows the accepted design. The blockers are missing proof and checks, not wrong logic I could find.

I had no shell or file tools in this session, so I reviewed only the diff and transcript you supplied. I could not read the repository at `9ebc2d25`, the base `f89169df`, or the CI logs.

**Unresolved blockers**

1. **No recheck after the base moved.** The JIT pins source `4cfb4181`, but the candidate base is now `f89169df`. Neighboring stories have landed on trunk since then, including #303 source qualification. The JIT requires rechecking the pinned scanner, adapter, Codex interpreter and typed-surface blobs when that happens, and the transcript has no such comparison. The diff also calls `matches_turn(..., require_root=...)` without adding that parameter, so it comes from the base, and that base was never rechecked.
2. **Version and type pins are not tested.**
   - No test pins `NativeSurface.CODEX_CLI_LINUX`, `ClientVersion.CODEX_0_167_0_ALPHA_3_2` or its normalization, or the existing `_SUPPORTED_CLIENTS[Provider.CODEX]` and `_CLIENT` pins.
   - The only wrong-version case is `0.167.0-alpha.3.3`, which differs after normalization too. It cannot show the match uses the raw string before normalization. A raw variant that normalizes to the same member must also be refused.
   - The diff never shows where `raw_client` is assigned, so I couldn't confirm it holds the raw string.
3. **The mixed Desktop source negative is missing.** The JIT lists it. Nothing tests the Desktop wrapper or Desktop rows in a Linux-classified file, or the Linux wrapper in a Desktop file.
4. **The shell token checks are copied, not reused.** `_linux_marker_command` repeats the 8-token, `shlex.join` and absolute-path checks instead of calling the existing ones. It also ignores `marker_root`, so it accepts any absolute project path where the Desktop path binds it. Either share the helper or enforce (assert plus test) that `linux_cli` only runs with `neutral_markers=True`.
5. **The trailing line feed on the receipt output isn't proven exact.**
   - The JIT requires the queued JSON followed by exactly one LF on Linux. The diff only adds the `{"type","text"}` key check, so whatever the Desktop parser allows also passes for Linux.
   - Tests are needed showing a body with no LF or two LFs is refused on Linux.
   - The same applies to a non-`queued` status or an extra field, which covers the JIT's "same tool result without an actual queued receipt" case. The `unforwarded` case only tests an empty body.
6. **The capture-fence path is untested for Linux.** The method that returns the first unsettled ordinal at a capture fence gained `_linux_cli` and a new host `ValueError`. No test runs it for Linux or for a wrong host. `test_linux_codex_fixed_capture_fence_...` only goes through `read_delta(_capture_limit=...)`.
7. **The hosted replay doesn't use the fixture's own digests.** The JIT says the hosted replay uses the sanitized fixture's derived digests and line boundaries. The test checks only a runtime prefix-hash comparison and `offset == len(archived)`. It never pins the fixture SHA `a63358dc…`, prefix SHA `b5d00e45…` or the 22-line boundary, so changes to the fixture would go unnoticed in CI.
8. **The origin-rejection test can pass without testing anything.** `test_linux_codex_rejects_unverified_origin` loops over `adapter.discover(root)`. If nothing is discovered, the test passes without asserting anything. That includes both wrong-host cases (Darwin/arm64 and the Desktop file on Linux). Each case needs to assert a locator plus the refusal diagnostic, or an explicit non-discovery.
9. **An unverified turn can stop blocking the cursor once a later turn verifies.**
   - `turn_start` always overwrites `linux_unsettled`, and so does `session_meta`. So an unverified turn, a stray counter between turns, or an invalid frame stops holding the cursor once a later verified turn ends.
   - That may be acceptable if a gap diagnostic is recorded, but the JIT says unverified context gives "no … cursor advance."
   - `test_linux_codex_unverified_mode_cannot_advance_cursor` only covers the case where the bad turn is the last turn. Add a test of a bad turn followed by a good turn and assert the intended result: either the gap diagnostic plus advance, or a hold.

**Needs confirmation, not blocking alone**
- The fixture's `session_meta` has no `format_version` field. Please confirm the existing check treats a missing field as qualified format 1, as the real capture did.
- The focused 265-test log ran with rootdir `.../aitm-303-source-qualification/trunk`, which doesn't tie it to `9ebc2d25`. The hosted run on the merge commit `a18b7608` is the evidence that counts.

**Checked and consistent with the JIT**
- **Classification:** the scanner requires `codex_exec`/`exec`/the exact version literal, `id == session_id` in canonical UUID form, and no fork fields. Host evidence stays separate.
- **Host matching:** `_qualified_host` matches surface and host both ways, and an unknown surface returns None and is refused.
- **Wrapper grammar:** it is a full match of the literal text with only JSON string escapes allowed. Nothing is evaluated, and extra statements or arguments are refused.
- **Turn context:** the sandbox and permission values must match exactly, `root_turn_id` is required, and `seen_context` is cleared on a gap or attempt error.
- **Receipt binding:**
  - The call is recognized only in the verified turn's segment.
  - The receipt is not carried to the next turn (`next_turn_receipt` is skipped).
  - It binds to the first distinct response after the output, ordinal 19 with 20836 tokens.
  - A counter with no response produces no usage.
- **Chronology:** fixture rows 12–19 match `verified-row-order.json` ordinals 7–14.
- **Cold restart:** cold restart, the round-trip cursor, single-read equality, idempotent replay and the fixed-prefix equality all hold in the tests.
- **Privacy:** IDs are zeroed and the checkout path is a placeholder. The only paths are container paths (`/pilot-state`, `/carrier`), with no credentials. Live cursor qualification stays false, and no coordinator or signed gate changed.
