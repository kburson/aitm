# #2 Governed PR and working branch lifecycle design

## Outcome

In managed hosted mode, agents use discoverable AITM commands for
provider operations. Each branch-backed story gets a linked Backlog
issue, origin working branch and draft PR. The commands enforce
story ownership, delivery policy and resource lifecycle. The skill
and MCP direct agents to the same governed operations.

This proposal extends the accepted [Core provider contract](core-design.md#providers).
Core owns policy, binding, durable intent, result types and CLI
discovery. The git-host extension owns provider effects. The managed
runtime and trusted service own identity, credential and network
isolation. GitHub is the first provider. GitLab and Bitbucket require
independent capability qualification.

## Managed workflow

- Provision the story issue through the existing permanent identity
  protocol. Atomically finalize the numbered Backlog story, parent
  relationship and pending provisioning action with one exclusive
  lifecycle slot per permanent story, repository and managed role.
  Dispatch branch and PR writes only after verified shared publication. Record repository,
  parent ref, initial base, working ref, PR identity and resource
  incarnation. Journal a separate broker dispatch claim for each
  external effect. Recover ambiguous outcomes with positive ownership
  evidence, and require proven safe replay before resending.
- Every managed working branch declares a literal delivery target
  independently of Backlog parentage. A child of a branch-backed
  feature or epic resolves the declared parent resource to its exact
  ref. A story under a pure aggregate or with no Backlog parent
  explicitly declares the default branch or another authorized literal
  target at graduation. A missing or unbound delivery target leaves
  provisioning pending. A branch-backed epic
  explicitly designates an ordinary integration delivery story to own
  the shared branch and its upstream draft. Declare the Backlog
  relationship, integration resource owner and literal delivery target
  separately. The epic's required scope includes the integration
  delivery, which uses its own Core review and delivery authority.
  Where the shared branch is also a governed merge target, its target
  policy controls writes, including those requested by its owner. A narrowly scoped Core source guard allows
  this delivery to prove an exact, nonempty composed source change
  against its literal upstream baseline from verified child deliveries
  when it has no source commits of its own. A pure aggregate epic
  and local-only planning remain supported.
- Open a draft PR during provisioning of every managed working branch.
  Qualify an immediate draft on GitHub when head starts at the same
  commit as its parent. If the host needs ahead history, qualify a
  content-free bootstrap commit. Record the OID, parent OID, equal
  tree, trusted service role and incarnation as a provisioning
  artifact. Pin ordinary attempt source baselines at or after the
  verified bootstrap and account for that artifact explicitly in
  composed source and delivery mappings. Its CI provides only
  provisioning evidence. A provider refusal leaves provisioning
  pending.
- The agent can query installed operations through help and a versioned
  machine-readable catalog. Each operation identifies permitted
  arguments, preconditions, side effects, result and next action.
  Expose the same operations through the skill and MCP. Governed
  read-only observation returns the authorized PR state, review
  threads, check results and allowed logs or artifacts. Bind those
  reads to the same scoped identity and capability catalog.
- Abandonment fences the current resource incarnation and journals
  terminal cleanup authority. Order the retirement fence with
  dependent admission, including parent selection and PR retargeting.
  Account for all routes that could introduce a dependent before
  deleting the exact source ref. Close its linked PR and use the
  owning manager to remove its worktree after safe disposition of
  local changes. Scrap requires a verified durable source-retention
  receipt. Refactor invalidates prior evidence when applicable.
- After verified delivery and required completion evidence, publish a
  terminal retirement action for the exact delivered incarnation.
  Preserve the merged PR and delivery receipts. Retain the ref and
  worktree until applicable dependents, outstanding actions and local
  source are safely resolved. Use the same retirement fence for an
  ordinary or integration delivery. Qualify GitHub automatic deletion
  and host-triggered PR base changes or closures. Retain the ref when
  host deletion cannot be controlled. If that can occur on merge,
  hold that managed merge before dispatch. Reconcile external base
  changes as retargets, invalidate earlier admission and CI, and
  require verified draft and fresh target evidence before re-entry.
  [GitHub branch deletion](https://docs.github.com/en/pull-requests/how-tos/commit-changes/managing-branches-within-your-repository)
  · [Automatic deletion settings](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-the-automatic-deletion-of-branches).

## Authority and delivery

A trusted service admits each effect against durable published state,
a runtime-attested principal or service role, the exact operation and
resource incarnation, effective policy, and anchored repository and
refs. Runtime identity stays outside the workspace and cannot be
selected or transferred by the agent. An incarnation survives ordinary session rebind. Current-session
mutations also require the current attempt and C16 binding generation.
Provisioning and terminal cleanup use narrowly scoped service claims.
Bind literal host resources exclusively to one incarnation. Terminally
reconcile outstanding host writes before reuse, unless qualified host
isolation prevents them reaching the replacement. Credentials stay
outside agent workspaces.
Managed mode requires qualified tool and network isolation for direct
provider calls, including anonymous API routes. Governed observation
provides scoped data while preserving this boundary. Unsupported
isolation leaves managed provider operations unavailable. Local Core and
supported observation remain available.

On a trunk-bound ready or merge request, the service reads the live
protected GitHub flag ref and resolves its record at the returned OID.
Local cached refs supply no authorization. The broker orders ready
dispatch with accepted hold and retarget admission for the exact PR,
head and target. Already-sent readiness may finish during a hold. It
carries no merge authority, and its result must be reconciled before
further ready or retarget operations. Retarget requires a verified
draft and fresh admission for the new target. While held, the
nominated repair may seek review. Only the exact independently reviewed repair
with full passing candidate proof is eligible to merge. Feature pushes
and non-default merges continue through their own policies. Apply
the declared target's exact C39–C41 delivery policy on every managed
merge. Default-branch
merge authorization also requires the #158 host-qualified flag, head,
base and tree boundary. Opening a draft does not authorize a merge.

The [#133 merge-only amendment](../../../001/133/design/2026-11-11-133-merge-only-stop-the-line-design.md)
owns CI, the repair-only hold and recovery. [#158](../../../001/158/plan/2026-11-11-158-merge-only-qualification.md)
owns qualification of the host enforcement. This review proposes no
product activation, protected-branch change or #159 pickup.

## Acceptance

Demonstrate exactly one linked draft through lost responses and repeated
calls, correct explicit targets including trunk from a pure aggregate,
supported draft CI, and cleanup after delivery or abandonment with
concurrent or stale operations. Show the composed-source guard and
durable scrap source recovery. Demonstrate scoped CI and review
observation and deny direct calls or cross-story access to another
live incarnation. Show fresh
flag readback, ordinary trunk denial during a hold, the exact repair
exception, and independent non-default integration. Verify that the
runtime's help and MCP catalog correspond to available governed actions.
See the [delivery plan](../plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md)
for the proof order and Core leaf handoffs.
