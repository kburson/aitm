[20:47:55]
**JIT_303: PASS**

## Closure of the original HOLD items

| Item | Status | Evidence |
|---|---|---|
| **B1**: tree identity and call-site excerpts | **Closed** | Both `8d794c5` and `ea73031` resolve `packages/aitm-usage` to tree `ede965e7…`, and `git diff --name-only` on the package path returns no paths. Every call site B1 said was missing is now excerpted and pinned to `ea73031`, including the complete `_native_delta`. The `cli.py` excerpts are labeled with a single line (`:183`, `:239`) but show several lines. That is cosmetic and doesn't block. |
| **B2**: settlement path and the read after commit | **Closed** | The excerpts confirm the claimed chain. `settle_disposition` calls `_require_settlement_side` twice around `_build_settlement_change`. That calls `_settled_side` for the owner and the rival, which calls `side._issuer._journal_view`, which calls `self._recheck_batch(batch)` before any per-release `_capture_position`. So the gate placed before `_recheck_batch` covers settlement inside the write transaction. The native readback after commit is now gated: the same live batch capability is rechecked before each prefix is reopened. If it fails, the call refuses and the committed row, claims and cursor stay in place. A stale retry also goes back through `_settled_side` → `_journal_view` and refuses, so it can't reach the existing-row return. Test 4 covers a revoke between commit and readback. |
| **B3**: refusal-type mapping | **Closed at the contract level** | The refusal type is a private `LedgerError` subclass, which `apply_pending` already turns into REJECTED. A refused approval raises from `_approve` before the identity loop, with `next_view = view`, so no ID is created. A refused enable is REJECTED, and healthy edges continue. A disable that needs an excluded read is translated to `BoundaryUnavailable` and held. Test 4 asserts each outcome. |

The two non-blocking conditions are also closed. The tuple comparison is now stored approval against the typed qualified tuple, executable identity comes from the #304/fixture verifier, and nothing is extracted before the read. Fixture hookup is limited to a timeboxed, test-scoped shim that resets after each test, and negative tests use a clean writer.

Scope and gates are unchanged: #304 issues authority, the product has no grant path, no Linux collectors are enabled, and the 2.7h estimate holds. The file list and the ownership split with #300, #121/#125 and #128/#129 match the earlier pass. The hosted signed Test, the independent source review and Close are still required.

## Binding implementation conditions

None of these adds scope, and Test 4 would already catch each one. They come straight from the `_apply_capture` excerpt:

1. **Where the enable check goes.** A gate placed only at the shared `_approved_candidate` seam will be held, not REJECTED, on the enable path. When `_make_arm` raises the private `LedgerError`, the stream loop's `except (LedgerError, ValueError): held = True` catches it. Also, `if not latest or all(epoch.gap_open …): return _permission(view, payload)` applies an enable without reading anything. So the live-enable policy check has to sit in `_apply_capture` in two places:
   - after the existing check that an earlier ordered command is pending, so an earlier queued disable keeps its priority;
   - before that early return, or be re-raised past the loop's held handler when `payload.enabled`.
2. **Where the disable translation goes.** Translate to `BoundaryUnavailable` only at the native proof call sites, `_make_arm` and `locate`. Don't raise anything from the first `try` block (`_check_capture_root`/platform):
   - Something that is a `ConflictError` or `ValueError` there appends lost epochs and applies the disable.
   - A plain `LedgerError` there would REJECT and discard the disable.

   One thing the JIT leaves implicit: inside the loop, `BoundaryUnavailable` still goes through `_locator_lost`. A proven locator loss there already produces a lost epoch, which is existing behavior. Keep that as is; don't count it as a fabricated success.
3. **Same-edge commands after a rejected enable.** A REJECTED enable doesn't add its edge to `held_edges`. Later commands on that same edge will therefore run in the same pass. Assert this in Test 4 alongside the healthy-edge case.
4. **The final side check.** `_settlement_side` isn't excerpted. "The final side check additionally revalidates authority" is new behavior to add inside the second `_require_settlement_side` call. Don't assume it already exists.
