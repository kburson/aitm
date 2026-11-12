# #210 native completion qualification JIT

**Goal** Read a fresh disposition command's same-turn completion and prove its native accounting on a fixed Desktop transcript. Use this evidence to qualify the carrier before #210 can implement any effective settlement.

**Base** Literal trunk `15b3076848e726c3fed62c2725621106a04246ef`. Scope follows the independently accepted completion-receipt proposal and its retained technical findings. The existing test-impact graph change leaves the monitor and hosted gates byte-identical. The owner directed Full-Auto continuation and removal of the second approval stop.

**Bound** 1.60 agent-hours for this read-only qualification slice, with a focused checkpoint at 0.75. #210's 4-hour scope bound applies to any independently accepted settlement work. Estimate stays a planning value until the applicable #210 JIT scope is accepted.

## Exact inputs

- [Scope proposal and independent review](2026-11-11-210-completion-receipt-proposal-review.md)
- [Producer evidence and corrected authority](2026-11-11-210-completion-receipt-followup.md)
- [Public reader probe](accounted-command-evidence.json)

The probe found an existing `REQUEST` receipt after the serial command output and its accounted response. Completion preserves that request link. A following turn may expose another receipt of kind `TURN`. Both observations are distinct. Ordinary pending-marker coverage and cursor semantics continue to apply. The native Desktop transport probe verified `custom_tool_call_output` using the installed pre-monitor launcher, which could not queue the command. A real typed queue in an isolated registry with synthetic Desktop rows exercises the reader before any genuine positive is claimed.

## Write set

- `packages/aitm-usage/src/aitm_usage/sources/codex.py` for the optional same-turn completion witness.
- `packages/aitm-usage/src/aitm_usage/sources/adapter.py` for transport through the authenticated scan.
- `packages/aitm-usage/src/aitm_usage/monitor_scope.py` for the opt-in read and writer-bound evidence lookup.
- `packages/aitm-usage/tests/test_monitor_scope.py` for public-reader qualification and compatibility tests.

Keep the existing CLI, scope and journal storage codecs, durable state, release paths and CI controls intact. #204 and #119 remain gated until #210 delivers. Epic #2, C01 and production cutover are outside this slice.

## Task 1. Observe the completion on the existing exact read

- [ ] Add a focused red test with the isolated typed disposition queue and append-only Desktop rows from the placement probe. Use explicit matching turn and root IDs. Read separately after queued custom-tool output, the linked post-output request and changed-total counter, and successful completion. Only the final fixed read supplies a completion witness. The legacy request/turn boundaries, ordinary cursor and diagnostics remain as on trunk.
- [ ] In `sources/codex.py`, keep a private transient `_CodexCompletionWitness` containing the existing receipt-linked request boundary, command output ordinal, closing ordinal, turn and root references, segment and accounting counter ordinal. No raw command text, request path, or output is exported. Differentiate the exact canonical dispose wrapper from the generic monitor-scope wrapper while preserving existing recognition for all three verbs. Capture only a serial matching `custom_tool_call_output` and its unique accounted post-output response. A normal positive delta and existing complete usage classification must both agree. A repeated cumulative snapshot never qualifies accounting.
- [ ] Let the pinned `_read_codex` opt in through a private optional witness sink. Use the existing `_Walk` and capture only committed frames. A successful matching `task_complete` needs the same root/turn and segment, eligible accounting with a baseline, a fully reconciled final response, no pending response, tool, compaction, ambiguity, taint, terminal error or persistence warning, and no usage or different boundary after it in the requested fixed read. The closing row must be at the fixed frontier. Return the witness separately while retaining the ordinary legacy next-turn checkpoint suppression and diagnostics. Retain a single current candidate per read.
- [ ] Cover the positive and fail-closed cases on the exact parser path. Include wrong verb/output type, missing post-output counter, unchanged totals, missing or deferred response accounting, terminal error or abort, wrong turn/root/segment, competing or duplicated call, disabled capture, and later usage including a same-turn response after close. Repeat the old next-turn tests and verify byte-for-byte prior durable state and cursor. The synthetic fixture may establish the code path and refusal behavior.

## Task 2. Expose read-only, writer-bound qualification

- [ ] Plumb the optional witness sink through `ProviderAdapter.read_delta` and the verified selected rescan. Bind the witness to the exact existing `REQUEST` boundary and closing frame by source/session/stream/segment and scanner prefix. Discard an unverified or superseded scan. Do not expose a fallback from a provider frame rejected by the capture scanner.
- [ ] Add `ScopeState.read_source(..., qualify_completion=False)` and its private result slot. Default reads do no additional work. Add `ScopeState.completion_witness(command, authority, batch, request_target)` for explicit read-only qualification. Reuse `verify_boundary` for the authorized command and first unique exact request boundary. Require `Disposition`, admitted Codex Desktop, matching project/checkout/source and the earlier fixed owned hold span. Recheck current fixed prefix and actor. Verify the exact typed queue and grant separately in the qualification fixture. The evidence object does not authorize settlement or act as a cursor.
- [ ] Run the scope, parser, journal, registry and installation regressions. Demonstrate held scope and unchanged journal/cursors before and after a successful evidence read and restart. Missing evidence stays unavailable without a state write.
- [ ] Attempt a genuine Desktop disposition on a disposable monitor and checkout using the current checkout's isolated launcher. Keep the installed launcher and real monitor untouched. Require an exact authorized queued result, positive earlier usage, accounted same-turn completion and no later usage on the selected fixed frontier. Test the separate genuine later-usage control. If no supported isolated Desktop invocation is available, record that exact gap. A source change or synthetic result alone supplies no genuine qualification and no release authority.

Once a genuine carrier qualifies, the existing #210 settlement requirements apply to the effective scope and one atomic journal change, with independent owner/rival proof and verified delivery. A later same-turn usage event must remain held and replayable even after an accepted earlier journal change.
