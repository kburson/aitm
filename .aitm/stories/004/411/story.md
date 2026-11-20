---
schema: "aitm.story/v0"
id: 411
title: "Accept any build of the requested runner label"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/411"
parent: 356
children: []
blocking: [360]
blocked-by: []
created: "2026-11-20T21:18:00Z"
updated: "2026-11-20T21:28:00Z"
last-branch: "planning"
estimate: {"agent-hours": 3, "size": "S"}
priority: "P2"
origin: ".aitm/stories/003/360/plan/2026-11-20-360-delivery-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# Accept any build of the requested runner label

[GitHub issue #411](https://github.com/kburson/aitm/issues/411) · [Parent #356](../../003/356/story.md) · [Blocked story #360](../../003/360/story.md)

Project 24 Rank 595. Priority P2. Size S. Estimate 3 agent-hours.

The trusted pull-request receipt accepts any observed build of the runner label the workflow requested for that run. It keeps both observed builds. It does not require the base job and the candidate job to draw the same image build.

The gate does not contain a fixed label. The workflow's `runs-on` value is the requested label. Today's jobs request `ubuntu-24.04`. A later change of that value to a newer versioned label, such as `ubuntu-26.04`, uses the same rule with no change to the gate.

This is an enhancement of the trusted-base rule. The current exact-build comparison does what it was written to do. A hosted label cannot assign one image build to every job in a run.

## Behavior

Each trusted job records two image facts. `runner` is the label that job requested, taken from its `runs-on` value. `image` is the observed `ImageOS:ImageVersion` build.

`tools/ci/python_gate.py` and `tools/ci/verify_pr.py` accept the base and candidate pair when both `runner` values are the same versioned label and each observed `image` is a build of that label. For a label `ubuntu-N.MM`, a build of that label has `ImageOS` `ubuntuN`. `ubuntu-24.04` matches `ubuntu24:20261116.376.1` and `ubuntu24:20261116.133.1`. `ubuntu-26.04` matches an `ubuntu26:` build. The gate derives `ubuntuN` from the recorded label. It does not store one Ubuntu release as a constant.

The observed `image` strings may differ. Both strings remain on the receipt.

The pinned runtime stays `3.13.9`. The source identity stays exact: base commit, tree, observer, policy, lock, and configuration. Two different requested labels fail. An observed image from another OS release fails. A missing label, a missing image, or a different runtime fails. The Darwin receipt is unchanged.

This story does not change the workflow's current `runs-on` value. The ordinary path map, the tests selected for a pull request, the sweep workflow, and the pinned #355 command stay unchanged. Do not put this change in PR #410.

## Acceptance

- A pair that both requested `ubuntu-24.04`, with different observed `ubuntu24:` builds, passes the gate and the verifier. The receipt shows both builds.
- A pair that both requested `ubuntu-26.04`, with different observed `ubuntu26:` builds, passes the same way. This pair shows that the gate follows the requested label.
- A pair whose observed builds are equal passes.
- Two jobs that requested different labels fail.
- An observed image whose OS release does not match the requested label fails.
- A missing label, a missing image, or a runtime other than `3.13.9` fails.
- A changed base commit, tree, observer, policy, lock, or configuration still fails.

[#360](../../003/360/story.md) stays blocked until this receipt is accepted.
