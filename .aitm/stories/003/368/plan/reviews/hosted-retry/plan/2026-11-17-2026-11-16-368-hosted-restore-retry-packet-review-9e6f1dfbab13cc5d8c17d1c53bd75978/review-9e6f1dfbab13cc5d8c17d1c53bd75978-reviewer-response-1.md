<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-9e6f1dfbab13cc5d8c17d1c53bd75978"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-16-368-hosted-restore-retry-packet.md"
artifact_commit: "41c129a1c5a10da34ead7afd74086d161cdcb411"
artifact_blob: "7352a3b8ab8f6e924078dd162459a1550e01da4c"
artifact_digest: "sha256:ba5f792ba3f84190926061c808a2e2c26b5d01d4f4cf79c555732d80fc22f00d"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:b06e9ca10c5c7a630bac2effe5a5a3757ebe6a0d49fb9165f20fe31a9b315605"
  identity_source: "runtime"
started_at: "2026-11-17T05:23:19.883Z"
submitted_at: "2026-11-17T05:25:29.748Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I reviewed `2026-11-16-368-hosted-restore-retry-packet.md` (blob `7352a3b`, digest `sha256:ba5f792b…`). I checked it against the accepted [Stage B packet](../../../../2026-11-16-368-hosted-preflight-packet.md) and the Stage B sources in the held worktree `/Users/kpburson/.codex/worktrees/aitm-344-functional-tia/trunk`, read as working-tree files:

- `.github/spikes/368/integrated.py` (all of it, especially `install_bundle` and the `except` block in `main`)
- `.github/spikes/368/admission.py` (`require`, `run`, `good`, `put_root`, `runtime_manifest` and `publish`)
- `.github/spikes/368/test_integrated.py`
- the `run:` steps of `.github/workflows/aitm-368-hosted-qualification.yml`

The change itself is small and sound as far as it goes. In the working-tree `install_bundle`, symlinks are created after all regular entries. The mode pass then runs in reverse archive order, so children are handled before parents. It uses `os.lchmod` for links, which sets the mode of the link without following it, and `Path.chmod` for everything else. The installed tree is then still compared in full with `runtime_manifest(INSTALL, VENV) == manifest`, which records `lstat` modes for links. Any mode the restore still gets wrong will therefore fail closed with `installed runtime differs`. The new `os_failure` record holds only `errno`, a frame's basename, function name and line number. It does not hold `str(error)` or the path, so the receipt does not gain any new path or environment content.

I am requesting revisions for two reasons, both about whether the retry will be informative:

- The packet's diagnosis may not explain the hosted `PermissionError` (Finding 1). A cheap offline check can find a second plausible cause before the hosted run is spent.
- The new diagnostic records the innermost traceback frame. For most of the likely failure sites, that frame is in the standard library, not in the spike (Finding 2). The packet's claim that "the next HOLD can be diagnosed" would then usually not hold.

Limits of this review:

- I did not run Git, compute SHA-256 or blob IDs, or query GitHub. Bash beyond the two prescribed peer-review commands was unavailable, and Git use was out of scope.
- I did not run the prescribed `git diff 58ebe2c… 1f036b3…`. I read the worktree's current `integrated.py` rather than the committed delta. I did not verify the head, the tree, blob `837402c…`, SHA-256 `3e4bf1a6…`, or the claim that `integrated.py` is the only changed path.
- I did not see the first attempt's receipt or artifact, the admitted `runtime-manifest.json`, or the local dry-restore output. Statements about them are taken from the packet.

## Findings

1. **The symlink-mode defect alone does not explain a `PermissionError`, and the dry restore did not exercise the step most likely to raise one.** Before this change, a link mode of `0700` against `0755` in the manifest makes `runtime_manifest(...) == manifest` false. That raises `ValueError("installed runtime differs")`, not `PermissionError`. A `PermissionError` at the `runtime-install` gate therefore needs a different mechanism. Two mechanisms are plausible:

   - (a) Darwin enforces permissions on a root-owned `0700` link when the non-root controller reads or follows it, through `readlink` or `resolve(strict=True)` in `runtime_manifest`. If so, the fix does address the hosted failure.
   - (b) After `ditto` and `chown -Rh root:wheel`, the controller still has to traverse and read every entry. It does this through `rglob`, `lstat`, `digest` and `resolve`, then `digest(python)` and `otool`. Any manifest entry that Stage A's build user could read only as owner becomes unreadable once root owns it. That means a file without `o+r` or a directory without `o+rx`. The result is a `PermissionError` that this change does not touch.

   The local replay was filesystem-only and ran as the ordinary account. On the packet's own description, it never ran the `sudo ditto`, root `chown` and non-root read-back sequence where (b) would appear. So it cannot tell (a) from (b). This matters because the packet already says the error was not conclusively attributed. Mechanism (b) can be checked offline in seconds from the admitted `runtime-manifest.json` alone.

2. **The new `os_failure` frame will usually point into the standard library rather than the spike.** `main` walks to the innermost frame of `error.__traceback__`. For the likely failure sites:

   - `Path.lstat`, `Path.resolve`, `Path.rglob`, `Path.open` and `Path.chmod` in `runtime_manifest` and `install_bundle`: the innermost Python frame is in `pathlib`.
   - `subprocess.run` launch failures, for example from `run("/usr/bin/otool", …)` or the venv `python`: the frame is `subprocess._execute_child`.

   Only C-level calls made directly from spike code (`os.readlink`, `os.lchmod`, builtin `open` in `digest`) give a spike frame. A future HOLD would typically read as something like `{"errno": 13, "file": "_local.py", "function": "lstat"}`. That does not say which spike line or which runtime entry failed, which is the stated purpose of the change. `error.filename`, the most useful field for a `PermissionError`, is dropped entirely, even in a sanitized form.

3. **Neither the restore change nor the diagnostic has an offline test.** `test_integrated.py` is unchanged and does not import `install_bundle` or `main`. The "nine offline tests" are the earlier intake and observer tests. They pass whether or not links are given the manifest mode, and whether or not `os_failure` is well formed. The hosted plan asks for paired offline and hosted evidence. Here the only proof of the corrected behaviour is an unrecorded local dry run.

4. **Minor wording and evidence binding.** The packet says the HOLD was "at runtime import". The harness's gate names are `runtime-install`, and later `assignment-replay`. The receipt fields that support the diagnosis are not quoted: `gate`, `failure_type`, `failure`, and the last `raw` streams present. The local dry-restore claim, "matched all 8,973 entries and the probe table digest", gives no record path, digest or scope. Scope means whether it covered only the extraction tree or also a `ditto` copy.

## Required changes

1. Before the hosted retry, scan the admitted `runtime-manifest.json` offline for mechanism (b) and record the result in the packet. Count the files whose mode lacks `0o004` and the directories whose mode lacks `0o005`.
   - If any exist, either change the restore so the non-root controller can read them (for example, verify before the root `chown`, or restrict the read-back to root through `sudo`), or explain why they are unreachable.
   - If none exist, state that, so mechanism (a) is the remaining explanation and the retry tests it directly.
2. Make `os_failure` locate the failure in spike code. Record the innermost frame whose `co_filename` is under `HERE`, in addition to (or instead of) the leaf frame. Add a sanitized `error.filename`, for example made relative to `ROOT` or to the evidence directory, or reduced to a fixed category such as `runtime/<relative>` or `private/<name>`. Leave it out only where it would be outside those roots. Update the head, tree, blob and SHA-256 in the packet.

## Optional suggestions

1. Add an offline test that runs `install_bundle`'s extraction and mode pass on a small synthetic tar under `umask 0o077`, containing a directory, a file and a relative link. Assert that the `lstat` modes equal the manifest, including the link. Add another test that raises a `PermissionError` through a `pathlib` call inside a spike function and checks the recorded spike frame and sanitized filename (Finding 3). Both need a small refactor that separates extraction from the root install.
2. Quote the first attempt's receipt `gate`, `failure_type` and `failure` values, and replace "runtime import" with the harness gate name (Finding 4).
3. Record the local dry restore as a durable artifact under #368. Include its scope (extraction only, or a copy as well), entry count, probe-table digest and the commit it ran against.
4. If practical, run the local dry restore once more through a root-owned copy and a non-root read-back. Use the same `ditto` and `chown -Rh` sequence, still without executing the interpreter. This reproduces the hosted ownership step and would settle Finding 1 without a hosted attempt.

## Decision

revisions-requested
