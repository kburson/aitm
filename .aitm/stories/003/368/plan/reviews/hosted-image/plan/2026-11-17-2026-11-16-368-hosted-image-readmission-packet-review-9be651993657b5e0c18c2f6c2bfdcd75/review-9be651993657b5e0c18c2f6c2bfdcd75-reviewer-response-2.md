<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-9be651993657b5e0c18c2f6c2bfdcd75"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-16-368-hosted-image-readmission-packet.md"
artifact_commit: "6df7bf7333df62371fb15e80574fc342551927af"
artifact_blob: "b5d244ba18db692df4be428aee138ebb68e79178"
artifact_digest: "sha256:1986cd3c8af25fef68f435877531ef13f214cb49ac3c1be117ce0b33acefecf8"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:d6251fd891350239116342c2c2cb3890ce5ea43fdbd601aaf99b554095c96576"
  identity_source: "runtime"
started_at: "2026-11-17T05:39:42.163Z"
submitted_at: "2026-11-17T05:43:30.443Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I re-reviewed the revised packet (blob `b5d244b`, digest `sha256:1986cd3c…`) against:

- the author's turn-1 response;
- the new attachment `.aitm/stories/003/368/attachments/2026-11-16-368-refreshed-image-dry-restore.json`;
- the existing attachment `2026-11-16-368-hosted-dry-restore.json`, which is unchanged and still records the accepted retry's dry restore of `5cf88db0…` at `3a0859d…`;
- the held worktree's `.github/spikes/368/stage-b-inputs.json`, which I read in turn 1.

Both turn-1 required changes are addressed.

- **Required change 1 (durable refreshed dry restore).** The new attachment is a separate record, so the earlier attachment remains intact as evidence for the accepted retry review. It binds the new restore to:
  - admission run `44024930299`, attempt `1` and artifact `14302787413`;
  - archive `3841df4c…`, manifest `1a5e9f5d…` and runtime archive `402dda54…`;
  - interpreter `a6d5935b…` and probe table `6f921286…`;
  - image `20261112.0504.1` and implementation head `ffe77e3e…`, with a different driver digest (`5a127f52…`) from the earlier run.

  Each value agrees with the packet's admission table and with the working-tree `stage-b-inputs.json`. The record gives 8,973 entries, made up of 8,570 regular files, 393 directories and 10 symlinks. Both access-exception counts, `files_missing_other_read` and `directories_missing_other_read_and_traverse`, are `0` for the rebuilt manifest. The record also has `instrumented_interpreter_executed: false`. Its scope states that the hosted root ownership transfer stayed outside the check. Together this restates, for the new runtime, the scan that ruled out turn-1 mechanism (b) in review `9e6f1dfb…`. The packet now links the record by relative path and gives its SHA-256, and it no longer relies on the fixed-string stdout hash alone.
- **Required change 2 (explicit identity delta).** The packet now says three things:
  - only the `admission` keys and `image_identity.image` changed;
  - every other bound identity key, including the native `ssh-keygen` digest, matches the previous admission;
  - the rejected job's full `identity` matches every new `image_identity` key.

  It replaces "stock SIP setting" with "SIP disabled (stock runner setting, unchanged)". This settles the reading I could only infer in turn 1.
- **Optional suggestions.** All three are taken up:
  - the packet explains why the probe-table digest is unchanged while the interpreter digest changed;
  - it states that a return to the earlier image during rollout is also an admission HOLD before product execution;
  - it names `ffe77e3e…` as the head for the eleven offline tests.

The integrated authority is unchanged from turn 1: one changed blob, `stage-b-inputs.json`, and an otherwise identical harness. The harness still refuses any further identity drift at `job-identity` and checks every new runtime digest in `install_bundle` before calibration. No product test can run unless the next job matches this pin and this runtime.

Limits of this review:

- I did not run Git, compute SHA-256 or blob IDs, query GitHub, or run tests. Bash beyond the prescribed peer-review command was unavailable, and Git use was out of scope.
- I did not verify the attachment's SHA-256 `329e3e18…`, workflow head `ffe77e3e…`, tree `65dccbb1…`, blob `732535f0…`, SHA-256 `f9b00f7c…`, the Stage A tree `672758a4…`, the single-blob diff, or the field-by-field identity comparison. These are taken from the packet, the attachment and the author response.
- I did not see the HOLD receipt, the admission receipt or the new `runtime-manifest.json`.

## Findings

None blocking. One wording note:

1. **"The stage independently recomputed…"** (packet line 34) does not say which stage. From context it means the Stage A re-admission build, whose `otool -s __TEXT __dof_python` read-back gave `6f921286…`, and also the local dry restore's Mach-O read-back. The meaning can be recovered from the table and the attachment, so I raise it only for clarity.

## Required changes

None.

## Optional suggestions

1. Change "The stage independently recomputed" to "The Stage A re-admission build and the local dry restore each recomputed" (Finding 1).
2. The attachment field `admission_artifact_sha256` holds the archive digest that the packet labels "archive sha256". Consider renaming it to `admission_archive_sha256` in any future receipt of this schema, so the terms match.

## Decision

accepted
