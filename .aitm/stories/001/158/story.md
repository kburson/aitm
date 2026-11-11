---
schema: "aitm.story/v0"
id: 158
title: "[#133 T21] Qualify the GitHub merge fence"
kind: "spike"
state: "plan"
issue: "https://github.com/kburson/aitm/issues/158"
parent: 133
children: []
blocking: [159]
blocked-by: []
created: "2026-11-10T16:51:45Z"
updated: "2026-11-10T22:29:00Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": ["design/2026-11-10-158-qualify-github-merge-fence-design.md"], "plan": ["plan/2026-11-10-158-qualify-github-merge-fence.md", "plan/2026-11-10-158-jit.md", "plan/reviews/spr-2026-11-10-jit/review-manifest.md"], "attachments": ["attachments/github-merge-fence-spike.md", "attachments/github-merge-fence-rules.json"]}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T21", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "4c57ac72e211b052a8b7ffee538b492427775b5dc3f365a1640c80f72ac54742"}
---

# [#133 T21] Qualify the GitHub merge fence

[GitHub issue #158](https://github.com/kburson/aitm/issues/158) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L507)

**Required predecessors** None.

The planning estimate is 3.5 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T21. Qualify the GitHub merge fence — 3.5h, P1, no predecessor

**Owns** spike report and disposable repository rules evidence.
**Interface** receipt for one qualified GitHub merge method or refusal.

- [ ] In an owner-authorized disposable repo, test a dedicated
  trusted actor, host-enforced exclusive target updates, and a
  head-conditional PR merge. Require proof that the tested tree
  is the exact result of the permitted merge method.
- [ ] Exercise direct push, web/API, other automation, queue,
  head/base movement at mutation, stop between reservation and
  dispatch, and ambiguous in-flight ordinary merge concurrent with a
  stop. Prove the host commit and stop can be ordered. An unsent
  superseded request cannot dispatch. An ambiguous request fences all
  further mutations until readback establishes whether it committed
  before the stop or cannot commit. Reject any route where an ordinary
  update can still commit after the stop. A read followed by an
  unrestricted write, status cache or local epoch alone is insufficient.
  If the host cannot enforce the boundary, hold T22 and its
  descendants. Do not change AITM's production protection.

## Accepted leaf design

[Design](design/2026-11-10-158-qualify-github-merge-fence-design.md) · [Scoped independent SPR](plan/reviews/spr-2026-11-10-jit/review-manifest.md).

The design adopts the accepted #133 contract for this leaf.

## Accepted Plan and JIT

[Implementation plan](plan/2026-11-10-158-qualify-github-merge-fence.md) · [JIT pickup](plan/2026-11-10-158-jit.md) ·
[Scoped independent SPR](plan/reviews/spr-2026-11-10-jit/review-manifest.md).

Refinement verified **3.5 implementation agent-hours**, size M, P1,
with Rank 10 preserved. Timebox one isolated GitHub merge-route qualification and record either exact proof or a bounded refusal.
The JIT pins trunk `a495d60a87ac4ca764f019dc266e579f13f1787e` for intended attempt 1.
The GitHub Project is in Planning.

**Execution hold.** A named owner-authorized disposable GitHub target, dedicated trusted test actor and isolated ruleset mutation permissions must be recorded before hosted qualification. T22 / #159 requires a qualified receipt.

## Hosted qualification follow-up

The owner questioned the need for a hosted fixture and indicated that
creating a cloud repository or maintaining recurring cloud CI for
this spike is undesirable. No hosted target or actor has been granted.
The proposed fixture was for one-time GitHub behavior verification,
with independent review of the retained evidence on planning.

A local Git repository or worktree can test the controller's
reservation, dispatch, timeout and reconciliation logic against a
simulated provider. The accepted T21 receipt requires real GitHub
evidence for actor exclusivity, bypass rejection, the tested merge
tree, and the ordering of a stop with an already-sent merge.

The JIT remains accepted and the story remains in Planning. No hosted
probe was attempted, and no provider verdict was recorded. #159 still
requires a qualified T21 receipt. An explicitly reviewed scope change
would be needed to substitute a local-only deliverable.

## Reviewed disposable GitHub measurements

The owner authorized creating a private disposable fixture, measuring
the endpoints, and deleting the fixture afterward. Two synchronous
requests reached terminal outcomes. The stale head returned HTTP 409
and left the target unchanged. The stale base returned HTTP 200 and
landed the expected tree with a different first parent. The endpoint
alone supplies a head condition and cannot enforce the reserved base.

The private repository could not use rulesets on the available
account entitlement. The dedicated App and role-separated controls
were unavailable. The independently accepted record covers the
bounded endpoint measurements. The full qualification and stop
ordering remain held, and #159 still requires a qualified receipt.
No recurring workflow was used. Repository teardown is tracked
separately from the retained measurement bytes.

[Exact report](attachments/github-merge-fence-spike.md) ·
[Rules and request evidence](attachments/github-merge-fence-rules.json) ·
[Independent SPR](plan/reviews/spr-2026-11-10-endpoint-evidence.md).

[Teardown receipt](plan/disposable-fixture-teardown.json) records GitHub's
deletion confirmation and the authenticated HTTP 404 readback.

## One-time repository authorization

The owner approved one disposable GitHub repository for this spike,
including its deletion after the measurements. That authorization was
used and the teardown is verified. The owner declined continual use of
disposable repositories. Further hosted qualification that depends on
another disposable repository is on hold pending a revised plan.

The retained endpoint evidence records that the REST merge accepted a
moved base. It leaves the proposed ruleset, App, and in-flight stop
controls unqualified. #159 still requires qualified merge evidence.
