# #188 delivery checklist

Attempt 1. Implementer is the assigned Codex agent. Closure owner is the coordinating Codex agent. Target trunk. Pickup base `e4701f2e89d34f93f13d717199254b66aa3f0457`. Predecessors #187 are delivered. File ownership is defined by the exact pickup.

- [x] [Design, Plan and JIT](jit.md) and [independent acceptance](jit-review.md).
- [ ] Local verification, applicable hosted CI and independent source acceptance.
- [ ] Verified merge, implementing-agent sign-off, and issue/Project closure.

[Initial PR candidate](https://github.com/kburson/aitm/actions/runs/42957297464) head `7f71c4869f0831a50e1854dda46bb83fc78e9157`, base `f7646bc4da35173e9b0e468e4810b4e9265b0f47`, tree `c2ad949b50066906754e32ded528ac493f5e5f44`, was superseded before the Test transition. Independent precheck reproduced arbitrary selection between equally timed starts for two explicit attempts without an authoritative Develop. The replacement holds that ambiguity and keeps valid named Develop selection. The author reproduced both input-order variants red and verified the regression green.

## Candidate 2

[Source PR #213](https://github.com/kburson/aitm/pull/213) targets trunk base `f7646bc4da35173e9b0e468e4810b4e9265b0f47`. Exact head `f557062c55dafb02990b02480d88213163eac094` and tree `0df8ed8cfebd9b597d20e6c4851f060cfada0618` contain only the reviewed story paths. Focused dashboard tests, the full dashboard suite, Ruff, and whitespace checks passed on the clean checkout.

- [ ] [Hosted CI](https://github.com/kburson/aitm/actions/runs/42957581045), delivered verifier and independent source review.

Exact local proof retained historical and current planning pins, all ten direct and inclusive legacy totals, 114 seed intervals with no same-actor overlap, the seed's watermark, and #111's 774000 ms implementation elapsed with all-phase Unknown. An independent preliminary check found unresolved wait scope, stale attempts and ambiguous endpoints, gaps from held work affecting independent timing measures, and missing all-phase age for open planning states. The author reproduced and corrected each case, and added regression coverage before this candidate.

An additional review regression covers tied implementation starts in distinct attempts and requires Unknown when no authoritative Develop selects one. A valid authoritative Develop continues to pair its own Done. Both planning pins retain exact historical parity after this correction.
