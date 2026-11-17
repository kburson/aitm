<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-c06f8b4bf4d27f7e06d1d22d7f382577"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-16-368-hosted-preflight-packet.md"
artifact_commit: "5eb4be712529b3e0fde2657f0c0b06e0cbfcf65e"
artifact_blob: "d0ec23bc2c34fd560fcfe304bd672af9a8843ee8"
artifact_digest: "sha256:effb021737e2324a2ccb78f6d00241de06fcdbd858be3f890be049d1dcddcf2d"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:102ec2fea75b4ebd4fe2a760a8281449fd5629f4d85c1c51dc4bdf17be118590"
  identity_source: "runtime"
started_at: "2026-11-17T05:06:03.516Z"
submitted_at: "2026-11-17T05:12:14.722Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I reviewed `2026-11-16-368-hosted-preflight-packet.md` (blob `d0ec23b`, digest `sha256:effb0217…`). I checked it against the accepted [hosted plan](../../../../2026-11-16-368-hosted-observation-plan.md) and its SAR, and against the Stage B sources it names. I read those sources as working-tree files in the held worktree `/Users/kpburson/.codex/worktrees/aitm-344-functional-tia/trunk`:

- `.github/workflows/aitm-368-hosted-qualification.yml`
- `.github/spikes/368/` files: `admission.py`, `integrated.py`, `observed.py`, `calibration.py`, `stage-b-inputs.json` and `test_admission.py`

I also read the #146 harness that Stage B loads at run time: `full_suite.py`, `selected_suite.py` and the `controller.py` outline from the `aitm-146-product-trial` worktree. To check the native-child enumeration, I read the product sources that launch `ssh-keygen`: the `isolated_grok_capture` fixture, `_IsolatedIssuer._verify_owner` and the `revise` callers in `test_grok_scope_receipts.py`. I also checked `tools/ci/policy.json`, `tools/ci/tia/suites.json` and `working_tree_obligations.json`.

Overall the packet is accurate and the harness matches it closely. I confirmed these points:

- **74 native launches.** The 22 fixture consumers each make one generate, sign and verify call in setup, which is 66. The four bodies that call `f.revise`, namely `source_approval…`, both `profile_revision…` rows and `rotation_between…`, each add one sign and one verify in call, which is 8 more. The remaining 8 IDs (`ordinary_checkout_mode…` and the seven `process_info_refuses_invalid_custody[…]` rows) do not use the fixture. The total is 74, which matches `native_children` and the packet text.
- **`native_shape` argv templates.** The three shapes match the product code exactly: the generate and sign argv in the fixture, and the 11-element verify argv with `control/<tmp>/allowed` and `signature` in `_verify_owner`.
- **Scope inputs.** The six `required_tests` in `policy.json` are the six IDs in `stage-b-inputs.json`, and none is in the Grok module. The two `suites.json` overrides select `test_service.py` and `test_cli_evidence.py`. `suites.json` has no entry for the module. The 30 IDs are identical to `working_tree_obligations.json`.
- **Product manifest.** It has 148 entries, all `executable: false`. `grok_scope_hook.py` carries the admitted comment digest `d71cd585…`.
- **Runtime import.** The `aitm_usage.pth` written by #146's `install_runtime` points to `<ROOT>/source/packages/aitm-usage/src`. Stage B stages `PRODUCT` at that same `ROOT / "source"` prefix. The admitted runtime therefore imports the staged copy that contains the comment, not a Stage A copy.
- **Stage A admission binding.** `receive` and `install_bundle` bind run, attempt, head, branch, actor, artifact name, artifact digest, receipt, manifest, runtime archive, per-file digests and modes, interpreter digest, probe table and pytest identity. The values match the packet.
- **Calibration.** It covers the plan's refusal list. The fixture with an independently observed failure and a stopped sibling relies on `test_failure` being defined before `test_success`, and it is.
- **Job identity.** `verify_job(FILES)` limits the head diff to the nine listed paths. The packet compares image, OS, Xcode, SDK, SIP and the `/usr/bin/ssh-keygen` digest with the admitted identity, and treats any drift as HOLD.

I am requesting one change (Required change 1). The packet says each native launch requires authenticated `/usr/bin/ssh-keygen` matched to controller-observed exec. But the kernel-side exec record that the harness reads is the process short name only. On Darwin, `curpsinfo->pr_psargs` is `p_comm`, and `validate_children` explicitly accepts the basename `ssh-keygen`. The full executable path comes only from the cooperative in-process event. The packet should either bind the path kernel-side or say exactly what is bound. The other items are fail-closed robustness or clarity points.

Limits of this review:

- I did not run Git, compute SHA-256 or blob IDs, or query GitHub. Bash was unavailable and Git use was out of scope.
- I read the held worktree's working files, not `git show 2909078…:<path>`. I did not verify the source table's blob and SHA-256 values, the #146 harness digests in `precedent_sha256`, or that the worktree files equal the committed bytes.
- I did not verify the Stage A run or artifact, the local report digests, or the #344 proof.
- The product test sources I read came from the same working tree, not from base `8218a69`.

## Findings

1. **The kernel exec record binds only `ssh-keygen`'s short name, not `/usr/bin/ssh-keygen`.** #146's `dtrace_program` records `proc:::exec-success` as `curpsinfo->pr_psargs`. On macOS, the `psinfo_t` translator fills `pr_psargs` from `p_comm`, without the path or arguments. `integrated.validate_children` acknowledges this by accepting `images[0].split()[0] in (KEYGEN, Path(KEYGEN).name)`. The full path and argv come only from `observed_init`'s `child-argument` event, which runs in the worker process. The DTrace origin filter limits which frame may emit that event, but not what the worker passes to `execve`.

   As a result, a child that execs any binary whose short name is `ssh-keygen` (for example a file the worker writes in its scratch directory, which the sandbox permits) and reports `/usr/bin/ssh-keygen` would pass. The job-start digest of `/usr/bin/ssh-keygen` proves the stock binary's bytes, not that the observed child executed it.

   For the reviewed closure this is a statement-accuracy issue rather than a demonstrated exploit, because the product source passes the literal path. It also overlaps the packet's stated `candidate_code_resistance=unqualified`. Even so, the packet's sentence "All require authenticated `/usr/bin/ssh-keygen` … matched controller-observed create, exec" claims a kernel binding of the executable that the evidence does not provide.

2. **The post-run report replay does not use the same invocation contract as the three bound replays.** In `main`, after observation, `working_tree_report` runs through `good(...)` with the inherited job environment. The earlier replays used `env={"PATH": "/usr/bin:/bin", "HOME": private, "LC_ALL": "C"}`. The result is then compared byte for byte with `hosted-report-1.json`. In the snapshot code I read, `snapshot.py` pins `/usr/bin/git` on Darwin and nulls the global and system Git config, so the difference is probably harmless. But the post-run check is not the same trusted invocation the packet binds. Any environment-sensitive output would produce a spurious HOLD and spend the hosted attempt.

3. **Some exception types skip the receipt.** `main` catches only `ValueError`, `OSError`, `SubprocessError`, `KeyError` and `IndexError`. An unexpected `StopIteration` (from `next(...)` in `calibrate_intake`), `TypeError` or `AttributeError` would escape before `publish`. The job would then have no `receipt.json` and no screened streams, and `upload-artifact` with `if-no-files-found: error` would fail. The outcome is still not a PASS, but the plan's evidence-custody rule expects a published HOLD with its streams.

4. **The new Stage B intake logic has no offline tests.** The workflow's "Check trace intake" step runs only `test_admission.py`, which exercises the Stage A `reconcile`. These pieces have no offline unit coverage: `native_shape` (relative, `..`, out-of-scratch, wrong namespace or principal, and wrong suffix refusals), `validate_children` (nonzero status, abnormal reason, two exec rows, path disagreement), `read_native`'s phase mapping, and the `allow_observed` anchor. The live calibration checks only the missing child and the unassigned child. The hosted plan asks for paired offline and hosted experiments.

5. **The phase mapping and the direct-child scope are narrower than the packet text suggests.** `read_native` changes phase only on `start`, `setup-ok`, `call-ok` and `end`. A child launched during teardown after `setup-failed` or `call-failed` is attributed to the earlier phase. This cannot produce a false PASS, because a failure blocks acceptance, but the receipt's phase rows would be wrong on failure runs. Also, `proc:::create` and `exec-success` are filtered to `pid == $target` and `ppid == $target`, so grandchildren are not observed. "Exactly 74 admitted native process launches" and "any discovered additional … launch" therefore cover direct children of the pytest process only.

## Required changes

1. Make the packet's native-child claim match the evidence. Choose one:
   - (a) **Bind the executable path kernel-side.** For example, add `syscall::execve:entry /ppid == $target && uid == <uid>/ { printf("… %s", copyinstr(arg0)); }`, or an equivalent exec-path probe for the actual spawn path, and require it to equal `/usr/bin/ssh-keygen`. Alternatively, restrict `process-exec*` in `worker.sb` to `/usr/bin/ssh-keygen` and the admitted interpreter paths. Prove that refusal in calibration with a worker-written `ssh-keygen` in scratch. Then update the source table, head, tree and packet.
   - (b) **Keep the harness as is and narrow the packet text.** State that the kernel binds create, exec, exit status, exit reason and the `ssh-keygen` short name to the attributed PID. State that the full executable path and argv come from the cooperative CPython event emitted at the allowed `observed_init` frame. State that the stock binary's digest is checked once at job start. List the executable-path binding with the other unqualified in-process properties.

## Optional suggestions

1. Run the post-run replay with the same `env=` and the same exit and stderr checks as the three bound replays (Finding 2).
2. Catch `Exception` in `main`, recording the type and message, so every failure path still publishes a HOLD receipt and the screened streams (Finding 3).
3. Add offline unit tests for `native_shape`, `validate_children`, the `read_native` phase mapping and the `allow_observed` anchor count. Run them in the "Check trace intake" step (Finding 4).
4. Map `setup-failed` and `call-failed` to `teardown` in `read_native`. Say in the packet that native-launch exactness applies to direct children of the pytest process (Finding 5).
5. State in the packet how the 74-launch enumeration was derived (source reading, a trusted local trace, or both), so that a multiplicity HOLD can be diagnosed. Also record the cumulative admission and preflight agent-hours at packet submission, so the plan's 3.75-hour gate for an accepted packet can be checked.
6. Note the operational risk that GitHub rolls the `macos-26` image past `20261102.0473.1` before the Stage B push. State that such drift is a re-admission HOLD and not a product finding.

## Decision

revisions-requested
