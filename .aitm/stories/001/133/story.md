---
schema: "aitm.story/v0"
id: 133
title: "Test impact analysis, CI sharding, and Stop the Line"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/133"
parent: null
children: []
blocking: []
blocked-by: []
created: "2026-11-10T15:32:13Z"
updated: "2026-11-10T15:35:27Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/drafts/2026-11/20261110-0915-test-impact-analysis/draft.md"
files: {"draft": "draft.md", "events": "events.jsonl", "design": ["design/test-impact-analysis-design.md"], "plan": [], "attachments": []}
expansions: []
trips: []
---

# Test impact analysis, CI sharding, and Stop the Line

[GitHub issue #133](https://github.com/kburson/aitm/issues/133)

As an AITM contributor, I want story validation to show which tests are
affected, run them on independent CI shards, and run the full suite
whenever impact is uncertain. If a defect escapes PR validation and
fails the scheduled trunk suite, restore trunk and deliver the fix to
all governed workspaces before ordinary work resumes.

This is a follow-on to the delivered [#103 CI quality gates](../103/story.md).

## Design review

The [graduated draft](draft.md) records the initial requirements. The
[design specification](design/test-impact-analysis-design.md) is the
team's review candidate. Use the [review intake](design/reviews/README.md)
to bind collateral to the exact revision. The story remains in Backlog
while the specification awaits acceptance.
