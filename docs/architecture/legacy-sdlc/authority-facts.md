# Legacy workflow operation and authority facts

C109 [#496][story] inventories legacy operation eligibility, directives and
host authority. The source is commit
`c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905` and Git tree
`844ae26bb169e8618e45fc3b1aedb57f44896fe0`. The [guard inventory][guards] and
[resident-action inventory][actions] hold the state-array and evidence facts.
[The C110 decision fixture][decisions] owns final disposition.

## Operation classes

- **Forward.** The executable graph admits the next built-in state. The move
  host validates the operation and selects source exit and destination entry
  guards. Body, source and provider observations can be refreshed before
  commitment. The Cursor resumes registered actions after the move. C28/C29 own
  typed edge, read-set and outcome. C43/C88 own admitted host effects and
  verification. Plan resource preparation and implementation pickup use separate
  capabilities.
- **Reverse and parking.** The canonical graph allows Refine or Ready for Plan
  to Backlog, Plan to Ready for Plan, Test to Develop, and Review to Develop or
  Test. The shelve operation requires a reason and has its own policy and guard
  phase selection. C28/C29 own explicit design and implementation rework. C31
  owns trip/pivot. C78 owns alternate profile edges. Preserve the reason and
  attempt lineage.
- **Supersede and exceptional execution.** Legacy supersession links the
  replacement, records an exceptional terminal move and closes the retired issue
  as Not Planned. Runtime policy exceptions have their own types, scope and
  proof. C07/C28/C29 can record an explicit non-delivery disposition and
  replacement, or a scoped policy decision. C88 owns exact hosted admission.
  Delivery evidence remains a separate obligation.
- **Actions-only.** Same-state execution can observe or resume a current
  resident action. The Cursor hydrates the current visit and the runner reuses
  or revalidates evidence under the existing correlation and authorization.
  C43/C78/C81/C87/C89 own action applicability, resource and recovery identity,
  and Explain/dispatch parity. Reconcile uncertain external effects by their
  original identity.

[Executable graph][graph] · [Guard phase selection][phases] ·
[Cursor][cursor] · [Shelve][shelve] · [Supersede][supersede].

The legacy resume verb restores a paused binding and can wake Review resident
work. An earlier-state issue uses the state walk rather than joining Plan as
an already approved task. Resume also accounts for the recorded pause
interval. Treat session continuation, edge legality, source reopening and a
trip disposition as separate authorities. The inspected local paths establish
the legacy resume conditions. Full host-wide stop and trip parity remains a
Core and M3 qualification item. [Resume and Review wake][resume] ·
[Activity authority][activity].

## Directives, roles and exceptions

The legacy guidance defines user-visible work beside the executable verbs.
Refine captures intent, scope, acceptance and estimate evidence. Plan checks
current story intent, deep dive, estimate, ownership and approval at pickup.
Develop work obeys the bound issue, worktree and verified command scope.
Review asks for current-head approval and distinguishes approval, reasoned
rejection and a paused unresolved choice. Closing requests explicit authority
and checks current requirements and target lineage. C63 and C87 carry typed
directive identity and evidence into the shared command surface. Defer loaded
host instructions and runtime parity to C89 and M3.
[Guidance contract][guidance] · [Approval directive][approval-guidance].

The legacy code checks eligibility at more than one boundary. Operation home
state uses the executable verb contract. Ownership and bound worktree checks
use current actor and issue observations. Main-worktree delegation has its
own orchestration and isolation contract. The evidence lane depends on the
issue kind and accepted proof. The compatibility kind map includes code,
docs-only, audit, research, spike and epic. A hosted provider actor, a reviewer
and an issue assignee supply different kinds of authority. C16 owns binding,
C77 kind normalization, C80 the provider contract, C88 the hosted operation,
and M3 host identity and enforcement. [Home-state guard][verb] ·
[Worktree scope][worktree] · [Kind evidence][kinds].

The workflow-policy catalog separates waivable requirements from guardrails.
Its `aitm.workflow-exception/v1` and `v2` records carry a reason, scope and
authorization. Validation qualifies the record and its chain before evaluation.
The evaluator distinguishes satisfied, missing, not-applicable, waived and
conflicting evidence under the current scope. Full-auto is a workflow mode
with particular authority. A scoped exception still needs matching evidence
and proof of authorization. C07 and C28 should preserve applicable conditions,
per-operation refusal and explicit audit lineage. C110 records policy owner
decisions for legacy exceptions that lack an accepted mapping.
[Exception schema][exception] · [Workflow catalog][catalog] ·
[Evaluator][evaluator] · [Effect boundary][enforcement].

## Outside-state authority surfaces

| Surface | Observations and outcomes | Placement and remaining proof |
| --- | --- | --- |
| [Activity guard][activity] | Classifies edits and shell activity against the bound issue and a local Kanban-state observation. A bound task with missing state refuses write activity. Evaluation and payload errors have explicit behavior. | C16 binds scoped authority. C23/C31 own activity and stop evidence. C32 and M3 own managed execution and enforced host scope. A cached state or hook observation needs independent qualification for active-time evidence. |
| [Agent guard][agent] | For main-worktree delegation, reads current orchestration ownership and isolation request. A valid lock and worktree isolation qualify the delegated invocation. | C16/C32/C80 and M3 own worktree separation, actor identity and delegated scope. Demonstrate concurrent host isolation and independence under the selected runtime. |
| [Bash guard][bash] | Classifies tool payload, shell target and project/worktree path scope. Internal evaluation failure blocks. Invalid harness payload parsing follows its distinct compatibility path. | C32/C35 and the contained lane C36/C37 own admitted verification. M3 owns enforcement across direct host routes. Treat this legacy hook as host-specific evidence. |
| [GitHub issue edit guard][gh-edit] | Checks issue creation and body changes against protected fields and stage rules. It protects recognized evidence comment mutations through a separate read and classification path. | C13/C14/C43/C80/C88 own typed ingress, projection and admitted execution. M2 bears provider write scope and stale observation proofs. M3 qualifies equivalent direct-host restrictions. |
| [Project board guard][gh-project] | Classifies agent-issued project operations and verifies the bound project identity for eligible queries. Unpinned, foreign or unreadable board identity refuses the classified provider path. | C15/C43 and M2 project authoritative records with bound target and readback. Prove scope and replay; host-wide protection belongs to M3. |
| [Worktree binding guard][worktree] | Compares current checkout identity and operation context with the active session binding. Its explicit foreign-worktree exception requires durable audit. | C06/C16/C17/C81/C83/C85 own binding, resource generation, retirement and recovery. Prove refusal for a wrong worktree and evidence for an authorized scope change. |
| [Verb eligibility guard][verb] | Resolves protected verbs against their home states using the executable contract. Contextual operations such as Plan and Refine also have their own entry rules. | C28/C63/C78/C87/C89 own the shared eligibility catalog, Explain, and dispatcher behavior. Qualify each routed operation through its normal entry point. |
| [Evidence entry guard][evidence] | Keeps the legacy v1 protocol path separate. The v2 path checks the supported operation and validates the host's runtime capability and resident entries. | C56/C26/C35/C73/C38 own typed provenance, acceptance and applicability. C39/C42 consume qualified delivery and sign-off. M2/M3 qualify transport and actual host authority. |
| [Blast-radius guard][blast] | Counts intended issue or generic write targets. Reports a threshold decision and separates interactive consent, supplied explicit confirmation and refusal. | C30/C31/C32/C41/C88 own scope escalation and admission. A legacy count alone establishes neither authenticated proof nor target policy. Keep the selected limit and its owner explicit. |
| [Workflow policy][enforcement] | Evaluates current requirement evidence and validated exceptions. Managed provider admission is checked at the effect boundary. | C07/C28/C29/C31 own enforce/advisory behavior. Preserve distinct policy and evidence outcomes. M2/M3 qualify provider/runtime inputs. |
| [Native hooks][hook] | The shell entry routes SessionStart, PreCompact and PostCompact to the installed handler. It depends on Node and the resolved project. The handler records or recovers the applicable timing/actor observation. | C12/C16/C23/C43 and M3 own chaining, binding and runtime qualification. Partial or absent hook observations remain unqualified. Cost Capture needs its own explicit enrollment and receiver proof. |

Each target must qualify its authority and refusal cases on the selected host.
Local source inspection and tests establish the observed legacy contracts.
The project-specific choices are the approved role and review depth, any
provider-only board checks, permitted exception scope, and which facts are
required by the installed profile. C110 links each uncovered case to a
decision owner and the earliest affected pickup or admission.

## Verified evidence

Eight pinned unit test files reported **56 passing cases** with the legacy
lockfile on Node 26.8.1. They cover activity failure, worktree binding and
audited exception handling, verb home states, target counts, exception
validation, policy enforcement, canonical authority and policy outcomes.
These are local or fixture results. Live host hook installation, shell
containment, and production provider mutation are separate qualification
work.

[Activity errors][activity-test] · [Worktree binding][worktree-test] ·
[Verb eligibility][verb-test] · [Target counts][blast-test] ·
[Exception validation][exception-test] · [Enforcement][enforcement-test] ·
[Canonical authority][canonical-test] · [Policy evaluation][evaluator-test].

[story]: https://github.com/kburson/aitm/issues/496
[guards]: guard-facts.md
[actions]: action-and-evidence-facts.md
[decisions]: https://github.com/kburson/aitm/issues/497
[graph]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/lifecycle-policy/executable-transitions.mjs#L3
[phases]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/move-state/guard-execution.mjs#L151
[cursor]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/state-cursor.mjs#L217
[shelve]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/verbs/shelve.mjs#L52
[supersede]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/verbs/supersede.mjs#L121
[resume]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/verbs/resume.mjs#L146
[guidance]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/instructions/aitm-guidance.yml#L375
[approval-guidance]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/instructions/aitm-guidance.yml#L401
[activity]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/activity-guard.mjs#L8
[agent]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/agent-guard.mjs#L6
[bash]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/bash-guard.mjs#L7
[gh-edit]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/gh-edit-guard.mjs#L35
[gh-project]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/gh-project-guard.mjs#L46
[worktree]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/worktree-binding-guard.mjs#L296
[verb]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/verb-home-state-guard.mjs#L47
[evidence]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/evidence-v2/entry-guard.mjs#L5
[blast]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/blast-radius-guard.mjs#L33
[kinds]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/issue-kind.mjs#L28
[exception]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/workflow-policy/exception-record.mjs#L13
[catalog]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/workflow-policy/catalog.mjs#L1
[evaluator]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/workflow-policy/evaluator.mjs#L101
[enforcement]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/workflow-policy/enforcement.mjs#L125
[hook]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/hooks/task-tracker.sh#L2
[activity-test]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/tests/unit/task-tracker/lib/activity-guard-error.test.mjs
[worktree-test]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/tests/unit/task-tracker/lib/worktree-binding-guard.test.mjs
[verb-test]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/tests/unit/task-tracker/lib/verb-home-state-guard.test.mjs
[blast-test]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/tests/unit/task-tracker/lib/blast-radius-guard.test.mjs
[exception-test]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/tests/unit/task-tracker/lib/workflow-policy/exception-record.test.mjs
[enforcement-test]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/tests/unit/task-tracker/lib/workflow-policy/enforcement.test.mjs
[canonical-test]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/tests/unit/task-tracker/lib/workflow-policy/canonical-authority.test.mjs
[evaluator-test]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/tests/unit/task-tracker/lib/workflow-policy/evaluator.test.mjs
