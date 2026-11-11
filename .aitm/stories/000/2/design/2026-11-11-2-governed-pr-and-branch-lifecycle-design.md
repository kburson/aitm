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
  relationship and pending provisioning action. Dispatch branch and
  PR writes only after verified shared publication. Record repository,
  parent ref, initial base, working ref, PR identity and generation.
  Recover partial or ambiguous outcomes without duplicating resources.
- Use the declared feature or epic parent as the child PR base. A
  missing parent is an unavailable binding. A tracked epic integration
  branch can have a separate draft delivery to the default branch.
  A pure aggregate epic and local-only planning remain supported.
- Open a draft PR during provisioning of every managed working branch.
  Qualify an immediate draft on GitHub when head starts at the same
  commit as its parent. If the host needs ahead history, qualify a
  content-free bootstrap commit and keep its CI separate from work
  validation. A provider refusal leaves provisioning pending.
- The agent can query installed operations through help and a versioned
  machine-readable catalog. Each operation identifies permitted
  arguments, preconditions, side effects, result and next action.
  Expose the same operations through the skill and MCP.
- Abandonment fences the current generation and journals cleanup.
  Reconcile outstanding effects, close the linked PR, conditionally
  delete its exact source ref, and use the owning manager to remove
  its worktree after safe disposition of local changes. Resolve
  dependents using the ref before deletion. Retain the issue, PR
  and host outcomes. Preserve the prior generation on scrap and
  invalidate prior evidence when applicable on refactor.

## Authority and delivery

A trusted service authenticates each operation against current
story generation, published intent, effective policy, and anchored
repository and refs. Credentials stay outside agent workspaces.
Managed mode requires qualified tool and network isolation for direct
provider calls, including anonymous API routes. Unsupported isolation
leaves managed provider operations unavailable. Local Core and
supported observation remain available.

On a trunk-bound ready or merge request, the service reads the live
protected GitHub flag ref and resolves its record at the returned OID.
Local cached refs supply no authorization. While held, the nominated
repair may seek review. Only the exact independently reviewed repair
with full passing candidate proof is eligible to merge. Feature pushes
and non-default merges continue through their own policies. Require
exact parent delivery evidence on every managed merge. Default-branch
merge authorization also requires the #158 host-qualified flag, head,
base and tree boundary. Opening a draft does not authorize a merge.

The [#133 merge-only amendment](../../../001/133/design/2026-11-11-133-merge-only-stop-the-line-design.md)
owns CI, the repair-only hold and recovery. [#158](../../../001/158/plan/2026-11-11-158-merge-only-qualification.md)
owns qualification of the host enforcement. This review proposes no
product activation, protected-branch change or #159 pickup.

## Acceptance

Demonstrate exactly one linked draft through lost responses and repeated
calls, correct parent selection, supported draft CI, and cleanup with
concurrent or stale operations. Demonstrate that a managed agent cannot
call the provider directly or redirect the trusted service. Show fresh
flag readback, ordinary trunk denial during a hold, the exact repair
exception, and independent non-default integration. Verify that the
runtime's help and MCP catalog correspond to available governed actions.
See the [delivery plan](../plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md)
for the proof order and Core leaf handoffs.
