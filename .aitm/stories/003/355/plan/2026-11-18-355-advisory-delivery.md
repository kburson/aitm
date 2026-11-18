# #355 advisory execution plan

The owner scope decision in #368 supersedes the strict observation route of the earlier plan. The accepted #353 cooperative boundary and #354 pinned obligations govern this delivery. Target trunk from #354 merge 8218a69ad6d9d9f33c6383bd5a6cd4930bef21d7.

- [ ] Add tests for exact, complete setup/call/teardown receipts, a legitimate test failure and a setup failure, invalid or missing evidence, and snapshot drift. Confirm the tests fail before implementing the command.
- [ ] Add `tools.ci.tia.working_tree_run` with the report's `--repo` and exact `--base` arguments. Share report admission and its captured snapshot, prepare a private copy and locked macOS/APFS runtime using the existing local launcher, revalidate the report immediately before and after one pytest subprocess, and invoke exactly the reported IDs. The output binds the report and the fresh invocation to the observed exit and worker receipt. Return 0 for a complete pass, 1 for a complete pytest failure, and 2 for unavailable or inconsistent evidence. The JSON labels the scope advisory and preserves the worker's receipt where available.
- [ ] Requalify the committed delivery shape in the report. Allow the two new runner files, the report update and the local launcher import adjustment on top of its prior delivery path set. Its anchor, report inventory, map consumer, audited source grammar, pytest inputs, and local worktree admission remain anchored as before. Check unsupported committed paths and unsupported worktree paths as refusal controls.
- [ ] Document the manual pre-commit command and advisory limits. Validate focused and adjacent tests, then replay the actual admitted change on a clean exact-tree scratch checkout with tracked source and raw index readbacks. Verify unsupported input launches zero tests and exercise a real failing cooperative subprocess using benign fixture code. Use authenticated hosted CI and exact-candidate independent source review before merge. After merge repeat the delivered command, publish verified delivery and implementer sign-off, and close #355. Keep #351 open for the requested delivery report.

The local launcher loaded the hosted Python gate on import, which in turn relies on the bare `path_map` module name. Move the gate import into the original stock outcome-validation function. The #355 command can reuse runtime setup without loading the hosted gate.

## Candidate local verification

Head `81a6602a7b045f081f597b0e0b3e6480258d01ff`, tree `4dffcbcfdfca38febd63463124f2f5e140e70c1d`. The focused runner, report, snapshot and path-map suite passed all 113 tests, including the real subprocess failure control. Ruff check and format passed across all 41 CI Python files. Git diff whitespace checks passed.

The [candidate replay](../attachments/2026-11-18-355-candidate-advisory-run.json) used the co-located exact candidate tree and a mixed staged/unstaged comment append. It ran the exact assigned 30 nodes, matched all 90 passing phase records and preserved Git status, the raw index, source bytes, and the absence of Python caches. An additional untracked path returned exit 2 before launch. An unrelated committed change separately returned `unqualified-base` before launch. A separate trusted-tooling checkout also ran all 30 pinned IDs against the #354 delivery base.

The broad local helper run stopped at the first legacy `test_tia_controls.py` failure, reproduced at the #354 baseline with the same `invalid_scope` result. The old stock planner fixture also fails at #354 on its bare `path_map` import. With import delayed, that fixture reaches its preexisting policy input, which currently returns `candidate-inventory: policy: invalid profile`. The delivered runner does not use stock selection or candidate inventory.

## Hosted CI attempt 1

[Run 44306782506, attempt 1](https://github.com/kburson/aitm/actions/runs/44306782506/attempts/1) completed all four test and quality jobs. The evidence collector failed, so the final attestation job skipped. Replaying the delivered gate against the job artifacts yielded the sole failure `missing or drifted trusted base identity`. The base job ran on image `macos26:20261102.0473.1` and the candidate ran on `macos26:20261112.0504.1`. All other base identity fields agreed. The [trusted verifier HOLD](2026-11-18-355-attempt-1-verifier-hold.json) records the failed hosted attempt. A full same-head rerun was requested. The story is still in Test.

The complete exploratory local helper run reported 471 passed, 101 failed and 60 errors. Repeating the helper run on the #354 base reported 449 passed, 102 failed and 60 errors. This broad legacy suite is outside the scoped local validation and is distinct from the hosted policy suite.
