---
schema: "aitm.story/v0"
id: 100
title: "Multi-project agent usage monitor"
kind: "epic"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/100"
parent: null
children: [111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129]
blocking: []
blocked-by: [101, 102]
created: "2026-11-10T00:36:14Z"
updated: "2026-11-10T14:15:31+00:00"
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
