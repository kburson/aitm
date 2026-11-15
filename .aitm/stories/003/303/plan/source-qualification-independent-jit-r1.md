[20:45:05]
**JIT_303: HOLD**

This JIT can't authorize the gated implementation yet. Three gaps in its evidence and wording block it. None of them adds implementation scope, so a re-JIT that closes them should be short. I used only the supplied evidence.

## Blocking findings

| # | Finding | Evidence | What the re-JIT must show |
|---|---|---|---|
| **B1** | Refine condition 1 is still not met. The JIT pins `ea73031` and says its usage package tree is byte-identical to `8d794c5`, but shows no tree hash or diff. Refine had already flagged this same claim as "asserted, not shown." The supplied excerpts cover only part of the call sites the JIT names. These are missing: `_native_delta` (cut off), `_capture_frontier`, `_verify_next`, `capture_progress`, `_make_arm`, `_apply_capture`, `ScopeState.read_source`, `_settled_side`, `view`, `command_status`, `as_of`, `cursor_for`, and the `cli.py` / `scopes.enqueue_command` paths. | Neither commit's package tree hash is supplied. The excerpts say nothing about which commit they come from. | The package tree hash at both commits, or an empty diff of the package path. Excerpts of every named call site, pinned to that tree. If anything differs, go back to Refine. |
| **B2** | Refine condition 3 (audit every payload path) is incomplete for settlement. The JIT says `settle_disposition` and `_settled_side` run "the same current protected live batch check through `_journal_view`." The excerpt doesn't show that: it goes through `_route_requests`, `_require_settlement_side` and `recheck()`. After the write commits, it also reopens the native frontiers with `_capture_position(...)`, which is a native payload read after commit. That read is neither gated nor marked historical-only. | The `settle_disposition` excerpt, including its post-commit `with self._store.transaction()` block. | The exact path from settlement to the proof check, plus a disposition for the post-commit `_capture_position` read: gated, or verification-only that admits nothing. Also a test where a revoke between commit and readback neither fabricates success nor loses the committed settlement. |
| **B3** | It doesn't say which error each refusal raises, which decides what `apply_pending` does with it. That loop turns only `ConflictError`, `LedgerError`, `OSError` and `ValueError` into a REJECTED receipt. `_CaptureArmed` and `BoundaryUnavailable` hold the command. Any other error type aborts the loop and leaves the command pending, so every later poll hits it again. The JIT pins only the disable case (held). It doesn't say how a refused new or repeated approval, or a refused capture enable, should end up. | `apply_pending` exception handling. | A mapping: approval refusal → REJECTED, with no ID; enable refusal → REJECTED or held, chosen explicitly along with what that means for the other commands queued behind it; disable needing a fresh excluded read → held via `BoundaryUnavailable`. The refusal types must be subclasses of the caught set. Add a control test for each. |

## What passes

- **No default grant, and no added issuer or coverage scope.**
  - The product exposes no grant method, command, env, flag or importable fixture.
  - The currentness hook is inert and budgeted inside the 0.7h types line.
  - Fixture state can only be installed through test-tree monkeypatching, and a test checks that the shim is unreachable through the package import path.
  - A refusal discloses only the broader authorized root, at unknown extent.
  - Representing Linux tuples does not enable those collectors.
- **Stored approvals.** The JIT now says explicitly that existing approvals keep their stored form and do not admit live reads. Test 1 checks this separately on the Codex and Grok reader paths.
- **Check placement.**
  - The approval check runs before the identity loop in `_approve`, so it covers the early return for a repeated approval.
  - Committed-receipt replay in `apply_pending` returns before `_apply` is called, so it stays historical-only.
  - `_read_grok` is named as its own check, separate from `_approved_candidate`.
  - Both `_fresh_view` calls in `_reserve` sit inside the write transaction, and the second runs after `_write_progress`. That covers the `current == read.progress` retry and rolls back on refusal.
  - The proof is rechecked before `_recheck_batch` reopens the native prefix. That is needed because supersede and revoke live in writer-memory slots that the `batch._registry != self.registry.view()` comparison can't see.
- **Captured boundaries.** `_require_direct_proof` accepts a boundary from `_verified` or from `_completed`. The JIT requires a current binding for every live enable, new epoch and progress write, so a completed boundary can't be reused after a revoke. Test 3 covers the old-boundary case.
- **Tests and ownership.** The required test plan meets Refine condition 5 (separate Codex and Grok refusals, lease loss, verifier unavailable, supersede and revoke, the shim boundary). The issuer is named as #304, and the ownership split with #300, #121/#125 and #128/#129 matches the accepted boundaries.

## Non-blocking conditions for the re-JIT

1. **Where the tuple comparison gets its values.** The Codex path in `_approved_candidate` currently observes only system, machine, surface and provider; it has no native version or executable field. State that build version and executable identity are compared between the stored approval and the #304/fixture qualification tuple, with no new pre-read extraction from the native stream. Otherwise this quietly brings back the executable-proof problem (H1) that Refine assigned to #304.
2. **Fixture hookup cost.** With admission closed by default, every existing test that approves a source and reads from it needs the fixture provider. If that turns out to be more than targeted hookups (for example, it needs a blanket autouse fixture), it collides with the rule that negative tests use a clean writer. That is the main risk to the 0.9h test line.

## Feasibility

0.7 + 0.6 + 0.5 + 0.9 = 2.7h, leaving 1.3h under the 4h ceiling. The B1–B3 fixes are documentation and test-spec changes, not new work, so the estimate holds. The B3 control tests and the B2 settlement test fit inside the existing 0.9h test line, but they use up some of the fixture-hookup slack. The hosted signed Test, the source review and Close sit outside the 2.7h implementation estimate.
