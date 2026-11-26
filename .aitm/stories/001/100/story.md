---
schema: "aitm.story/v0"
id: 100
title: "Multi-project agent usage monitor"
kind: "epic"
state: "done"
issue: "https://github.com/kburson/aitm/issues/100"
parent: null
children: [111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 134, 137, 182, 194, 199, 201, 202, 203, 209, 210, 269, 282, 300, 303, 304, 310, 320, 325, 326, 329, 330, 331, 335]
blocking: []
blocked-by: [101, 102, 456]
created: "2026-11-10T00:36:14Z"
updated: "2026-11-26T15:06:19.931Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/000/83/design/usage-capture-design.md"
files: {"draft": "draft.md", "events": "events.jsonl", "design": ["design/multi-project-usage-monitor-design.md"], "plan": ["plan/multi-project-usage-monitor-implementation-plan.md", "plan/2026-11-19-100-portable-service-amendment.md", "plan/2026-11-25-100-session-owned-scope-disposition.md"], "attachments": []}
expansions: []
trips: []
---

# Multi-project agent usage monitor

## Closeout

**Superseded.** The original global-monitor epic was not delivered. All 42 direct children are closed, with 32 Completed and 10 Not planned. The accepted replacement [#456](https://github.com/kburson/aitm/issues/456) shipped session-owned capture, pinned reports and the fixture-qualified Core producer. Completed #456 now directly satisfies the producer prerequisite for Core #2. Live Core receiver qualification remains in #230 after #51, using the completed #459 producer.

Standalone follow-ons are #468 for routine chat capture and closeout, #469 for pinned Claude pricing, #466 for ordinary Claude CLI on Linux, and #467 for live Claude parent and child accounting. [Successor delivery evidence](https://github.com/kburson/aitm/blob/2ec8bca0934c62bbb44866ea57fb5c2776960c0c/.aitm/stories/004/456/retro/2026-11-26-delivery-sign-off.md).

[GitHub issue #100](https://github.com/kburson/aitm/issues/100)

Extend the delivered [#83 collector](../../000/83/story.md) to concurrent registered projects with Codex, Claude Code and Grok Build CLI, event-assisted park/resume, project totals, and story drilldown.

## Current direction

The agent in the live chat owns activity and cost measurement for its own turns and the turns it supervises, including spawned headless agents, subagents, and SPR/XPR reviewers. Record each measured turn against the story active in the owning session when the turn starts or is dispatched. Publish sanitized evidence to that story on `planning`, with exact recovery, replay, and coverage gaps visible. The delivery target is a lightweight session-owned reporter. Global project monitoring and an always-on host service are outside the current direction.

Use #100's existing work as a learning foundation alongside #422–#435. The earlier monitor plan remains a historical record. The standalone [Spike #455](https://github.com/kburson/aitm/issues/455) will compare the session-owned approach with the ten open monitor children. For each child, it will assess whether to recommend closure as **Not delivered** or whether the remaining capability offers significant value. For work worth retaining, it will outline a lightweight delivery path based on what we learned from #422 onward and trace the implications for Core #2 and #230.

## Evidence and review order

1. [#101 Grok Build CLI evidence](../101/story.md) and [#102 Linux evidence](../102/story.md) are independent blockers for spec acceptance. Incorporate both reports into the spec and carry their implementation constraints into the plan.
2. Review the [spec](design/multi-project-usage-monitor-design.md) through SAR, independent SPR and independent XPR to acceptance. Retain exact revisions, full-file coverage and review collateral in `design/reviews/`.
3. Draft the implementation plan after spec acceptance. Retain the plan and its separate review collateral under `plan/`.

This is a follow-on to the closed #83. The original assignment covered research, spec review and planning.

## Accepted specification

Accepted SHA-256 `1a5e9bb35335ab294bfc3c0d3a925bcd5eefc72d399fee52971842c6a1c241a9` after [SAR](design/reviews/sar-2026-11-09-monitor-spec/review-manifest.md), [independent manual SPR](design/reviews/spr-2026-11-09-monitor-spec/review-manifest.md) and [native Claude XPR](design/reviews/xpr-2026-11-09-monitor-spec/review-manifest.md). Both spike reports were incorporated before review. Full-file retrieval was verified for all three SPR rounds and both XPR rounds. This acceptance authorizes drafting the plan under the owner’s planning direction.

## Accepted implementation plan

The [implementation plan](plan/multi-project-usage-monitor-implementation-plan.md) was drafted after spec acceptance and accepted at SHA-256 `8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21`. It defines 19 leaves and separate native macOS and Linux qualification gates.

The full cycle includes [SAR](plan/reviews/sar-2026-11-10-monitor-plan/review-manifest.md), [independent manual SPR](plan/reviews/spr-2026-11-10-monitor-plan/review-manifest.md) and [native Claude XPR](plan/reviews/xpr-2026-11-10-monitor-plan/review-manifest.md). Full-file retrieval was checked in every independent round. Plan acceptance ends this review assignment.

## Verified implementation backlog

#100 is the aggregate parent of the 19 numbered stories. The [leaf catalog](plan/leaf-stories.md) maps the accepted M01–M19 order to their GitHub numbers and 24 direct dependencies. The [verification receipt](plan/leaf-issue-receipt.json) records the native parent links, reciprocal dependency edges and Backlog status. The parent stayed in Backlog through that verification.

## Full-Auto delivery

The owner authorized source delivery after [#103](../103/story.md) closed. Development starts with [#111](../111/story.md) on the exact delivered trunk. Close each accepted leaf on its own evidence. Production cutover follows the separate decision in the accepted plan.

The #103 delivery found the installed launcher cleared the Codex chat identity before authenticating a scope marker. The accepted plan already calls for the exact legacy carrier in M07 and the installed invocation in M18. Carry this observed launcher failure into those checks. [Usage observation](../103/attachments/delivery-evidence.md#agent-measurement)

Full-Auto paused at the owner’s direction after [#111](../111/story.md) closed as Done at `2026-11-10T14:28:21Z`.

Full-Auto resumed November 10, 2026. [#112 M02](../112/story.md) and [#113 M03](../113/story.md) delivered to trunk with exact signed CI, independent source review and implementing-agent sign-off. Both issues were read back as closed and Done. M02's ext4 proof records the observed [Python 3.13.18 baseline pricing import incompatibility](../112/attachments/ext4-publication-proof.md) for later Linux runtime selection.

The reviewed M04 pickup split unavailable Linux carriers into [#134 M04-LC](../134/story.md) and [#135 M04-LA](../135/story.md). Each follows #114 and blocks #129. The original accepted plan is preserved. [Split receipt](../114/plan/linux-carrier-split.json).

The reviewed M07 split retains [#117 M07a](../117/story.md) for native routing and holds and assigns [#182 M07b](../182/story.md) the producer, compatibility and installed launcher work. Both gate #118. [Split and native evidence](../117/plan/2026-11-10-117-m07-split.md) · [Board receipt](../117/plan/2026-11-10-117-m07-split-receipt.json).

The reviewed disposition split assigns [#203](../203/story.md) the separate native receipt proof, [#209](../209/story.md) atomic journal recording and [#210](../210/story.md) qualified effective settlement. All three directly gate #119, and #210 also gates #204. [Accepted split and native readback](../203/plan/2026-11-10-203-disposition-proof-split.md).

## GitHub Project metadata

[Board reconciliation receipt](plan/project-metadata-receipt.json). Rank follows the board's increment of ten in accepted leaf order, with the Linux carrier prerequisites before #129. The epic is sized Feature. Size and Estimate on each leaf follow its recorded JIT, and Start date follows its first recorded Development entry in America/Chicago. Carry those three fields into the Project pickup readback for each subsequent leaf. Pending leaf estimates and starts stay blank until those gates. An aggregate epic estimate remains open.

The reviewed M05 pickup recorded [#137 M05-LG](../137/story.md) for the unavailable Linux Grok carrier. It follows #115 and blocks #129. [Split and board readback](../115/plan/linux-carrier-split.json).

## Later product enhancement

After base monitor proof, develop independent distribution and optional
AITM-Core runtime configuration as a separate enhancement.
[Proposed design](design/independent-deployment-enhancement.md) ·
[Proposed plan](plan/independent-deployment-enhancement.md).

The independently reviewed M08b split narrows [#199](../199/story.md) to the writer-issued Claude source proof and adds [#201](../201/story.md), [#202](../202/story.md), [#203](../203/story.md), [#204](../204/story.md) as separate #119 gates. The folded usage leaf stays open unless exact covering native evidence and the atomic intent pass or an independently re-accepted parent change has a verified replacement blocker. [Native split receipt](../199/plan/2026-11-10-199-m08b-proof-split-receipt.json).


## Production Cost qualification from #181

Monitor completion includes #123 fenced reports and #124 versioned exports with approved receiver-fixture qualification. [#230](../../002/230/story.md) moved to Core #2 for the live integration check, after #51. [Dependency replan](../../002/230/plan/2026-11-11-230-cost-dependency-replan.md).

## Qualified-source release amendment

[Independently accepted R3](https://github.com/kburson/aitm/blob/54f2a7f93668d1a5c744be8a8a654a51b073e2cc/.aitm/stories/001/119/plan/2026-11-13-119-qualified-sources-reacceptance-r3.md) assigns [M08b6 #295](../../002/295/story.md) as a direct prerequisite of #119. [M09-Folded #296](../../002/296/story.md) owns the later positive delivery proof. See the [verified native graph](../119/plan/qualified-source-graph-readback.json).

## Completion scope

The independently accepted [completion amendment](plan/2026-11-14-100-qualified-monitor-activation.md) moves the open folded Claude work to sibling [Epic #297](../../002/297/story.md). #100's remaining release scope retains R3 containment, qualified per-turn accounting, and all integrated and native gates. [Verified graph and closure manifest](plan/qualified-monitor-completion-readback.json).

## Ordinary Claude CLI carrier

The independently accepted [#298 carrier](../../002/298/story.md) precedes [#295 containment](../../002/295/story.md). [Current closure manifest](plan/qualified-monitor-carrier-readback.json).

## Qualified-cost release re-acceptance

R2 independently passed. The current native graph stays authoritative until the replacement blockers, sibling parentage and final exact edge sets are verified. [Exact amendment](plan/2026-11-14-100-qualified-cost-acceptance-r2.md) · [Receipts](plan/qualified-cost-reacceptance-receipt.json).

## Verified qualified-cost release scope

[#300](https://github.com/kburson/aitm/issues/300) directly blocks #119 and #129. The live Claude work now belongs to [#301](https://github.com/kburson/aitm/issues/301). #297 retains the folded scope. See the [current graph and exact release child set](plan/qualified-cost-release-graph.json).

## Verified admission and coverage split

#303 owns first-release admission enforcement and must deliver before #300. Both directly gate #119 and #129. [Independent acceptance](https://github.com/kburson/aitm/blob/f98161a1728343cf2761fb9317735cd2241c0090/.aitm/stories/003/300/plan/2026-11-14-300-qualified-policy-split.md).

## Verified isolated issuer ownership

#304 owns the actual isolated installation's executable and authorization evidence. #303 owns the closed contract. [Accepted amendment](https://github.com/kburson/aitm/blob/79aecafe17c5dc0417fd00c2ecd37cdfe3651d58/.aitm/stories/003/303/plan/2026-11-14-303-isolated-source-issuer-amendment.md).

## Accepted M10 split

[#120](../120/story.md) owns the wake scheduler and private ingress. [#320](../../003/320/story.md) owns the native installers before #125. [Exact accepted amendment](../120/plan/2026-11-15-120-wake-scheduler-installer-split.md).

## Accepted M11 split

[#325](../../003/325/story.md) owns native watch resources at Rank 245. [#326](../../003/326/story.md) owns metadata-first selected admission at Rank 247.5. Both block [#121](../121/story.md), which retains the coordinator. [Accepted amendment](../121/plan/2026-11-15-121-watch-inventory-coordinator-split-r2.md).

## Accepted Grok delivery prerequisites

[#329](../../003/329/story.md) owns verified Grok capture at Rank 248. It blocks [#330](../../003/330/story.md), which owns guarded journal delivery at Rank 249 and blocks [#121](../121/story.md). [Accepted amendment](../121/plan/2026-11-15-121-grok-guarded-delivery-amendment.md).

## Portable service amendment

Owner direction on 2026-11-19. The monitor service is one Python program. The host supplies CPython 3.13. [#125](../125/story.md) delivers `ServiceSupervisor` and a JSON registration. The Apple plist, the LaunchAgent, and the systemd user unit leave the first release. Login restart is a later epic. [#128](../128/story.md) stays the Mac Codex Desktop carrier qualification. [#129](../129/story.md) stays the Linux carrier qualification. [Amendment](plan/2026-11-19-100-portable-service-amendment.md).

## Accepted session-owned replan

[Successor Epic #456](https://github.com/kburson/aitm/issues/456) owns the lightweight capture, reporting, and producer outcomes. The ten legacy monitor contracts have an approved **Not delivered** disposition. [Disposition and verified dependency rebaseline](plan/2026-11-25-100-session-owned-scope-disposition.md).

GitHub confirmed all ten legacy monitor issues closed as **Not delivered**. [Successor Epic #456](https://github.com/kburson/aitm/issues/456) carries the retained work.
