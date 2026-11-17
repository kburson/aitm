<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-878d48dc52fb7e3aa45b7e4d0000888f"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-17-368-queue-inclusive-run-findings.md"
artifact_commit: "b3c025146fffc29ac3cef328819b46f868f8b715"
artifact_blob: "6f026669ea35c1c5661af7b9d4ce1c9e37b27b66"
artifact_digest: "sha256:e5b0a68a1c222db44adce3490a9331b8eea22506bb7198544f89bda3f5c9d360"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:1a4b5871d0ae663f960edb235062db5a061cf86161c6214f1801fff2d8265c30"
  identity_source: "runtime"
started_at: "2026-11-17T13:19:21.906Z"
submitted_at: "2026-11-17T13:22:12.702Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I reviewed `2026-11-17-368-queue-inclusive-run-findings.md` against the machine receipt
(`attachments/2026-11-17-368-queue-inclusive-run-receipt.json`), the accepted queue-inclusive execution packet, the
prior ancestry-run HOLD, the first hosted findings, and the product source on disk. The HOLD verdict is correct and the
report's factual claims match the receipt. I found no inaccuracy that needs a revision.

Verified against the receipt and packet:

- **Timing and budget.** Packet acceptance at 13:10:47Z. Run created at 13:11:28Z and job started at 13:11:31Z, a
  3-second allocation. Dispatch decision at 13:12:46.148321Z, before the 14:48:02Z deadline. Job completed at 13:13:06Z.
  I recomputed the charges from the 3.301 h opening at 13:03:02Z. Dispatch: 3.301 + 9m44.1s ≈ 3.4633 h. Completion:
  3.301 + 10m04s ≈ 3.4688 h. Both are under the 5.96 h packet ceiling and the 6.0 h overall ceiling.
- **Identity.** Head `56428a6c…`, tree `6f61e6d1…`, base `8218a69a…`, image `20261112.0504.1`, macOS 26.7.2 `25G332`
  on arm64, and artifact `14332020353` with digest `ce219514…6f33`. All match the packet and the receipt.
- **Isolation.** Five `ANCESTOR` readback rows plus the physical row. All eight entries in `entry_denials` are EPERM.
  `worker_controls`, `root_metadata_read_and_listing_denied` and `root_child_metadata_denied` are true.
- **Observer.** Stock providers: proc 30 and syscall 1,116. USDT is true. `trace_clean` is true and `tracer_exit` is 0.
- **Report replays.** `hosted-report-1.json` and `hosted-report-2.json` have identical SHA-256 values. The third replay
  is a 117-byte refusal, and `unsupported_change_refusal` is true.
- **Calibration.** The positive control has one native record and passes `test_success`. The failure control fails.
  The missing control reports `test_success` as missing.
- **Scoped run.** 30 outcomes: 14 passed, 16 failed, 0 missing. `native_records`/`native_direct_verified` is 74.
  `driver_exit` is 1, `post_run_custody` is `not reached`, and `github_conclusion` is `failure`.
- **Phase arithmetic.** `call-failed` has 9 IDs and `teardown-failed` has 15. Their intersection is exactly 8 IDs.
  Teardown-only IDs are 15 − 8 = 7. The only call-only ID is `test_platform_native_process_custody_has_no_provider_request`.
  The union is 16, which matches the `scoped-product.failed` list. `calls_passed` 21 + `calls_failed` 9 = 30. The
  report's 21/9/15 and 14/16 reconciliation is correct.
- **Lineage.** PID 2551 has UID 550 and parent 2550. PID 2550 has UID 0 and parent 1300.
- **Local controls.** The metadata-only sandbox probe shows `ancestor_stat` allowed, `ancestor_directory_open` EPERM,
  `ancestor_list` EPERM, and the direct child read succeeding at UID 501. The local suite control passed 30/30 with
  `isolated: false` on Python 3.13.9, pytest 9.2.0 and pluggy 1.7.0.
- **Historical comparison.** The first hosted run recorded 7 passed and 22 of 74 direct children matched
  (`2026-11-16-368-hosted-qualification-findings.md:74`). The prior ancestry attempt was the queue-only HOLD.

Verified against the product source in `/Users/kpburson/.codex/worktrees/aitm-344-functional-tia/trunk`, without Git.
I could not confirm that this worktree is at `8218a69a`.

- `scan.py:41` defines `_DIRECTORY_FLAGS = O_RDONLY | O_DIRECTORY | O_NOFOLLOW`. `scan.py:419-438` `_directory` opens
  `path.anchor` (`/`) and then `openat`s each component with those flags.
- `grok.py:777-799` `GrokAdapter.discover` wraps the walk in `except OSError: return`. Discovery therefore silently
  yields nothing when an ancestor open fails. The test suite's `(locator,) = …discover(…)` idiom then raises `ValueError`
  on an empty iterator, which is consistent with the reported locator failure.
- `install.py:215-249` `_process_identity` returns `None` when `info.uid != os.geteuid()`. On Darwin,
  `test_grok_scope_receipts.py:464-466` calls it on `os.getppid()` and asserts the result is not `None`. With a UID-0
  parent and a UID-550 worker, this fails exactly as described.

Limits of this review: I had no access to the authenticated hosted artifact or the `scoped-product.stdout.log` body. I
therefore could not independently confirm the per-ID exception classes behind the two failure-path attributions, or the
hosted interpreter and plugin versions. Those claims are consistent with the receipt's phase lists and the source, but
the committed receipt does not bind them.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. **Bind the failure-path attribution in durable evidence.** The receipt records which phase each ID failed in, but not
   why. The claims that all 15 teardown failures and the 8 body failures were transcript-locator `ValueError`s, and that
   the custody failure was the `parent is not None` assertion, rest on `scoped-product.stdout.log`. That log is retained
   only in GitHub artifact `14332020353`, which expires on `2026-12-01T13:12:58Z`. Consider adding a per-ID
   `{phase, exception_type, failing frame}` table to the receipt, or a short excerpt bound to the log's recorded SHA-256
   (`29bca4d3…`). This keeps the diagnosis checkable after the artifact expires.
2. **State plainly that the current layout makes the two requirements mutually exclusive.** On macOS, the sandbox gates
   `open(O_RDONLY|O_DIRECTORY)` on a directory and its listing with the same read-data permission. The local probe shows
   both returning EPERM together. So "descriptor-based traversal while preserving reviewed listing denials" cannot hold
   for the current `/Users/…/aitm368-hosted` ancestors. Saying so directly would make the next decision clearer. The
   options are to relocate the source/scratch root under ancestors whose listing can be admitted, or to approve a reviewed
   relaxation of the listing denials. Both remain outside this packet, as the report already says.
3. **Cite the source of "matching the hosted versions".** The receipt's `local_suite_control` records the local Python,
   pytest and pluggy versions, but no hosted counterpart is recorded. Consider adding the hosted versions to the receipt,
   or citing the runtime-admission manifest entry that binds them.
4. **Cite pinned source locations for the diagnosis.** The paragraphs on `sources.scan._directory`, `GrokAdapter.discover`
   and `install._process_identity` would be easier to re-verify with file:line or blob references at base `8218a69a`.
   The receipt's `source_sha256` covers only the ten harness files, not these product files.

## Decision

accepted
