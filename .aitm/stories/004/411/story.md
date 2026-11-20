---
schema: "aitm.story/v0"
id: 411
title: "Accept any Ubuntu 24.04 build in the trusted receipt"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/411"
parent: 356
children: []
blocking: [360]
blocked-by: []
created: "2026-11-20T21:18:00Z"
updated: "2026-11-20T21:18:00Z"
last-branch: "planning"
estimate: {"agent-hours": 3, "size": "S"}
priority: "P2"
origin: ".aitm/stories/003/360/plan/2026-11-20-360-delivery-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# Accept any Ubuntu 24.04 build in the trusted receipt

[GitHub issue #411](https://github.com/kburson/aitm/issues/411) · [Parent #356](../../003/356/story.md) · [Blocked story #360](../../003/360/story.md)

Project 24 Rank 595. Priority P2. Size S. Estimate 3 agent-hours.

The trusted pull-request receipt accepts any observed build of the requested `ubuntu-24.04` label. It keeps both observed builds. It does not require the base job and the candidate job to draw the same image build.

This is an enhancement of the trusted-base rule. The current exact-build comparison does what it was written to do. GitHub's `ubuntu-24.04` label cannot assign one build to every job in a run.

## Behavior

Each trusted job records two image facts. `runner` is the requested label, `ubuntu-24.04`. `image` is the observed `ImageOS:ImageVersion` build, such as `ubuntu24:20261116.376.1`.

`tools/ci/python_gate.py` and `tools/ci/verify_pr.py` accept the base and candidate pair when both `runner` values are `ubuntu-24.04`. The observed `image` strings may differ. Both strings remain on the receipt.

The pinned runtime stays `3.13.9`. The source identity stays exact: base commit, tree, observer, policy, lock, and configuration. A label other than `ubuntu-24.04`, a missing image, or a different runtime still fails. The Darwin receipt is unchanged.

The ordinary path map, the tests selected for a pull request, the sweep workflow, and the pinned #355 command stay unchanged. Do not put this change in PR #410.

## Acceptance

- One base and candidate pair with `runner` `ubuntu-24.04` and different observed builds passes the gate and the verifier. The receipt shows both builds.
- The same pair passes when the observed builds are equal.
- A different runner label, a missing image, or a runtime other than `3.13.9` fails.
- A changed base commit, tree, observer, policy, lock, or configuration still fails.

[#360](../../003/360/story.md) stays blocked until this receipt is accepted.
