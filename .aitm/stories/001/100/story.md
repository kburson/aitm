---
schema: "aitm.story/v0"
id: 100
title: "Multi-project agent usage monitor"
kind: "epic"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/100"
parent: null
children: [111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 134, 135, 137]
blocking: []
blocked-by: [101, 102]
created: "2026-11-10T00:36:14Z"
updated: "2026-11-10T16:41:02+00:00"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/000/83/design/usage-capture-design.md"
files: {"draft": "draft.md", "events": "events.jsonl", "design": ["design/multi-project-usage-monitor-design.md"], "plan": ["plan/multi-project-usage-monitor-implementation-plan.md"], "attachments": []}
expansions: []
trips: []
---

# Multi-project agent usage monitor

[GitHub issue #100](https://github.com/kburson/aitm/issues/100)

Extend the delivered [#83 collector](../../000/83/story.md) to concurrent registered projects with Codex, Claude Code and Grok Build CLI, event-assisted park/resume, project totals, and story drilldown.

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

## GitHub Project metadata

[Board reconciliation receipt](plan/project-metadata-receipt.json). Rank follows the board's increment of ten in accepted leaf order, with the Linux carrier prerequisites before #129. The epic is sized Feature. Size and Estimate on each leaf follow its recorded JIT, and Start date follows its first recorded Development entry in America/Chicago. Carry those three fields into the Project pickup readback for each subsequent leaf. Pending leaf estimates and starts stay blank until those gates. An aggregate epic estimate remains open.

The reviewed M05 pickup recorded [#137 M05-LG](../137/story.md) for the unavailable Linux Grok carrier. It follows #115 and blocks #129. [Split and board readback](../115/plan/linux-carrier-split.json).
