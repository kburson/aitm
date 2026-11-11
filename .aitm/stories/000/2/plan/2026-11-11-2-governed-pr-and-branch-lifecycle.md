# #2 Governed story branch and PR lifecycle proposal

**Spec** [Governed PR and working branch lifecycle design](../design/2026-11-11-2-governed-pr-and-branch-lifecycle-design.md).

**For review.** This is a cross-epic planning proposal. Core owns the
agent-facing workflow and provider contract. GitHub-specific behavior
belongs in `aitm-github`, with skill and MCP guidance in
`aitm-harness`. The existing [Core design](../design/core-design.md#providers)
and [accepted Core plan](core-implementation-plan.md) remain the
reviewed baseline. The [#133 merge-only plan](../../../001/133/plan/2026-11-11-133-merge-only-stop-the-line.md)
and [#158 qualification plan](../../../001/158/plan/2026-11-11-158-merge-only-qualification.md)
supply CI and protected-default-branch requirements. #159 stays blocked.

## Agent interface

Expose the workflow through discoverable `aitm` commands. Reuse the
existing Core story graduation, binding, action journal, service
composition and CLI registration. The proposed command families below
describe behavior. Final command spelling belongs to leaf refinement.

| Agent request | Governed operation |
| --- | --- |
| Create a branch-backed Backlog story | Create or reconcile the permanent issue identity, establish the exact parent ref, create the origin working branch from that parent, open its draft PR, and record the linked identities. The story remains in Backlog. |
| Pick up or resume work | Bind the story, branch, draft PR and authorized worktree. Reuse the existing worktree ownership and lifecycle rules. |
| Push or refresh a story branch | Resolve its bound remote and ref. Push only that story branch through the authorized route. Refresh against its actual parent and record the resulting head and CI identity. |
| Mark the PR ready | Resolve the actual PR, target, head and lifecycle state. For a default-target PR, read the live line flag and apply the promotion policy. While held, only the nominated repair can be promoted. Non-default targets follow their own policy. |
| Merge the PR | Apply the declared parent's review, CI and exact-delivery policy. Require a qualified host route for the literal target, reviewed head, applicable base and tested result. For a default-target PR, also enforce the live line version at mutation. While held, allow only the exact full-passing, reviewed repair binding. |
| Abandon a story | Record abandonment, close the linked PR, retire its exact working branch, and remove its owned worktree after safe disposition of local work. Record each verified outcome. |
| Discover or inspect | List available operations and explain their usage, arguments, applicable policy, side effects, status, and next permitted action. Support normal CLI help and a versioned machine-readable catalog through the same command registration. |

Every **managed working branch** has a draft PR on provisioning,
including a tracked epic integration branch. The contract applies to
branches used to deliver stories, features or epics. The default branch,
planning branch, authority refs and temporary fixtures have their own
roles. A child story uses its declared feature or epic parent branch as
the PR base. A missing or unbound parent blocks provisioning. It cannot
fall through to the default branch. An epic's eventual default-target PR
is a distinct delivery, with its own review and validation. Provision
that branch-backed integration as its own binding. A pure aggregate
epic keeps C62's child-based state and has no implied implementation
attempt or PR. Existing local-only planning remains available without
hosted resources. A managed hosted branch cannot be marked provisioned
until its draft is verified.

For GitHub, first test whether the host accepts an immediate draft when
the new branch starts at the same commit as its parent. If it requires
ahead history, qualify an explicitly authorized, content-free bootstrap
commit as the creation mechanism. Check draft creation, CI behavior,
and the absence of source changes. Keep the bootstrap result distinct
from validation of later work. Until the route is proven, a provider
refusal leaves a resumable provisioning record. Report the issue and
branch state and the missing draft explicitly.
[GitHub draft PR API](https://docs.github.com/en/rest/pulls/pulls#create-a-pull-request).

Issue creation, ref creation and PR creation are separate provider
effects. Reuse Core's published semantic reservation and dispatch
ownership before the first external call. Finalize the numbered
Backlog story, reciprocal relationships and pending provisioning
action in one Core transaction. Dispatch branch and PR effects
only after that transaction is verified on the shared planning ref.
A pending issue
finalization cannot create branch or PR resources. Freeze the
declared parent binding and its repository/ref identity in the
provisioning read-set. Verify the initial source OID and recheck
the binding at every step. An explicit reparent or replacement
must reconcile the old intent before authorizing a new one.
Record each successful step by stable issue, repository, literal
head/base ref and provider PR ID. Resume the same operation after
a partial failure. Reconcile a lost
response before another create, merge or delete. A retry must not issue
a second story, open a second draft, change the parent, or erase another
agent's work. Provisioning completeness gates pickup of the hosted
working branch without advancing the story out of Backlog.

Use C16's generation binding. On scrap, fence the old generation,
retain its exact ref OID, source and evidence through the approved
retirement disposition, and retire its PR and branch before
publishing the replacement as ready for pickup. Bind a new branch and draft for the replacement. A refactor
that retains a branch also retains its PR, with prior review and CI
evidence invalidated as appropriate. Core binds an existing worktree.
Provision or retire an actual worktree through its owning lifecycle
adapter, preserving C16's no-create/remove/reset boundary in Core.

## Live flag and enforcement

The GitHub adapter reads the protected flag ref from the anchored
provider at the ready or merge boundary, then reads the record pinned to
that returned commit OID. Agent worktrees need no ref checkout or fetch
for this decision. A remote-ref lookup can return its OID and an
explicit one-ref Git fetch can retrieve the object when needed. Cached
`origin/*` data cannot authorize a trunk action. Missing or unverified
flag data defers trunk actions only. Feature pushes and non-default
integration continue. [Git remote ref listing](https://git-scm.com/docs/git-ls-remote)
· [Targeted Git fetch](https://git-scm.com/docs/git-fetch)
· [GitHub ref readback](https://docs.github.com/en/rest/git/refs#get-a-reference).

Core owns the policy entry point and typed results. The provider
extension performs scoped host calls through a trusted process outside
the managed agent's tool and credential boundary. The service
authenticates the caller and binds the operation to the current
story generation, published intent, policy and anchored repository
and refs. It derives provider destinations from that binding.
Caller arguments, a story-controlled config, or a stale session
cannot select another repository, base, action, or credential.
The agent receives the decision and receipt without a provider
token or a generic HTTP/GitHub proxy. The runtime removes direct
provider tools and credentials from the agent and restricts direct
provider API/network routes to enforce the user's requirement, including
anonymous calls to public APIs. Feature pushes remain available through
the authorized route. GitHub branch protection and the #158 qualified
merge path enforce default-branch writes at the host. A CLI wrapper,
skill, or MCP instruction alone cannot supply these controls.
Qualify the provider and harness/runtime together before offering
managed mode. Where direct calls cannot be restricted, report
managed-provider operations as unsupported and retain local
planning and supported observation. Never advertise a CLI-only
installation as a provider enforcement boundary.

Apply Core C39–C41's admitted target mutation and verified delivery
contract to all managed merge commands. A feature or epic target uses
its own approved base, CI, review and provider delivery policy without
consulting the trunk flag. A head-conditioned call that can land
against an unintended base supplies no exact-target guarantee.
If a provider cannot enforce the required tuple at mutation, defer
that managed route as unsupported. Preserve the existing ability to
observe and verify independently authorized external delivery under
its own policy. A mismatched result never satisfies Core delivery.

The GitHostProvider surface exposes typed operations and provider
capabilities, including remote PR creation, transition, merge, retirement
and exact live readback. Core handles story identity and orchestration.
GitHub is the first implementation. GitLab and Bitbucket use the same
capability contract, with provider-specific proof of draft creation,
protection, flag readback and merge enforcement. An unavailable capability
returns a documented hold or unsupported result. Skills and MCP expose
the same supported operations and point the agent to their help.
They do not gain a separate provider authorization path.

## Retirement

Journal abandonment and its pending cleanup in the Core terminal
disposition transaction. Fence the exact story generation against new
pickup, pushes, refresh, provisioning, merge and stale cleanup requests.
Reconcile already-dispatched writes and quiesce the owned worktree
before removal. Close its exact PR and retire the exact source branch
using an expected-OID delete or a proven exclusive writer over the
deletion interval. A changed tip or an unsupported deletion predicate
holds cleanup. Revalidate the current generation, ownership and
dependent branches or open PRs that target this source before deletion.
Use the owning worktree manager to remove the bound worktree after
preserving unpushed or dirty work, unless the owner explicitly
disposes of it. Preserve the closed PR and issue receipts. A partial
cleanup retains pending actions. If a previously authorized merge
already landed, preserve the verified host outcome in history and
reconcile the disposition. Cleanup cannot create delivered status
or recreate retired resources.

## Bounded delivery

1. **Core contract and command discovery.** Refine the additions
   against C13 provider contracts, C16 bindings, C20/C22 identity
   and graduation, C39–C41 delivery, C43 action recovery, C62 epic
   aggregation, and the installed CLI ledger. Test one branch-backed
   story identity, exact parent, replacement generations, each failure
   point, duplicate callers, and recovery from lost acknowledgments.
2. **GitHub adapter and runtime isolation.** Qualify draft provisioning
   and retirement with temporary AITM refs only. Prove the managed
   agent cannot call the provider directly, while the constrained
   AITM operations can create, push, promote, merge and retire only
   their authorized targets. Verify scope, capability reporting,
   actual CI behavior and denied credential or route reuse.
3. **Delivery integration.** #133 owns selected CI, full fallback,
   recovery and post-release refresh. #158 owns default-target
   exactness, writer exclusivity and in-flight ordering. Wire the
   commands to those qualified capabilities without extending the
   hold to feature and epic parents. Keep #159 blocked on #157/#158.
4. **Guidance and acceptance.** Verify each exposed operation has
   current CLI help and a machine-readable entry. Prove skill/MCP
   routing invokes the same commands and respects the runtime
   restriction. Treat new or changed Core leaves, credentials,
   hosted probes, and cutover as separate reviewed work.
