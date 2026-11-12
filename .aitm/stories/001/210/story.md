---
schema: "aitm.story/v0"
id: 210
title: "[M08b4c] Verified paired disposition settlement"
kind: "story"
state: "test"
issue: "https://github.com/kburson/aitm/issues/210"
parent: 100
children: []
blocking: [119, 204]
blocked-by: [209]
created: "2026-11-11T02:38:35Z"
updated: "2026-11-12T16:03:31+00:00"
last-branch: "codex/aitm-210-native-quota-recovery"
estimate: {"agent-hours": 4.4, "size": "M"}
priority: null
origin: ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-12-210-native-quota-recovery-jit.md", "plan/2026-11-12-210-paired-settlement-jit.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan-split", "story": 100, "key": "M08b4c", "source-leaf": 199, "raw-sha256": "8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21", "split-sha256": "1c97ab7d36b9fe162e59472e89da03a36b2ddbcf83717f6fb70a89eeba85000f", "path": ".aitm/stories/001/199/plan/2026-11-10-199-m08b-proof-split.md", "refinement": {"source-leaf": 203, "sha256": "0158b267bcfcee8989639d7aa89a84bdf4e1687849ec449abfab07fe198a6cbf", "path": ".aitm/stories/001/203/plan/2026-11-10-203-disposition-proof-split.md"}}
---

# [M08b4c] Verified paired disposition settlement

[GitHub issue #210](https://github.com/kburson/aitm/issues/210) · [Epic #100](../100/story.md) · [Accepted split](../203/plan/2026-11-10-203-disposition-proof-split.md)

Direct child of Epic #100. Requires #209 and directly gates #119 and #204.

Qualify a genuinely settled native terminal with no later usage under chronological public-reader evidence. A proof-only EOF receipt with an unresolved boundary or absent cursor cannot settle it. Independently verify both owner and rival source/span/frontier authorities before any paired release. Derive the admitted routing ScopeView's effective hold from the one committed journal change under the existing writer and publication fence. Keep earlier evidence, first ownership, unsupported coverage, and all unresolved frontiers. M09 retains publication and project ACK.

Project 24 Rank 228.2. Size and Estimate follow independent Refine and JIT. Start Date follows Develop.

## Independent Refine checkpoint

[Refine](plan/2026-11-11-210-native-terminal-refine.md) held because no chronological public-reader control qualified a genuinely settled no-later-usage terminal. [Independent verdict](plan/2026-11-11-210-native-terminal-refine-review.md) · [Native qualification evidence](plan/native-terminal-qualification.json).

## Active Refine and qualification JIT

Project 24 shows Refine at Rank 228.2. The independent Claude review passed the amended read-only qualification JIT. The owner already authorized continuation. The synthetic qualification reader can recognize the completion while preserving existing reader outputs. A genuine Desktop disposition and later-usage control remain required for effective settlement. The installed launcher predates the monitor subcommand. The partial Actual derived from bounded coordinator progress is 0.1853 hours. [Exact amended JIT](plan/2026-11-11-210-native-completion-qualification-jit.md) · [Independent verdict](plan/2026-11-11-210-native-completion-qualification-jit-review-r2.md) · [Actual evidence](attachments/timing/native-completion-qualification-actual-input.json)

## Genuine Desktop capture

The staged launcher queued a genuine Desktop disposition, and the public reader verified its owned request. The completion was attributed to the coordinating chat's root and the reader recorded quota coverage gaps. The later-usage control kept the hold intact. [Capture and exact refusals](plan/2026-11-12-210-native-desktop-capture.md).

## Qualified Desktop capture

The re-run passed the self-root, authenticated quota, exact accounting and fixed prefix checks, and the genuine later-usage control refused the witness. The native Refine prerequisite is met. Effective paired settlement still requires its independent JIT and verified delivery. [Native pass](plan/2026-11-12-210-native-quota-capture-pass.md).


## Paired settlement Develop

The [accepted exact JIT](plan/2026-11-12-210-paired-settlement-jit.md) and its [independent PASS](plan/2026-11-12-210-paired-settlement-jit-review.md) cover a durable two-project ownership dispute and two independently proven physical frontiers. The accepted split and the live issue define the other shapes as unsupported coverage to retain. No undisputed, GAP-only, mixed, same-project content, missing-rival or diagnostic case supplies a release or advances a held frontier. [Recorded owner direction for the completion anchor](plan/2026-11-11-210-completion-receipt-followup.md).

Project 24 reads back Dev, Rank 228.2, Estimate 4.4 hours, Size M, Start date 2026-11-12, and Actual 0.4958 hours partial. Estimate includes the roughly 0.4 hours of recorded coordinator work entering Develop and up to 4 hours planned for settlement. It is a planning forecast. Review and hosted wait are tracked separately. [Project readback](plan/project-settlement-develop.json) · [Partial Actual evidence](attachments/timing/paired-settlement-actual.json).


## Exact Test entry

[PR #266](https://github.com/kburson/aitm/pull/266) is ready for review at head `ede095d8ce46d6d1dc5138a849259cfc74e34787`, tree `6f1ae4a5707f2344bbeb4c15efdb823480866feb`, and literal trunk `22f265b6aa7c24050c2d798d7e16c1796701cf64`. All 1,216 product and CLI tests and 196 helpers passed on the locked local runtime. Raw lines covered were 11,272/12,276 product and 806/849 helpers. Both required child processes produced verified coverage, and the literal v4 reader refused a v5 store. [Exact local evidence](plan/local-settlement-verification.json) · [Native chronology](plan/native-fixed-prefix-chronology.json).

The hosted run and independent exact source review remain separate gates. Project 24 reads back Test, Estimate 4.4 hours and Actual 0.5998 hours partial. [Project readback](plan/project-settlement-test.json) · [Partial Actual evidence](attachments/timing/paired-settlement-test-actual.json).
