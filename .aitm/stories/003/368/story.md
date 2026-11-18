---
schema: "aitm.story/v0"
id: 368
title: "Qualify protected local pre-commit test observation"
kind: "spike"
state: "done"
issue: "https://github.com/kburson/aitm/issues/368"
parent: 351
children: []
blocking: []
blocked-by: []
created: "2026-11-17T00:52:11Z"
updated: "2026-11-18T02:11:58Z"
last-branch: "planning"
estimate: {"agent-hours": 6, "size": "M"}
priority: "P2"
origin: ".aitm/stories/003/355/plan/2026-11-16-355-execution-qualification.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-16-368-protected-local-observation-plan.md", "plan/reviews/2026-11-16-368-plan-sar.md", "plan/reviews/plan/2026-11-17-2026-11-16-368-protected-local-observation-plan-review-313cdd3310f5b10187ba4f4c97d28a27/review-313cdd3310f5b10187ba4f4c97d28a27-review-manifest.md", "plan/2026-11-16-368-qualification-results.md", "plan/reviews/qualification/plan/2026-11-17-2026-11-16-368-qualification-results-review-c8e605ff766427ca85555b716fd164d2/review-c8e605ff766427ca85555b716fd164d2-review-manifest.md", "plan/2026-11-16-368-live-tracing-findings.md", "plan/reviews/live-qualification/plan/2026-11-17-2026-11-16-368-live-tracing-findings-review-0b6b44993f1e7efe90bb3f968157eb0d/review-0b6b44993f1e7efe90bb3f968157eb0d-review-manifest.md", "plan/2026-11-16-368-hosted-observation-plan.md", "plan/reviews/2026-11-16-368-hosted-plan-sar.md", "plan/reviews/hosted-plan/plan/2026-11-17-2026-11-16-368-hosted-observation-plan-review-6243e4d7fcda5797d0d41af00514157d/review-6243e4d7fcda5797d0d41af00514157d-review-manifest.md", "plan/2026-11-16-368-hosted-preflight-packet.md", "plan/2026-11-16-368-hosted-restore-retry-packet.md", "plan/2026-11-16-368-hosted-image-readmission-packet.md", "plan/2026-11-16-368-hosted-discovery-retry-packet.md", "plan/2026-11-16-368-hosted-qualification-findings.md", "plan/reviews/hosted-qualification/plan/2026-11-17-2026-11-16-368-hosted-qualification-findings-review-465e6e343ae2e7bc3ff567f646c08386/review-465e6e343ae2e7bc3ff567f646c08386-review-manifest.md", "plan/2026-11-17-368-hosted-ancestry-implementation-plan.md", "plan/reviews/2026-11-17-368-hosted-ancestry-sar.md", "plan/2026-11-17-368-hosted-ancestry-execution-packet.md", "plan/2026-11-17-368-hosted-ancestry-run-findings.md", "plan/reviews/hosted-ancestry-results/plan/2026-11-17-2026-11-17-368-hosted-ancestry-run-findings-review-a4a8291ce43671588b36a83b461ad7fa/review-a4a8291ce43671588b36a83b461ad7fa-review-manifest.md", "plan/2026-11-17-368-queue-inclusive-execution-packet.md", "plan/reviews/hosted-queue-packet/plan/2026-11-17-2026-11-17-368-queue-inclusive-execution-packet-review-bc77b92cf0572db34f16881721f8db19/review-bc77b92cf0572db34f16881721f8db19-review-manifest.md", "plan/2026-11-17-368-queue-inclusive-run-findings.md", "plan/reviews/hosted-queue-results/plan/2026-11-17-2026-11-17-368-queue-inclusive-run-findings-review-878d48dc52fb7e3aa45b7e4d0000888f/review-878d48dc52fb7e3aa45b7e4d0000888f-review-manifest.md", "plan/2026-11-18-368-owner-scope-decision.md", "plan/closure-receipt.json"], "attachments": ["attachments/2026-11-16-368-qualification.json", "attachments/2026-11-16-368-live-tracing-receipt.json", "attachments/2026-11-16-368-hosted-dry-restore.json", "attachments/2026-11-16-368-refreshed-image-dry-restore.json", "attachments/2026-11-16-368-hosted-discovery-dry-check.json", "attachments/2026-11-16-368-protected-pytest-check.json", "attachments/2026-11-16-368-hosted-qualification-receipt.json", "attachments/2026-11-17-368-ancestry-local-reproduction.json", "attachments/2026-11-17-368-hosted-ancestry-run-receipt.json", "attachments/2026-11-17-368-hosted-ancestry-api-readback.json", "attachments/2026-11-17-368-queue-inclusive-run-receipt.json", "attachments/2026-11-17-368-product-failure-evidence.json"]}
expansions: []
trips: []
---

# Qualify protected local pre-commit test observation

[GitHub issue #368](https://github.com/kburson/aitm/issues/368) · [Parent #351](../351/story.md) · [Blocked story #355](../355/story.md)

Project 24 Rank 465. Priority P2. Size M. Estimate 6 agent-hours.

Can a disposable local macOS/APFS guest establish the protected runner, independent outcome evidence, and exact scoped assignment required for #355? Use the accepted #353 boundary and the delivered #354 pinned obligations. Record PASS only when all three gates and one live integrated run pass independent findings review.

[Spike plan](plan/2026-11-16-368-protected-local-observation-plan.md) · [Plan SAR](plan/reviews/2026-11-16-368-plan-sar.md).

## Plan accepted

SAR and two broker-backed XPR rounds with Opus 5.5 at high effort accepted the exact plan. The spike was in Planning when the plan was accepted. A bounded qualification can clear #368 as an effective blocker only when #355's remaining trust requirements have an approved scope decision or a verified native successor blocker. [XPR manifest](plan/reviews/plan/2026-11-17-2026-11-16-368-protected-local-observation-plan-review-313cdd3310f5b10187ba4f4c97d28a27/review-313cdd3310f5b10187ba4f4c97d28a27-review-manifest.md) · [Final reviewer verdict](plan/reviews/plan/2026-11-17-2026-11-16-368-protected-local-observation-plan-review-313cdd3310f5b10187ba4f4c97d28a27/review-313cdd3310f5b10187ba4f4c97d28a27-reviewer-response-2.md).

## Execution pickup

The owner authorized the live qualification. Started the runner admission gate under the accepted plan. #355 remains blocked.

## Runner admission HOLD

The offline guest installed and booted to Apple’s license notice. At this checkpoint, guest setup awaited the owner’s confirmation. The protected worker, local independent observer and live assignment remain unqualified. The archived 30 IDs were checked statically. Zero product tests ran. Opus 5.5 at high effort independently accepted the HOLD findings in round two.

#368 stays open and #355 remains blocked. [Findings](plan/2026-11-16-368-qualification-results.md) · [Machine receipt](attachments/2026-11-16-368-qualification.json) · [XPR manifest](plan/reviews/qualification/plan/2026-11-17-2026-11-16-368-qualification-results-review-c8e605ff766427ca85555b716fd164d2/review-c8e605ff766427ca85555b716fd164d2-review-manifest.md) · [Final reviewer response](plan/reviews/qualification/plan/2026-11-17-2026-11-16-368-qualification-results-review-c8e605ff766427ca85555b716fd164d2/review-c8e605ff766427ca85555b716fd164d2-reviewer-response-2.md).

## Live execution resumed

The owner reviewed and accepted Apple’s license for the disposable guest and authorized the live run. The retained guest identity matched the prior receipt. #355 remains blocked.

## Live tracing HOLD

The retained guest completed setup and verified its offline configuration. The restricted worker exercised scratch-write and protected-path controls. Stock DTrace refused the required process program, and the guest inventory exposed only its internal and profiling providers. Live assignment and outcome calibration remain unqualified. Zero product tests ran. Opus 5.5 at high effort independently accepted these findings after two rounds.

#368 stays open and #355 remains blocked. [Live findings](plan/2026-11-16-368-live-tracing-findings.md) · [Machine receipt](attachments/2026-11-16-368-live-tracing-receipt.json) · [XPR manifest](plan/reviews/live-qualification/plan/2026-11-17-2026-11-16-368-live-tracing-findings-review-0b6b44993f1e7efe90bb3f968157eb0d/review-0b6b44993f1e7efe90bb3f968157eb0d-review-manifest.md) · [Final reviewer response](plan/reviews/live-qualification/plan/2026-11-17-2026-11-16-368-live-tracing-findings-review-0b6b44993f1e7efe90bb3f968157eb0d/review-0b6b44993f1e7efe90bb3f968157eb0d-reviewer-response-2.md).

## Hosted qualification plan revision

The local trial exercised the offline pre-commit boundary and stopped because its DTrace configuration lacked the required process provider. The owner authorized a hosted experiment using the runner family from #146 to test live tracing and the same scoped assignment under fresh isolation controls. Both results belong to #368. [Hosted plan](plan/2026-11-16-368-hosted-observation-plan.md) · [Plan SAR](plan/reviews/2026-11-16-368-hosted-plan-sar.md).

## Hosted plan accepted

SAR and Opus 5.5 at high effort accepted the hosted revision after three findings were resolved. Stage A starts with the protected worker and tracing probes. #355 remains blocked. [XPR manifest](plan/reviews/hosted-plan/plan/2026-11-17-2026-11-16-368-hosted-observation-plan-review-6243e4d7fcda5797d0d41af00514157d/review-6243e4d7fcda5797d0d41af00514157d-review-manifest.md).

## Results of the local and hosted experiments

The offline local guest exercised the intended pre-commit isolation boundary. Its DTrace inventory lacked the required process and syscall probes, so it stopped with zero product tests. The #146 runner family was needed to verify independent kernel and user-space observation on a protected hosted worker and run this exact assignment. Hosted calibration passed. The integrated trace recorded all 30 outcomes, with 7 passes, 22 setup failures and 1 call failure in filesystem ancestry checks. It matched 22 of 74 expected direct native-child records. The verdict is HOLD. #368 remains open and #355 remains blocked.

Opus 5.5 at high effort independently accepted the paired findings. [Paired findings](plan/2026-11-16-368-hosted-qualification-findings.md) · [Machine receipt](attachments/2026-11-16-368-hosted-qualification-receipt.json) · [Live evidence review](plan/reviews/hosted-qualification/plan/2026-11-17-2026-11-16-368-hosted-qualification-findings-review-465e6e343ae2e7bc3ff567f646c08386/review-465e6e343ae2e7bc3ff567f646c08386-review-manifest.md) · [Exact hosted run](https://github.com/kburson/aitm/actions/runs/44028499403/attempts/1).

## Revised hosted ancestry policy and rerun

The integrated worker now has literal metadata access on the three required scratch ancestors. The pinned local ledger validator passed under the revised policy, all eight new isolation denials held, and 13 harness tests passed. Opus 5.5 at high effort accepted the plan and packet through SAR and XPR. GitHub kept the rerun queued through the reviewed 6:52:24 a.m. Central deadline with no runner or steps. Cancellation was confirmed with zero product tests and no hosted artifact. The attempt is HOLD. #368 stays open and #355 remains blocked by #368.

[Accepted plan](plan/2026-11-17-368-hosted-ancestry-implementation-plan.md) · [Opus SAR](plan/reviews/2026-11-17-368-hosted-ancestry-sar.md) · [Execution packet](plan/2026-11-17-368-hosted-ancestry-execution-packet.md) · [Findings](plan/2026-11-17-368-hosted-ancestry-run-findings.md) · [Exact receipt](attachments/2026-11-17-368-hosted-ancestry-run-receipt.json) · [Independent findings review](plan/reviews/hosted-ancestry-results/plan/2026-11-17-2026-11-17-368-hosted-ancestry-run-findings-review-a4a8291ce43671588b36a83b461ad7fa/review-a4a8291ce43671588b36a83b461ad7fa-review-manifest.md) · [Hosted run](https://github.com/kburson/aitm/actions/runs/44085388689/attempts/1).

## Queue-inclusive hosted qualification

The Opus-reviewed admission window gave the hosted job time to start. The live rerun passed the five ancestry readbacks and eight isolation denials. The independent observer recorded all 30 assigned outcomes and verified all 74 native child lifecycles. Fourteen tests passed and sixteen failed. Fifteen IDs encountered transcript discovery failures, and the native process-custody test required a same-UID parent. The scoped run is HOLD. The earlier local guest could exercise local isolation but lacked a usable process observer. The hosted run supplied independent observation and exposed the remaining execution incompatibilities. #368 stays open and #355 remains blocked by #368.

[Execution packet](plan/2026-11-17-368-queue-inclusive-execution-packet.md) · [Packet review](plan/reviews/hosted-queue-packet/plan/2026-11-17-2026-11-17-368-queue-inclusive-execution-packet-review-bc77b92cf0572db34f16881721f8db19/review-bc77b92cf0572db34f16881721f8db19-review-manifest.md) · [Findings](plan/2026-11-17-368-queue-inclusive-run-findings.md) · [Machine receipt](attachments/2026-11-17-368-queue-inclusive-run-receipt.json) · [Failure details](attachments/2026-11-17-368-product-failure-evidence.json) · [Independent findings review](plan/reviews/hosted-queue-results/plan/2026-11-17-2026-11-17-368-queue-inclusive-run-findings-review-878d48dc52fb7e3aa45b7e4d0000888f/review-878d48dc52fb7e3aa45b7e4d0000888f-review-manifest.md) · [Hosted run](https://github.com/kburson/aitm/actions/runs/44090243525/attempts/1).

## Owner scope decision

The owner accepted this investigation as complete. The deliverable is the Opus-accepted HOLD above. #355 resumes on the cooperative advisory run from #353, and #368 stops blocking it. The unqualified claims stay on this spike. [Decision](plan/2026-11-18-368-owner-scope-decision.md).

## Closure

GitHub closed this spike as Completed at 2026-11-18T02:10:27Z. Project 24 shows Done with Delivered disposition because the investigation is complete. The strict three-gate PASS was not met. The Opus-accepted HOLD is the completed answer. [Verified closure receipt](plan/closure-receipt.json).
