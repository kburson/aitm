<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-465e6e343ae2e7bc3ff567f646c08386"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-16-368-hosted-qualification-findings.md"
artifact_commit: "c3cc41fc1e14697fd707c17fac6371280185617f"
artifact_blob: "c1f436e594ad8e89948f67e47c2b662926803e56"
artifact_digest: "sha256:7af4c6094fec8726fe686cbcc7ef6c3e8560521051aa86cdb385f483476d24b6"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:ca2e6e5dd8544fac11d41eec2903c201b5ea9783bb31dcfd24948053f30276aa"
  identity_source: "runtime"
started_at: "2026-11-17T06:10:27.377Z"
submitted_at: "2026-11-17T06:17:02.670Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I re-reviewed the revised artifact (commit `c3cc41fc`, blob `c1f436e5`, digest `sha256:7af4c609…`) against my turn-1 findings and the author's turn-1 response. Both required changes are resolved, and the optional suggestions were taken up.

**Required change 1 (cause and resume condition): resolved.**

- The integrated-result bullet now states the cause from the exported policy:
  - metadata is granted only on the literal admission root `/Users/Shared/aitm368-hosted`;
  - `/` has `file-read-data` only;
  - `/Users` and `/Users/Shared` have no metadata grant.
- This matches the retained `raw/worker.sb` I read in turn 1.
- The cited profile digest `39732ec0…` matches both `boundary.profile_sha256` and the `export["worker.sb"].sha256` entry (1305 bytes) in the hosted controller receipt `raw/receipt.json`.
- The ledger caveat is kept: the error leaves the failed ancestor and operation unspecified. The `/Users` EPERM is correctly limited to the registry path.
- The passed gates (boundary, tracing, runtime, report replays, calibration) are now explicitly separated from the policy-dependent failure.
- The closing paragraph gives a concrete resume condition:
  - a reviewed worker policy that permits scratch-ancestry metadata and any narrowly required ACL read, with directory-listing and protected-path denials preserved;
  - fresh admission;
  - packet review;
  - an integrated rerun that includes native observations and the final custody check.
- The "Why both experiments" paragraph now names the same ancestor-metadata cause.

**Required change 2 (intake-refusal evidence): resolved.**

- The bullet now says the refusals are in-process assertions in `calibrate_intake`, called immediately before the product launch. It says they produce no per-case raw stream, and that the product launch corroborates that they returned.
- I read `.github/spikes/368/integrated.py` in the held worktree `/Users/kpburson/.codex/worktrees/aitm-344-functional-tia/trunk`:
  - `calibrate_intake` is at line 293. It asserts refusal for each listed case:
    - a bare `{"exit_code": 0}` record (`untrusted-origin`);
    - identity mutations of `invocation`, `head`, `attempt`, `snapshot_sha256` and `observed_pid` (`assignment-identity-mismatch`);
    - dropped and duplicated `collect`, `dispatch`, `body-enter` and `teardown-ok` events;
    - empty, unclean and extra-start traces;
    - empty and reassigned native children.
  - Each failed assertion raises.
  - The call at line 388 sits between the failure calibrations and `observe(LABELS[3], …, product=True)` at line 391.
- The hosted receipt records `product_invocation_started: true` and a `scoped-product` invocation. That is consistent with the assertions having returned.
- The cited controller hash `86e1b245…` equals the `integrated.py` SHA-256 bound in the accepted discovery-retry packet.
- "Uncertainty" has been replaced by "gate results", which the receipt does carry.

**Optional suggestions.**

- **Mixed fleet:** "Fresh allocations landed on both runner images during the rollout", plus the exact image-to-runtime match condition.
- **Run count:** "Further fresh integrated runs".
- **#368 wording:** "verified native dependency blocking #355".
- **Runtime provenance:** admission run `44024930299`, artifact `14302787413`.
- **Native shortfall:** setup stopped before sign and verify, and the profile-revision bodies never ran, which accounts for the 52 missing launches.

Limits of this review:

- As in turn 1, I did not run Git, compute SHA-256 values, query GitHub or open the cited GitHub links.
- I read `integrated.py` as a working-tree file in the held worktree. I did not confirm that it is byte-identical to blob `d06b0e7f…:.github/spikes/368/integrated.py` or to hash `86e1b245…`. The source agreement rests on the matching hash in the accepted discovery-retry packet and on the line numbers matching the artifact's links.
- I did not check whether the paired receipt changed. The author states it is unchanged, and the artifact still cites `04685c06…`.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. Lines 19–21: after the change to "Further fresh integrated runs were needed …", the next sentence, "It reached the integrated test …", has no singular antecedent. Consider "The final run reached the integrated test …".

## Decision

accepted
