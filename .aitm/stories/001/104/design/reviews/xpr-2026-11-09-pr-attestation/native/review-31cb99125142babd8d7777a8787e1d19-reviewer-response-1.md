<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-31cb99125142babd8d7777a8787e1d19"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/001/104/design/github-tested-merge-binding-replan.md"
artifact_commit: "eaa2e3f06a464ec4275946add0c094f96d322c50"
artifact_blob: "79d94debb1a418e4b86302dfbfcf2336364353f1"
artifact_digest: "sha256:1b9afd6e13275d1a35ef3be66c8ca98ac4186d0ce94f49257909b2731bb5c20f"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:19aba777a140232c905945ba92b3184a1498366bb62ff2b21341e5c323631b7f"
  identity_source: "runtime"
started_at: "2026-11-10T04:18:50.207Z"
submitted_at: "2026-11-10T04:23:06.724Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

**Read coverage.** I freshly read the exact artifact `.aitm/stories/001/104/design/github-tested-merge-binding-replan.md` (frontmatter blob `79d94deb…`, commit `eaa2e3f`) through EOF in contiguous chunks of at most 20 lines: lines 1–20 and 21–40. Line 40 is the last line, since a line count of the file returned 40. I reread line 20 on its own to confirm that it is blank. I also read the exact #104 design `.aitm/stories/001/104/design/design.md` in full (lines 1–13, EOF at 13). For context only, I read lines 1–20 of the failed-probe attachment `attachments/github-binding-probe-attempt-1.md` and the author startup note. I also used grep to find the parent #103 design's refresh-route disposition (#103 SPR `reviewer-response-3.md`, finding SPR-CI02: `synchronize` after an allowed branch update, or an authorized `reopened`; old-event reruns stay separate). I did not read the rest of the probe attachment or the parent plans in full. No prior dispositions exist for this review because this is turn 1. I used no Git and no network access.

**Assessment.** The core trust argument is sound, and it fixes the gap that probe attempt 1 found. GitHub mints the OIDC token, and Fulcio copies its `sha`, `ref`, `repository_id`, `workflow_sha`/`job_workflow_sha`, `event_name`, `runner_environment` and `run_id`/`run_attempt` claims into signed certificate extensions. A verified certificate therefore binds a run attempt to a source digest. That binding comes from GitHub as issuer, not from the candidate. Lines 15 and 23 also restrict authority correctly. The plan compares only authenticated certificate extensions and never the signed predicate. The JSON only reports evidence. Job success comes from the authenticated jobs API. Workflow content is trusted only through a review of the exact workflow blob at the signed config digest. For a top-level `pull_request` workflow, the merge-commit workflow is the code that runs, so requiring the config and signer digests to equal the selected merge (line 23) closes the "which workflow ran" question. Line 15 correctly states that the PR `sha`/`ref` values are a hypothesis that a live probe must confirm.

**Requested checks that pass.**
- *Approval before privilege scope changes:* lines 11, 31 and 35. The new `id-token`/`attestations` write is called out as a scope change that needs separate authorization and exact control review before execution.
- *Signer isolation:* line 30. Test, build and lint jobs get no token or attestation permission. The signer has no checkout, scripts, cache, secrets or environment. It takes a fixed path and literal subject, and candidate values are never interpolated.
- *Live probe stop:* line 35. A failed signed source, config, signer, invocation, archive or signing route returns to Planning before helpers or the wheel. Line 40 states that no live proof is authorized.
- *Ordinary branch workflow:* line 7 forbids CI branches, copied merges and direct pushes.
- *Budget:* line 38. 0.35 + 3.45 + 0.20 = 4.00 h. The allocations add up to 3.45 h, and the plan reforecasts after the diagnostic.
- *90% floor:* line 36. The unrounded line floor applies separately to product packages and CI helpers and includes unimported source, with branch coverage reported separately.
- *Meaningful tests:* lines 36–37. Tests need behavior, failure or invariant assertions. #105 uses signed fixtures or test PKI and never a production bypass.

**What blocks acceptance.** Three gaps would leave a builder guessing, and one of them can make the route infeasible:
- Finding 1: the plan never establishes that GitHub artifact attestations are available for this repository, or what signing publishes.
- Finding 2: the signer's download mechanism does not fit its permission budget, and the artifact namespace is shared with candidate-code jobs.
- Finding 3: the rerun and partial-rerun eligibility rules lack a detection criterion and conflict with GitHub's rerun SHA semantics after base movement.

## Findings

1. **The plan does not establish that artifact attestations are available for this repository, or the irreversible publication that signing causes (lines 17, 30, 31 and 35).** GitHub artifact attestations behave differently depending on repository visibility and plan. For a **public** repository, `actions/attest` signs through the public-good Sigstore instance. The Fulcio certificate is then permanently recorded in the public Rekor transparency log. That certificate contains the repository, the workflow path, `refs/pull/<n>/merge`, the merge SHA, the run/attempt invocation URI, the runner environment and the subject digest. For a **private or internal** repository, artifact attestations require GitHub Enterprise Cloud and use GitHub's private Sigstore instance. On other plans, the signing step is unavailable. Either way, `attestations: write` also stores the attestation in the repository's attestation API. The artifact covers none of this. Line 30 says to "explicitly disable registry and storage publication", but the GitHub attestation record, and the Rekor entry for a public repository, cannot be disabled. So the "data handling" the diagnostic reviews (line 35) leaves out the one durable external write the route depends on. The visibility and plan of `kburson/aitm` are not stated anywhere in #103 or #104. I found only a passing note in an unrelated draft that GitHub Free protection does not work on private repositories. *Failure scenario:* If the repository is private on a non-Enterprise plan, the diagnostic fails at signing. That spends the 0.55 h allocation on a route that could never work, and nobody knew beforehand. If it is public, the authorizer approves "a fixed non-sensitive probe file and one bundle" without being told that each run also creates a permanent, public, undeletable transparency-log record. That is an outward-facing, irreversible action that the authorization text does not cover.

2. **The signer's download route does not fit the stated permission budget, and the artifact namespace is shared with candidate-code jobs (lines 23 and 30).** Line 30 limits the signer to `id-token: write`, `attestations: write` and `contents: read`, "with every other permission disabled". Yet it asks for "a pinned downloader that does not auto-extract", keyed by "immutable artifact ID". The two usual mechanisms cannot both meet these conditions. `actions/download-artifact` uses the run's runtime token, which needs no `GITHUB_TOKEN` permission, but it extracts the archive. The REST route `GET /repos/{owner}/{repo}/actions/artifacts/{id}/zip` returns the raw ZIP but needs `actions: read`. The artifact also does not say where the signer gets the artifact ID and archive digest from. A second issue: every job in the run can upload artifacts with the runtime token, whatever its `permissions:`. That includes the test jobs, which run candidate code. In step 3 (line 23), "GitHub artifact association" ties an artifact only to a run, not to the job or attempt that uploaded it. *Failure scenario:* (a) The implementer adds `actions: read` without authorization, or swaps in an extracting downloader. Either change is outside the reviewed scope. (b) A candidate test step uploads `aitm-ci-evidence-a<n>` before the signer does, or a collector-named archive before the collector does. If the signer or verifier selects artifacts by name, the plan does not say whether the result is a hold or a confusing failure. If anything trusts the name-based association, it attributes attacker-chosen bytes to the attempt. The bundle check still protects integrity, but the plan should state that it is the only binding.

3. **Rerun eligibility conflicts with GitHub's rerun SHA semantics, and the plan gives no way to detect a partial rerun (lines 21, 24, 25 and 37).** GitHub reruns reuse the original event's `GITHUB_SHA` and `GITHUB_REF`. A full rerun's certificate therefore carries the original merge SHA, even if GitHub has since recomputed `refs/pull/<n>/merge` after the base moved. Line 24 lets "a full rerun" with a new bundle count as eligible. Line 25 says that after movement, fresh evidence comes "through the existing authorized PR update route". It does not say that a rerun can never be that route. The parent's SPR-CI02 disposition (`synchronize` after an allowed update, or authorized `reopened`, with old-event reruns kept separate) is the governing rule, but this replan neither cites nor restates it. Line 24 also makes partial reruns ineligible without saying how the verifier tells them apart. After "re-run failed jobs", the new attempt's job listing can include jobs carried over from the earlier attempt. `aitm-ci` depends on every job, so it is rerun too and produces a valid attempt-`n` bundle with the unchanged merge SHA. Certificate checks alone therefore cannot tell a partial rerun from a full one. *Failure scenario:* (a) During the line 37 integration proof, after the controlled base movement, an operator reruns the old run to "refresh" it. The new bundle's source digest is the stale merge, step 2 holds the gate, and the 0.45 h integration allocation goes to diagnosing an outcome the plan could have predicted. (b) A partial rerun whose carried-over jobs report success, plus a fresh signer, passes every listed check, because "every applicable job exactly once with success" (line 21) is met by jobs that did not run in attempt `n`.

## Required changes

1. **For Finding 1:**
   - State the repository's visibility and plan as a precondition in "Decision and limits" (line 11). If the repository is private or internal without GitHub Enterprise Cloud, record the route as infeasible and return to Planning before any probe.
   - In lines 30–31 and the diagnostic authorization in line 35, name exactly which publication is unavoidable: the GitHub attestation-store record, plus a permanent public Rekor entry for a public repository. List the identifying fields it exposes. Name which publication is disabled: the registry push and any optional storage record.
   - Make that publication an explicit part of the future execution authorization.
   - Have the diagnostic record which Sigstore instance and trust root verified the bundle.
2. **For Finding 2:**
   - Name the signer's download mechanism and its exact permission needs. Either add `actions: read` to the budgeted scope change in lines 30–31, or name a pinned same-run downloader that does not extract and needs no extra permission. The diagnostic in line 35 must prove whichever is chosen.
   - State that the signer takes the collector's artifact ID and archive digest only from the collector job's outputs, never from a name lookup.
   - In step 3 (line 23), state that the attempt binding of the evidence archive comes only from the verified bundle's Run Invocation URI and subject digest.
   - State that an artifact name collision, a duplicate name or an unexpected artifact on the run is a hold.
3. **For Finding 3:**
   - Restate or cite the parent's refresh rule in line 25. After any movement of base, target or merge, only a new `synchronize` from an allowed branch update or an authorized `reopened` can produce eligible evidence. A rerun cannot, because GitHub reuses the original event SHA.
   - Limit line 24's full-rerun eligibility to the case where the original event's merge SHA still equals the live merge.
   - Name the authoritative partial-rerun detection rule. For example: every required job record from `/actions/runs/{id}/attempts/{n}/jobs` has `run_attempt == n` and a start time no earlier than the attempt's start, and any job carried over from an earlier attempt disqualifies the evidence. Add a partial-rerun case to the #105 negative fixture matrix in line 37.

## Optional suggestions

1. **Observe a real attempt-2 certificate in the diagnostic (line 35).** "A mismatched expected ... attempt" can be simulated by changing the expected value, but that does not show GitHub's actual behavior. If the 0.55 h allocation allows, one full rerun of the diagnostic would confirm three things directly: the attempt-2 Run Invocation URI, an unchanged source digest, and refusal of the attempt-1 bundle against attempt 2. That would ground lines 24–25 in observed evidence, not documentation.
2. **Merge-ref stability as a liveness risk (line 22).** The plan correctly treats a same-tree commit with a different SHA as ineligible. If GitHub regenerates `refs/pull/<n>/merge` without a head or base change, the evidence goes stale and only `synchronize` or `reopened` can refresh it. The diagnostic could re-read the merge ref and `merge_commit_sha` at the start and end of verification and record any change. That would show whether this liveness risk is real.
3. **Who runs the procedure before #105 (lines 19–25 and 37).** #105 builds the automated verifier, so #104's own closure will run steps 1–5, including bounded ZIP handling and `gh attestation verify`, by hand. Consider stating that the #104 closure owner runs these steps manually with the pinned `gh` and trusted roots, and keeps the exact command lines and JSON output. Then the bootstrap gate's evidence will not depend on helpers that do not exist yet.

## Decision

revisions-requested
