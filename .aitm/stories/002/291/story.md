---
schema: "aitm.story/v0"
id: 291
title: "[#133] Rehearse a human-operated trunk merge hold"
kind: "story"
state: "review"
issue: "https://github.com/kburson/aitm/issues/291"
parent: 133
children: []
blocking: [294]
blocked-by: [279, 289]
created: "2026-11-14T13:09:51Z"
updated: "2026-11-15T13:29:33Z"
last-branch: "planning"
estimate: {"agent-hours": 3, "size": "M"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-14-133-behavior-driven-validation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-15-291-trunk-hold-rehearsal-plan.md", "plan/verified-repair.json", "plan/recovery-replay.json", "plan/effective-after-release.json", "plan/2026-11-15-291-trunk-hold-rehearsal-results.md", "plan/hold-review.md", "plan/repair-nomination.json", "plan/repair-review.md", "plan/target.json", "plan/normal-rules.json", "plan/hold-rule.json", "plan/hold-released.json", "plan/effective-before-repair.json", "plan/effective-after-repair.json", "plan/rule-suite-5130601933.json", "plan/rule-suite-5130601719.json", "plan/rule-suite-5130624236.json", "plan/rule-suite-5130629935.json", "plan/rule-suite-5130629667.json", "plan/ordinary-after-release.json", "plan/operator-red-refusal.log", "plan/operator-push-refusal.log", "plan/ordinary-probe.log", "plan/ordinary-post.log", "plan/repair-ci.log", "plan/simulate_operator.py", "plan/replay-recovery.py", "plan/fixture/fixture.yml", "plan/fixture/hold-probe.yml", "plan/delivery.json"], "attachments": []}
expansions: []
trips: []
---

# [#133] Rehearse a human-operated trunk merge hold

Parent #133. Rank 120.

Rehearse the human-operated trunk-only hold on a disposable target. Verify ordinary agents cannot merge or push to the held target, other refs remain writable, only the designated separate human can approve one repair through the normal review path, and stale green cannot lift the hold. Keep live rules unchanged.

[Reviewed epic plan](../../001/133/plan/2026-11-14-133-behavior-driven-validation-plan.md). #103 governs production.

## Rehearsal plan

[Disposable GitHub rehearsal](plan/2026-11-15-291-trunk-hold-rehearsal-plan.md) records the target, independent actor controls and exact repair requirements.

## Reviewed disposable hold rehearsal

[Provider observations](plan/2026-11-15-291-trunk-hold-rehearsal-results.md) · [Signed independent review](plan/hold-review.md) · [Shadow recovery](plan/recovery-replay.json).

The scoped agent credential could update an unheld ref while GitHub refused trunk updates, merges and hold edits. The separately identified operator role used a simulated authorization to merge one exact passing repair and acknowledged fresh recovery. The rehearsal used synthetic data. Production credential separation and cutover remain for #294.
