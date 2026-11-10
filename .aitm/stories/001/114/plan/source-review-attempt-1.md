# #114 source review · attempt 1

Declared manual review in a separate Claude Code session. The provider reported `claude-opus-5-5` with high effort requested.

Exact packet SHA-256 `1909937ce8b36d939894988ed3aebd52d229a195889c4d81cb6701f3a676ddd3`.

## #114 M04 independent source review: FAIL, November 10, 2026

**Subject:** head `ee74b3f084798cf80404cba3877ba34e6aa55dcd`, tree `212a5bc2e6c40154e1016de1b06e50616802b4a0`, base `dc037364ba617b97244c93670d12358d0b5cbba7`. I judged only the material you pasted. I did not access GitHub and did not run anything.

### Blocking findings

**B1. A Codex restart from a saved cursor has no proof for new usage, and the Claude nested-agent split is unproven.**

- **Codex.** Every Codex read builds a new `CodexState(source._ledger, neutral_markers=True)`. The only memory it gets is the `ProviderCheckpoint` inside the cursor. The code comment in `read_codex` says the old reader relied on in-memory state to resume mid-turn. The monitor path drops that state (`_have_history`, `_exact_only`, `_thread_counts`) between turns. No test shows this works:
  - `test_desktop_retains_unfinished_native_turn_before_restart` resumes from `pending.cursor`, which is `None`. A held read returns the cursor it was given, and the first read was given `None`.
  - `test_codex_archive_counter_epoch_replays_once` resumes from a real saved cursor, but against an identical copy with no new usage.
  - So no test shows a saved cursor taken after a completed turn, followed by an appended turn, yielding exactly that turn's usage. The other outcomes (the running session total counted again, or the new turn dropped) are exactly the discard or double-count risk you asked about.
- **Claude nested agents.** The hold in `read_claude` only checks `routes.route.tool` and `routes.route.receipt` after the committed frames. Its comment says this covers "nested-tool overlap". The `_Route` source wasn't supplied, so I can't confirm that a pending parent `Agent` call stays pending while the child sidechain runs its own tool calls. If `_Route` holds only one pending tool, a child's tool result could clear it, and the cursor could cross mid-agent. The nested test reads once from `None` and never splits the stream.
- **Fix:** add a split-and-resume equivalence test. Use at least a two-turn Desktop rollout, the Claude nested fixture, the streamed fixture and the linked-receipt fixture. For every row boundary k:
  1. Read `rows[:k]` from the previous saved cursor, round-tripped through `_encode` and `_decode`, with the committed view.
  2. Append the remaining rows and read again.
  3. Assert the latest revision for each key matches a single full read, with no extra keys and no lost keys.
  4. Assert the returned cursor never lands inside an open turn, a pending receipt or a pending `Agent` call.

**B2. The additive CI test count doesn't add up.** The diff adds 18 test cases: 8 functions, plus a 10-case parametrized test. That matches both the delivery note ("16 + 2") and the provider count going from 220 to 238. The hosted subject says `tests: 589` and `baseline_tests: 570`, a difference of 19. If the diff is complete, the base should have 571 tests. Until the missing (or extra) test is explained, the control doesn't show the change was additive only. This is an evidence problem, not a source defect, and an explanation is enough to clear it if it holds up.

### What I could verify from the source
- **Scope:** the change is limited to the approved files. The `discover` and `read_delta` signatures match the JIT. Linux carriers stay disabled, and nothing activates in production.
- **Tuple refusal:**
  - `_origin_from` only sets the Codex surface when both `originator=Codex Desktop` and `source=vscode`.
  - `read_delta` refuses before decoding any usage: no surface, or a host other than Darwin/arm64, gives `UNSUPPORTED_FORMAT`, no observations and no cursor.
  - `_read` checks the surface again under `_monitor`, and there's a test that rewrites the origin after discovery.
  - The 10 parametrized cases cover each rejected tuple, including a Desktop originator with a source other than `vscode`.
- **Same-root isolation:** a Desktop file and a CLI file in one root admit only the Desktop surface.
- **Neutral markers:**
  - In neutral mode a declared `--project` path only has to be absolute and is then discarded.
  - Claude binds `--session-id` to the row's own `sessionId`.
  - The receipt shows up only as a keyed `receipt_ref`, with no project context, and the Codex sentinel checks pass.
- **Old code path unchanged:** with `neutral_markers=False`, both `_marker_command` changes and the Claude session gate behave exactly as before. The `discover` refactor only delegates. `_monitor` defaults to `False`.
- **Unfinished state, as far as the supplied source shows:**
  - An open Codex turn or `next_turn_receipt` holds the cursor.
  - A pending Claude Bash receipt or tool link holds it.
  - A partial Claude message crosses only if the cursor carries a matching keyed `RequestPrefix` (`retains_streamed_prefix`). Otherwise the cursor stays where it was.
  - The scanner's safe position stops before incomplete trailing input and before rows that are only held as boundaries.
  - Any held read drops its usage observations but keeps the old cursor, so usage is replayed later rather than lost. The hold itself discards nothing; the remaining double-count risk is cold resumption (B1).
- **Hosted run:** all six jobs succeeded on the exact head, and the signed tree and base match.

### Advisory items
1. **Exact version isn't checked per surface.** The adapter never compares `origin.client` and format against that surface's single approved pair. Correctness depends on `ClientVersion` and on `_origin_from` branches I couldn't see. Confirm only `0.167.0-alpha.3.2` and `2.1.318` can get through, or add an explicit surface → (version, format) table checked in `read_delta` and `_read`.
2. **Weak signals for "native Claude Code" and the host.** "Native Claude Code" is decided only by `"sessionId" in row`, so SDK or other launchers writing the same format would be admitted. The host check looks at the machine reading the file, not the one that wrote it, so a Linux transcript copied into an approved Mac root would pass.
3. **Holds are coarse and can stall.**
   - A hold returns the previous cursor, not a position just before the pending turn, so completed turns in the same read are also held back.
   - A session whose last action is `scope mark`, with no following request, never releases that read's usage.
   - Every normal in-progress hold also emits `BOUNDARY_UNVERIFIED`, which is the wrong label and could pollute coverage reasons later.
4. **Boundaries can repeat.** Boundaries are emitted from held reads and from rows beyond the cursor, so they come back on replay. Consumers must deduplicate by stream, ordinal and `receipt_ref`. Document this for M07.
5. **`cursor` has two meanings.** A refusal returns `None` even when a prior cursor exists, while a hold returns the input cursor. Document "`None` means keep the prior cursor", or return the input cursor in both cases.
6. **A project id leaks into "service" scope.** `discover` builds a `Registration` from `as_of().project_id` and sets `state_root=root.path`, and the tests use a project ledger (`PROJECT`) as both the pseudonym key and the view. Confirm eligibility can't admit a row through a project enrollment without checkout proof, and don't use the source root as the state root.
7. **Restart test doesn't isolate the cursor.** The Claude restart test passes the checkpoint in both the cursor and `LedgerView.checkpoints`. Add a case with an empty `checkpoints` field in the view to prove the prefix is rebuilt from the cursor alone.
8. **Missing Claude receipt sentinel check.** The startup and receipt tests never check that `declared-project-secret` and `marker-command-secret` are absent from the encoded output.
9. **Possible stall on finalized messages.** `retains_streamed_prefix` checks every provisional row among the committed frames, including messages finalized later in the same read. If the old checkpoint ever drops completed prefixes, the stream stalls. Add a single read from `None` covering partial plus final rows.
10. **Equality fields.** `_native_surface` and `_monitor` on `CandidateSource`, and `native_surface` on `_Origin`, take part in equality. Mark them `compare=False`, or confirm nothing compares these objects.

### Limits
- **Source I didn't see:** `ClientVersion`, the hidden `_origin_from` branches, `_Route`, `_UsageWalk`, `_explicit_session`, `_eligibility`, `scope_evidence`, how the old checkpoint prunes prefixes, the helpers in `test_codex`, `test_claude` and `test_scan`, and the CI workflow and control definitions.
- **Not checked:** I didn't verify the diff hash `e5a7…`, the subject hash `4af3…` or the tree contents. I took the hosted results as supplied.
- **Excluded:** Linux carriers (#134, #135) and authoritative scope routing belong to their own owners.

## Implementer disposition

B2 is resolved by the authenticated raw inventories. All 570 trusted-base cases remain. The candidate adds 18 M04 cases plus the existing candidate-only CLI smoke test. Replaying the delivered gate reproduced the signed result. B1 requires split-and-restart proof and any repairs it exposes.
