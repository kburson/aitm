# #203 resumed independent source review PASS

Claude Opus 5.5 medium reviewed this exact candidate locally through the off-platform CLI on November 11, 2026 America/Chicago. The owner authorized one additional paid review. This record contains that single verdict. Packet SHA-256 `3fd66d50aed2f61b7019bfb9857289598cbdaf2ffdacf43efc4a36d5382f4fb5`.

Head `8d8cb2874aefba1898dc7b73c5695c4e7b0cd611`, reviewed tree `6b684109b1d85d98ba01563fb034a2d3040ddc5d`, literal trunk `bc8063b66522ed3a27c95d1bb0546f1e73249612`. [Signed hosted receipt](hosted-ci-resumed-receipt.json).

PASS

This verdict covers candidate `8d8cb2874aefba1898dc7b73c5695c4e7b0cd611`, reviewed tree `6b684109b1d85d98ba01563fb034a2d3040ddc5d` and literal trunk `bc8063b66522ed3a27c95d1bb0546f1e73249612`. I worked only from the supplied packet, with no tools, network access or changes. I did not recompute any hash, so the claim that this diff is byte-identical to the earlier accepted diff rests on the packet.

## Identity and rebase

- **Hosted evidence:** it binds `base` bc8063b6, `head` 8d8cb287 and `reviewed_tree` / `tree` 6b684109. `tested` is 07727ebc, and its `tree` equals the reviewed tree. All six jobs and the trusted controls are present, `status: pass`, PR 211, run attempt 1.
- **Files changed:** the candidate diff touches only `monitor_scope.py` and `test_monitor_scope.py`. The parent-side blob for `monitor_scope.py` (`de18a02d`) is unaffected by the incoming parent changes, which are only in `tools/story_dashboard/*`. So the rebase cannot change the accepted product logic.
- **Coverage:** hosted and local frozen-gate runs agree at 10655/11604 product lines and 778/821 helper lines, the same as the earlier PASS. The local baseline of 10461/11407 equals the JIT's baseline on `e4701f2e`. That fits the dashboard files being outside the counted suites.

## Baseline test identity

- **Local:** 996 baseline IDs retained, 1071 candidate IDs, 75 new IDs. I counted the list against the parameter sets in the diff:

  | Test | Cases |
  |---|---|
  | `test_v2_decoder_rejects_malformed_or_unowned_shape` | 29 |
  | `test_v2_writer_requires_service_custody_before_mutation` | 10 |
  | `test_issued_route_disposition_requires_current_evidence` | 9 |
  | `test_disposition_proposal_needs_current_owned_span_and_receipt` | 6 |
  | `test_legacy_writers_preserve_both_v2_collections` | 5 |
  | `test_ordered_native_disposition_records_only_proof_and_replays_after_restart` | 3 |
  | `route_target` and `interrupted` tests | 2 each |
  | Nine single tests | 1 each |

  The total is 75, and 996 + 75 = 1071.
- **Hosted:** baseline 995. The only difference is the named local control `tools/ci/tests/test_cli_evidence.py::test_usage_console_help`. `hosted_only_baseline_ids` is empty and `hosted_and_local_candidate_sets_equal` is true, so all 996 local baseline IDs are present in the 1071 tests that passed on hosted CI.

## Fixes for the first HOLD (still present in the diff)

- **B1 (empty original span):** `AffectedScope.__post_init__` raises when `end <= start`. `_snapshot` turns that into `LedgerError("Invalid private scope state")` when it decodes `_ScopeSnapshotV2`. The `[empty-span]` case changes only `hold.affected.end`.
- **B2 (tests isolating their cause):**
  - `issued…[expire]` runs with release false, asserts `record.outcome is HoldState.GAP`, calls only `expire()`, and matches `"Scope disposition is no longer current"`. Only the `(hold, record)` comparison in `require_route_disposition` can produce that refusal.
  - `[expired-proposal]` is the only case with release true. It never calls `expire()` and matches `"original scope cannot be proposed"`.
  - `[legacy-dispose]` appends legacy `0x607` inside the span (`start <= legacy_at < end`) and asserts the native bytes are unchanged. It matches `"Current scope hold cannot authorize"`, which only the `_Resolution` check in `_route_proposal` produces.
  - `test_legacy_resolution_blocks_first_route_proposal_without_rewriting_native_rows` covers refusal at first issuance, with the view, scope bytes, empty `route_dispositions` and cursor all unchanged.
- **B3 (baseline count):** resolved as described under "Baseline test identity".

## Requested checks

- **Strict v1/v2 and legacy writes:**
  - `_snapshot` tries v1 first, then v2. `_validate_scope_snapshot` and `_validate_route_records` enforce the exact format, digests, states, uniqueness, at most one record per hold, joins, terminal ordering and prefix identity.
  - Legacy writers use `replace(state, …)`, so a v2 file stays v2. `test_legacy_writers_preserve_both_v2_collections` checks this for mark, handoff, hold, expire and dispose.
  - `test_default_hold_keeps_v1_and_cannot_be_retroactively_retained` checks the exact v1 bytes.
  - The frozen old reader refuses v2 at the strict codec, and the v2 file is byte-identical before and after the read (`8002ac…`). A v1 file re-encodes byte-identically (`fe929a…`).
- **Source custody:** `_require_route_custody` runs on every writer `_snapshot` and every v2 `_save`. It requires an initialized source key, an approved source with matching surface and provider, valid refs on each new object, and a receipt ref keyed to its own command. `_route_proposal` also requires `type(source) is CandidateSource`. Tests: the 10 custody cases, `…uninitialized_source_key…` and `…does_not_follow_a_link…`.
- **Queue grant custody:**
  - `_route_request` requires the `DispositionRequest` type plus matching project, hold and `release_previous`. It runs `open_grant` and `require_witness` before the yield, and `recheck()` plus `require_witness` after it.
  - The `[wrong-typed-request]` case refuses.
  - The `[consumed]`, `[withdrawn]`, `[revoked]` and `[advertisement-expired]` cases each refuse.
- **Lock ordering:**
  - `_route_request` checks the writer lease (`self.registry.lease`) before taking `inbox.publication()`.
  - Inside that lock it opens the grant, then proposes, publishes and confirms.
  - `_save` takes no further lock.
  - Nothing calls `_apply` or the legacy `dispose`, and no queue item is consumed.
- **Terminal and older span binding:** `_route_proposal` refuses unless all of these hold:
  - the terminal is a TURN and the last recognized boundary;
  - the batch has no cursor (`cursor is None`) and only `BOUNDARY_UNVERIFIED`;
  - terminal ordinal `>= affected.end`, on the same stream, with the same anchor owner;
  - the receipt and command are distinct from the hold's;
  - the original boundary appears exactly once, with the same checkout;
  - the span is eligible for the owner;
  - the new prefix offset is greater than the saved one;
  - the saved prefix reauthenticates through `_capture_position(fixed=…)`;
  - the current physical extent equals the read prefix.

  The decoder repeats the ordinal, receipt, boundary and prefix checks.
- **Live-token invalidation:** `require_route_disposition` checks token identity in the weak map, then re-runs the full request and proposal checks and compares `(hold, record)` with the issued proof. All 9 issued-token cases refuse with the view and cursor unchanged. A copy made with `replace(proof)` refuses, and so does a reopened writer.
- **Historical replay:**
  - Replay with the same ID requires `existing == record`.
  - A second command for the same hold raises `ConflictError` (`test_a_second_verified_command…`).
  - Records survive later hold transitions as history.
  - After real later usage, issuing or reissuing refuses, including after a restart.
  - Across issuance and replay, the journal bytes, `as_of()`, cursor and `view()` are unchanged. The proof stays proposal-only, leaving recording to #209 and settlement to #210.
- **Atomic publication recovery:**
  - `test_interrupted_retained_hold_publication_preserves_atomic_snapshot` covers interruption before and after the file replace.
  - `test_native_disposition_reconfirms_visible_proof_after_directory_sync_failure` asserts that `_route_proofs` stays empty, and that an exact replay only reissues after confirming and rechecking.

## Non-blocking

1. Nothing in the packet records why the hosted baseline leaves out `test_usage_console_help`. Write it down before Close.
2. `[empty-span]` matches `"Invalid private scope"`. Changing it to `"Invalid private scope state"` would tie it to the decode refusal.
3. There is still no test of a `DispositionRequest` sent under a grant registered only for `mark` (R1 note 3).
4. Hand #210 the limitation that a GAP proposal overtaken by `expire()` can never be reissued (R1 note 5).
5. The packet doesn't show whether the incoming `tools/story_dashboard` tests run in any counted suite. That's a parent-side matter, outside #203.
6. The merge, the parent/tree/ancestry checks, the Closed (Completed) and Project Done provenance, and the recheck of the native graph for #209, #210, #204 and #119 all come after this review. None of them is evidenced yet.
