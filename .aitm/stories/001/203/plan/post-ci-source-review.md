# #203 independent exact source review

Claude Opus 5.5 medium, local off-platform review, November 10, 2026 America/Chicago. Head `735b068e4664ab6e1f1f65a55b4116b9a0917537`, tree `ca59518be6c1374892be1d9d5e77a46deabb5608`, literal trunk `72ca2d2535248844b164014d7817bffec0e9fb7e`. Review packet SHA-256 `1ea3ae89d4a4dc209aa8069cc808cfd8f60616926c735f3d8bbdf8ec2223ca61`. Native GitHub review absent.

# PASS

This PASS covers candidate `735b068e4664ab6e1f1f65a55b4116b9a0917537`, tree `ca59518be6c1374892be1d9d5e77a46deabb5608`, against literal trunk `72ca2d2535248844b164014d7817bffec0e9fb7e`. I used only the evidence you supplied: no tools, no mutations and no network. I did not recompute any hashes. It replaces the retained R1 HOLD.

## B1: empty original span — resolved

- **Where it is enforced:** `AffectedScope.__post_init__` raises `ValueError("Expected a nonempty native scope span")` when `end <= start`. In `_snapshot`, a v2 file with an empty span fails `_decode(data, _ScopeSnapshotV2)`. The `ValueError` becomes `LedgerError("Invalid private scope state")` before the route validator runs.
- **Why the refusal comes from the span:** the new `empty-span` case in `test_v2_decoder_rejects_malformed_or_unowned_shape` changes only `hold.affected.end = start`. No other check in `_validate_scope_snapshot` or `_validate_route_records` depends on that field being equal to `start`. `terminal-too-early` cannot fire, because the terminal ordinal is still above `end`. If the decoder skipped `__post_init__`, the file would be accepted and the test would fail, so the passing test shows the decoder runs the span check.
- **The writer path is covered too:** every `ProofHold` is built through `AffectedScope`, so `hold()` and `_route_target` cannot create an empty span. A separate check in `_validate_route_records` is not needed.

## B2: issued-token tests now isolate their cause — resolved

- **`[expire]`:** this case now uses `release=False` and asserts `record.outcome is HoldState.GAP`. It then calls only `expire()`. In `_route_proposal`, a GAP hold is still allowed, there is no `_Resolution`, and no clock check applies to a GAP outcome. The only remaining difference is the `(hold, record) != (proof.hold, proof.record)` comparison in `require_route_disposition`. The test now asserts that exact message: `"Scope disposition is no longer current"`. This is the issued-GAP-token-after-`expire()` case that was missing.
- **`[expired-proposal]`:** this is the only case that still uses `release=True`. It runs with no `expire()` and asserts `"original scope cannot be proposed"`. That separates it from `[expire]`.
- **`[legacy-dispose]`:** the legacy `Disposition` 0x607 is now appended inside the span before the hold is read. The fixture asserts `start <= legacy_at < end`, and the proof comes from `held_batch`. The test no longer rewrites the transcript, and it asserts the native bytes are unchanged across `dispose`. The hold becomes GAP, which is still allowed, and the project is unchanged, so the only clause that can fire is the `_Resolution` check. The test asserts `"Current scope hold cannot authorize"`.
- **Refusal at first issuance:** the new `test_legacy_resolution_blocks_first_route_proposal_without_rewriting_native_rows` checks a hold already changed by a resolution. It asserts the same message, and also that the view, the scope file bytes, the empty `route_dispositions` and the cursor are all unchanged.

## B3: baseline count — resolved

- **Same trunk:** the hosted `base` and the replay's `literal_base` are both `72ca2d25`, so the hosted "before" evidence is taken from the literal trunk, not a stale tree.
- **The gap is one known test:** the local baseline is 996 and the hosted one is 995. The single extra local ID is named: `tools/ci/tests/test_cli_evidence.py::test_usage_console_help`. `hosted_only_baseline_ids` is empty and `hosted_and_local_candidate_sets_equal: true`.
- **The counts add up:** I counted the new IDs myself and got 75: the earlier 73, plus `[empty-span]`, plus the new legacy-resolution test. 996 + 75 = 1071, which matches both the hosted and the local candidate count. Preservation is checked against the larger local baseline.

## Unchanged from R1

- **Product source:** it is byte-identical to R1 and the full diff matches. Everything verified in R1 still holds:
  - the v1/v2 codecs and the old reader refusing v2 (`8002ac…`)
  - writer custody in `_require_route_custody`
  - writer lease, then the inbox `publication()` lock with `open_grant` and `require_witness`
  - an unsettled final TURN with only `BOUNDARY_UNVERIFIED`
  - reauthentication of the saved prefix
  - the RESOLVED route check at each endpoint
  - no calls to `_apply` or the legacy `dispose`
  - no writes from `require_route_disposition`
  - recovery after a directory sync failure
- **The proof stays proposal-only:** across issuance and replay, `view()`, `journal.as_of()`, the journal store bytes and the cursor are unchanged. Neither prefix is used as a cursor. Later usage refuses issuance and reissuance after a restart. That leaves recording to #209 and settlement to #210.
- **Hosted and local agree:** all six jobs pass, and coverage is the same in both runs: 10655/11604 product lines and 778/821 helper lines. The 3 extra covered lines since R1 fit the new refusal tests.

## Non-blocking

1. The `empty-span` case uses `match="Invalid private scope"`, which also matches the "route custody" errors. Matching `"Invalid private scope state"` would tie the case to the decode refusal.
2. The evidence doesn't say why the hosted baseline leaves out `test_usage_console_help`. Write the reason down before Close.
3. R1 notes 1–6 still apply. Note 3 is still open: there is no test of a `DispositionRequest` under a grant registered only for `mark`. Note 5, the limitation where a GAP proposal overtaken by `expire()` can't be reissued, should be handed to #210.
4. The merge, the parent/tree/ancestry checks, the "closed" provenance and the recheck of the native graph come after this review. None of them is evidenced yet.
