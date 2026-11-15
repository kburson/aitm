[09:37:04]
SOURCE_134: HOLD. One blocker remains: the invalid-frame case from R1 item 9. Items 1–8 are resolved.

I had no shell or file tools in this session, so I reviewed only the packet you supplied. I could not read the repository or run anything.

## Unresolved blocker

**Item 9, invalid-frame case.** R1 named three ways a later verified turn could carry the cursor past bad data: an unverified turn, a stray counter, or an invalid frame. The packet fixes the first two but not the invalid frame.

- **Unverified turn: fixed.** A mismatched turn context calls `retain_linux_gap`, which records a gap that stays set. `test_linux_codex_a_later_valid_turn_does_not_skip_an_unverified_active_turn` proves the hold with the full fixture.
- **Stray counter: fixed in the code.** A counter seen outside a verified context in `step` calls `retain_linux_gap`. `test_linux_codex_cold_cursor_waits_for_verified_turn` only tests the counter as the last row, but the gap stays set, so a later turn can't clear it.
- **Invalid frame: not fixed.** The invalid branch near `codex.py:1607` only sets `linux_unsettled = min(invalid)` and resets `self.context = _Context(ambiguous=True)`, which leaves `context.turn` empty. It never calls `retain_linux_gap`.
  - The next `turn_start` sees no turn, so it doesn't record a gap. It then sets `linux_unsettled = frame.ordinal`, overwriting the invalid ordinal.
  - When that turn verifies, `linux_unsettled` is cleared and the cursor moves past the invalid row.
  - This can't happen if that branch only runs after the last frame. I can't see its surrounding code, so that is not established.

**To resolve it, add one test and, if needed, one line of code:**
- **Test:** use the full fixture and insert an invalid line after the turn `…13401` completes and before the turn `…13402` starts. Assert the intended result: either a hold (`cursor is None`, no observation at ordinal 29), or a deliberate advance with the existing malformed-row diagnostic.
- **Code:** if the intended result is a hold, call `retain_linux_gap` on post-cutoff invalid frames in that branch, keeping the existing `pre_cutoff` exemption.

## R1 items 1–8: resolved

1. **Base recheck:** all six pinned blobs are identical at `4cfb4181` and `75d4bc06`. The diff's index lines start from those exact blobs. `require_root` comes from the unchanged `codex.py` blob, and the 1333 tests passing confirms it exists. #319 changed only the workflow; the gate, lock, observer, policy and verifier are byte-identical.
2. **Type and version pins:** the surface type, the client version, its normalization, `_CLIENT is _SUPPORTED_CLIENTS[CODEX]`, and the implicit format 1 are all pinned. `raw_client` comes straight from `metadata.get("cli_version")` (`scan.py:690`). The raw version check is literal and runs before normalization. The alias test refuses a variant that normalizes to the same member.
3. **Mixed Desktop source:** `test_codex_wrapper_does_not_cross_native_surfaces` covers both directions: the Desktop wrapper in a Linux file, and the Linux wrapper in a Desktop file. Neither gets a receipt, while the cursor still advances.
4. **Shell argument checks:** both carriers now share `_canonical_scope_arguments`. `test_linux_codex_scope_command_can_bind_the_project` shows the project root is enforced when one is given; it failed on the pre-fix (red) run and passes now.
5. **Exact queued output:** `test_linux_codex_requires_the_exact_queued_body` refuses a missing LF, an extra LF, a non-`queued` status and an extra field. The existing `unforwarded` case still covers an empty body.
6. **Capture-fence path:** `_capture_gap_start` returns 23 on Linux, which matches where turn `…13402` starts. With the Linux-classified file on Darwin it raises `ValueError`.
7. **Fixture digests:** the test pins the fixture SHA `a63358dc…`, the prefix SHA `b5d00e45…`, the 22-line boundary and the trailing LF. The raw capture hashes `e0c49028`/`5b7b06b3` appear nowhere in the test.
8. **Origin-rejection test:** `(locator,) = adapter.discover(root)` requires exactly one discovered file, so the test can no longer pass with nothing found. Each case must produce exactly `[UNSUPPORTED_FORMAT]` with no cursor, boundary or observation. Both wrong-host directions are covered, plus x86_64, the wrong `arm64` machine string, other originators and sources, the wrong raw version, format 2 and a forked session.

## Weak spots in the tests (not blocking)

- **The alias test never checks its own setup.** Add an assertion that, with the patched normalizer, the provider checkpoint's `client_version is pin`. Otherwise the test would still pass if the scanner never called the patched function.
- **`test_linux_codex_withholds_unpaired_marker` only checks that no receipt appears.** It would also pass if the whole file were refused. Assert that no `UNSUPPORTED_FORMAT` diagnostic was emitted, or that the clean turn's observation at ordinal 29 survives.
- **A gap holds the file permanently.** Once a gap is recorded, that file's cursor never advances again. That matches the JIT and `qualifies_live_cursor: false`; #129 should know about it.

## Checked and consistent

- **Hosted run:** passed on head `f3848b9d`, tested merge `fe4aee7f`. Its tree `9ebe8f13` matches the reviewed tree and the replay's `source_tree`, and the locked local run passed 1333 tests.
- **Red/green:** the two new tests fail on the pre-fix run and pass after it.
- **Private replay:** the archived and reopened prefixes match, the marked response is 20836 tokens, exactly one ordinary observation after restart, zero replayed, and the keyed checkpoint is stable.
- **Package provenance:** the npm registry integrity equals the recomputed archive integrity, the tar member is the aarch64 musl binary, and the extracted binary was compared byte-for-byte.
- **Scope:** five files changed, matching the JIT. No signed gate changed, and nothing touches #129, Epic #2, C01 or cutover.
