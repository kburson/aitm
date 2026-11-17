<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-c8e605ff766427ca85555b716fd164d2"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-16-368-qualification-results.md"
artifact_commit: "5d66d3486b8543c5910fc9e78fa9655b6c828901"
artifact_blob: "44579a5f89052eac463106f26b3e261a61f4a584"
artifact_digest: "sha256:add1b41d5dcccd4f8076d91a156508407cbf09f7b0bb2dd90c9be427e00caab0"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:4a4e00a67f0d500b2aa384a480bbb27143ca3fa0c72c7558c8ff7105149bd114"
  identity_source: "runtime"
started_at: "2026-11-17T02:46:58.016Z"
submitted_at: "2026-11-17T02:52:36.935Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I re-reviewed the revised `2026-11-16-368-qualification-results.md` (blob `44579a5`) and the revised receipt `attachments/2026-11-16-368-qualification.json` against my four turn-1 findings and author response 1. I also read the retained private attempt directory `~/Library/Caches/aitm-368-live.1R0LSSSt` (read-only) to check the new resumption and provenance claims. All four findings are resolved. The HOLD verdict, the opening-line scope statement, the gate table, zero product execution, and the #368 open / #355 blocked disposition are unchanged and still correct.

Resolution of the turn-1 findings:

1. **#146 link and hash source: resolved.** Line 20 now links `../../../001/146/plan/full-suite-observation-readback.json`, which exists. That file carries the archive SHA `cc28de0c…` (line 338) and receipt SHA `39930957…` (line 506) that the receipt's `precedent` cites. The findings link now uses the correct filename, `2026-11-12-146-full-suite-observation-findings.md`.
2. **Privilege approval: resolved.** The artifact no longer calls the root route "approved". It separates the owner's authorization of the spike under the accepted plan from the executor's pre-provisioning limits. It also states that any protection change or extra entitlement is outside the recorded scope.
   - The receipt's new `scope_decisions_before_provisioning` block covers the decisions the plan asked for: the root controller, SIP and tracing posture, the stock DTrace privilege, additional guest entitlements (none), and the host virtualization entitlement.
   - That block is timestamped `02:19:31Z`, before the `02:36:43Z` install start, and it matches the retained `admission-policy.json` field for field.
   - The account wording is now consistent: the artifact's "disposable guest-only administrator" and the receipt's `expected_next` ("guest-only local administrator for the controller role … restricted worker as a separate identity") agree. Both match the plan's separation of controller and worker roles.
3. **Manifest and recovered sources: resolved.** Every `prepared_input_artifacts` entry now has a role and a filename. The two `provision` digests are explained by separate signing of the standalone installer and the AppKit console bundle (`vm_controller_binary_note`), which fits the retained `native-vm/provision` and `native-vm/AITM 368 Guest.app/Contents/MacOS/provision`.
   - The USDT emitter (`qualification`, `461b0245…`) and `guest-preflight.sh` (`609b2895…`) match the retained `diagnostic/SHA256SUMS`.
   - `precedent.recovered_sources` now pins the controller and build recipe, the probe patch, the probe program and reconciler, and the reference catalog by Git blob and SHA-256.
   - Three of those SHA-256 values (`a8b375ad…`, `757ef83d…`, `f9d08e02…`) appear in the retained `precedent/hosted-receipt.json`. The fourth, `7f68d796…`, appears in both that file and the #146 product-trial receipts in this repo. The recovered sources are therefore tied to the authenticated hosted proof.
4. **Resumption and budget anchors: resolved.** The receipt's `resume` block names the private attempt directory and the `native-vm` guest directory. It pins the machine-identifier, hardware-model, installer-log, diagnostic-manifest and readiness-receipt digests, and I confirmed the directory and those files exist. The `attempt` block records start `02:17:16Z` and finish `02:46:12Z`, which is 1736 s, or 0.482 h, rounded up to 0.483 h. That leaves 2.017 h of the 2.5 h admission and preflight budget, and charging the whole wall-clock window is the conservative choice.

The author declined to record the Parallels VM UUID because it was not retained. That is acceptable: the incident did not touch the selected guest, and the receipt records that the cleanup was verified against the live VM list.

Limits of this review: I did not recompute any SHA-256, including the receipt digest `bcf00457…` or the `decision_record_sha256`. I did not verify the four Git blob IDs, inspect the guest, or re-run the AST inspection; this session cannot run hashing tools or Git. The checks above are file-existence checks and cross-document digest matches.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. The retained evidence and the guest disk (`native-vm/guest.raw`, about 20 GB with the IPSW) live under `~/Library/Caches`. macOS and cleanup tools may purge that location. Consider moving the attempt directory to a non-cache private location before resuming, or noting that the resumption digests must be re-verified after any purge risk.
2. `scope_decisions_before_provisioning.decision_record_sha256` does not name the file it digests. Naming it (apparently `admission-policy.json`) would let a reader re-verify it directly. Similarly, `diagnostic/SHA256SUMS` omits the generated `qualification.h`. That is harmless if it is a build intermediate, but it is worth stating.
3. The root-controller permission is an executor limit recorded under the owner's general authorization of the plan. The owner will be at the guest setup prompt anyway, so a one-line explicit owner confirmation of guest-local root and stock DTrace, recorded in the next checkpoint, would remove any doubt before those privileges are first exercised.

## Decision

accepted
