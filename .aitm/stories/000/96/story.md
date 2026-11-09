---
schema: "aitm.story/v0"
id: 96
title: "[Usage U11] Project Mac activation and dogfood proof"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/96"
parent: 83
children: []
blocking: []
blocked-by: [95]
created: "2026-11-09T14:42:23Z"
updated: "2026-11-09T14:43:23+00:00"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 83, "key": "U11", "path": ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md", "publication": "6ee371590ff3ce0cb5a108bdd1e89cfb17bc2300", "raw-sha256": "07919dde4475310b7fe277791206f611ce5cd615eeaed491d3a619e61142daf5", "section-sha256": "b5ed262c26a3ce66312ea851a5e1b8161dff72e5074df7b8180cc7785fe58d2e"}
---

# [Usage U11] Project Mac activation and dogfood proof

[GitHub issue](https://github.com/kburson/aitm/issues/96) · [Parent #83](../83/story.md) · Backlog

**Required predecessors** [#95](../95/story.md)

## Accepted parent decomposition

**Files** `README.md` and the sanitized receipt at `.aitm/stories/000/83/attachments/activation-receipt.json` on planning. U10 supplies the installed qualification command and tests.

- [ ] After execution and activation are authorized, use scheduled Core #2 child preparation for C01/#3 and C02/#4 as the normal shared-chat observation where separately authorized. Use one controlled real Codex planning session with an epic and two draft children to supply any missing hydration, focused planning or graduation evidence. Use disposable scoped identities for graduation in that proof and label them controlled. Run an overlapping normal Claude review. The validator distinguishes these live sources from fixture-only evidence. The time spent on observed planning and review is outside U11’s 3.5-hour qualification estimate. If neither route produces sufficient evidence, retain the gap and keep the C01 checkpoint open.
- [ ] Build the two rehearsal environments from the reviewed wheel and a version-only rehearsal wheel of the same reviewed source, each with a recorded digest. Rehearse upgrade and rollback in isolated project state before installing the production collector.
- [ ] Install the reviewed package on the project Mac. Observe unattended launchd startup, verify restart catch-up, rehearse supported backup and upgrade with verified recovery and same-cutoff parity, exercise the real routes including supported nested work, model/effort changes and retry evidence or explicit coverage gaps, and validate and publish the receipt with the version, dated evidence and digest. Demonstrate an export replay without duplication and that Unknown remains visible.
- [ ] Verify that the collector is active and coverage is current before authorizing C01 pickup. The same service and ledger continue when Core is released and when C44 starts accepting compatible usage.
