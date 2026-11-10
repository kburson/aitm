---
schema: "aitm.review-response/v0"
story: 158
round: 2
level: "spr"
execution: "declared-manual"
input_commit: "58d2eb0840bfcd8652d7b05b26e6d7e26c150086"
inputs: {"design": {"path": ".aitm/stories/001/158/design/2026-11-10-158-qualify-github-merge-fence-design.md", "sha256": "4f390fc1c0f20c8c08b8be2b6ca90ccbe74d48c46e7a202a215bfb7dfd61b4d9", "lines": 128}, "plan": {"path": ".aitm/stories/001/158/plan/2026-11-10-158-qualify-github-merge-fence.md", "sha256": "53c09ab58c857d04384eb9ac08e0c206c4b71b502e509b0b48ea96eaabcc5a38", "lines": 191}, "jit": {"path": ".aitm/stories/001/158/plan/2026-11-10-158-jit.md", "sha256": "101ef7993f01e5c5e242e8c8f5945a166a7f3b207b100d2e8476f7a328678685", "lines": 127}}
role: "reviewer"
role_session: "codex-collaboration:/root/prep139"
finding_ids: []
---

# #158 independent SPR, round 2

Reviewer `codex-collaboration:/root/prep139`. Candidate `58d2eb0840bfcd8652d7b05b26e6d7e26c150086` in physical checkout `/Users/kpburson/.codex/worktrees/aitm-158-jit-review/trunk`. Verified HEAD and clean status, matched each physical file byte-for-byte with its candidate Git blob, and read every physical numbered line.

| Document | Physical lines read | Raw SHA-256 |
| --- | ---: | --- |
| `.aitm/stories/001/158/design/2026-11-10-158-qualify-github-merge-fence-design.md` | 1–128 | `4f390fc1c0f20c8c08b8be2b6ca90ccbe74d48c46e7a202a215bfb7dfd61b4d9` |
| `.aitm/stories/001/158/plan/2026-11-10-158-qualify-github-merge-fence.md` | 1–191 | `53c09ab58c857d04384eb9ac08e0c206c4b71b502e509b0b48ea96eaabcc5a38` |
| `.aitm/stories/001/158/plan/2026-11-10-158-jit.md` | 1–127 | `101ef7993f01e5c5e242e8c8f5945a166a7f3b207b100d2e8476f7a328678685` |

## Dispositions and evidence

- `R1-F001` resolved. Design lines 71–92 and plan lines 115–143 place M10 after the last authority check and immediately before external send, using an independent transport observation or forced contention with the actual serialization primitive. M11a keeps lost acknowledgment separate. M11b requires causal overlap or an independently verified host invariant that covers an already-sent request, durable fencing through restart, and refusal if the order remains unproved. Plan M06 additionally follows a terminal async enqueue to its distinct queue outcome. These preserve the accepted mutation and stop boundaries. [Accepted design](https://github.com/kburson/aitm/blob/2ff1b49ed3a3f91c8164d6c7b0e1dbe4c15cd3f9/.aitm/stories/001/133/design/test-impact-analysis-design.md#L394) · [Accepted T21](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L507)
- `R1-F002` resolved. Design lines 96–107, plan lines 168–188 and JIT lines 88–104 bind the non-source route to a separate isolated `codex/aitm-158-merge-fence-evidence` worktree based on authenticated `origin/planning`, with literal target `planning`. The route requires a pinned candidate, two exact payload digests, real matrix validation, independent review, authenticated publication mapping and sign-off. The disposable GitHub experiment and the AITM evidence delivery use separate checkouts and authority. [Manual delivery checklist](https://github.com/kburson/aitm/blob/93ac3a8e3ccc228762395cde87ea2aca109d32bc/.aitm/manual-delivery-checklist.md)
- Authenticated recheck found #158 open in Project Backlog, trunk still `a495d60a87ac4ca764f019dc266e579f13f1787e`, and ruleset `26821811` active with zero bypass actors. The current `origin/planning` ref was `0b5339b2d7dcba2ea2a25acee450360f953caa8e` when read and is deliberately re-pinned only at authorized pickup. JIT lines 57–86 preserve separate execution authorization, named disposable repo and target, actor and credential grants, and a custodian for unresolved intent. No live fixture mutation, execution or capability claim was part of this review. [Issue #158](https://github.com/kburson/aitm/issues/158) · [Production ruleset](https://api.github.com/repos/kburson/aitm/rulesets/26821811)

JIT lines 119–127 repeat the exact leaf-input digest block. The copies match the verified bytes and carry no conflicting instruction. This is editorial and leaves no required finding.

## Decision

accepted
