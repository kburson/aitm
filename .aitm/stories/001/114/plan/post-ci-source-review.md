# #114 independent post-CI source re-review

Declared manual off-platform review in a separate Claude Code session. The provider reported `claude-opus-5-5` with medium effort requested. Native GitHub review was absent.

Exact packet SHA-256 `787a2e9470db528b376e064f3c9378f57beedee179f901586eced6ff8698a3aa`. Full candidate diff SHA-256 `ec2f2c86a8ea85ac3f8207f2b24834ba9e22c7bd37def8b4ee49dc95563bc9d4`. [Hosted attempt](https://github.com/kburson/aitm/actions/runs/42852838878/attempts/1).

## #114 M04 independent source re-review: **PASS**, November 10, 2026

**Subject:** head `805c9e16da0b112cdb8e15543e9c2408c1041978`, tree `5ca29c2890eefadd8fc8000aff442144335c4cae`, base `dc037364ba617b97244c93670d12358d0b5cbba7`. I judged only the material you supplied. I did not access GitHub, run anything, or recompute any digest.

### B1 (cold split-and-restart proof): closed

`test_every_native_split_matches_one_read_after_restart` covers all four fixtures the prior review asked for. For every row boundary 1…n−1, it:
- reads `rows[:split]`;
- round-trips the cursor through `_encode` and `_decode`;
- rebuilds the evidence from `_committed_view(prefix)`;
- rediscovers the source and reads the full file with a new `ProviderAdapter`.

`NativeObservation` is a plain dataclass, so the `latest()` dict comparison checks keys, revisions, usage and `project_context`. A lost key, an extra key, a session total counted again, or a wrong checkout context would each fail it. The receipt-proof sets must also match.

- **Codex restart after a completed turn (the original gap).** In the Desktop case, `first_turn_end` is in `safe_splits`. The cursor is saved after the first complete turn, then a second turn is appended. That turn has a cumulative total of base+5/+2 and a last-turn value of 5/2, and the new `CodexState` has no in-memory history. The test requires exactly the full-read observations. Codex needed no source change, and the test now proves the existing behaviour.
- **The cursor never lands inside an open turn, pending receipt or pending Agent call.** `safe_splits` is an exact set. Any split outside it must return `cursor is None` with no observations, and any split inside it must return an offset equal to the split. The safe sets are:
  - Desktop: {1, end of turn 1}
  - Receipt: {1}
  - Nested: {1}
  - Streamed: every boundary, which relies on the keyed prefix
- **Nested Agent repair (`claude.py` `_RouteWalk.user`).** In neutral mode, a nested user frame no longer resets the route while an outer Agent call is pending. A frame with a different parent marks the call `uncertain_child`. Without this, split 4 in the nested fixture (just after the child's `tool_result`) would have cleared `route.tool` and let the cursor cross mid-Agent. The test now requires a hold there. This resolves the `_Route` concern from the prior review.
- **Checkout context on revisions (`scan._read` `revision_checkouts` → `adapter` `prior_checkout`).** This is used only when `_monitor`, the provider is Claude, a checkpoint exists, the ordinal is in the checkpoint's `request_prefix`, and the anchor was derived again in this read. Otherwise the context is absent, so it fails closed. The streamed every-split equality checks that the context matches the single read.

### B2 (inventory count): closed

570 + 22 + 1 = 593 matches the signed `tests: 593` / `baseline_tests: 570`.
- **22 M04 cases:** the 18 already reviewed plus the new 4-case parametrized test.
- **1 extra:** the candidate-only `test_usage_console_help`.

The raw set difference reports no baseline removals, and the CI-helper count of 182 is reported separately. This agrees with the accepted disposition from the prior review.

### Regressions in the exact changes since the prior verdict: none found
- **Legacy path unchanged.** The nested-user change is guarded by `self.neutral_markers`. `prior_ordinals` and `revision_checkouts` are guarded by `source._monitor`, and `_prior_checkout` defaults to `()`. Legacy `discover(Registration)` keeps its ledger open and now delegates.
- **Discovery.** `SourceRoot` now provides `project_id` and `source_roots` directly. No `Registration` is built, and the source root is no longer used as `state_root`, which fixes part of prior advisory 6.
- **Equality fields.** `compare=False` on `_native_surface`, `_monitor` and `_Origin.native_surface` closes advisory 10. Surface changes are still caught by the explicit `origin.native_surface is not source._native_surface` check in `_read`.
- **Exact version per surface.** `_SUPPORTED_CLIENTS` pins Codex to `0.167.0-alpha.3.2` and Claude to `2.1.318`. Any declared format must be integer 1. The surface is set only on the branch with no issue. This closes advisory 1.
- **Consistency.** The production diff blob indices match the rework diff, and the test blob `c0affc1…` matches the delivered test file.

### Gates
- **Hosted run:** run 42852838878, attempt 1, ran on the exact head. All six jobs succeeded, and the signed tree and base match.
- **Coverage:** product 6,623/7,245 and helpers 778/821, matching the local result. Ruff ran in the `quality` job.
- **Remaining:** only this review was outstanding, so no required source gate remains. Merge and closure belong to the owner.

### Advisories (not blocking)
1. **No chained restarts.** Each split restarts once, from `None`. No test chains cursor → cursor → cursor, so the `revision_checkouts` path is never fed a checkpoint from an earlier restart.
2. **Cursor isolation still unproven (prior advisory 7).** `_committed_view(prefix)` supplies the view on restart, so the test doesn't show the prefix is rebuilt from the cursor alone.
3. **Prior advisory 8 is still open.** The Claude receipt test doesn't check that `declared-project-secret` and `marker-command-secret` are absent from the output.
4. **Holds are coarse (prior advisory 3).** You can see this in Desktop splits inside turn 2: turn 1's usage is held back and replayed later. A trailing `scope mark` can still stall, and `BOUNDARY_UNVERIFIED` is still the wrong label for an ordinary hold.
5. **Equivalence only.** The test matches the latest observation per key against a single read, not absolute totals, and doesn't count identical re-emissions. Add an absolute check for the new nested fixture (child request counted once, report suppressed through `saw_child`).
6. **Prior advisory 2 remains:** the `sessionId` signal for "native Claude Code", and the host check looking at the reader's machine rather than the writer's. Also, a missing `format_version` field is accepted as format 1.

### Limits
- **Source I didn't see:**
  - Test helpers: `_committed_view`, `_write`, `_desktop`, `CLAUDE_FIXTURE`, `_native_tool_turn`, `Evidence`, `_encode`, `_decode`, `_adapter`.
  - Production code: `_nested`, `_parent_tool`, `_UsageWalk`, the rest of `_read` (including whether `last_timed` can be `None` in the new branch), and any remaining reads of `_registration` beyond the protocol fields.
- **Not checked:** I didn't recompute the diff digest `ec2f…` or the tree. I took the hosted run, signed subject and raw inventory statement as supplied. I didn't see the raw inventory lists themselves.
- **Excluded:** Linux carriers (M04-LC, M04-LA) and authority to route rows to projects (M07) belong to their own owners.

## Implementer disposition

Both required findings closed on the exact replacement. The retained test control includes a Claude startup evidence serialization check that rejects the declared project path, marker command and raw session ID sentinels. The full locked suite also retains the nested absolute count assertions. The adapter deliberately holds a whole delta when its trailing native linkage is unresolved. Chained and live scheduling behavior, service-origin enrollment and the atomic persisted frontier belong to later accepted leaves. The prior view and cursor share the same durable checkpoint under the accepted contract. This source review did not certify runtime admission for Linux.
