---
schema: "aitm.story/v0"
id: 274
title: "[#146 Spike] Test exact-tree admission for observed pytest"
kind: "story"
state: "review"
issue: "https://github.com/kburson/aitm/issues/274"
parent: 146
children: []
blocking: []
blocked-by: []
created: "2026-11-13T04:56:25Z"
updated: "2026-11-13T05:08:18Z"
last-branch: "planning"
estimate: {"agent-hours": 2, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/146/plan/2026-11-12-146-trusted-observation-replan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/manifest.sha256", "plan/independent-review.md", "plan/admit.py", "plan/run.py", "plan/test_admit.py", "plan/full-policy.json", "plan/selected-provisional-policy.json", "plan/evidence-full.json", "plan/evidence-selected-provisional.json", "plan/plan.md", "plan/findings.md", "plan/verification.log"], "attachments": []}
expansions: []
trips: []
---

# [#146 Spike] Test exact-tree admission for observed pytest

Determine whether the selected and full observations can be consumed for explicitly reviewed, immutable product and observer inputs. Exercise an admitted exact tuple, a changed executable tree, a changed observer, and stale attempt and assignment inputs. Document the candidate-code trust boundary and production integration decision.

Rank 50. #148 and #267 remain on hold.

## Independently reviewed result

[Findings](plan/findings.md) · [Signed review](plan/independent-review.md) · [Evidence manifest](plan/manifest.sha256).
