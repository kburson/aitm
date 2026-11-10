# #158 GitHub Merge Fence Spike Plan

**Goal** Produce a reviewable receipt for one qualified GitHub merge
method or an evidence-backed refusal.

**Approach** Run the controlled hosted matrix with one trusted
actor, one disposable target and one direct PR merge method. Use
fresh synthetic PRs per case, capture host and ordered local events,
and keep every credential out of the report.

**Tools** GitHub rulesets, PR UI, REST/GraphQL, Git, authorized
automation and a disposable request driver with explicit fault
barriers. The driver and fixtures are throwaway. No AITM implementation
or source change is needed.

**Design** [#158 merge fence design](../design/2026-11-10-158-qualify-github-merge-fence-design.md).
Read the [JIT note](2026-11-10-158-jit.md) before pickup.

## Global constraints

- Make probe mutations only on the approved disposable repository
  using scoped actors. Keep production AITM gate, protections and
  source outside the spike. Prepare and deliver the sanitized
  evidence separately on the AITM planning branch route.
- Budget 3.5 active implementation agent-hours. Stop and replan by
  four active hours. Owner, provider queue and reviewer waits are
  separate. The estimate assumes the sandbox and roles are available.
- Permit only one candidate method, synchronous PR merge with exact
  head SHA and the merge-commit method. Keep alternate routes
  unavailable under the tested configuration. Account for any
  alternate available to the trusted credential through the approved
  driver and its custody boundary.
- Prefer a decisive real-host counterexample to collecting additional
  unsafe writes. Preserve unrun rows with reasons. A passing sample
  is necessary evidence and needs the host ordering and mutation
  invariant described in the design.

## Task 1 · Pin the fixture and positive/negative gate controls (45 min)

- [ ] Before any mutation, match authenticated sandbox slug and
  immutable repository ID to owner authority. Confirm rule
  administrator, dedicated App installation and scope, separate
  reviewer and check publisher, ordinary writer, and automation
  credentials. Pin the API version and available platform features,
  effective rules and repo flags. Record the fixture's authorized
  teardown or retention and evidence owner.
- [ ] Configure the two target rulesets from the design. Record the
  full active rules with IDs, bypass modes, inherited rules, and
  ruleset enforcement mode. Scope the fixture check to its trusted
  source. Capture queue/auto-merge state and all enabled merge methods.
  Establish roles with successful control operations on disposable
  topic refs, valid API authentication and successful fixture review
  and checks. A negative from an unauthenticated or read-only token
  alone supplies no write-route evidence.
- [ ] Run the M01 and M02 controls below. Record approved and landed
  parents/tree by reading the Git objects with
  `git show -s --format='%P %T' <commit>` from the fixture clone.
  Independently read the exact target with
  `git ls-remote origin refs/heads/<target>` after verifying
  `origin` resolves to the authorized sandbox. Use
  `GET /repos/{owner}/{repo}/pulls/{number}` and
  `GET /repos/{owner}/{repo}/git/ref/heads/{target}` for provider
  readback, and retain the exact GitHub request ID when returned.
  A gate bypass or wrong tree ends the candidate route.

## Task 2 · Probe exclusive updates and exact proof binding (65 min)

- [ ] Run M03 through M09 against green fixtures unless the row is
  specifically testing a red or stale gate. Capture before/after
  target and PR identity and host response or event per route.
- [ ] For M08, move the head after final driver admission and before
  the request is forwarded. Assert a host refusal and no target
  write. For M09, advance the target via an independently admitted
  fixture merge by the exclusive actor. Forward the stale request
  under its original proof while the head remains unchanged.
  Separately challenge the endpoint's base contract with an ancestor
  advance. Prebuild `B → B′ → H` and seed `B′` on a fresh disposable
  fixture target after reservation, using authorized fixture setup
  and restoring the pinned protections before sending. Record the
  setup change and use this case to test the endpoint, separate from
  any claim about normal writers under the pinned rules. Keep the
  same head and make the moved-base PR review/check eligible so
  a guard against an out-of-date head cannot mask the base gap.
  Also attempt to retarget the reserved PR to another disposable
  protected target with the same head after admission. Show the
  retarget is blocked or the old request cannot land on either ref.
  If the candidate relies on exclusive serialization, separately
  show the approved driver cannot dispatch the second target mutation
  with an outstanding first dispatch and invalidates any reservation
  after that competing merge. Prove that no other actor or deferred
  route can still produce the intervening write. Identify precisely
  whether the evidence supports a host condition or this equivalent
  fenced update.
- [ ] Read back rule drift in the disposable fixture, such as a
  temporary bypass entry or disabled check rule with the owner
  configuration authority. Verify the driver holds admission on
  missing or mismatched effective protection. Preserve the evidence
  and restore the pinned fixture rules before further probes. This
  check supplements the actual host enforcement cases.

| Case | Action and required evidence |
| --- | --- |
| M01 | Authorized dedicated App merges a green reviewed PR using the pinned head and method. Record API/PR/target evidence and exact equality of ordered base/head parents and tested tree. |
| M02 | Same App with missing or withdrawn required review, missing or failed check, and a passing check from the wrong publisher. Each is refused with no target update. Stale approval/check data cannot admit a new tested tuple. |
| M03 | Attempt ordinary fast-forward push, force update and branch delete, plus direct target push by the dedicated App. Attempt equivalent direct ref API updates using write-capable identities, including an exact matching candidate tree. Target stays unchanged. |
| M04 | As a non-bypass write collaborator and as the applicable configured admin role acting without editing rules, try web merge and REST/GraphQL merge against green PRs. Verify no target movement and retain host denial or verified unavailable control. |
| M05 | Give ordinary automation an otherwise write-capable fixture token. Try PR merge and direct target write. Verify denial and separate identity from the trusted App. |
| M06 | Attempt auto-merge and queue through applicable web/API routes, including async enqueue and direct async with an ordinary writer. Verify feature disablement, no deferred pending entries and unchanged target. If queue is unavailable for this owner/plan, retain that effective configuration and an actual rejected/unavailable entry route. If any deferred route can be armed under the candidate configuration, arm a fixture before a stop and show host-enforced prevention of a later update, or refuse. Read a 202 to terminality. If the result is enqueued, follow the queue and target to a conclusive outcome because the enqueue result ends only the async API request. |
| M07 | Attempt another merge method with the trusted App. Confirm configured refusal. Check how the driver and credential custody exclude an unrestricted merge with the same trusted credential, including async direct mode, omission of the expected head and GraphQL/web paths where applicable. A token that can escape the trusted route invalidates the shape. |
| M08 | Change head H after admission and send the prior H through the real endpoint. Expect a stale-head refusal with unchanged target. Include same-tree new head to show identity is pinned. |
| M09 | Exercise divergent base advance, an advance already reachable from H, and PR retargeting as above. Require host refusal or provable exclusion of the interleaving by the equivalent fence. A merge against the wrong base or to the wrong target, even with the same tree, violates the receipt. |

## Task 3 · Exercise stop ordering and unknown outcomes (65 min)

- [ ] Record an ordered sequence with fixture intent ID, reservation
  and final admission, stop receipt and durable stop/fence state,
  dispatch boundary, provider request/event identity, any terminal
  result and PR/ref/Git-object readback. Use controlled causal
  barriers. Keep the actual host evidence distinct from driver
  assertions, network timing and timestamps.
- [ ] Run M10 and M11. Place a barrier after the driver's final
  authority check, immediately before its first outbound merge
  request bytes can reach GitHub. Observe the send boundary from
  the disposable relay or an equivalent independent transport
  observer. If the mechanism serializes the stop and send and
  excludes this pause, force contention at that boundary and
  record the actual ordering primitive and transport event.
- [ ] Use the relay to withhold the response for M11a and a
  separate observer for provider readback. For M11b, prove causal
  overlap with a provider operation that could still commit when
  stop is recorded, or demonstrate a documented, independently
  verified host invariant that covers that overlap. A local pause
  before forwarding belongs to M10. Delaying only the response
  cannot show that the operation was in flight at the stop.
  Preserve ambiguous outcomes durably across a driver restart and
  demonstrate blocked ordinary, repair and retry attempts while
  the intent is unresolved.

| Case | Action and required evidence |
| --- | --- |
| M10 | After reservation, pause after the last authority check and before the first external merge request bytes. Record stop, release the barrier and show zero outbound requests and unchanged target. If the verified serialization makes that interleaving unreachable, force contention and demonstrate both orderings. Stop first means no send. A possible send first keeps durable intent and goes to M11. |
| M11a | Forward an ordinary merge and suppress its acknowledgment. Establish through a provider result observed behind a causal barrier that the exact commit already landed before recording stop. Demonstrate the driver's hold under uncertainty, then admit the proven earlier commit into incident baseline evidence without retry. |
| M11b | Test the actual overlap or verify the host invariant above. Require provider-side exclusion or terminality, or causal proof of an exact earlier commit together with the verified invariant covering unresolved overlap. A response-only delay or a known earlier commit alone belongs to M11a. A provider commit proven after the stop, or a route that can do so, refuses the candidate. If ordering is unproved, retain unresolved intent and refuse qualification. A stale or unchanged ref, timeout, expiry or missing acknowledgment supplies no release evidence. |

At two active agent-hours require working role-separated M01/M02,
the control results available so far, and a concrete way to run M11
and obtain evidence of host order. A decisive provider limitation may
instead move directly to the refusal report. If access or remaining
proof does not fit the cap, stop the experiment and report the
precise hold or missing guarantee with partial evidence.

## Task 4 · Verify and publish the disposition (35 min)

- [ ] Assemble the evidence pair described by the design under
  `.aitm/stories/001/158/attachments/` when authorized. Each matrix
  case gets its actor, exact input tuple, request or event ID, rule
  snapshot, expected and observed result, before/after target, and
  `passed`, `failed`, `unknown` or `unrun` with reason. Record the
  event that makes each ordering conclusion causal and the
  `qualified` or `refused` capability disposition in the report.
  An unavailable probe cannot supply a pass.
- [ ] Independently replay the Git readback and compare recorded
  trees and ordered parents. Reconcile any ambiguous request before
  teardown or hand its still-fenced sandbox and evidence to the
  named owner. Preserve the raw safe provider evidence with
  digests or reproducible links and retain only sanitized material
  in AITM planning. Record cleanup or retention per owner authority.
- [ ] Commit the sanitized evidence on
  `codex/aitm-158-merge-fence-evidence` in an isolated AITM
  worktree pinned from authenticated `origin/planning`. Record
  its exact base, evidence commit and raw digest for each file.
  Validate real matrix evidence against the accepted spike and
  have an independent agent review that exact report and rules pair.
  A refused host route can pass this evidence review when the report
  proves the limitation and retains any unresolved fence.
- [ ] Publish to `planning` through the authorized planning route
  and verify the target commit and the exact published file digests
  by authenticated readback. Recheck evidence and review when
  the candidate or applicable target changes. Record the route,
  validation, reviewer, verdict and delivery mapping using the
  [manual delivery checklist](../../../../manual-delivery-checklist.md).
  There is no product change or applicable trunk-source CI run
  for this non-source deliverable.
- [ ] Record the published capability disposition and successor
  effect. If pickup authority is absent, record a hold and keep
  the execution checklist pending.
  Obtain the implementer's signed retrospective and reconcile issue
  and Project closure through the normal authorized process. #159
  stays held on refusal, unknown, owner hold or administrative
  completion without a qualified receipt. Retain the existing
  full PR gate.
