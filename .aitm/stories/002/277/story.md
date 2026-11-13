---
schema: "aitm.story/v0"
id: 277
title: "[#133] Verify canonical full-CI evidence for advisory warnings"
kind: "story"
state: "test"
issue: "https://github.com/kburson/aitm/issues/277"
parent: 133
children: []
blocking: [278]
blocked-by: []
created: "2026-11-13T05:14:12Z"
updated: "2026-11-13T10:57:00Z"
last-branch: "planning"
estimate: {"agent-hours": 3, "size": "M"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-12-133-ci-warning-manual-recovery-replan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-13-277-canonical-ci-intake-plan.md", "plan/reviews/plan-review.md", "plan/live-current.json", "plan/shadow.json", "plan/shadow.py", "plan/local-test.log", "plan/offline-replay.py", "plan/offline-replay.log", "plan/historical-rerun.json", "plan/hosted-attempt-1.json", "plan/hosted-attempt-2.json", "plan/hosted-attempt-3.json", "plan/reviews/source-assessment.md"], "attachments": []}
expansions: []
trips: []
---

# [#133] Verify canonical full-CI evidence for advisory warnings

<!-- aitm-133-advisory-canonical-intake -->

Parent #133. Rank 70. No implementation predecessor.

Read canonical #103 full trunk push metadata and exact attempt jobs. Pin the repository, workflow, target, current SHA and latest attempt. Retain failure with missing sibling evidence. Validate green against complete #103 evidence. Exercise failure without artifact, stale delivery and unavailable evidence in shadow. Deliver read-only replayable decisions. Existing #103 remains the gate.

[Reviewed replacement scope](https://github.com/kburson/aitm/blob/7d5e0d332ef328c48c4e3428089cb33253c65a8e/.aitm/stories/001/133/plan/2026-11-12-133-ci-warning-manual-recovery-replan.md).

## Reviewed plan

[Implementation plan](plan/2026-11-13-277-canonical-ci-intake-plan.md) · [Independent review](plan/reviews/plan-review.md).

## Test evidence

[Live green](plan/live-current.json) · [Shadow decisions](plan/shadow.json) · [Replay recipe](plan/shadow.py) · [Local tests](plan/local-test.log) · [PR #281](https://github.com/kburson/aitm/pull/281).

## Replacement candidate

The source review found a readback path that dropped authenticated red evidence and a timestamp rule that rejected valid reruns. The replacement retains red with a freshness gap, distinguishes malformed sibling evidence, and accepts provider rerun record timestamps. The exact candidate passed 158 local tests and repeated [live and shadow validation](plan/offline-replay.log).

## Hosted base timeouts

The exact candidate's Python, quality and file checks passed on attempts 1 and 2. The inherited serial base lane reached its configured eight-minute job limit before artifact upload on both attempts. [Attempt 1](https://github.com/kburson/aitm/actions/runs/43409093456/attempts/1) · [Attempt 2](https://github.com/kburson/aitm/actions/runs/43409093456/attempts/2).

## Independent source assessment

[Exact candidate source and advisory evidence assessment](plan/reviews/source-assessment.md) found no material issues. Formal review admission depends on complete hosted #103 evidence. [Hosted attempt 3](https://github.com/kburson/aitm/actions/runs/43409093456/attempts/3) retained the same base timeout.
