<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-c8e605ff766427ca85555b716fd164d2"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-16-368-qualification-results.md"
artifact_commit: "834257c9789e9bcef591d629477dc679695bb08a"
artifact_blob: "2413d45349bfe0c8426d2aad43c97b25d639aa0b"
artifact_digest: "sha256:566cc5717ab0f811ff9f6199d1e78a0cdeb637f0ea77cae956da4c03cb0d3c68"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:4a4e00a67f0d500b2aa384a480bbb27143ca3fa0c72c7558c8ff7105149bd114"
  identity_source: "runtime"
started_at: "2026-11-17T02:46:58.016Z"
submitted_at: "2026-11-17T02:48:30.163Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I reviewed `2026-11-16-368-qualification-results.md` (blob `2413d45`) against the accepted plan `2026-11-16-368-protected-local-observation-plan.md` and the receipt `attachments/2026-11-16-368-qualification.json`. I also checked the #146 retained evidence and the #368 `story.md` and `events.jsonl`.

The HOLD verdict is correct and conservative. The opening line names the exact reviewed closure and states that candidate-code resistance is unqualified, as the plan's Evidence section requires. The gate table matches the receipt's `gate_results` and `first_stop`, and no gate is overstated as passed. Zero product tests ran (`executed_pinned_node_count: 0`). #355 stays blocked and #368 stays open, as the plan requires on HOLD. The static assignment counts match the receipt. There are 30 `selected_module_node_ids`. There are 22 `direct_or_staged_fixture_arguments`, and the 8 others are `test_ordinary_checkout_mode_can_be_physically_identified` plus the 7 `test_process_info_refuses_invalid_custody` parameters. There are 6 `hosted_required_tests` in other modules, plus 2 `hosted_required_children` and the local overrides. The checkpoint time (`2026-11-17T02:46:12+00:00`), the plan SHA, the install timestamps, the installer size and SHA, and `networkDevices=0 directorySharingDevices=0` all match the receipt. The #146 run, artifact, archive SHA and receipt SHA match the retained #146 readback.

Before acceptance, these items need fixing: one broken evidence link, a few claims the receipt does not back, and missing resumption anchors. All are documentation fixes. None changes the HOLD verdict.

Limits of this review: I could not recompute any SHA-256, inspect the guest or the scratch evidence, or re-run the AST inspection. The product source at `8218a69` is not in this worktree, and this session cannot use Git. The `/usr/bin/ssh-keygen` two-call-site claim and the 22-node AST result are checked only for consistency with the receipt, not independently.

## Findings

1. **Broken #146 evidence link, and the cited document does not hold the hashes.** Line 20 links `../../../001/146/plan/full-suite-observation-findings.md`, which does not exist. The file is `2026-11-12-146-full-suite-observation-findings.md`, and the accepted plan links it under that name. Also, the archive SHA `cc28de0c…` and receipt SHA `39930957…` are not in that findings document. They are recorded in `001/146/plan/full-suite-observation-readback.json` (lines 338 and 506) and in `001/146/plan/reviews/2026-11-12-146-full-suite-observation-review.md`. The claim that the archive and receipt "matched the retained SHA-256 values in #146 full-suite observations" therefore points readers to the wrong place twice.

2. **The privilege approval is asserted but not recorded.** Line 18 says "The approved execution route uses guest-local root only for evidence custody, role setup and tracing". The plan's preamble requires that, before setup, the pickup record: the approved guest; the exact privileges and security configuration the observer needs; an explicit decision on a guest root-owned controller, the existing SIP and diagnostic-tracing restrictions, and any entitlement; and the person or preexisting approval that authorizes each. The receipt's `controller_selection.approval_basis` only says "Owner-authorized disposable local Apple Silicon macOS/APFS guest under the accepted plan". The `events.jsonl` entry at 02:17:57Z only says "Owner authorized live execution of the accepted #368 plan". Neither records the root-controller decision, the tracing privilege, or the entitlement decision. Since the next step is guest setup with an administrator and root use, that record must exist and be cited before resumption, or the artifact must not call the route "approved". There is also a related wording mismatch. The artifact asks the owner for a "disposable guest-only administrator", while the receipt's `first_stop.expected_next` says "isolated local controller … verify the guest from the controller account". The plan separates controller and worker identities, so the account being created should be named consistently.

3. **The manifest and observer-source claims are not traceable in the receipt.** Line 16 says a manifest identifies "the scratch VM controller, the read-only diagnostic disk, the benign USDT emitter and the preflight script". The receipt's `prepared_input_artifacts` has roles `provision.swift`, `provision` twice with different digests and sizes (194880 and 194864 bytes), `input.img`, `qualification` (33792 bytes), and `guest-preflight.sh`. No entry is identified as the USDT emitter. The two `provision` entries are not explained, for example as a rebuild or as unsigned and signed copies. The role `qualification` is ambiguous. Separately, line 10 and the table claim "Recovered the prior authenticated #146 source". The receipt's `precedent` records only the hosted run, artifact, archive SHA, receipt SHA and source commit. It has no digest for the recovered observer source, build recipe, probes or reconciler that plan §0 and §2.1 ask to recover and authenticate. "Recovered" is not supported by recorded identities.

4. **Resumption and stop-rule anchors are missing.** The artifact says "The intended Apple Virtualization guest and its scratch evidence have been retained for resumption". Neither the artifact nor the receipt identifies the guest: no VM bundle path or identifier, disk image digest, or machine identifier. Neither gives the location or digest of the retained scratch evidence and manifest. A resumer or independent reader cannot confirm they are continuing on the same admitted guest. The plan also sets an elapsed-effort stop rule: publish partial findings if admission and runner preflight exceed 2.5 agent-hours. It requires start and finish times in the receipt. The receipt has only installer timestamps and the checkpoint time. It has no attempt start (the `develop` entry at 02:17:57Z suggests one) and no agent-hours consumed, so the remaining budget for resumption cannot be checked.

## Required changes

1. Fix the #146 link to `../../../001/146/plan/2026-11-12-146-full-suite-observation-findings.md`. Cite `full-suite-observation-readback.json`, or the #146 review table, as the source of the retained archive and receipt SHA-256 values.
2. Either cite the existing record that approves the guest-local root controller, the tracing privilege and SIP posture, and any entitlement, with who approved each, or remove "approved" and state that this decision must be recorded before resuming guest setup. Use the same name for the account being created in the artifact and in the receipt's `expected_next`.
3. Make the manifest claim traceable. Label each `prepared_input_artifacts` entry so that the VM controller, diagnostic disk, USDT emitter and preflight script can each be identified, and explain the two `provision` digests. Either record digests or identities for the recovered #146 observer source, build recipe, probes and reconciler, or reword the observer claim to what was actually authenticated (the hosted archive and receipt).
4. Record the retained guest's identity, the retained scratch evidence location and digest, the attempt start time, and the agent-hours used so far against the plan's 2.5-hour admission and preflight stop rule.

## Optional suggestions

1. Line 3, "The first-boot screen still displays the software license notice", is present tense in a durable record. Consider "displayed … at the checkpoint" so it does not read as a current claim after the owner acts.
2. The Parallels incident (line 30) involved a host-side provider outside the selected Apple Virtualization controller. Consider recording the removed VM's UUID and noting that it did not touch the approved guest or any product input, so the cleanup claim can be checked independently.
3. Consider adding a short reproduction pointer for the host-side provisioning: the command, the inputs and where the provisioning source is retained. The plan asks for a setup and reproduction recipe, and the partial record is the natural place to start it.

## Decision

revisions-requested
