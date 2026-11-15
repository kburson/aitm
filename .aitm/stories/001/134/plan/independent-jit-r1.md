[06:36:44]
**JIT_134: HOLD**

## Blockers

1. **A Refine condition is missing.** The package-evidence condition does not appear anywhere in the JIT. The JIT must label which sha512 line is the registry value and which is the local tarball. It must also tie binary `e7f91e14…` to the verified tarball. Add both as a gate before delivery.

2. **A Darwin arm64 host would admit the new surface.** The current gate in `adapter.read_delta` refuses only when `surface is None` or the host is not `("Darwin","arm64")`. So any surface that isn't None passes on Darwin arm64. Adding `CODEX_CLI_LINUX` while making "no changes to Darwin arm64" means a macOS Codex CLI rollout with the same tuple (`codex_exec`/`exec`/`0.167.0-alpha.3.2`) gets admitted on Darwin. The JIT should state the host binding in both directions:
   - `CODEX_CLI_LINUX` is admitted only on `("Linux","aarch64")`.
   - Desktop and Claude surfaces stay Darwin arm64 only.
   - Add a negative test: a Linux-classified source read on a Darwin arm64 host must refuse.

3. **The supplied evidence doesn't show the typed surface or the client pin.** The file list leaves out `monitor_types.py` and pins its blob `2ad81edf` as unchanged. That only works if `NativeSurface.CODEX_CLI_LINUX` already exists there. Separately, `codex.py` checks a single client (`frame.client_version is not _CLIENT`), and `scan.py` checks `_SUPPORTED_CLIENTS[provider]`. Nothing supplied shows that `0.167.0-alpha.3.2` maps to that existing pinned client. Either cite the existing enum member and client mapping at the pinned blobs, or add `monitor_types.py` and the version change to the scope and send it back to Refine. Also say whether classification compares the raw `cli_version` string exactly or the normalized value.

4. **The row order doesn't match the existing call/output pairing.** The existing output pairing throws the output away unless `call.response_seen` is true. That means a response has to land between the call and its output. The fixture boundary list ("start, mark, output, response") has no such response between mark and output. The JIT should pin the exact observed sequence and row kinds, for example `custom_tool_call` → emitting `token_usage_record` → `custom_tool_call_output` → following `token_usage_record`. If the capture doesn't match that order, it should return to Refine, not loosen the pairing.

5. **The replay contract contradicts itself.** It asks for "actual archived byte replay" and also says fixtures contain no raw IDs or paths. The `e0c49028…` and `5b7b06b3…` digests are over the raw bytes, so a sanitized fixture can't reproduce them. The JIT should state that:
   - Replay of the actual bytes is a local proof held under custody. It is never committed or run in hosted CI, and it runs before custody close.
   - The two raw readings are recorded as provenance.
   - The sanitized fixture has its own pinned digests and line boundaries, and those are what the hosted test checks.

6. **Refine negatives and conditions were dropped.** Add these to the JIT:
   - a thread-mismatch negative (Refine listed "turn, thread or session"; the JIT negatives list only session/turn/root);
   - a non-`exec` source-mode negative;
   - a `permission_profile` variant negative, kept separate from sandbox type;
   - an explicit statement that `product_linux_adapter_cursor_proven` stays false;
   - a check that there are no live credentials or raw IDs in CI as well as in fixtures.

## Checked and consistent

- **Wrapper input:** the recorded input matches the literal wrapper byte for byte, with exactly two LFs.
- **Command:** the 8 tokens round-trip through `shlex.join`.
- **Output:** the header matches the existing `_DESKTOP_OUTPUT`. The receipt has only two fields plus one LF.
- **Receipt binding:** binding to the first distinct response after output, in the same segment and turn, matches the existing `serial`/`same_turn` gating in `_Walk.response`.
- **Desktop-only paths:** the quota and completion paths stay Desktop-only.
- **Prefix readings:** both readings have matching digests and complete-line boundaries.
- **Deferred items:** #129, Epic #2, C01 and the cutover exclusions are carried over correctly.
