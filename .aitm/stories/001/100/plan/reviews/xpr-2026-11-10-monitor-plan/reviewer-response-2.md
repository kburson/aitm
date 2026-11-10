# Native reviewer response, round 2

Native source SHA-256 `sha256:37834c98130ca61de62bef49bb33019cfd34e10ce9c1e0ef2ee59e740228e528`. Submitted `2026-11-10T13:42:32.874Z`.

Mode: `normal`

## Summary

I re-read the full revised plan: 256 lines, artifact digest `sha256:8899a4d1…5f21`, commit `5956372`. I checked it against round 1's findings, author response 1 and the accepted #100 specification. The revision resolves all five required findings and all four optional suggestions from round 1. It introduces no new blocking contradictions.

**R1-F001 (legacy surface after adoption).** Resolved. The new "Legacy command surface after adoption" section (plan lines 67–79) gives every #83 entry point an owner and an adopted behavior:

- The exact `scope mark` and `development bind` invocation stays a live native carrier, routed through the admitted compatibility path (M07, M04 and M11).
- Corrections and relationships are drained by M11 and pinned by M13.
- `register` and `add-anchor` are refused with a stable reason (M06).
- Legacy writers, lifecycle, backup, restore and qualify are refused (M15 and M16). The old binary is refused by schema (M03).
- Read-only `status`, `rollup` and `export` are confined (M13 and M14).

M09 now keeps the original writer guard for the whole coordinator custody (lines 79 and 163). M16 records the pending-command manifest under the guard and inbox lock and transfers it with the original IDs (lines 79 and 226). The argparse destination collision is fixed with separate `legacy_state_dir` and `project_id` destinations, and mixed forms are refused (line 69, test at line 111). The M16 test `test_pending_legacy_commands_apply_once_and_native_mark_remains_live` and the M18 legacy-marker run (line 243) cover the live path.

**R1-F002 (Grok types and rates).** Resolved. M05 now owns the monitor-only provider and model enums in `S/monitor_types.py`, a separate versioned `S/rates/` resource, and provider-specific rate validation. It explicitly keeps the legacy decoder types, `2026-11-09.json`, its default and its RateBasis digest unchanged (line 125), with matching tests (line 129). The ownership table (line 45) matches. M05 shares `S/monitor_types.py` with M03, but the M03→M04→M05 chain serializes those edits. None of the parallel leaves M06–M09 list that file.

**R1-F003 (cutover continuity).** Resolved. M09's contract (line 163) defines late-legacy-revision recognition: native lineage is verified against the existing row with the adopted #83 key and request-key algorithm, the claim is bound to the original project, and a pseudonym alone cannot seed a claim. M16 adds `test_post_cutover_revision_updates_legacy_row_once` and `test_codex_counter_epoch_continues_across_cutover`, checks the frozen export bytes after each case, and fails closed on ambiguous lineage (line 228).

**R1-F004 (live acceptance completeness).** Resolved. NA-1 (line 83) lists every item from spec line 75: two checkouts for one project, a dependency handoff with zero rollup across the edge, an unmarked review, project-wide work, an ambiguous claim, the ordinary-marker conflict, and mixed qualified and unqualified sources in one root. The macOS case uses a real Codex CLI rollout and the Linux case an actual unsupported client. M17 mirrors NA-1 deterministically and adds the review-focus #5 test (line 235). The M18 and M19 receipt validators reject any missing NA-1 outcome (lines 242 and 249).

**R1-F005 (hook location and privacy).** Resolved. M10 names user-local, owned install targets for each provider. Hook commands embed no checkout, state or socket path, no tracked repository files change, and tests use isolated provider homes (lines 172 and 174). M16 installs production hooks only inside the authorized cutover and removes the exact owned entries, or proves them inert, on rollback (lines 226 and 228).

**Round 1 optional items R1-F006–R1-F009.** All incorporated:
- M11 sleep/wake and fallback test (line 183).
- M07 persisted UTC hold expiry across restart (line 147).
- M10 consumed-wake retirement and M06 default driver (lines 136 and 174).
- Checked ctypes bindings and FSEvents run-loop ownership (lines 91, 103, 172 and 181).

Three small non-blocking clarifications are listed under Optional suggestions.

## Findings

None.

## Required changes

None.

## Optional suggestions

### R2-F001 — M03's dispatch test names commands that later leaves introduce

`test_legacy_global_state_and_report_project_uuid_are_separate` is an M03 test (line 111). However, the first subcommand with `--project UUID` arrives in M06, and the `report` subcommand arrives in M13. Have M03 prove the dispatch separation with a test-only subcommand. Then add the concrete invocation-form and mixed-form refusal cases for `monitor capture` and `monitor project anchor add` (M06), `monitor hooks install` (M10) and `report stories` (M13), each when it introduces the command.

### R2-F002 — Give the M06 adopted-registry refusals a named test

Line 75 assigns the `register` and `source add-anchor` refusal (`project-adopted-use-monitor`) to M06, and line 136 says M06 enforces it. M06's test list (lines 138–139) does not name a test for it. M15 (line 215) does name explicit refusal tests for the lifecycle commands. Add an M06 test showing that both legacy commands refuse on adopted state with no registry or inbox mutation.

### R2-F003 — State how the cutover freeze treats an old-binary marker invocation

Line 79 freezes legacy ingress when the pending-command manifest is recorded under the inbox publication lock. Schema adoption follows that freeze. In the window between the two, an AITM workflow turn may still run the old installed binary's `scope mark`, which writes to the legacy per-project inbox. State that this invocation must fail visibly, either by contention on that lock or by a stopped-ingress marker the old binary honors, rather than enqueue after the manifest. If neither is possible, the M16 sequence must stop or replace the old binary on PATH before the freeze. Add this case to `test_pending_legacy_commands_apply_once_and_native_mark_remains_live`.

## Decision

accepted
