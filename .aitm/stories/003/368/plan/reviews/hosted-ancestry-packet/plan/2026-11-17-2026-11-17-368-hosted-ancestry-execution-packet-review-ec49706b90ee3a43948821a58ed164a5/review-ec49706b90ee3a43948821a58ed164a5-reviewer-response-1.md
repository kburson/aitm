<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-ec49706b90ee3a43948821a58ed164a5"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-17-368-hosted-ancestry-execution-packet.md"
artifact_commit: "82535b53a0d4efd26a66d528f8d4c60b79500c62"
artifact_blob: "d4519756d4bf65a56a6f2d636e7104f9154ff637"
artifact_digest: "sha256:d16be608871c267227c3ed63d3ebcfab9049f68a9abcb0056069885359b1e7e8"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:9158ee2a1df867609e500da50f790e8fb88b27bbb5887d66955626f990108822"
  identity_source: "runtime"
started_at: "2026-11-17T12:36:58.818Z"
submitted_at: "2026-11-17T12:39:48.725Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I reviewed the execution packet at artifact digest `sha256:d16be608…e7e8` (commit `82535b53`). I checked it against the accepted implementation plan, the committed workflow sources in the held worktree, the local reproduction attachment, the image re-admission packet and the pinned product sources. I had no shell access in this session, so I could not run `git diff` or recompute blob or file SHA-256 values. Every check below comes from reading files directly.

Verified:

- **Plan binding.** The packet's plan digest `361618e5…885f` matches the accepted digest in the review manifest and reviewer response 2 of `review-84fdbdfe…`. `stage-b-inputs.json` carries the same digest and `plan_accepted_utc` `2026-11-17T12:31:32Z`.
- **Clock arithmetic.**
  - 12:31:32Z + floor(0.348 h × 3600 = 1252.8 s) = 1252 s gives `12:52:24Z`. This matches the packet, the inputs file and the attachment's `clock.dispatch_deadline`.
  - The cumulative charge at acceptance follows from the draft figure: 2.688 + (12:26:15 → 12:31:32 = 317 s = 0.088 h) = 2.776. The attachment records 2.775611.
  - The packet-submission figures are consistent with submission at about 12:36:02Z: 2.851 − 2.776 = 0.075 h = 270 s, and 2.227 − 2.152 = 0.075 h. That leaves 0.273 h ≈ 983 s to the same 12:52:24Z bound.
  - All values stay inside the 2.5 h admission/preflight stop, the 3.75 h packet limit and the 6 h overall limit.
- **Timed dispatch gate (`integrated.py:327-336, 363-368`).**
  - `authorize_dispatch` runs only on the `product=True` invocation. It runs after all three calibrations and `calibrate_intake`, and after boundary, trace, runtime install and replay in `main`. It runs before `product_invocation_started` is set and before `full.observe` launches anything.
  - It records `decision_utc` and `deadline_utc` before any refusal. It requires a strict `YYYY-MM-DDTHH:MM:SSZ` string; an impossible date such as `2026-11-31` fails in `strptime` with `ValueError`.
  - It refuses when the decision is later than the deadline. Sub-second precision makes this conservative.
  - In `main`, the `ValueError` becomes a HOLD at gate `calibration-and-scoped-observation` with `product_invocation_started: False`, and evidence is still published.
  - The deadline comes from the reviewed input file, so it cannot change across an exact-head retry.
  - The unit test covers: equal-to-deadline accept, +1 s expiry, `None`, empty, offset form, space form, invalid date and missing key. The red run in the attachment shows `AttributeError` for the missing function. The green run shows 13 tests passing, which matches "twelve existing plus the new dispatch test".
- **Profile delta (`admission.py:131-150`, `test_integrated.py:89-95`).** In the integrated builder, the single metadata rule is now the literals `/`, `/Users`, `/Users/Shared` and `ROOT`, derived from `ROOT.parents`. The non-integrated builder has no metadata rule.
  - The attachment's `prior_profile` and `revised_profile` differ only in that one line (`profile_delta`). The driver asserts `old.replace(before, after) == new`.
  - The `file-read-data (literal "/")` exception, the protected-path, network, write, `/dev/dtrace` and exec allowlist rules are unchanged.
- **Ancestry probe matches the product predicate.**
  - The probe's ownership/mode rule (`qualification.c:158-160`) is equivalent to `ledger._validated_path` (`ledger.py:198-208`). Both require a directory owned by root or the current uid, with group/other write allowed only on a root-owned sticky directory.
  - The `deny-delete` text in the C probe is byte-identical to `host_fs._ACL_DENY_DELETE`. The empty-ACL form `!#acl 1\n` and the ENOENT → none rule match `_check_mac_acl`.
  - `acl_get_link_np(..., ACL_TYPE_EXTENDED)` is the no-follow call the product uses. Any other ACL or error is refused (exit 83), so it fails closed.
  - Both the real and effective worker UID must equal the pinned non-root UID. `realpath(scratch)` must equal the pinned scratch path byte for byte.
- **Controller vs worker comparison (`admission.py:153-173`).**
  - Before running the probe, Python checks with `lstat` that the admission root is 0:0:0755 and scratch is uid:20:0700. It also checks that the home directory is a direct child of `/Users` and that the canary is a regular file.
  - The root-run `ancestry-readback` must return exactly six rows with empty stderr. The sandboxed worker's stdout must equal the controller stdout followed by the eight fixed EPERM rows, in the order the C loops emit them.
  - So a sandbox-masked ACL (an ENOENT inside the sandbox where the controller sees an ACL) would differ and refuse.
- **Negative controls.**
  - `opendir` must fail with exactly EPERM on `/Users`, `/Users/Shared` and the admission root.
  - `lstat` and `acl_get_link_np` must each fail with EPERM on the controller home and on the prefix-sharing canary. `open(O_RDONLY)` on the canary must also fail with EPERM.
  - A missing target gives ENOENT, which fails the probe.
  - The canary is created with `O_CREAT|O_EXCL|O_NOFOLLOW`, mode 0644 and public bytes (`admission.py:211-222`). Its uid, mode and SHA-256 are recorded and rechecked after the boundary (`admission.py:289-292`).
  - The probe runs only for the integrated (`admitted_executables`) path, before trace capability and any product execution.
  - `ancestry-probe.bin`, `ancestry-controller.*` and `ancestry-worker.*` are in the screened export list, next to the receipt's `probe_sha256` for the same root-owned staged binary.
- **Local reproduction.** The attachment shows:
  - prior profile → `LedgerError: Private ledger ancestry is unavailable` (exit 4);
  - revised profile → a six-identity chain, and `monitor_registry._directory` returning the exact synthetic physical path;
  - matching controller and worker rows, including all new EPERM rows;
  - a 39-entry source manifest checked byte-for-byte against `git show 8218a69…`;
  - `product_test_ids_executed: 0`;
  - `native_probe_source_sha256` equal to the packet's `qualification.c` SHA-256 `2764393a…7b0`.

  `monitor_registry._directory` uses `Path.resolve(strict=True)`, which needs only component metadata, so this is consistent with metadata-only ancestor grants.
- **Runtime pins.** Run `44024930299/1`, head `e38d67d0…`, artifact `14302787413`, and the archive, manifest and runtime SHA-256 values all match the reviewed image re-admission packet and `stage-b-inputs.json` `admission`. So do the 393/8,570/10 member counts and image `20261112.0504.1`.
- **Scope and status.** The scope statements match the plan: 30 IDs, 74 direct native processes, the 7/23 baseline kept visible, #368 open and #355 blocked. Local execution and resistance to unreviewed candidate code remain outside hosted PASS.

## Findings

None blocking.

Observations that need no change:

1. The packet says the controller "verifies its identity and public bytes" for the canary. In practice, the recorded and rechecked identity is owner uid, mode and SHA-256, not dev/inode. Combined with `O_EXCL|O_NOFOLLOW` creation and the `lstat` regular-file check, this is enough for a disposable VM. I note the wording only for precision.
2. The plan asks that "role and mode readbacks [be verified] in the probe". The implementation does this check in Python with `lstat` immediately before the probe. The probe then prints the full mode, and the controller and worker rows must match. The effect is equivalent, so I do not count this as a deviation.
3. The integrated receipt's top-level `plan_sha256` is still the original hosted plan constant. The new plan digest is bound through `stage-b-inputs.json` (`ancestry_execution.plan_sha256`) and its `assignment_input_sha256`. This is acceptable, but readers of the receipt should not take the top-level field as the ancestry plan binding.
4. **Timing risk.** The remaining window to 12:52:24Z is short compared with fresh user creation, probe compilation, boundary and trace, runtime restore (8,973 entries), two replays, three calibrations and intake refusals. A bounded timed HOLD before product dispatch is a realistic outcome. The packet and plan already accept this, and the gate fails closed with retained evidence, so it is not a defect.

## Required changes

None.

## Optional suggestions

1. When publishing the result, state the observed `dispatch_timing.decision_utc` next to the deadline, whichever outcome occurs. That keeps the timebox outcome auditable without anyone reading the raw receipt.
2. In the result write-up, note that the integrated receipt's top-level `plan_sha256` is the earlier hosted-plan constant, and that the ancestry plan is bound through the inputs file.

## Decision

accepted
