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
| Mark the PR ready | Resolve the actual PR, target, head and lifecycle state. Require a qualified exact promotion transition. For a default-target PR, enforce the live flag and promotion policy at that transition. While held, only the nominated repair can be promoted. Non-default targets follow their own policy. |
| Merge the PR | Apply the declared parent's review, CI and exact-delivery policy. Require a qualified host route for the literal target, reviewed head, applicable base and tested result. For a default-target PR, also enforce the live line version at mutation. While held, allow only the exact full-passing, reviewed repair binding. |
| Abandon a story | Record abandonment, close the linked PR, retire its exact working branch, and remove its owned worktree after safe disposition of local work. Record each verified outcome. |
| Discover or inspect | List available operations and explain their usage, arguments, applicable policy, side effects, status, and next permitted action. Support normal CLI help and a versioned machine-readable catalog through the same command registration. |

Every **managed working branch** has a draft PR on provisioning,
including a tracked epic integration branch. The contract applies to
branches used to deliver stories, features or epics. The default branch,
planning branch, authority refs and temporary fixtures have their own
roles. A child story uses its declared feature or epic parent branch as
the PR base. A missing or unbound parent blocks provisioning. The
explicit parent record selects the branch owner and incarnation. A
branch-backed epic designates an ordinary, explicitly related
integration delivery story to own its working branch and default-target
draft. The aggregate epic retains C62's child-based state and acquires
no implementation attempt or PR. Provision the delivery story's
branch and draft in Backlog before children need the parent. Hold
the integration story's delivery on its declared child prerequisites,
independently of that early provisioning. Children deliver to the
integration branch under C39–C41. The integration story then binds
its own attempt to the resulting head and obtains its own review,
CI and C41 admission for the default target. Child evidence alone
cannot authorize that PR. The integration story owns its retirement.

Add a bounded Core contract amendment for a declared integration
delivery whose only changes came from the children. Accepted C76
otherwise requires nonempty story-tagged implementation commits, which
a child-only integration attempt cannot supply. Add a typed composed
source receipt as an alternative Develop-exit proof for the explicitly
designated integration delivery story only. Bind the receipt to its
current attempt and declared parent binding, pinned default-target
baseline, exact integration head and tree, and verified C39–C41
child-to-integration delivery receipts. Verify a nonempty source delta
and prove its complete source mapping from the admitted child
deliveries to the exact candidate, including the recorded history
after any base refresh. A missing, stale, unexplained or empty delta
fails this alternative. Re-evaluate it after source or baseline
changes. Keep ordinary C76 tagged-source guards for every other
story and defect. This typed receipt supplies source eligibility only.
Require the integration attempt's own current Test, independent
source review, and C41 admission for the exact default-target
delivery. Do not create an empty tagged commit to pass the guard.
A pure aggregate epic has no inferred delivery story, branch or PR. Existing local-only planning remains available without
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
effects. Reuse Core's numbered issue reservation and dispatch
ownership for issue creation. Finalize the numbered Backlog story,
reciprocal relationships and pending provisioning action in one Core
transaction. Verify shared publication before any branch or draft
dispatch. Freeze the declared parent incarnation, literal repository
and ref, and initial source OID in the provisioning read-set.
Verify the initial source and recheck the binding at each stage.
Reconcile old intent before admitting explicit reparent or replacement.

Identify a managed resource incarnation by permanent story identity,
anchored repository, and a durable allocated incarnation ID. Record
the exact parent binding, working ref and provider PR ID under that
incarnation. Ordinary C16 recovery rotates the session binding while
preserving this record, ref and PR. Current-session mutations require
the live C16 generation and attempt where applicable. Before pickup a
trusted provisioning role may act only on a published provisioning
claim. Terminal cleanup uses its own service role and exact
retired-incarnation claim after the working session is fenced. Old
claims confer no authority over replacement resources.

For every provider effect, acquire one durable dispatch claim for
its stage, role or principal, resource incarnation, exact target,
effective policy and replay state before dispatch. Duplicate callers
reconcile the same claim. A lost response requires positive
provider-specific attribution before adopting a result. A matching
name or head/base tuple alone cannot adopt a foreign resource. Resend
only after fencing the old dispatch and proving provider-side absence
of its effect and any outstanding request, or by reusing a qualified
provider idempotency key for the same effect. Unresolved ownership or
execution remains pending. Verify a single linked draft before pickup.
Provisioning leaves the issue in Backlog.

Scrap allocates a replacement incarnation after terminal disposition
of the original. Before hosted deletion, publish and verify a durable
receipt binding the old incarnation and exact source OID to an
authorized retained source that can recover that OID independently
of the working ref. Complete prior PR and ref retirement before
making the replacement ready for pickup. A refactor that keeps its
incarnation also keeps its PR and invalidates superseded evidence.
Core binds an existing worktree. Its owning lifecycle adapter
performs worktree creation and retirement.

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
resource incarnation, applicable binding generation, published
operation claim, policy and anchored repository and refs. It derives provider destinations from that binding.
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

Ready promotion is ordered at the verified provider status
transition. Require a provider-qualified ordering for the exact PR,
head and target, including the current flag and nomination for a
default-target transition. A hold, head change or retarget that wins
before transition invalidates the old request. A transition already
committed before a hold may leave an ordinary PR ready, with its
merge still blocked. Reconcile timeouts with terminal provider
evidence before retrying. Hold unresolved promotions and report the
actual draft state when it becomes verifiable. If the host cannot
prove this ordering, the managed promotion route stays unavailable.
Retargeting uses separate governed admission and cannot carry a prior
promotion or merge allowance to the new target.

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

Journal abandonment and pending cleanup in the Core terminal
disposition transaction. Place a durable retirement fence on the
exact parent-resource incarnation in the same authority order that
admits child provisioning, reparenting and retargeting. An admitted
dependent that wins keeps the parent ref until resolved. If retirement
wins, reject subsequent dependent admissions. Reconcile already
dispatched or ambiguous dependent writes, and require control or
proof excluding new dependents through every applicable host route
until deletion completes. An uncontrolled route holds cleanup even
when the parent head stays unchanged.

Fence the current working session and reconcile already-dispatched
effects before retirement. Use the exact terminal cleanup claim to
close its linked PR and conditionally delete its source ref. Require
expected-OID deletion or a proven exclusive writer for the deletion
interval. A changed tip or unqualified deletion predicate holds
cleanup. Quiesce the owned worktree and use its owning manager to
remove it after preserving unpushed and dirty work or recording the
owner's disposition. Preserve the issue, closed PR, retained-source
receipts and verified host outcomes, including a previously authorized
merge that already landed. Partial cleanup stays pending. Cleanup
cannot create delivered status or recreate retired resources.

## Bounded delivery

1. **Core contract and command discovery.** Refine the additions
   against C13 provider contracts, C16 bindings, C20/C22 identity
   and graduation, C39–C41 delivery, C43 action recovery, C62 epic
   aggregation, C76 source eligibility, and the installed CLI ledger.
   Refine the designated integration source guard as a bounded Core
   leaf before hosted integration delivery. Test one branch-backed
   story identity, exact parent, replacement generations, each failure
   point, duplicate callers, and recovery from lost acknowledgments.
2. **GitHub adapter and runtime isolation.** Qualify draft provisioning
   and retirement with temporary AITM refs only. Prove the managed
   agent cannot call the provider directly, while constrained AITM
   operations access only their authorized targets. Qualify
   non-default delivery independently. An unsupported route confirms
   denial only. Default-target merge qualification belongs to step 3.
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


## Proof matrix

Use deterministic local fixtures for Core ordering and replay. Hosted
proof uses separately approved temporary AITM refs. Record exact
request, repository, ref and object identities, before and after
provider readback, and provider request IDs where available. For each
hosted route record either the required positive outcome or a reviewed
unavailable disposition. The latter leaves the corresponding
capability disabled and supplies denial evidence only.

| Fixture and prerequisite | Entry point and required result | Retained evidence |
| --- | --- | --- |
| Deterministic Core store, restart and concurrent callers | Provision and recover at each effect boundary. One branch and draft survive rebind. Deny stale mutation and replay against replacement. Hold foreign collisions and unresolved dispatch. | Published claims, dispatch counts, result ownership, restart and rebind trace. |
| Deterministic parent retirement fixture, then managed temporary AITM parent | Race child provisioning, reparent and retarget against retirement with unchanged parent OID. Exercise both winners, an ambiguous admitted write and an uncontrolled host route. Verify retained scrap source is recoverable before deletion and old cleanup cannot touch replacement. | Ordered admissions, dependent and ref readback, source-retention and cleanup receipts. |
| Temporary AITM parent and working refs, qualified adapter credential | Provision an actual draft, including any required bootstrap. Push a later change and show CI for the actual target. | Draft ID, exact head and base, source diff, bootstrap disposition and actual CI run. |
| Installed CLI and contained runtime with trusted broker | Deny direct Git and API calls, including anonymous routes. Prove broker rejects unauthorized repository, ref, action and stale generation. An authorized feature push succeeds. | Runtime route and credential inventory, observed denies, broker receipts and host readback. |
| Temporary non-default and default stand-in targets, live fixture hold | Promote the permitted PR through the managed command. Race a hold, head change and retarget with provider transition and include an ambiguous result. Deny stale transitions when the competing change wins. | Ordering receipts, actual PR state, terminal request reconciliation and independent merge-denial observation. |
| Temporary non-default parent, qualified C39–C41 route, trunk hold | Merge an independently reviewed child into the declared feature or epic parent, then deny a stale base. Verify a pure aggregate has no PR and child evidence cannot admit the integration story's default-target delivery. | Target CI, exact reviewed and delivered tuple, actual parent readback and authorization denials. |
| Deterministic Core integration guard with verified child deliveries | Exercise the real Develop-exit guard for a declared child-only integration attempt. Accept an exact, nonempty, fully mapped composed change. Reject missing, stale, unrelated, empty or unexplained source. Verify ordinary stories retain their existing guard. Require the integration attempt's own Test and Review before C41. | Source mapping and receipts, guard result, current exact candidate and negative traces. |
| Temporary default stand-in, accepted #158 capability and independently reviewed fixture | Exercise ordinary merge denial, exact repair, held recovery, reopen and first refreshed delivery. A branch-backed epic fixture then completes its separately reviewed integration delivery. | #158 qualification receipt, flag and trunk-equivalent history, repair and post-release CI, per-delivery review and host receipts. |
| Installed distribution with CLI, skill and MCP | Enumerate operation and argument schemas, invoke each available operation through supported interfaces, and compare admission and typed results. | Catalog/version, actual help and dispatch traces, capability and unsupported outputs. |
