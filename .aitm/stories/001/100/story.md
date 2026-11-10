---
schema: "aitm.story/v0"
id: 100
title: "Multi-project agent usage monitor"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/100"
parent: null
children: []
blocking: []
blocked-by: [101, 102]
created: "2026-11-10T00:36:14Z"
updated: "2026-11-10T03:08:15Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/000/83/design/usage-capture-design.md"
files: {"draft": "draft.md", "events": "events.jsonl", "design": ["design/multi-project-usage-monitor-design.md"], "plan": [], "attachments": []}
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

This is a follow-on to the closed #83. The authorized work is research, spec review and planning.

## Accepted specification

Accepted SHA-256 `1a5e9bb35335ab294bfc3c0d3a925bcd5eefc72d399fee52971842c6a1c241a9` after [SAR](design/reviews/sar-2026-11-09-monitor-spec/review-manifest.md), [independent manual SPR](design/reviews/spr-2026-11-09-monitor-spec/review-manifest.md) and [native Claude XPR](design/reviews/xpr-2026-11-09-monitor-spec/review-manifest.md). Both spike reports were incorporated before review. Full-file retrieval was verified for all three SPR rounds and both XPR rounds. This acceptance authorizes drafting the plan under the owner’s planning direction.
