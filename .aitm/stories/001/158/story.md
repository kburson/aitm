---
schema: "aitm.story/v0"
id: 158
title: "[#133 T21] Qualify the GitHub merge fence"
kind: "spike"
state: "done"
issue: "https://github.com/kburson/aitm/issues/158"
parent: 133
children: []
blocking: [159]
blocked-by: []
created: "2026-11-10T16:51:45Z"
updated: "2026-11-12T03:09:23Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": ["design/2026-11-10-158-qualify-github-merge-fence-design.md"], "plan": ["plan/2026-11-10-158-qualify-github-merge-fence.md", "plan/2026-11-10-158-jit.md", "plan/reviews/spr-2026-11-10-jit/review-manifest.md", "plan/2026-11-11-158-merge-only-qualification.md", "plan/2026-11-11-158-merge-only-jit.md", "plan/2026-11-11-158-atomic-ref-trial.md", "plan/reviews/spr-2026-11-11-merge-only-jit/review-manifest.md", "plan/reviews/2026-11-11-158-atomic-ref-trial-review.md", "plan/2026-11-11-158-merge-only-disposition.md", "plan/reviews/2026-11-11-158-merge-only-disposition-review.md"], "attachments": ["attachments/github-merge-fence-spike.md", "attachments/github-merge-fence-rules.json", "attachments/2026-11-11-158-atomic-ref-trial.json", "attachments/2026-11-11-158-merge-only-disposition.json"]}
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

## Completion sign-off

Completed as a research spike with an evidence-backed refusal. The native merge route accepted a moved base. The atomic ref update enforced the measured base, head and stop flag conditions. Specific PR authorization and independent role enforcement remain open production qualification requirements under [#133's design evidence](../133/attachments/2026-11-11-merge-fence-design-evidence.md).

[Reviewed disposition](plan/2026-11-11-158-merge-only-disposition.md) · [Independent review](plan/reviews/2026-11-11-158-merge-only-disposition-review.md) · [Teardown readback](attachments/2026-11-11-158-merge-only-disposition.json).

GitHub closed the issue as Completed at `2026-11-12T03:08:32Z`. AITM-PY Backlog read back Done. Codex signed the closeout as closure coordinator. Active implementation time is Unknown. The entries below retain the trial's historical scope and status.

## Reviewed merge-only qualification scope

[Revised #158 plan](plan/2026-11-11-158-merge-only-qualification.md)
· [#133 design amendment](../133/design/2026-11-11-133-merge-only-stop-the-line-design.md).

Qualify a single GitHub flag and host-enforced trunk merge route in the
existing AITM repository. Cover an exact repair, fresh full validation
on repaired trunk, and new PR CI after refresh. Background feature pushes
and non-default merges continue. The earlier disposable-repository plan,
workspace pause, and routine pre-run hold are superseded for this work.
Prior measurements remain evidence. #158 stays in Planning and #159
stays blocked pending a qualified receipt and its other prerequisites.

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

## Existing-repository branch trial

The owner approved the [existing-repository trial
scope](plan/2026-11-10-158-existing-repo-qualification-proposal.md).
GitHub allowed a direct fast-forward push while the test branch was
open and rejected the same actor's fresh fast-forward after the
exact-branch stop rule took effect. The trial removed the temporary rule
and branch and verified the `trunk` and `planning` protections.

[Trial report](plan/2026-11-10-158-existing-repo-branch-trial.md) ·
[Machine-readable evidence](attachments/2026-11-10-158-existing-repo-branch-trial.json).

The trial record documents a preflight deviation. Claude's behavior
on push and ruleset events was unverified when the temporary branch
and rule were created. The hosted PR merge and already-sent request
cases remain open. #158 stays in Planning and #159 stays in Backlog
pending a qualified merge receipt.

## Existing-repository PR merge trial

[Trial report](plan/2026-11-10-158-existing-repo-pr-trial.md) ·
[Synchronous receipt](attachments/2026-11-10-158-existing-repo-pr-trial.json) ·
[Asynchronous receipt](attachments/2026-11-10-158-existing-repo-async-merge-trial.json).

The active exact-branch rule denied a fresh synchronous REST merge
and blocked the web merge button. One synchronous merge sent before
the simulated stop also returned a terminal denial. In the async
trial, GitHub accepted a merge before the stop, reported it pending
after activation, and returned a terminal rule denial for the same
UUID. Both stopped targets stayed fixed. The trial removed the
temporary rules and refs and verified the production protections.
The exact-base and exclusive-writer guarantees remain open. #158 stays
in Planning and #159 remains blocked.

## Exact-base and merge-writer boundary trial

[Trial report](plan/2026-11-11-158-merge-boundary-trial.md) ·
[Measurement receipt](attachments/2026-11-11-158-merge-boundary-trial.json).

GitHub's head-conditioned async merge accepted a moved base with
an identical head and tree. Strict status checks rejected the stale
test-merge status and accepted a head-only status. The exact-target
PR-only exception allowed the named user's explicit PR merge and
denied direct ref writes. The connector and CLI resolved to the same
GitHub user. Distinct-writer enforcement and the interval after the
final host update check remain unqualified. Both temporary rules
and all test refs were removed. Production protections matched
their pre-trial readbacks. #158 stays in Planning and #159 remains
blocked.

## Atomic ref transaction trial

[Revised JIT](plan/2026-11-11-158-merge-only-jit.md) ·
[Independent JIT SPR](plan/reviews/spr-2026-11-11-merge-only-jit/review-manifest.md) ·
[Trial report](plan/2026-11-11-158-atomic-ref-trial.md) ·
[Measurement receipt](attachments/2026-11-11-158-atomic-ref-trial.json) ·
[Independent trial review](plan/reviews/2026-11-11-158-atomic-ref-trial-review.md).

The owner-authorized run used only four temporary AITM refs and one
exact-target fixture rule. It observed the expected atomic results
and a protected fixture update followed by PR recognition. Exact PR
authorization and independent writer, reviewer and check roles remain
unqualified. External-app event scope remained unverified at dispatch,
a deviation from JIT preflight. Terminal readback found no app or
workflow activity on the fixture. Temporary refs and the fixture rule
were removed, production protections matched, and the original
measurements were retained. #158 remains in Planning and #159 remains
blocked by #157 and #158.

## Final trial disposition

The temporary-ref trial is complete with a bounded refusal. The atomic ref primitive passed its measured controls. The production merge route remains unqualified because PR-specific authorization and independent actor enforcement are unresolved. [Disposition](plan/2026-11-11-158-merge-only-disposition.md) · [Independent review](plan/reviews/2026-11-11-158-merge-only-disposition-review.md) · [Live readback](attachments/2026-11-11-158-merge-only-disposition.json).
