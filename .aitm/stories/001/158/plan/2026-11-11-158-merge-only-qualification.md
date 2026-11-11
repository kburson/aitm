# #158 Merge-only Stop the Line qualification plan

**Goal** Qualify one host-enforced AITM trunk merge route that uses
the same GitHub flag for ordinary admission, one exact repair and
recovery release.

**Spec** [#133 merge-only design](../../133/design/2026-11-11-133-merge-only-stop-the-line-design.md)
· [#133 delivery plan](../../133/plan/2026-11-11-133-merge-only-stop-the-line.md).
This proposal replaces pre-run fencing as the planned behavior for
routine scheduled runs. It authorizes no hosted trial, permission
grant, or production change. #158 remains in Planning.

## Candidate and retained evidence

Use only literal temporary refs and synthetic PRs in existing
`kburson/aitm`. Capture authenticated production protection readbacks
before, during and after any later trial. Keep `trunk` and `planning`
protections, repository settings, existing workflows and the full PR
gate outside the trial write scope. Name a custodian for unresolved
requests. Preserve the [original spike](../attachments/github-merge-fence-spike.md),
[branch trial](2026-11-10-158-existing-repo-branch-trial.md),
[PR and in-flight trial](2026-11-10-158-existing-repo-pr-trial.md),
and [exact-base and writer trial](2026-11-11-158-merge-boundary-trial.md).

The earlier trials showed that head-conditioned REST can merge on a
moved base, strict checks can accept a head-only status, and the
CLI and connector used the same identity. GitHub denied one accepted
pending async request once the stop rule became effective. That
result leaves the interval after its final update check unresolved.

Qualify GraphQL `updateRefs` as a candidate host transaction. Pin AITM
repository ID `1450406435` and GraphQL node `R_kgDOVnNyIw`. For the
approved merge commit `M`, require ordered parents `B,H` and tested
tree `T`. Use one mutation with literal refs, expected old OIDs, and
`force: false` to advance target `B → M` and the shared flag
`F → Fnext`. Test whether a compare-only `H → H` entry atomically
asserts the actual head. Both substantive ref updates must fail if
the base, head, or flag changed. Use explicit stale-OID tests in
which the requested update would otherwise pass fast-forward
validation. A documented API shape still requires a real hosted test.
[GitHub atomic ref updates](https://docs.github.com/en/graphql/reference/git#updaterefs).

The broker is the only prospective writer allowed to update the
protected fixture target and flag. Test the primitive with existing
authorized access first. A separately approved, distinct service
identity and normal writer are needed for exclusivity, with review
and trusted check publishers outside the broker. Keep raw credentials
and token minting out of candidate jobs and agent access. Preserve
independent PR, review and check rules without a writer exception
to those gates. The host transaction has no PR ID input. Prove the
specific reserved PR is the one whose evidence authorizes the update,
including a second eligible PR with the same Git objects. If the
provider cannot prove PR association, the no-op head assertion,
check source, or gate enforcement at mutation, refuse this route.

## Qualify the merge-only flow

T21 has no implementation predecessors. Drive the health, repair and
post-release cases with clearly labeled synthetic evidence from a
throwaway local harness. Use real GitHub PRs, protected fixture refs,
writes, source-bound check controls and result readbacks. The hosted
mutation proof must exercise the real gate and must not depend on
#159 or the later recovery implementation. T36–T40 own the integrated
scheduled workflow, actual full recovery and refreshed PR TIA traces.

| Case | Required proof |
| --- | --- |
| Routine run while open | A synthetic scheduled-run start leaves the flag open. Draft updates and background feature pushes remain permitted. |
| Verified failure | Stop new service dispatch on accepting the failure. Advance the one flag from the current `OPEN` version to `HELD`. Exercise already-ready PRs and available web, REST, GraphQL, Git, auto-merge, queue and automation routes. No ordinary update may land after the committed hold. |
| Unsent and already-sent intents | A superseded unsent intent emits zero writes. Race the in-flight mutation against the flag update. If the merge won, reconcile its exact commit as part of the baseline before recording the hold. If the hold won, the old flag OID must fence the entire transaction. Test both winners and a lost response. Require a host invariant at the ref write even if the rule evaluation was already complete. Report what the host can prove without inferring timing from response arrival. |
| Ambiguity | Preserve the pending operation and stop all new merge dispatch. A proposed exception permits one journaled flag-only hold transition while a target request is unresolved, once its atomic behavior is qualified and that exception is approved. Permit no target mutation in that write. Otherwise wait for terminal provider proof. Unchanged refs, timeout or a lost response leave the intent held. Freeze further writes and teardown until the custodian reconciles both requests. |
| Scope isolation | While held, push another feature branch, record fixture draft CI evidence and deliver a valid PR into a non-default fixture parent. Deny its trunk delivery and an already-ready trunk PR through the qualified gate. A retarget to the default target must lose any old allowance. |
| Exact repair | One nominated repair can leave draft for review. Require full-candidate fixture evidence and independent review before the real protected merge. Deny a self-claimed, stale or second passing PR. Consume the authorization and keep ordinary PRs held. Reopen only for matching fresh, complete recovery evidence on the verified current target. Include delayed failure with proof of an already-landed fix, a late success, repeated failure and missing evidence. |
| First merge after recovery | Old green PR evidence fails, including a same-tuple run admitted before release that finishes afterward. Refresh the head with current repaired target, push, and admit only fixture proof bound to a new post-release run and applicable review. An already-current head still requires fresh proof. Move the target again after CI and prove the prior tuple cannot land. |

Every applicable case needs a terminal readback or an independently
reviewed reason for refusal. A rule change, an agent-side flag check,
a draft indicator, or a cached status alone supplies no host ordering
proof. Dispose of only the trial resources after resolution and retain
the exact configuration, Git object IDs, flag history, request IDs,
review and measured results on `planning`. A qualified #158 receipt
remains a prerequisite for #159, which also still requires #157 and
its own authorized pickup.
