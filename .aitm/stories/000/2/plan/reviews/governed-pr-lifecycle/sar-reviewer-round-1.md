# #2 governed PR and working-branch lifecycle SAR

**Verdict — Changes requested.** SAR-PR-01 through SAR-PR-05 require disposition before these exact drafts are accepted.

## Review identity and scope

Physical worktree `/Users/kpburson/.codex/worktrees/aitm-158-evidence/trunk`. Its worktree HEAD pointer resolved to `refs/heads/codex/aitm-133-158-merge-only` at `54f9f08b44096e44a9465dfeae80b60d455f0227`. I read the complete design first and then the complete plan and independently verified both SHA-256 digests.

| Artifact under `.aitm/stories/000/2/` | SHA-256 |
| --- | --- |
| `design/2026-11-11-2-governed-pr-and-branch-lifecycle-design.md` | `5bf6605f0366d878b5f3c88e3019bcef6c8ba97da48ca555148be62712481027` |
| `plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md` | `57e0a0972aeeaa4e47d02f41df09267246c4a0b17543b879600a292e03dd870b` |

The review covers the owner scope represented by the drafts, the accepted Core provider, binding, admission, delivery and epic contracts, and the linked #133 and #158 boundaries. The draft split between Core orchestration, provider-specific effects and runtime isolation is coherent. The drafts preserve local-only planning and separate protected-default-branch enforcement from non-default integration. Hosted behavior and runtime isolation were reviewed as proposed qualification obligations.

## SAR-PR-01 · P1 · Parent retirement has a dependent-admission race

**Locations** Design lines 39–44 and 74–76. Plan lines 31–43, 63–66, 139–152 and 160–171.

The plan checks dependent branches or PRs before deleting the source ref. Consider a child provisioning or reparent operation that establishes the retiring branch as its parent after that check, or an already-dispatched child PR creation that becomes visible afterward. Adding a dependent does not change the parent's head. The parent's expected-OID deletion can therefore succeed and remove the target of an authorized child PR. Exclusive control of writes to the parent ref alone leaves the same race.

Require a durable retirement fence on the exact parent-resource identity in the same authority order used to admit child provisioning, reparenting and retargeting. Account for already-admitted or ambiguous dependent writes before deletion. Define which routes can introduce dependents at the host and hold retirement when they cannot be excluded or reconciled through the deletion interval. The hosted fixture should race a dependent admission on both sides of the fence with the parent head unchanged. A winning dependent keeps the ref until disposition. A winning retirement fence prevents the new or retargeted dependent from being authorized against that parent.

## SAR-PR-02 · P1 · Broker admission and replay need an exact resource incarnation and effect

**Locations** Design lines 20–25 and 39–51. Plan lines 55–82, 97–106 and 141–155. Baseline `design/core-design.md` lines 343–349, 409–411 and 590–596. Baseline `plan/core-implementation-plan.md` C16 and C43.

The draft uses C16's generation for a long-lived branch and PR and instructs the broker to authenticate against the current story generation and published intent. Provisioning begins in Backlog, before implementation pickup. Ordinary C16 recovery fences an old session and issues a new binding generation while retaining the work. Abandonment fences the active generation before its cleanup can resume. These are three distinct authority situations. The plan does not specify which identity remains stable across ordinary rebind, which principal can act without an active implementation binding, or what lets an exact retired-generation cleanup remain valid while denying stale cleanup against a replacement.

The numbered-issue protocol supplies a published dispatch claim for issue creation. Publishing the later provisioning action and reusing the issue reservation does not by itself establish single dispatch for each branch or draft creation. Two recovery processes could see the same pending action after a lost response and both decide to create, or could mistake an unrelated preexisting ref or draft with the same visible tuple for the result. The plan requires reconciliation but leaves its ownership and safe redispatch predicate unspecified for those stages.

Define the lifecycle resource incarnation and its relation to the attempt and session binding. Require an operation-specific broker admission derived from durable published state, with exact stage, principal or service role, applicable resource identity, policy and replay status. Cover the distinction between pre-pickup provisioning, current-session mutations and terminal cleanup authority. For uncertain effects, identify positive adoption proof and a fenced prior dispatch plus provider-specific proof of absence before resending, unless the same request is qualified as idempotent. Demonstrate that ordinary rebind keeps exactly one branch and draft, superseded sessions are denied, duplicate workers cannot dispatch twice, a foreign collision stays unresolved, and an old cleanup replay cannot touch a new incarnation. For scrap, identify a durable source-retention receipt that preserves the old generation's recoverable source through deletion of its hosted working ref.

## SAR-PR-03 · P1 · The tracked epic delivery has no defined Core authority

**Locations** Design lines 26–29 and 62–65. Plan lines 26–27, 31–41, 119–127 and 160–165. Baseline `design/core-design.md` lines 409–411, 432–436 and 450–455. Baseline `plan/core-implementation-plan.md` lines 949–963 and 1163–1177.

The plan gives a tracked epic integration branch its own binding, PR and independent validation. The accepted C62 epic has no implementation attempt, effective source review or PR. C41 requires current attempt or binding authority and effective passing source review for an admitted target mutation. A distinct binding alone supplies none of the missing lifecycle owner, evidence eligibility or dispatch authority. An implementation either stalls or invents a way to substitute aggregate child evidence for the epic delivery's own proof.

Name the owner of the branch-backed integration delivery and the existing or explicitly revised Core contract it uses. Show how that identity provisions its branch early enough to serve as a child's declared parent, receives its own review and CI evidence, obtains C41 admission, and retires independently of the aggregate epic. Include a positive trace from epic-parent provisioning through child-to-epic delivery and separately authorized epic-to-default delivery. Prove a pure aggregate still receives no inferred branch or PR and that child success alone cannot authorize the epic PR. The proposal can leave the command spelling and implementation choice to a leaf.

## SAR-PR-04 · P2 · Ready promotion lacks a defined race boundary

**Locations** Design lines 57–65 and 74–79. Plan lines 26–27, 84–95 and 166–176. #133 merge-only design lines 52–66. #158 qualification plan lines 66–74.

The plan says only the nominated repair can be promoted while held, but its ready flow reads the flag and then invokes a separate provider transition. An ordinary request may read OPEN and complete after the durable hold, or a non-default PR may be retargeted between the service's check and its ready transition. #158 supplies a mutation boundary for the target ref. The ready transition has no stated ordering, cancellation or recovery rule.

Specify whether the ready convention is ordered at trusted service admission or at the provider status transition. Bind the transition to the actual PR, head and target. If earlier admitted in-flight promotions may complete, define how the outcome is reported or reconciled and preserve the guaranteed merge denial. If the guarantee applies at the status transition, require a qualified ordering primitive or defer that route. Add fixture cases where a hold, head change and retarget win between policy read and transition, including an ambiguous response.

## SAR-PR-05 · P2 · Hosted qualification lacks a finite per-boundary acceptance contract

**Locations** Design lines 72–82. Plan lines 45–52, 97–127 and 158–181. #158 qualification plan lines 56–83.

The four delivery steps give broad proof categories but no explicit handoff between the adapter/isolation merge case in step 2 and the #158-qualified default-target mutation in step 3. Step 2 could be reported complete using a mock/default-looking command result or could depend on the qualification it precedes. The non-default positive path is also material to the scope. A capability-unavailable result is the correct safety behavior for an unqualified route but does not establish that non-default integration remains usable during a hold.

Add a compact proof matrix naming the fixture, prerequisite, tested entry point, expected terminal outcome and retained evidence for each boundary. Include at least a Core deterministic restart/concurrency fixture, real draft creation and actual-target CI evidence, real contained-runtime denial for direct provider Git/API operations including anonymous routes, broker denial across repository/ref/action and stale-generation boundaries, exact non-default fixture delivery while trunk is held, a #158-gated default-target case, and installed CLI/skill/MCP catalog and dispatch parity. Distinguish positive capability proof from a demonstrated unavailable result. Keep real hosted writes on separately approved temporary refs and retain provider request IDs and before/after readback where applicable. The matrix can be fixed here while leaf plans specify the exact commands.

## Disposition

Revise the two source drafts, preserve the finding IDs in the author response, and return both new digests for scoped re-review. This SAR concerns only the listed bytes and does not confer implementation, hosted-trial, gate-change or #159 pickup authority.
