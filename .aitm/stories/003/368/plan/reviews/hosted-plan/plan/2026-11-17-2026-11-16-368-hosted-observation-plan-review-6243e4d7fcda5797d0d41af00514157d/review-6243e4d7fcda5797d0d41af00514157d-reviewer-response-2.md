<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-6243e4d7fcda5797d0d41af00514157d"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-16-368-hosted-observation-plan.md"
artifact_commit: "4d4458ddb0a50da9f68c7cceee61d03a23d2dadf"
artifact_blob: "b3525957973846479093ef5313165a08d2c92443"
artifact_digest: "sha256:51f56908994e273e9adce20f5d60813cb7b45cddd52051580241f9119e47bba9"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:8fc7ae3d6719f6e60e348c7e1e29c6f1abc1a36bb6a271375be89095a109ecba"
  identity_source: "runtime"
started_at: "2026-11-17T04:30:53.831Z"
submitted_at: "2026-11-17T04:36:58.284Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I re-reviewed the revised plan (blob `b352595`, digest `sha256:51f56908…`, which matches the author response's stated digest). I checked it against my round-1 findings, the author's dispositions, and the same sources as before: the accepted local plan, the live-tracing HOLD, and #146's selected-observation findings and independent review. Each of the three required changes is resolved in the artifact text, not only in the author response:

1. **Raw evidence export (round-1 Finding 1).** The first Evidence bullet now meets the requirement:
   - It exports a reviewed allowlist of byte-exact controller, observer, process-event, driver and build streams, with byte counts and SHA-256 values.
   - Redaction is allowed only through a reviewed, pinned, deterministic sanitizer. The sanitizer must record raw-input and output digests and preserve every field consumed downstream.
   - A sensitive stream that is required for review becomes a HOLD.
   - The artifact must be downloaded before any rerun.
   - The trusted side must independently reparse the evidence, verify digests and recompute the verdict. A missing or unparseable required stream is a HOLD.

   This is equivalent to the #146 precedent. The misleading "synthetic evidence bundle" wording is gone.
2. **Runtime build and cross-job admission (round-1 Finding 2).** Stage A ¶3 chooses option (b):
   - The build runs after the capability gate, using reviewed commands, pinned public sources, the patches and the #368 product lock on the same hosted image.
   - The bytes are installed at a stable prefix, with a build log, toolchain identities, a per-file mode and SHA-256 manifest, interpreter and pytest digests, and the Mach-O probe-table digest.
   - The plan checks that no Stage A-only inputs are embedded.
   - The bundle is exported, downloaded before any rerun, verified through the authenticated run, attempt and artifact, and bound in the packet. Build failure or missing provenance stops Stage B.

   Stage B ¶2 then verifies and unpacks the bytes at the exact prefix. It rechecks the manifest, probe table, installed pytest and live provider availability before calibration. Image drift is a HOLD. The packet reviewer can now see exactly which runtime bytes are being admitted.
3. **Tree binding and replay location (round-1 Finding 3).** "Bind the authority" now does the following:
   - It enumerates the only branch additions: the workflow file plus allowlisted files under `.github/spikes/368/`.
   - It binds their blob digests and the expected job tree.
   - It requires the run head's tree to differ from `90f2cc40` only by those additions.
   - It pins both the tooling and candidate checkouts to `8218a69`/`90f2cc40` in both jobs.
   - It places the three CLI replays on the trusted local side before packet review, and repeats them on the hosted controller before calibration, with cross-location comparison.

   Stage B ¶3 now names which snapshots are rechecked.

The optional suggestions were also adopted:

- The USDT check is now unconditional.
- Stage B is a single named fresh job.
- The six `required_tests` now cite `tools/ci/policy.json`.
- The workflow uses least-privilege `contents: read`, plus `actions: read` only in Stage B, with branch, repository, ref and actor checks.
- The plan checks other branch triggers.
- A fenced invocation is now defined: no surviving worker process and a scratch reset before each invocation.

The revisions introduce no new trust gap. The experiment question, scope, unqualified properties, stop rules and #355 hold are unchanged.

Limits of this review: as in round 1, I did not run Git, query GitHub or compute digests. I did not inspect the `16df827e` harness, the `8218a69` lock or a live hosted image. Those checks belong to the Stage A admission receipt and the independent packet review.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. "Check other branch triggers" does not say what result is expected. Consider recording the outcome in the Stage A receipt: either no other workflow fires on `codex/368-hosted-qualification`, or any run that does fire is listed and excluded from evidence.
2. Stage A ¶3 still calls the Stage A run the "admission-only job", but that job now also builds the runtime. Consider "admission and runtime-build job". Also consider recording a build failure as a HOLD distinct from a capability HOLD, so the findings report separates the two causes.
3. The "stable private runtime prefix" is later exported as a "public runtime bundle". Consider saying that "private" means controller-owned and not writable by the worker, so it is not read as confidential.

## Decision

accepted
