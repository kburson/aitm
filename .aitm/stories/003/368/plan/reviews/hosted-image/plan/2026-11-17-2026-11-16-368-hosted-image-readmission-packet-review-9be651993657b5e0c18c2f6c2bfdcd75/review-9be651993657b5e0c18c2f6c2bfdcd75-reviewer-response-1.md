<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-9be651993657b5e0c18c2f6c2bfdcd75"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-16-368-hosted-image-readmission-packet.md"
artifact_commit: "3a5cdce226af4c820df177c1d5023c7b542bdd99"
artifact_blob: "d7fff3c875c4c7b3abea3584a467b80fcbd9df40"
artifact_digest: "sha256:8c06223244f85a8f84140101811d3fdec55d9187d9d92677b270230fee24692e"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:d6251fd891350239116342c2c2cb3890ce5ea43fdbd601aaf99b554095c96576"
  identity_source: "runtime"
started_at: "2026-11-17T05:39:42.163Z"
submitted_at: "2026-11-17T05:41:36.929Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I reviewed `2026-11-16-368-hosted-image-readmission-packet.md` (blob `d7fff3c`, digest `sha256:8c062232…`) against:

- the accepted [Stage B preflight packet](../../../../2026-11-16-368-hosted-preflight-packet.md) and the accepted [restore retry packet](../../../../2026-11-16-368-hosted-restore-retry-packet.md), plus both reviewer responses of review `9e6f1dfb…`;
- the durable dry-restore attachment `.aitm/stories/003/368/attachments/2026-11-16-368-hosted-dry-restore.json`;
- the held worktree `/Users/kpburson/.codex/worktrees/aitm-344-functional-tia/trunk`, read as working-tree files: `.github/spikes/368/stage-b-inputs.json` (all of it), `integrated.py` (`main`, `install_bundle` checks at lines 110–137, the `image_identity` comparison at lines 431–435), and `admission.py` (`verify_job`, the probe-table and `python_sha256` build records).

What holds up:

- **Admission table.** All ten rows in the packet's table match the `admission` object in the working-tree `stage-b-inputs.json` exactly.
- **The HOLD was the designed outcome.** `main` records `receipt["identity"]` in `verify_job` and then requires every `image_identity` key to equal the pin before `prepare_boundary`, `trace_attempt` or `install_bundle`. A drift in `image` alone therefore gives `gate=job-identity`, no runtime load and zero product tests, as the packet states. This is the re-admission path that the hosted plan (Stage B ¶2) and the preflight packet's closing paragraph prescribe.
- **The new pin is narrow.** The packet says the HOLD job matched every other reviewed identity field. The new `image_identity` keeps macOS 26.7.2 / `25G332`, `arm64`, Xcode 26.6 / `17F113`, SDK 26.5, the clang 21.0.0 lines and SIP "disabled". This agrees with the preflight packet's "macOS 26.7.2 build 25G332, ARM64 … stock runner reported SIP disabled". So the only identity value that should differ from the accepted pin is `image`. The Stage B job will still refuse any further drift, including in `/usr/bin/ssh-keygen`.
- **The runtime is genuinely new and fully re-bound.** The archive, manifest, runtime archive, receipt and interpreter digests all differ from the accepted Stage A values (`19a4dc3f…`, `5cf88db0…`, `bc06090b…`, `33d8cfef…`, `fbe3a4ea…`). `install_bundle` checks each of these new values before calibration, as before. The probe-table digest `6f921286…` is unchanged. That is plausible: it hashes `otool -s __TEXT __dof_python` output for the same CPython sources and the same toolchain, while the interpreter digest changes for reasons outside that section (for example build-time strings).
- **Authority scope.** The packet says only `stage-b-inputs.json` changed relative to the accepted retry head `3a0859d…`, and only in its `admission` and `image_identity` keys. The scope, 30 IDs, 148-file product manifest, precedent hashes and harness are unchanged. If that is accurate, the harness that the restore-retry review accepted runs unchanged against new pins, which is the correct minimal change.

I am requesting revisions for one evidence-binding reason (Finding 1), with a smaller clarity point (Finding 2). Neither affects the harness. Both concern whether this packet, on its own, shows that the new archive was checked the way the restore-retry review required for the old one.

Limits of this review:

- I did not run Git, compute SHA-256 or blob IDs, query GitHub, or run tests. Bash beyond the two prescribed peer-review commands was unavailable, and Git use was out of scope.
- I did not run the prescribed `git diff 3a0859d… ffe77e3e… -- .github/spikes/368/stage-b-inputs.json`. I read the working-tree file and did not see the accepted version of `stage-b-inputs.json`. So I did not verify head `ffe77e3e…`, tree `65dccbb1…`, blob `732535f0…`, SHA-256 `f9b00f7c…`, the Stage A tree `672758a4…`, or that `image` is the only `image_identity` value that changed.
- I did not see either run's receipt or artifact, the HOLD job's identity record, or the new `runtime-manifest.json`. Statements about them are taken from the packet.

## Findings

1. **The new dry restore is not durably bound to the new archive, and the owner-only access scan is not restated for the rebuilt manifest.** The packet's only evidence for the dry restore is "stdout SHA-256 `df2b078f…`". That value is byte-identical to `stdout_sha256` in the existing attachment, which records the dry restore of the *old* manifest `5cf88db0…` at head `3a0859d…`. This is expected, because the stdout is a fixed string ("Exact staged and copied runtime modes and manifest match. Mach-O probe table digest matches.\n"). It follows that the hash carries no information about which manifest, archive or installer was checked. A reader cannot tell this run's evidence from the earlier one.

   This matters for one specific check. In review `9e6f1dfb…` turn 1, required change 1 asked for an offline scan of the admitted manifest for files without `o+r` and directories without `o+rx`. That scan is the evidence that ruled out a second `PermissionError` mechanism after the root `chown`. The ordinary-account dry restore cannot detect that mechanism, and the attachment says the root ownership transfer stayed outside its scope. The attachment's `files_missing_other_read: 0` and `directories_missing_other_read_and_traverse: 0` apply to `5cf88db0…`, not to the rebuilt `1a5e9f5d…`. The packet does not say that the scan was repeated, or give the new entry, file, directory and symlink counts. The rebuild used the same sources and toolchain, so a different result is unlikely. Still, the lchmod fix has not yet run on a hosted job, and the earlier analysis depended on this scan being clean.

2. **The identity delta is stated indirectly.** "Only its authenticated admission keys and image identity changed" does not say which `image_identity` fields changed. The narrow reading (only `image`) is supported only by inference from "Every other reviewed identity field matched" in the first paragraph. The difference matters to a reviewer: a changed `/usr/bin/ssh-keygen` digest, compiler or SDK would bear on the 74 reviewed incidental children and on probe provenance, which the hosted plan's step 1 binds. In the same way, "the stock SIP setting" is less precise than the pinned value, which is SIP *disabled*, as the preflight packet said explicitly.

## Required changes

1. Record a durable dry-restore receipt for the new archive under #368. Either add a new attachment or a dated second record; do not overwrite the existing one, because it remains the evidence for the accepted retry review. It should include:
   - the manifest SHA-256 `1a5e9f5d…`, and preferably the runtime archive SHA-256 `402dda54…`;
   - the implementation head the installer ran from;
   - the counts of entries, regular files, directories and symlinks;
   - `files_missing_other_read` and `directories_missing_other_read_and_traverse` for the new manifest;
   - the probe-table digest and the `instrumented_interpreter_executed: false` flag.

   Link the receipt and give its SHA-256 in the packet, in place of (or in addition to) the bare stdout hash. If either access count is non-zero, treat it as the turn-1 mechanism (b) in review `9e6f1dfb…` and resolve it before the push.
2. State explicitly which `image_identity` fields differ from the accepted `stage-b-inputs.json`. I expect this to be `image` only. Also state that the archived HOLD receipt's `identity` matches the new pin for every `image_identity` key. Replace "the stock SIP setting" with "SIP disabled (stock runner setting, unchanged)".

## Optional suggestions

1. Add one sentence explaining why the probe-table digest is unchanged while the interpreter digest changed. For example: the `__dof_python` section output is unchanged for identical sources and toolchain, while the interpreter differs in build-time data outside it. This saves later reviewers from asking whether the probe-table pin was copied rather than recomputed.
2. GitHub rolls out runner images gradually, and a job can land on either image during a rollout. Consider pushing Stage B promptly, and note in the packet that a HOLD caused by a newer image, or by a reversion to `20261102.0473.1`, needs a further re-admission and is not a product finding.
3. Say which head the "eleven offline harness tests" ran against: `ffe77e3e…`, or the same `3a0859d…` run recorded in the existing attachment.

## Decision

revisions-requested
