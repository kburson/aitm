<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-84fdbdfe0dd75c4a33ae32978465093a"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-17-368-hosted-ancestry-implementation-plan.md"
artifact_commit: "d4bb3d7f6bdaf0c8d937ae79b7ac3381d15fa296"
artifact_blob: "8810fd841a5da4bd9f7e3459acb87b39719cbf5d"
artifact_digest: "sha256:2ca6900a4c72224c44c710e32d8ed1f800f4a8e1c811a8c3c5eeb58d32959182"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:a3aefea571c34dba0defe3439ea1d9d5946cf7b46dd4524a6cd5b3df66a84530"
  identity_source: "runtime"
started_at: "2026-11-17T12:24:55.979Z"
submitted_at: "2026-11-17T12:28:53.335Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I reviewed the implementation plan at artifact digest `sha256:2ca6900a…9182` (commit `d4bb3d7f`). I checked it against:

- the predecessor plan `2026-11-17-368-hosted-ancestry-plan.md` and its SAR response (`review-60b56c66…`, revisions-requested);
- the accepted hosted plan `2026-11-16-368-hosted-observation-plan.md`, especially the stop rules;
- the reviewed findings `2026-11-16-368-hosted-qualification-findings.md`;
- the paired receipt `attachments/2026-11-16-368-hosted-qualification-receipt.json`;
- the retained run 44028499403 profile `raw/worker.sb` and `raw/scoped-product.stdout.log`;
- the trusted pinned product sources in the local cache: `ledger.py`, `host_fs.py`, `monitor_registry.py`, `tests/test_grok_scope_receipts.py`, and the `_control_root` monkeypatches across the test suite.

I could not read the spike sources (`admission.py`, `qualification.c`, `test_integrated.py`) at `d06b0e7f`. They are not in this worktree, and the review rules prohibit Git use. Claims about how the controller creates the admission root and scratch root are therefore checked only as bound expectations that the planned probe enforces fail-closed.

**Both prior required changes are addressed:**

- **Prior RC1 (predicate-enforcing probe).** Item 3 now requires all of the following on the four literal ancestors and the scratch root, as the actual worker:
  - a directory owned by root or the worker;
  - group/other write bits only on a root-owned sticky directory;
  - an ACL that is ENOENT, exactly `!#acl 1\n`, or the pinned non-inheriting everyone-deny-delete text;
  - fixed rows with ACL class enums only;
  - explicit root:wheel 0755 and worker:staff 0700 expectations for the admission root and scratch root.

  This matches `ledger._validated_path` (`ledger.py:193-221`) and `host_fs._check_mac_acl` (`host_fs.py:12-17, 41-63`). The deny-delete text is accepted only for ancestors (`ancestor=True`), and the probe's five directories are all ancestors of the product's private paths, so the acceptance set is not too wide. Because the accepted set excludes inheritable entries, pytest-created descendants cannot inherit an unsafe ACL, which `_check_path(..., ancestor=False)` would refuse. Item 4 states that the same-account local check leaves cross-UID ownership to the hosted gate.
- **Prior RC2 (budget).** Item 7 names the 2.5, 3.75 and 6-hour limits. It specifies the carried-forward 2.152 h, the closeout interval, the pickup start (12:08:39 UTC), and the checkpoints at acceptance, packet submission and pre-dispatch, with a bounded HOLD on expiry.

**Prior optional suggestions:**

- Suggestion 1 is adopted in item 3: the probe is called only for Stage B's integrated profile.
- Suggestion 2 is adopted in item 4: the complete positive and negative probe runs locally, including the EPERM controls.
- Suggestion 3 (local smoke of the 30 IDs) is explicitly declined. Item 4 says the masked bodies are first dispatched in the hosted run, so a body-level HOLD would not be unforeseen. That is an acceptable scope choice.

**The policy change still fits the evidence:**

- The retained profile grants `/` only `file-read-data` and has no rule for `/Users` or `/Users/Shared`. The walk therefore fails at `lstat("/")`, the first ancestor, and nothing below it was ever evaluated on hosted.
- Python's `posixpath.realpath` uses per-component `lstat`. Darwin's `acl_get_link_np` fails in `lstatx_np` before classifying the ACL. A metadata-only literal grant therefore covers both the ledger and `monitor_registry._directory`, while `opendir` on those directories stays denied.

**Other checks:**

- The control-root concern does not apply. `Ledger.initialize` → `project_guard` → `_guard_path` resolves `account_control_root(worker_uid)`, which would otherwise walk the worker's home outside the sandbox. The scoped fixture chain (`isolated_grok_capture`, `test_monitor_grok_capture.py:343`) monkeypatches `ledger._control_root` to `tmp_path / "control"`, so no home-directory grant is needed.
- The supply-chain additions in item 5 close the remaining packet-level gaps: GitHub artifact digest matched to the downloaded SHA-256 before extraction, prefix and link confinement, installer manifest recheck, and compiled-probe hash comparison.

**One material issue remains: execution feasibility under the plan's own budget accounting.** The plan never states the remaining headroom. Under its own conservative classification, the admission/preflight headroom is about 0.35 h before implementation starts, so the plan is very likely to stop at a bounded HOLD before an accepted packet exists. The owner should see this before execution begins.

## Findings

1. **The remaining budget headroom is not computed, and the binding 2.5-hour admission/preflight limit leaves about 21 minutes for all of the plan's pre-dispatch work.** (Required)
   - Item 7 states that "the 2.152-hour historical figure is a conservative upper bound for prior runner admission/preflight", and that "the current admission/preflight clock starts at accepted plan execution and includes packet prep and review". Applied to the cumulative 2.5-hour stop, this leaves 2.5 − 2.152 = **0.348 h (≈21 min)** of admission/preflight time from plan acceptance onward.
   - That window must cover every pre-dispatch step:
     - the red/green boundary test change and `boundary_profile` rule;
     - a new native `ancestry` probe in `qualification.c`, with predicate, ownership/mode and EPERM negative controls;
     - the full spike suite;
     - the ordinary-account local regression under the prior and revised generated profiles, with staged pinned sources and manifest verification;
     - the execution packet;
     - an independent Opus 5.5/high packet review;
     - presumably the fresh hosted admission of the revised policy that item 5 places inside the integrated job.

     Reaching an accepted packet in that window is not realistic.
   - The packet limit is less tight but still unstated. The receipt records `hosted_last_run_finished_at` = `2026-11-17T06:05:28Z`. The closeout interval to the 06:20 UTC upper bound is therefore 0.242 h, giving 2.394 h before this pickup. Adding the pickup from 12:08:39 UTC puts the cumulative charge at roughly 2.7–2.9 h at plan acceptance, which leaves only about 0.85–1.05 h before the 3.75-hour packet gate.
   - The plan also does not say whether the in-job fresh admission of the revised policy (item 5) is charged as admission/preflight or as product execution. That classification decides whether the hosted job itself can start under the 2.5-hour stop.
   - **Consequence:** the plan is formally compliant, since expiry records a bounded HOLD. In practice, though, its own arithmetic predicts a HOLD part-way through implementation or packet review, with no new hosted evidence. That outcome should be a conscious owner decision before execution, not a surprise discovered at a checkpoint.

2. **The non-integrated builder test does not cover the probe call site.** (Optional)
   - Item 2's test asserts that the non-integrated builder adds no metadata rule. Item 3 says the `ancestry` probe is called "only for Stage B's integrated profile".
   - No test asserts the call-site condition. A refactor that also called the probe on the non-integrated path would fail only at Stage A runtime.

3. **Ancestors below the scratch root are not covered by the probe.** (Optional)
   - The product's walk also passes through `/Users/Shared/aitm368-hosted/worker/pytest` (the basetemp, per `scoped-product.stdout.log`) and the per-test numbered directories. These are outside the probe's five directories.
   - They are safe only if pytest, running as the worker, creates them at mode 0700 and the controller does not pre-create basetemp. This is very likely true, but the plan does not state it.

4. **The rebind condition overlaps with the retry and new-image rules.** (Optional)
   - Item 1 allows a reviewed `stage-b-inputs.json` rebind "if a genuinely new runner image requires it". Item 5 separately says an image mismatch refuses and may be retried on the same pin, while an unadmitted platform needs a fresh Stage A build and packet review.
   - It is not stated whether landing on the other already-admitted image (`20261102.0473.1`, admission run 44020525466) permits a rebind to that image's runtime or only a retry.

## Required changes

1. **State the computed budget headroom and make the feasibility decision explicit before execution.**
   - In item 7 (or a recorded acceptance note bound by the packet), state the exact figures at plan acceptance:
     - the cumulative overall/packet charge: 2.152 h + 0.242 h for 06:05:28→06:20 UTC + the pickup since 12:08:39 UTC;
     - the remaining headroom to 3.75 h and to 6 h;
     - the remaining admission/preflight headroom: 2.5 − 2.152 = 0.348 h.
   - State whether the fresh hosted admission of the revised policy inside the integrated job is charged as admission/preflight or as execution.
   - Then do one of the following:
     - (a) record before implementation starts that the owner has explicitly re-authorized the admission/preflight limit for this pickup, with a stated new bound; or
     - (b) state that execution proceeds knowing the 2.5-hour stop is expected to trigger before packet acceptance, and that the expected result is a bounded HOLD that retains the implemented, locally regressed revision for a later pickup.

## Optional suggestions

1. Extend the item 2 unit test, or add a sibling test, to assert that `prepare_boundary` invokes the `ancestry` probe only for the integrated profile, and that the non-integrated path neither calls it nor expects it to pass.
2. In the packet, state that the controller does not pre-create the pytest basetemp under the scratch root, and that pytest (as the worker) creates basetemp and numbered directories at 0700. Alternatively, have the controller record their owner/mode from the post-run scratch replay so that ancestry below the scratch root is evidenced.
3. Clarify item 1's rebind condition. Say whether a fresh allocation onto the previously admitted `20261102.0473.1` image may rebind to that image's admitted runtime, which needs a reviewed rebind, or must only be retried until the bound `20261112.0504.1` image is allocated.
4. In the packet, cite the `admission.py` lines that install the admission root (root:wheel 0755) and the scratch root (worker:staff 0700). This lets the bound expectation in item 3 be checked against the source as well as at runtime.

## Decision

revisions-requested
