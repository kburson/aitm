<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-9e6f1dfbab13cc5d8c17d1c53bd75978"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-16-368-hosted-restore-retry-packet.md"
artifact_commit: "3b1b2813579082046e6527847dc5f8d4c8fcfc30"
artifact_blob: "6e61eaa157b9c2fd4699c86c0bceff21e495c179"
artifact_digest: "sha256:086cade1941fe06df033a9f6cf91938f4ae00be6e7bd1cbf667f50697273b693"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:b06e9ca10c5c7a630bac2effe5a5a3757ebe6a0d49fb9165f20fe31a9b315605"
  identity_source: "runtime"
started_at: "2026-11-17T05:23:19.883Z"
submitted_at: "2026-11-17T05:30:07.316Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I re-reviewed the revised packet (blob `6e61eaa`, digest `sha256:086cade1…`) against the author's turn-1 response and these files:

- the working-tree `.github/spikes/368/integrated.py` in the held worktree: `extract_runtime`, `install_bundle`, `describe_os_error` and the `except` block in `main`
- the same worktree's `test_integrated.py`
- `admission.py`'s `HERE`, `ROOT` and `runtime_manifest`
- the dry-restore attachment `.aitm/stories/003/368/attachments/2026-11-16-368-hosted-dry-restore.json`

Both turn-1 required changes are addressed.

- **Required change 1 (manifest access scan).** The attachment records 8,570 regular files, 393 directories and 10 symlinks. That totals the 8,973 admitted entries. It reports `files_missing_other_read: 0` and `directories_missing_other_read_and_traverse: 0` against manifest `5cf88db0…`, which is the admitted manifest digest in the accepted Stage B packet. Its probe-table digest `6f921286…` matches the admitted value. This rules out mechanism (b) from turn 1: an owner-only file or directory made unreadable by the root `chown`.

  The remaining hypothesis is consistent with the harness. Before this change, the installed links stayed at `0700`: the dry restore shows that `ditto` carries link modes. `runtime_manifest` then calls `path.resolve(strict=True)` and `os.readlink` on each link as the non-root controller. On XNU, `readlink` authorizes read-data access on the link vnode, so a root-owned `0700` link would plausibly refuse it with `EACCES`. That produces a `PermissionError` at `runtime-install` before any probe-table or pytest-identity streams are written. This matches the quoted receipt and the stream inventory. The packet correctly leaves the root-ownership step as what the hosted retry tests.

- **Required change 2 (diagnostic location).** `describe_os_error` walks the whole traceback and keeps two frames:
  - `leaf`: the innermost frame
  - `spike`: the innermost frame whose `co_filename` is under `HERE`

  It adds `path` only when `error.filename` is absolute, has no `..`, and lies under `ROOT` (`/Users/Shared/aitm368-hosted`) or the private evidence directory. The path is then rendered relative, as `runtime/…` or `private/…`. `str(error)` is still left out for non-`ValueError` failures. The new receipt content is therefore limited to controlled relative paths, basenames, function names and line numbers.

- **Offline coverage (Finding 3).** Extraction is now the separate `extract_runtime`. `RuntimeRestoreTest` covers both turn-1 gaps:
  - It extracts a synthetic directory, file and relative link under `umask 0o077` and asserts each `lstat` mode and the link target.
  - It forces a `PermissionError` through a spike function and asserts the `errno`, the spike function, the relative `private/…` path, and that an out-of-root filename is omitted.

  The workflow's `unittest discover` step runs these tests in the hosted job.

- **Wording and evidence (Finding 4).** The packet now quotes `gate=runtime-install`, `failure_type` and `failure`. It names the streams that are present and absent, and links a durable dry-restore receipt that states its scope.

The authority section now lists two changed paths, both within the existing ten-path allowlist. `verify_job` checks additions against that allowlist, so this does not widen the job's authority.

Limits of this review:

- I did not run Git, compute SHA-256 or blob IDs, query GitHub, or run the tests. Bash beyond the prescribed peer-review commands was unavailable, and Git use was out of scope.
- I read the held worktree's current files, not `git diff 58ebe2c… 3a0859d…`. I did not verify head `3a0859d…`, tree `d6144f2…`, the two blob and SHA-256 rows, the attachment's own SHA-256 `b10bd236…`, or the "eleven tests passed" claim.
- I did not see the first attempt's receipt or the admitted manifest itself. Their contents are taken from the packet and the attachment.

## Findings

None blocking. One residual note:

1. **The `spike` frame depends on `co_filename` matching `HERE` after symlink resolution.** `HERE` is `Path(__file__).resolve().parent`, but `co_filename` is not resolved. If the hosted checkout path ever went through a symlink, `spike` would be absent and only `leaf` would be recorded. On the standard runner workspace path this should not happen, and the result would still be a correct HOLD with less detail. I note it only so a missing `spike` key is not mistaken for a failure outside the spike.

## Required changes

None.

## Optional suggestions

1. In `describe_os_error`, compare `Path(code.co_filename).resolve()` with `HERE` so the spike frame does not depend on the checkout path being free of symlinks (Finding 1).
2. Consider also recording a sanitized `error.filename2`, for failures in two-path calls such as `rename` or `symlink`. None of those calls is on the current `runtime-install` path, so this is only for future gates.

## Decision

accepted
