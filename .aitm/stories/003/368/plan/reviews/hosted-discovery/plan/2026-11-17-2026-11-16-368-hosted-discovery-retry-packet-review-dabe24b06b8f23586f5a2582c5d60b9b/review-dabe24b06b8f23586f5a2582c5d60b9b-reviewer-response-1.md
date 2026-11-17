<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-dabe24b06b8f23586f5a2582c5d60b9b"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-16-368-hosted-discovery-retry-packet.md"
artifact_commit: "6b7edfc7782c600fc805f97387269e4f17968333"
artifact_blob: "8bae4d50b334eccf4f2ae93f798f0f64f12b25e0"
artifact_digest: "sha256:e460f722a7398baff7aecff2a29f63c7e69c8b996338c28464780cdde9e84994"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:798081e6024e566a3c838afa796a5d1589eec2b43d480ae37902c4d6555493c0"
  identity_source: "runtime"
started_at: "2026-11-17T05:52:31.375Z"
submitted_at: "2026-11-17T05:56:30.037Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I reviewed `2026-11-16-368-hosted-discovery-retry-packet.md` (blob `8bae4d5`, digest `sha256:e460f722…`) against:

- the accepted [image re-admission packet](../../../../2026-11-16-368-hosted-image-readmission-packet.md) and its turn-1 reviewer response in review `9be65199…`;
- the durable attachment `.aitm/stories/003/368/attachments/2026-11-16-368-hosted-discovery-dry-check.json`, which I read in full;
- the held worktree `/Users/kpburson/.codex/worktrees/aitm-344-functional-tia/trunk`, read as working-tree files. Its `.git` file points at `trunk/.git/worktrees/trunk`, whose `HEAD` is `refs/heads/codex/368-hosted-qualification`, and that ref holds `3b603c6aa1c60b3dec895237beb2d3120a6914cf`, the head this packet authorizes. I read:
  - `admission.py`: `verify_job` (lines 93–120), `worker_command`, and `prepare_boundary` (lines 131–254), including the profile text and the new admission-root control;
  - `qualification.c`: `check` (lines 25–85), including the new `argc == 11` stat/opendir branch;
  - `integrated.py`: the constants (lines 17–36), `install_bundle`, `archive_products` and `run_scope` (lines 326–395), including the revised pytest argument vector;
  - `stage-b-inputs.json` (all of it) and the product `packages/aitm-usage/pyproject.toml`.

What holds up:

- **The policy change is as narrow as stated.** The only new policy line is `(allow file-read-metadata (literal "/Users/Shared/aitm368-hosted"))` (`admission.py:183`). It is a `literal` rule, not `subpath`, and it is emitted only when `admitted_executables` is non-empty, so only in the Stage B call (`integrated.py:438`). The Stage A call (`admission.py:489`) still gets the unchanged profile. The base `(deny file-read*)`, the allowed read roots, the network and write denials, the `/dev/dtrace` denial and the exec allowlist are unchanged. A metadata grant does not permit `open(O_DIRECTORY)`/`getdirentries`, which need `file-read-data`. So the worker still cannot enumerate `ROOT`, and it still cannot read or stat the `outside` marker or any other sibling under `ROOT`.
- **The live control is fail-closed and placed before any calibration.** In Stage B the boundary probe receives `ROOT` as `argv[10]`. It returns 78 if `stat` fails or `ROOT` is not a directory. It returns 79 if `opendir`/`readdir` produces an entry or fails with an errno other than `EACCES`/`EPERM`. `prepare_boundary` then requires both new lines in stdout. Any of these failures stops the job inside `prepare_boundary`, before `run_scope`. The existing same-named scratch executable, `/dev/dtrace`, loopback, checkout, controller-home, controller and credential cases still run in the same probe, as the packet says.
- **The launcher change is consistent with the bound IDs.** `observe` now passes `-c PRODUCT/packages/aitm-usage/pyproject.toml --rootdir PRODUCT --confcutdir PRODUCT` (`integrated.py:356–357`), where `PRODUCT = ROOT / "source"`. With the rootdir at `PRODUCT`, node IDs are relative to the repository root. This matches the 30 bound `packages/aitm-usage/tests/test_grok_scope_receipts.py::…` IDs and the `calibration/test_probe.py::test_{failure,success}` controls. The product `pyproject.toml` has no pytest section, so `-c` only pins the configuration and stops the upward search; it adds no `addopts`, markers or plugin settings. That file is already in the 148-file product manifest that `archive_products` checks before staging.
- **The allowlist claim holds.** `FILES = ALLOWED (5) + EXTRAS (5)` is the ten-path allowlist that `verify_job` checks as exact `A` additions over `BASE`. All three changed paths are in it. Stage A authority is still bound only by run, artifact, archive, receipt, manifest, runtime, interpreter and probe-table digests in `install_bundle`. Changing the Stage A probe sources (`admission.py`, `qualification.c`) therefore does not invalidate the reused admission: Stage B rebuilds the probe and the boundary from source in the job, and `receipt["boundary"]["profile_sha256"]` and `probe_sha256` record them.
- **The diagnosis is coherent.** Before this change pytest inferred its rootdir and config by walking up from the arguments. That walk reaches `ROOT`, where every read is denied, and an `EPERM` from `Path.is_file`/`stat` is not one of the errnos pathlib ignores. A `PermissionError` naming `ROOT`, zero collected items, `collection-end 0` and then `dispatch-refused inventory-mismatch` are what that failure should produce. The observer refused correctly, before dispatch. The packet also says the original launcher was reproduced locally and refused there first, which is the right order: reproduce, then fix.

I am requesting revisions for one evidence-binding reason (Finding 1). It does not affect the harness or the boundary. It is the same class of gap that review `9be65199…` raised for the dry restore: the attachment's stdout hashes cover fixed strings, so they do not show what was actually run or collected.

Limits of this review:

- I did not run Git, compute SHA-256 or blob IDs, query GitHub, or run tests. Bash beyond the two prescribed peer-review commands was unavailable, and Git use was out of scope. I did not run the prescribed `git diff ffe77e3e… 3b603c6a… -- .github/spikes/368`. So I did not verify tree `485cc52b…`, the three blob IDs or SHA-256 values, or that exactly these three paths changed. I read the working tree only, and I did not check it for uncommitted edits.
- I did not see run `44026166553` attempt 2, artifact `14302419973`, its receipt, the driver traceback, the observer trace or the platform streams. Statements about the hosted failure, the 9.2.0 readback, the replays and the trace contents come from the packet.
- I did not see the local collection driver (`collection_driver_sha256` `2470a35c…`) or the profile the local check used.

## Findings

1. **The local discovery check is not durably bound to what it ran or collected.** The packet's evidence that the fix works is the dry-check attachment. Its two content fields are fixed strings:
   - `collection_stdout` is a prose sentence ("Original discovery refused the ancestor. A literal metadata rule and explicit discovery scope collected both IDs. Directory listing stayed denied.\n"), and `collection_stdout_sha256` hashes that sentence;
   - `boundary_stdout` is the probe's fixed `puts` output, which any passing run produces byte for byte.

   Neither hash carries information about:
   - which profile text was applied. The attachment has no profile SHA-256, and "the same protected profile shape" is not a digest;
   - which node IDs were collected. The packet says "the two exact synthetic IDs", but the attachment does not list them or bind a digest of them;
   - where the original launcher failed. The packet says the hosted driver failed "while statting the known admission root", and that the local run reproduced the refusal. Neither the path, the errno nor the pytest frame is recorded for either run;
   - the driver itself. Only its hash is given, and the driver source is not retained anywhere reviewable under #368.

   This matters because the literal-`ROOT` rule fits only one specific failure. If pytest 9.2.0 also stats another denied path (for example `/Users/Shared`, `ROOT/pytest.ini` or `ROOT/conftest.py`), the literal rule does not cover it. The local check is the only evidence that `ROOT` itself is the only such path. A same-profile local run that collected both IDs would rule this out, but only if the attachment shows that the run used the generated Stage B profile and actually collected those IDs. As written, a reader cannot tell this run's evidence from a run that used a broader profile or collected nothing. If the guess is wrong, the hosted job fails closed: one more HOLD, and the charge grows. Safety is not at stake, but the packet's main claim rests on this record.

## Required changes

1. Strengthen the dry-check record under #368. Either amend this packet's attachment, which has not yet been accepted, or add a dated second record. Update the SHA-256 in the packet to match. It should include:
   - the SHA-256 of the worker profile the local check applied, and a statement that `prepare_boundary` at `3b603c6a…` generated it with the Stage B arguments (`INPUTS`, `EXECUTABLES`), with only path roots substituted for the local layout. If roots were substituted, state which ones;
   - for the original launcher: the denied path, the errno, and the innermost pytest frame (file, function, line) of the `PermissionError`. State whether this matches the hosted driver's frame in artifact `14302419973`;
   - for the revised launcher: the exact collected node IDs, or their SHA-256 together with the IDs, and the pytest exit status. State that the run included `-c`, `--rootdir` and `--confcutdir` exactly as in `integrated.py:356–357`;
   - the collection driver source. Either attach it or bind it to a committed path and blob, so that `collection_driver_sha256` refers to something reviewable.

   If the original-launcher frame shows a stat on any path other than literal `ROOT`, explain why the revised launcher avoids it, before the push.

## Optional suggestions

1. The live control proves that `ROOT` can be stat'ed and cannot be listed. It does not distinguish the reviewed `literal` rule from an accidental `subpath` rule, because a `subpath` metadata grant also leaves `opendir` denied. Consider also requiring that `stat` on a sibling under `ROOT` (for example the existing `outside` marker, `argv[4]`) fails with `EACCES`/`EPERM`. The probe could then print a third line, such as `DENY admission root child metadata`. That would make the narrowness a live, recorded property rather than one inferred from the profile text alone.
2. No offline test covers the change: `test_admission.py` and `test_integrated.py` are not in the delta, and the count stayed at eleven. Consider one small assertion that the generated Stage B profile contains exactly one `file-read-metadata` rule, a `literal` on `ROOT`, and that the Stage A profile contains none. Consider another that the `observe` argument vector contains `-c`, `--rootdir` and `--confcutdir` bound to `PRODUCT`.
3. The local check was collect-only. Positive calibration also dispatches `test_success`, with its native `generate` child, and the two failure controls. A local protected run of those three calibration invocations, with zero product tests, would lower the chance of a second hosted HOLD in the execution phase, for example under `--basetemp`, `tmp_path` or the native child, after collection now succeeds. If that was already done, say so in the packet.

## Decision

revisions-requested
