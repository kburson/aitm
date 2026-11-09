---
schema: "aitm.review-response/v0"
level: "sar"
story: 1
role: "reviewer"
round: 1
artifact_path: ".aitm/stories/000/1/design/architecture.md"
artifact_base_commit: "e78ae2b1328861801b4917dd1669f8b2c1ab559a"
artifact_digest: "sha256:99ad57e2eb487255c0615083c94ef17156bbe7955f9972ee4fb20fddeaad2e09"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6-astra"
  effort: "high"
reviewer_session: "01a1be33-1c95-7543-b2ef-73ebbae4b8f6"
started_at: "2026-11-09T02:46:30Z"
submitted_at: "2026-11-09T02:50:52Z"
finding_ids:
  - R1-F001
  - R1-F002
  - R1-F003
  - R1-F004
  - R1-F005
  - R1-F006
  - R1-F007
  - R1-F008
  - R1-F009
  - R1-F010
  - R1-F011
  - R1-F012
answered_finding_ids: []
---

## Summary

**Revisions requested.** The separation of the authoritative local store, rebuildable index, provider projections and optional harness adapters is consistent with the rewrite's purpose. The architecture nevertheless promotes an unconfirmed policy to a rule, omits several accepted cross-section contracts, and overstates enforcement, repair and recovery guarantees. These issues would give section designers incompatible instructions.

This is a full first-round review of the exact FUR identified above. I read the required sources in the requested order, the handoff, and the optional old-tool survey. `core-design.md` and `master-plan.md` are consistency evidence only; **all requested changes are confined to `architecture.md`**. Implementation algorithms, section-level schemas and review-tool setup are outside this review. “High” means the text can lead to an incorrect policy or architecture; “medium” means a material contract or consistency omission.

No finding requires an immediate new owner choice. Existing calls and open decisions may remain open if represented accurately. In particular, this review does not choose the meta-package name, patch-refactor implementation repository, review-depth policy, second-trip cap, or a replacement for the agreed planning-branch protection scheme.

## Findings

### R1-F001 — High — Preserve the unresolved trip policy instead of presenting it as settled

**Evidence:** FUR lines 29 and 123–125 define trips as requesting a second/nested expansion or exceeding time, and unconditionally send a second trip to Backlog. The decision record, `.aitm/stories/000/1/draft.md:147–150`, confirms fresh clocks and allowances but explicitly labels the second-trip cap a **call requiring confirmation**. The owner's wording at line 150 is “the one expansion slot used and the story still not complete,” which the FUR silently narrows to needing another expansion. `core-design.md:391` preserves the cap's uncertainty.

**Requested fix:** Mark the cap as a proposed, unconfirmed call and include it in the open items. Distinguish the owner's trip rule from the operational interpretation of “slot used and still not complete.” Explain that interpretation or retain it as an explicit unresolved interpretation; do not silently change the owner rule or invent an immediate trip when an expansion is created. Keep the confirmed fresh-attempt clock and allowance.

**Decision-record basis:** `[user]` and `[call]` at draft lines 147–150; the expansion absorption rule at lines 47–48 and 148. Accurate uncertainty is sufficient for this review; owner confirmation need not occur now.

### R1-F002 — High — Reconcile advisory mode, integrity refusals and optional deny hooks

**Evidence:** FUR line 125 says every trip stops work and demotes the story; lines 131–134 say advisory failures proceed. Lines 87 and 149 respectively say harness hooks deny commands and only record/warn. Lines 58 and 88 combine “all enforcement lives here” with out-of-band branch protection, without separating workflow policy from store integrity. The core context explicitly keeps integrity refusals in advisory mode (`core-design.md:137–141`) and records advisory trips without moving stories (`:387–388`). The FUR also omits the human-only boundary on `pivot`.

**Requested fix:** State the distinction between workflow enforcement (refusal/demotion in enforce mode, recorded/report-only behavior in advisory mode) and store-integrity failures that stop unsafe writes in either mode. Say optional hooks may deny dangerous operations as a backstop while core correctness remains independent of them. Preserve human-only pivot attribution so an agent cannot relabel a planning failure. Define the CLI/core as the authoritative workflow enforcement surface rather than implying that it is the only protection layer.

**Decision-record basis:** Draft lines 40–41, 125, 152 and 164–170. These decisions already coexist; the fix is to explain their scope, not relax one of them.

### R1-F003 — High — Acknowledge the planning audit trigger conflict and the limits of forward repair

**Evidence:** FUR lines 78 and 83–89 require `.aitm/`-only planning data and an Action auditing every push. A conventional push-triggered workflow must exist under `.github/workflows` in the event's associated ref. With no such path allowed on planning, placing that workflow only on trunk does not supply the promised planning-push trigger. This follows from [GitHub's workflow trigger documentation](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows#workflow-triggers). Separately, line 88 presents forward repair without the core design's caveat: restoring a tree cannot remove shared ancestors introduced by a bad merge (`core-design.md:140–141`). Git's [merge documentation](https://git-scm.com/docs/git-merge) describes the retained parent histories; the repair limitation is an inference from that ancestry model.

**Requested fix:** Preserve the agreed six-layer intent, but mark the audit trigger/location as an unresolved implementation conflict owned by the GitHub section. Require that design to explain how every push is audited, including pushes outside aitm; do not claim a normal trunk-only `on: push` workflow achieves it. Do not add `.github/` to planning or replace every-push auditing with polling without an owner decision. Also distinguish restoring valid current files from restoring history isolation: the latter cannot be promised by a fast-forward tree repair. Record the exceptional recovery constraint and explicit authorization requirement rather than advertising universal automatic repair.

**Decision-record basis:** Draft lines 89, 157 and 163–172. The owner chose both branch isolation and layered auditing. Naming the technical conflict is required; choosing which owner requirement to alter is not.

### R1-F004 — High — Separate authored documents from generated views and define the logical writer boundary

**Evidence:** FUR lines 98–100 say events are authoritative, “Markdown is output,” every frontmatter block is generated, and no file has two writers. The system also depends on agent-authored designs, plans and review records. The core context assigns markdown bodies to authors and frontmatter to core (`core-design.md:165–184`), then calls `events.jsonl` a multiple-writer exception with cross-clone replay. The present summary obscures which source survives regeneration and whether “writer” means a process, owning component or author.

**Requested fix:** State that events govern workflow state and timing; authored document bodies and portable review collateral remain authoritative content; `story.md` and generated metadata are projections. Define one owning writer/API per persisted surface, with producers submitting events through the core, and identify concurrency/ordering and authored-file conflicts as contracts the core must satisfy. Explicitly acknowledge any remaining disagreement with the core's multiple-writer call instead of silently inheriting it. No particular lock, merge algorithm or event ID format is required here.

**Decision-record basis:** Draft lines 52, 88, 91, 95–97 and the per-turn review-record decisions at 67–70. The agreed single-writer principle must be preserved, not discarded to match a builder's call.

### R1-F005 — High — Carry the accepted portable review contract into the architecture

**Evidence:** FUR lines 107 and 110 require accepted design/plan artifacts, but line 161 describes only a “bridge,” and line 186 still asks for confirmation of SAR/SPR/XPR definitions. It contains none of the accepted per-turn patches, shared response format, no-precommit contract or interim import boundary. The peer-review draft confirms the definitions and portable record at `.aitm/drafts/2026-11/20261108-1310-peer-review/draft.md:17,37–49`; the master plan does not deliver the integration until M4 (`master-plan.md:32`).

**Requested fix:** Add a compact review contract: iterative SAR/SPR/XPR with common collateral, every author revision retained as a numbered patch, a self-contained record that does not depend on review commits, caller-chosen story-local output, and acceptance tied to the reviewed artifact version. Clarify that changed design/plan bytes require renewed acceptance; a historical acceptance must not automatically approve later content. Link the manual interim process for the period before M4. Remove the obsolete open definitions item while retaining genuinely open choices, including document review depth and where the refactor is built. Preserve any unconfirmed patch-000 implementation detail as a call.

**Decision-record basis:** Draft lines 59, 62 and 66–71; peer-review draft lines 39–49 and 53–65. This asks for the agreed interface and version boundary, not a full peer-review design or an unapproved review-depth matrix.

### R1-F006 — Medium — Scope the lifecycle table to leaves and explain epic aggregation and JIT freshness

**Evidence:** FUR lines 105–114 apply implementation commits, tests, PR review and a four-hour refinement exit to an undifferentiated “story.” Yet epics are stories (`.aitm/README.md`, Rules), and the core explicitly exempts epics from leaf checks and aggregates child progress (`core-design.md:343–355`). The FUR's “JIT recorded against current trunk” also reads as exact-tip equality, whereas the core proposes allowing unrelated intervening merges when touched paths are unaffected.

**Requested fix:** Label the table as the normal executable leaf flow and state that epics aggregate children rather than requiring their own implementation clock/PR/test artifacts; point section designers to the kind-specific rules. Clarify whether “current” means applicable to current code, with the exact freshness check left to core, rather than accidentally mandating exact-tip equality. Do not canonize unreviewed core builder calls merely to remove the inconsistency; identify them as such where needed.

**Decision-record basis:** Draft lines 51, 61–63 and 129–130; master-plan lines 19–21. The owner limits leaf implementation, not planning or an entire epic to four hours.

### R1-F007 — High — Preserve delivery as a condition of the delivered disposition

**Evidence:** FUR lines 113–114 and 176 allow PR review passing plus retrospective to move directly to Done with disposition “delivered,” without identifying delivery. PR approval and delivery are different events: a reviewed story branch can still be unmerged. The core context repeats the same omission (`core-design.md:360`), so citing that design does not resolve it.

**Requested fix:** State that the normal delivered path records delivery before the sign-off completes Done, and assign the core/provider boundary for authoritative delivery evidence. Leave merge strategy and provider mechanics to section design. Preserve the separate abandoned/superseded/duplicate dispositions and the agreed clock end at passing PR review; delivery need not extend the four-hour clock. No human approval gate is requested.

**Decision-record basis:** Draft line 75 says sign-off is after delivery; lines 147 and 151 refine the clock and the signing actor, without removing delivery. The fix restores that sequence rather than adding a new owner gate.

### R1-F008 — High — Distinguish retryable projection from authoritative remote creation

**Evidence:** FUR lines 24 and 39 classify the backlog as a downstream view whose failed sync is simply rerun. Line 97 simultaneously makes issue creation the source of the permanent story ID. If issue creation succeeds remotely but its response or local recording fails, blindly rerunning it can create a second identity. This is a logical failure case in the stated sequence, not a claim that a particular GitHub endpoint lacks an idempotency feature. Similarly, the architecture names git authority but does not distinguish a locally committed transition from successful push/projection.

**Requested fix:** Narrow the “no recovery machinery for remote state” non-goal to reconstructible projections. State that graduation/provider creation must reconcile an uncertain result to one stable identity, with details assigned to the provider/core designs. Explain that the durable local event/store transition is distinct from retryable push and projection, and that action failure cannot roll back or fabricate that local state. Retain sparse sync and avoid prescribing a new distributed transaction framework.

**Decision-record basis:** Draft lines 58, 65, 87–91 and 104. The owner-selected issue-first graduation is retained; the architecture must identify its exceptional authority role.

### R1-F009 — High — Bound bookkeeping recovery and enforcement by what the tool can actually observe

**Evidence:** FUR line 28 promises missing records are rebuilt; lines 112–113 require passing evidence; line 125 promises immediate stopping; line 149 makes hooks optional. Core context says time is approximated from activity gaps, CLI commands supply activity until harness integration, and limits are checked on the next touching command (`core-design.md:368–369,387–388`). Git history alone does not establish that an unrecorded test passed or how long unobserved agent work took. A CLI cannot itself interrupt arbitrary work that never invokes it.

**Requested fix:** Describe the observational boundary: authoritative operations capture their own durable evidence, recovery reconstructs from retained proof or reruns verification, and unavailable timing/evidence is not silently turned into success or an exact measurement. State how the hook-independent workflow detects a trip at its command boundary and directs agents to stop, while preserving the owner's immediate-stop policy after detection. Identify the telemetry/freshness contract for core and harness designs instead of promising continuous control from optional hooks. Keep bookkeeping repair automatic and distinguish missing records from a genuinely failing test or undelivered change.

**Decision-record basis:** Draft lines 40–41, 49, 52–53 and 147–150. This does not weaken the policy or add a manual receipt gate; it prevents unimplementable guarantees from being mistaken for acceptance criteria.

### R1-F010 — Medium — Correct the package naming and initialization ownership boundary

**Evidence:** FUR line 164 names `aitm` as the distributable meta-package, although `master-plan.md:46–48` records that it is taken and the replacement is open. The unrelated distribution is still visible on [PyPI](https://pypi.org/project/aitm/). Lines 141 and 158 assign `init` to the backlog/GitHub extension, while core initialization must also work with only `aitm-core` installed (`core-design.md:114–124,470–472`).

**Requested fix:** Distinguish the `aitm` CLI/product name from the unresolved full-install distribution name, and add the latter to open items without selecting it. Describe core `init` as owning generic store/config/hook installation and invoking provider-specific setup/protection capabilities, with the GitHub package supplying GitHub steps. Clarify that installing packages and enabling/configuring their extensions are separate responsibilities consistent with the full-install requirement.

**Decision-record basis:** Draft lines 108–111 and 156–158; handoff's known-open meta-package item. No naming decision or packaging implementation is required now.

### R1-F011 — Medium — Restore the agreed learning-data contract before the rubric section is designed

**Evidence:** FUR line 30 promises learning, line 163 lists ML, and lines 178–180 discuss tutorials only. It omits the agreed Refine/Plan/Close records, complete-triad calibration boundary, lessons retrieval and token/cost capture. The master plan places history import before rubric (`master-plan.md:35–38`), making the distinction between imported/incomplete records and valid calibration records material to the store contract.

**Requested fix:** Add a short architecture-level account of the recorded estimation/outcome data and ownership: phase estimates and actual outcomes, expansions/trips and post-acceptance defects, lessons, and available token/cost telemetry; only complete triads calibrate. Keep incomplete/imported/unavailable measurements identifiable, with exact schemas and learning algorithms delegated to core/rubric/harness designs. Preserve comparable-story retrieval and quantile regression as the agreed starting direction rather than treating ML as an unspecified package label.

**Decision-record basis:** Draft lines 119–120 and 115. This reinstates accepted cross-extension requirements; it does not demand the rubric's detailed model design before its milestone.

### R1-F012 — Medium — State that core never calls models and retain specialized-role boundaries

**Evidence:** FUR line 31 excludes lab SDK dependencies, but that does not prohibit a model call through generic HTTP. Line 125 says the agent analyzes and decides, while line 151 lists roles without their permissions or relationship to existing skills. This leaves a section designer room to put agent reasoning in the core or grant the planner implementation-write authority.

**Requested fix:** Explicitly state that core never calls a model: the harness agent performs reasoning and records decisions through core interfaces. Preserve the agreed read-only researcher, design/plan-only planner, and independent plan reviewer boundaries, including their use of existing superpowers skills and the fixed plan-output contract at an architectural level. Module layout and harness-native definitions remain section work.

**Decision-record basis:** Draft lines 39–40 and 81–83. These are accepted boundaries, not new capability restrictions.

## Required changes

Address R1-F001 through R1-F012 in the FUR. The changes should mostly be precise qualifications and short cross-section contracts, not a larger implementation specification. In particular:

- Preserve the authority and uncertainty of owner decisions; update the open list rather than resolving known-open choices.
- Reconcile workflow enforcement, integrity safety, hook behavior, lifecycle kinds, freshness and delivery.
- Explain authoritative content, evidence, remote creation and portable review records sufficiently for section designers to agree on boundaries.
- Record the GitHub audit conflict and forward-repair limit; correct the package/init boundaries and restore the agreed model/agent/learning contracts.

Where the context-only core design differs, it is sufficient for this round to identify that difference and the rule a later core review must reconcile. Do not change that file to satisfy this review.

## Optional suggestions

- Clarify that the hosted-service non-goal excludes a new hosted backend, while the agreed viewer can be a prebuilt static Pages site backed by generated JSON. A small viewer paragraph could also distinguish local reads from hosted snapshot freshness; the detailed deployment design belongs to M6.
- In the later packaging design, verify released-core consumer tests outside editable workspace dependencies. [uv documents workspace-member dependencies as editable](https://docs.astral.sh/uv/concepts/projects/workspaces/), so an in-workspace integration test alone would not demonstrate the agreed released-core dogfooding boundary. The architecture's current released-version requirement is correct; no new release policy is requested.
- Retain the GitHub section's explicit REST-before-GraphQL capability investigation. The draft already distinguishes verified reads from unverified item-field updates; there is no reason to settle those endpoint details in this FUR.

## Decision

**revisions-requested**

The next round should review the revised FUR and the author's disposition of every finding. Existing open decisions may stay open. There is **no newly required owner choice before the author can make these architecture corrections**. A future proposal to change the `.aitm/`-only branch policy or the every-push audit requirement would require the owner; this review only requires the conflict to be accurately recorded.
