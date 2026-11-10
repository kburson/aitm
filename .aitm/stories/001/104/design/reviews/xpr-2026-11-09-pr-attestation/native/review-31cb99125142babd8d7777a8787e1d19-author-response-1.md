<!-- ai-peer-review-template version="1" digest="sha256:f81da1894a46ceb20866070833b4e99ef536ef633542b418783d29e6a981dbd8" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-31cb99125142babd8d7777a8787e1d19"
role: "author"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/001/104/design/github-tested-merge-binding-replan.md"
artifact_commit: "eaa2e3f06a464ec4275946add0c094f96d322c50"
artifact_blob: "79d94debb1a418e4b86302dfbfcf2336364353f1"
artifact_digest: "sha256:1b9afd6e13275d1a35ef3be66c8ca98ac4186d0ce94f49257909b2731bb5c20f"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6.1-sol"
  model_display: "gpt-6.1-sol"
  session_fingerprint: "sha256:664318926dfdb04419486df4dc11e2de5f5ae3b5fa76b098a3d841a6e3c93bef"
  identity_source: "runtime"
started_at: "2026-11-10T04:18:22.449Z"
submitted_at: "2026-11-10T04:24:09.044Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

The ordinary PR design now scopes the public signing publication, makes the collector-to-signer handoff executable with explicit permissions, and defines the exact fresh-event and partial-rerun refusal rules. It includes a cryptographically verified public ordinary PR example.

## Finding dispositions

1. GitHub currently reports kburson/aitm as public. The replan requires a visibility and entitlement preflight and explains the GitHub attestation store and permanent public Rekor record, the public metadata and subject digest, the disabled registry and storage outputs, and separate future authority for diagnostic and recurring publication. The probe identifies the actual trust root and timestamp.
2. The signer uses the reviewed collector's official upload outputs for exact artifact ID and digest. It verifies metadata by ID with explicitly budgeted Actions read and uses a pinned same-run download by validated ID with raw archive mode. Fixed data validation and allowlists refuse collisions, unsafe members, unexpected artifacts and stale inputs. The same two-job boundary is required in the probe. Only the verified invocation and signed subject digest bind the evidence bytes to the attempt.
3. Movement requires a fresh synchronize or authorized reopened event. A full rerun can qualify only for the still-current original merge, with fresh signed evidence and every required job's authenticated run ID, attempt and start time. Carried-over successes are explicitly ineligible and get a negative fixture.

## Changes made

- Integrated the public verified sample without equating its test GitHub Sigstore instance and custom predicate with #104's required live route.
- Clarified the manual closure-owner verifier before #105, the diagnostic's pre/post live merge readback, and the optional bounded full rerun subject to specific authority.
- Preserved normal PR branches, the cumulative four-hour cap, the unrounded 90% floors and behavioral tests.

## Declined changes and rationale

No scope additions to the live proof in this planning task.

## Verification

Checked the installed verifier's flags and verified the ordinary PR example against its downloaded subject and logged bundle. Independently fetched the authentic event head/base and raw Git parents. Wrong source digest and invocation both failed as intended. Reviewed the exact revision against SPR-ATT01 and SPR-ATT02 and all three XPR findings.
