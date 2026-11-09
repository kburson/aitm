<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-6662b36bd4cbe2e3a7fbecc3fb7dc330"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/83/plan/usage-capture-launch-health-replan.md"
artifact_commit: "e88eb90047db8abfee09cec4d1515ed565bd175f"
artifact_blob: "9fb51b6efcbf85d241f4e4cc7cab853453b1af0d"
artifact_digest: "sha256:92052b1066427e339601501f3cafcc4b98da89bf6f9a889ede702ac877102dda"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:e4fa9f0da9324635d8b92a67b1ff93fb5fb7f68f34b4b3caea236c8cc5903284"
  identity_source: "runtime"
started_at: "2026-11-09T20:45:50.472Z"
submitted_at: "2026-11-09T20:48:45.623Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is turn 1 of an independent XPR review of `.aitm/stories/000/83/plan/usage-capture-launch-health-replan.md` at sealed digest `sha256:92052b1066427e339601501f3cafcc4b98da89bf6f9a889ede702ac877102dda` (commit `e88eb90`, blob `9fb51b6`).

**Read evidence.** I read the current artifact with the Read tool in contiguous ranges of at most 20 lines. The first call (offset 1, limit 20) returned lines 1–17, and the file ends at line 17. A second call (offset 17, limit 20) returned only line 17, which is blank, and confirmed EOF. Coverage is complete: lines 1–17 of 17. Neither call was truncated or replaced by an omission marker. This is the first turn for this review ID, so there are no prior dispositions to verify.

**Context read.** For context I read the following:

- the reviewer invitation;
- the protocol and context JSON;
- `leaf-stories.md`, where the estimate table at lines 9–21 has U08 4, U12 4, U09 4 and U10 3.5;
- the sizing table in the baseline plan, the command contract and the first amendment's estimate rows (U08 3.5→4; the aggregate is 48.5);
- the #94 implementation plan (lines 1–28, EOF), `jit.md` and the #94/#83 `events.jsonl` entries for the return to Planning at preserved candidate `1d0dd02b…`;
- the #92 story contract (files `service.py`, `cli.py`, `test_service.py`) and the plan's heartbeat line;
- the #93 source review head `05318125…`;
- the #95 story contract.

This worktree contains no `src/` tree, so I could not re-run the reproduction. I took the three reproduced failures as stated in the artifact and in the event records. I checked whether the amendment closes each failure class at the right owner.

**Assessment by topic.**

- *Live PID plus service mode (U08 and U09).* This closes the reproduced false health. A closed producer mode and a positive PID are derived from the real current process and entry point, never from caller data. A one-shot collection cannot claim service mode. U09 requires the loaded job's PID to equal the heartbeat PID in service mode, a post-bootstrap fresh timestamp, matching project, version and interpreter, and a repeated job inspection. In the reproduced case, a different process ran `collect-once`. That case now fails on both mode and PID. A manual `service run` outside launchd fails on PID. A missing legacy witness is Unknown and cannot retire recovery. This part is sound.
- *Fresh status and runtime proof.* The required facts are freshness relative to bootstrap, readable and valid registered state, and an exact executable and arguments from a verified wheel environment. Together with the #94 plan's line 26 executable/digest requirement, these give an adequate runtime proof. One exception is F1, below.
- *Immutable backup and operation boundaries.* Backup output inside the physically resolved store is refused. A restore source inside the target store is refused before any swap, including path aliases, with physical ancestry checked against pinned identity. Both the store and the backup are preserved on refusal. This closes the reproduced deletion during restore. The prune fix covers only the backup. F2 asks for it to cover all of the retained recovery material that the same plan relies on.
- *Startup hook execution.* The amendment requires filesystem inspection of the retained runtime's import and startup surface before executing anything. That is the necessary core, but it does not constrain the process environment that the installer and the plist pass in (F1).
- *Recovery and sequencing.* Several things are preserved separately: the accepted integration `05318125…`, the unaccepted candidate `1d0dd02b…`, the review history and the usage evidence. The order is: #92 repair, then the U12 rerun, then a new accepted integration. After that, #94 is re-pinned, only its owned changes are carried over, the fix is reviewed and the cumulative source gets an independent review. #95 is admitted only after all of that. The order is correct and does not skip any phase. Both #83 and #94 are in `plan` per events.
- *Estimates and ownership.* U08, U12 and U09 stay at 4. U10 is implicitly unchanged at 3.5, and the aggregate stays at 48.5 (it matches `leaf-stories.md`). Every leaf stays at or under the four-hour cap, and a stop rule applies. The U08 witness stays within #92's existing files, and U09 is limited to the U09 files. #83 remains the permanent collector, and all qualification stays #83-only (line 16).

## Findings

1. **F1 (required): the startup-surface check ignores the inherited execution environment.** Line 9 constrains only the retained environment's files ("by safe filesystem inspection"). The installer then runs the retained runtime's Python or console script during verification or `service run`. That process inherits the caller's environment. `PYTHONPATH`, `PYTHONHOME`, `PYTHONSTARTUP` and similar variables can load an unapproved `sitecustomize` or `.pth` from outside the inspected directory. Launchd can also inject variables through plist `EnvironmentVariables` or `launchctl setenv`. In each case, code runs before the wheel digest is accepted, which is the same failure class the review reproduced, and a clean filesystem inspection would still pass. The amendment should require that every pre-acceptance execution, and the generated plist, use a fixed minimal environment: Python isolated mode or explicit clearing of `PYTHON*` variables, and no user site. It should also require a U09 test for the injected-environment hook path. This stays within U09's files and its estimate.
2. **F2 (required): prune protects only the backup, not the other recovery material.** Line 9 makes prune refuse only when "its required retained backup" lies within the selected runtime directory. The accepted #94 plan (line 9 and line 26) also requires these to survive pruning: a retained recovery wheel, and the prior environment and plist bytes held by an unretired interrupted-upgrade record. Suppose a retained recovery wheel sits inside `versions/<version>-<digest>/`, or the selected version is the rollback target of a pending recovery record. Prune would then delete the material that recovery depends on, which is the same class as the reproduced backup deletion. The fix: prune must refuse, before any deletion, whenever any required recovery material physically lies within the selected runtime or is referenced by it. That material is the backup, the recovery wheel and any environment named by an unretired recovery record. Prune should use the same physical-ancestry check and have a test for each case.

## Required changes

1. **F1.** Line 9 should require a fixed, sanitized execution environment for every execution of a retained runtime before acceptance and for the generated plist. That means isolated mode or cleared `PYTHON*` variables and no user site, plus refusing unexpected plist environment entries. Add a U09 test in which an injected environment hook does not execute and the runtime is refused or ignored.
2. **F2.** Line 9 should extend the prune refusal from the retained backup to all required recovery material: the backup, the retained recovery wheel and any environment or plist referenced by an unretired interrupted-upgrade record. Use the same physical-ancestry validation, refuse before any deletion, and test each case.

## Optional suggestions

1. **PID reuse.** The repeated job inspection rejects a dying or restarted job. Adding the producer's process start time (or an equivalent per-process nonce) to the witness would also make it robust to PID reuse within the freshness window, at negligible cost in U08.
2. **Backup integrity after success.** The reproduced bug lost the backup during an *otherwise successful* restore. The restore and prune tests could assert that the backup's verified digest is unchanged after a successful operation, not only after a refusal.
3. **Cap pressure.** U08 and U09 are already at the four-hour cap and absorb new obligations here. Their JITs could forecast the added cases explicitly so that any overrun triggers the stop rule early.
4. **U10 estimate.** State explicitly that U10 stays at 3.5 agent-hours. The 48.5 total implies it, but line 16 names only U08, U12 and U09.

## Decision

revisions-requested
