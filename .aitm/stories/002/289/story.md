---
schema: "aitm.story/v0"
id: 289
title: "[#133] Qualify scheduled full-suite validation on trunk in shadow"
kind: "story"
state: "review"
issue: "https://github.com/kburson/aitm/issues/289"
parent: 133
children: []
blocking: [290, 291]
blocked-by: [277, 279]
created: "2026-11-14T13:09:50Z"
updated: "2026-11-15T11:44:15Z"
last-branch: "planning"
estimate: {"agent-hours": 4, "size": "M"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-14-133-behavior-driven-validation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-14-289-scheduled-full-shadow-plan.md", "plan/local-validation.md", "plan/local-test.log", "plan/reviews/plan-review.md", "plan/local-native-diagnostics.md", "plan/local-full-setup-trace.log", "plan/exact-local-full-setup-trace.log", "plan/reviews/source-assessment.md", "plan/trusted-verifier.json", "plan/hosted-signature.json", "plan/tree-disposition.json", "plan/reviews/formal-review.md", "plan/delivery.json", "plan/premerge-verifier.json", "plan/premerge-rules.json", "plan/active-shadow-workflow.json", "plan/dispatch-diagnostic.md", "plan/dispatch-red.json", "plan/2026-11-14-289-shadow-toolchain-repair-plan.md", "plan/first-shadow-deployment/delivery.json", "plan/first-shadow-deployment/trusted-verifier.json", "plan/first-shadow-deployment/premerge-verifier.json", "plan/first-shadow-deployment/hosted-signature.json", "plan/first-shadow-deployment/tree-disposition.json", "plan/first-shadow-deployment/reviews/formal-review.md", "plan/reviews/toolchain-source-assessment.md", "plan/toolchain-local-tests.log", "plan/dispatch-green.json", "plan/scheduled-gap-pending.json", "plan/scheduled-gap.json", "plan/scheduled-gap-provider.json", "plan/reviews/schedule-gap-review.md", "plan/reviews/independent-schedule-gap.json", "plan/reviews/independent-schedule-gap-provider.json", "plan/2026-11-15-289-scheduled-qualification-amendment.md", "plan/schedule-delay-diagnosis.md", "plan/scheduled-historical.json", "plan/scheduled-historical-provider.json", "plan/scheduled-historical-runtime.log", "plan/verify-late-schedule.py", "plan/schedule-late-review.md", "plan/independent-late/independent-late-provider-run.json", "plan/independent-late/independent-late-provider-job.json", "plan/independent-late/independent-late-attempt.json", "plan/independent-late/independent-late.zip", "plan/independent-late/independent-late-runtime.log", "plan/independent-late/independent-late-inventory.json", "plan/independent-late/github-status-projection.json", "plan/independent-late/independent-late-reader.json", "plan/independent-late/independent-late-rejection.json", "plan/independent-late/independent-late-fixtures.log"], "attachments": []}
expansions: []
trips: []
---

# [#133] Qualify scheduled full-suite validation on trunk in shadow

Parent #133. Rank 110.

Qualify a default-branch-only scheduled full run and read-only evidence contract in shadow. Verify exact SHA, run/attempt identity, full outcomes, delayed/missing evidence, and genuine failure retention. Exercise a separate scheduled-evidence route into the #278 warning and #279 recovery flow in shadow. Keep the existing gate and trunk protections.

[Reviewed epic plan](../../001/133/plan/2026-11-14-133-behavior-driven-validation-plan.md). #103 governs production.

## Scheduled full-GitHub shadow candidate

[Reviewed plan](plan/2026-11-14-289-scheduled-full-shadow-plan.md) · [Local controls](plan/local-validation.md) · [PR #305](https://github.com/kburson/aitm/pull/305).

## Final candidate freshness handling

[Updated exact candidate evidence](plan/local-validation.md) includes a still-active timely run past grace. Provider completion remains the source for its disposition.

## Independent source and native diagnostics

[Exact source assessment](plan/reviews/source-assessment.md) · [Retained local setup diagnostics](plan/local-native-diagnostics.md). Local full-suite evidence remains incomplete.

## Exact candidate and review

[Trusted #103 verifier](plan/trusted-verifier.json) · [Signed review](plan/reviews/formal-review.md).

## Delivery

[Verified exact-tree delivery](plan/delivery.json) · [Pre-merge #103 verifier](plan/premerge-verifier.json).

## Shadow workflow deployment

[Registered workflow](plan/active-shadow-workflow.json) · [Diagnostic dispatch](https://github.com/kburson/aitm/actions/runs/43670107921). The story remains In review pending a genuine scheduled full green and independent readback. The current production #103 controls and effective trunk rules matched the original snapshots.

## Hosted diagnostic and follow-up

[Dispatch diagnosis](plan/dispatch-diagnostic.md) · [Authenticated diagnostic red](plan/dispatch-red.json) · [Repair PR #307](https://github.com/kburson/aitm/pull/307). The first independently reviewed [shadow deployment](plan/first-shadow-deployment/delivery.json) remains recorded.

## Toolchain correction evidence

[Independent exact-source assessment](plan/reviews/toolchain-source-assessment.md) · [105 planned focused checks with the checksum-verified CLI](plan/toolchain-local-tests.log).

## Exact candidate and review

[Trusted #103 verifier](plan/trusted-verifier.json) · [Signed review](plan/reviews/formal-review.md).

## Delivery

[Verified exact-tree delivery](plan/delivery.json) · [Pre-merge #103 verifier](plan/premerge-verifier.json).

## Corrected hosted diagnostic

[Manual diagnostic 43671830880/1](https://github.com/kburson/aitm/actions/runs/43671830880/attempts/1) and [verified evidence](plan/dispatch-green.json) recorded 1,215 product and 540 helper passes on the protected tree. Suite runtimes were 369.91 seconds and 151.87 seconds respectively. The pinned CLI passed the checksum check. This manual result is excluded from scheduled qualification.

## Live scheduled slot evidence gap

[Pending observation](plan/scheduled-gap-pending.json) · [Post-grace evidence](plan/scheduled-gap.json) · [GitHub readback](plan/scheduled-gap-provider.json) · [Signed independent assessment](plan/reviews/schedule-gap-review.md).

GitHub had no scheduled event for the November 15 03:47 UTC slot when the 45-minute grace period elapsed. The workflow remained active on protected default trunk. The prior hosted diagnostic stays classified as a dispatch. The independent readback confirmed the incomplete slot without test outcomes. #289 remains In review awaiting a qualifying scheduled run. The production gate and branch rules matched the baseline.

## Reviewed genuine scheduled execution

[Qualification amendment](plan/2026-11-15-289-scheduled-qualification-amendment.md) · [Delay diagnosis](plan/schedule-delay-diagnosis.md) · [Exact execution and custody](plan/scheduled-historical.json) · [Signed independent review](plan/schedule-late-review.md).

GitHub's genuine scheduled run passed the complete suite on exact protected trunk. The post-deadline reader still reports the daily slot incomplete. The late receipt cannot authorize recovery. Production #103 and effective trunk rules matched the baseline.
