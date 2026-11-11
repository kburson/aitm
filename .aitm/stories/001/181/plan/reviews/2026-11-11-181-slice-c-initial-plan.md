# #181 Slice C implementation plan

> For agentic workers, use subagent-driven development or executing-plans for each authorized leaf. Apply the repository's leaf Design, Plan and JIT gates.

**Goal.** Automate evidence-backed Actual and Cost projection on AITM-PY and serve the same scoped measures to the viewer.

**Architecture.** Read pinned Core workflow and timing facts and independently pinned monitor usage. Assemble one reproducible reporting view. The GitHub extension projects fields from an authorized published view. The viewer consumes it read-only.

**Stack.** The released Python Core and monitor interfaces, the supported GitHub extension, and the M6 viewer. The shipped Python and HTML tools under `tools/story_dashboard/` are the parity fixtures and interim operator path. [Design](../design/story-timing-dashboard-design.md#ownership-and-transition) · [Refinement and live capability evidence](2026-11-11-181-slice-c-refinement.md)

## Boundaries and dependencies

A/B are delivered and remain independently usable. This plan records dependencies at the Slice C checkpoint inside #181. It schedules no changes to upstream work, creates no leaf issues, and grants no runtime pickup. Use exact accepted contract and release/build identities at each JIT. Assign production paths when the owning packages land, checking overlap with their current work. No interim automatic writer or duplicate timing/pricing engine is part of this plan.

| Gate | Exact dependency and qualifying evidence |
| --- | --- |
| Core read | C18 [#23](https://github.com/kburson/aitm/issues/23) supplies a pinned story/index/ancestry read, and C60 [#72](https://github.com/kburson/aitm/issues/72) supplies released Core for production. These are open. |
| Native timing | C23 [#28](https://github.com/kburson/aitm/issues/28), C25 [#34](https://github.com/kburson/aitm/issues/34), and C27 [#36](https://github.com/kburson/aitm/issues/36) are open. Core/M3 must qualify stable actor, phase, attempt, story/draft and turn identity, real in-turn tool boundaries, all-phase start/delivery and explicit owner request/response or resolution where claimed. Use #100 M07a/b/c routing evidence only where it proves the binding, and require separate timing proof when a provider adapter supplies intervals. Monitor M18 [#128](https://github.com/kburson/aitm/issues/128) and M19 [#129](https://github.com/kburson/aitm/issues/129) remain host-specific qualification checkpoints for monitor-backed claims. |
| Legacy adoption | C46 [#53](https://github.com/kburson/aitm/issues/53) inventories and maps. C47 [#54](https://github.com/kburson/aitm/issues/54), C48 [#55](https://github.com/kburson/aitm/issues/55) and C51 [#56](https://github.com/kburson/aitm/issues/56) prepare, apply and prove exact-pin/fresh-clone replay. All are open. An owner-authorized cutover is needed before applying to production planning. Unsupported facts remain visible as legacy evidence with their original coverage. |
| Fenced usage and ingress | M13 [#123](https://github.com/kburson/aitm/issues/123) and M14 [#124](https://github.com/kburson/aitm/issues/124) are open, as is Core C44 [#51](https://github.com/kburson/aitm/issues/51). Open monitor predecessors include [#203](https://github.com/kburson/aitm/issues/203), [#209](https://github.com/kburson/aitm/issues/209), [#210](https://github.com/kburson/aitm/issues/210) and [#204](https://github.com/kburson/aitm/issues/204) for settlement/coverage, then [#119](https://github.com/kburson/aitm/issues/119) delivery ACK, [#120](https://github.com/kburson/aitm/issues/120) scheduler, [#121](https://github.com/kburson/aitm/issues/121) coordinator and [#122](https://github.com/kburson/aitm/issues/122) recovery/publication fence. Consume M13's exact publication, window and rate basis. Prove compatible M14 delivery and C44 receiver reconciliation before production Cost and rubric ingestion. |
| Board and viewer | Master #1 [M2 GitHub and M6 Viewer](https://github.com/kburson/aitm/blob/9fab8da0de9326b7b307fb627c23f12680674330/.aitm/stories/000/1/plan/master-plan.md#L40-L53) have draft ownership. M2 must prove supported endpoints, field ownership, published-source ordering and fenced writes/readback. Include evidence changes and new report revisions that occur without a story-state transition. M6 needs versioned schema input, an approved refresh route and hosted freshness proof. |

## Proposed delivery order

Estimates are preliminary integration agent-hours, including local verification and independent review. Refresh at JIT. C01 is an independently useful read-only qualification. The remaining leaves have explicit runtime holds.

| Key | Scope | Estimate | Pickup requirements |
| --- | --- | ---: | --- |
| C01 | Pin producer capabilities and shared acceptance fixtures | 2.25 h | Delivered A/B. Refresh upstream capability readback. |
| C02 | Map and replay legacy timing and usage evidence through Core | 3.75 h | C01, applicable Core legacy adoption and pinned read contracts. |
| C03 | Qualify native Actual and separate elapsed/wait measures | 3.75 h | C01, Core read/activity/review/attempt and applicable provider timing proof. |
| C04 | Bind fenced Cost and comparable outcomes | 3.75 h | C01, M13/M14 and C44. |
| C05 | Qualify the supported GitHub field projection | 3.75 h | C02/C03 for historical/native Actual, M2 writer and authorization. C04 only for enabling Cost. |
| C06 | Qualify shared view and hosted viewer | 3.00 h | C01 and M6 for read-only shape; C02/C03 for integrated timing, C04 for priced evidence, C05 for shared board/view parity. |

Total **20.25 h** for #181 integration. A/B's separate 26.0 h estimate remains the historical baseline. Add a later leaf only through reviewed refinement when an owning contract exposes a new bounded gap.

### C01. Freeze input and parity evidence

- [ ] Inventory the existing A/B seed, per-story receipts, exact board fields, and known #181/#111 cases. Record planning commit, UTC cutoff, receipt digests, metric versions, Core build/capability, and independent report identity, publication, cutoff/window and rate card/basis where present. Verify that absent capability returns an explicit unavailable result.
- [ ] Assemble sanitized acceptance fixtures with full and missing evidence. Pin expected 3,600,000 ms for two child contributions of 900 and 1,800 seconds plus 900 seconds of direct epic work. Pin the existing #181 partial rollup of 10,605,711 ms and #111 scoped elapsed of 774,000 ms. Run the delivered dashboard tests from trunk as the starting parity check. Identify each upstream contract in the dependency table and hand any gap to its single owner.

### C02. Adopt legacy receipts through Core

- [ ] Use C46 inventory and C47/C48 approved writer on a disposable clone. Map stable source digests and original qualified intervals without changing identity, provenance or coverage. Canonicalize a verified draft alias once. Hold overlap without supported identity linkage. Preserve prior published views.
- [ ] Exercise identical replay, proven split, late correction/reattribution, and interruption before and after a multi-story publication. Replay must be a no-op for identical evidence. Conflicts and incomplete publication must hold. Confirm C51 fresh-clone/index equality, preserved historical totals and no promotion of partial evidence. Production apply requires the exact adoption declaration and authority.

### C03. Qualify native Actual

- [ ] Use C18/C23/C25/C27 facts to produce direct and inclusive work by actor and phase, and separate elapsed, owner wait and working wall time. Prove concurrent distinct actors add, same-actor duplicates union, scope switches and review handoffs partition proven time, tool intervals inside a turn count once, and owner wait, idle and unattended work add no Actual. Verify unsupported sources and missing boundaries yield Partial or Unknown. The narrower Core trip clock remains independent.
- [ ] Run native qualification on each claimed client/host. Include an open owner request, a completed wait, separate all-phase and implementation boundaries and a concurrent agent. Recompute one pinned report from a fresh reader. Retain safe evidence and explicit coverage for every metric.

### C04. Bind Cost and calibration independently

- [ ] Consume the exact fenced M13 publication, canonical project/story/attempt scope, window, cutoff, and rate digest/basis. Reconcile direct and inclusive known-price and unpriced counts, and prove an unchanged token set yields the same Cost when tool runtime changes. A foreign project, disputed scope or unpriced request cannot supply complete story Cost. A retained priced subtotal may be shown with coverage in the viewer.
- [ ] Prove M14/C44 immutable delivery and receiver reconciliation under replay, rate revision, delayed evidence, partial coverage and ambiguity. Feed only complete estimates and outcomes matched to the same phase, actor/role scope, attempt and timing basis into calibration. Retain incomplete outcomes for diagnosis.

### C05. Project through the GitHub extension

- [ ] Confirm M2 owns the exact Project/issue/field mappings and authorized trigger. Actual uses verified milliseconds divided by 3,600,000 and rounded once to four decimal hours. Include Partial coverage with any partial numeric value. Separate Elapsed and Owner wait use calendar hours and per-measure coverage, with Unknown kept explicit. Populate Cost only with complete, verified API-equivalent pricing for the selected scope. Missing usage leaves a new Cost blank and cannot block Actual.
- [ ] Test a published view with later receipts and no state change, stale retry, duplicate replay, uncertain server ACK, concurrent human field changes, a superseded report, and interrupted actual/coverage readback. Use M2's serialized/fenced ownership and latest publication check; hold unresolved drift. Verify the exact item, value and coverage by readback. Reconcile pre-existing values under field authority before overwriting or clearing them. Qualify on a disposable project and authorize production target separately.

### C06. Prove viewer and board parity

- [ ] Read the same approved view and provenance from M6, exposing direct/descendant Actual, elapsed and wait scopes, parallel working wall time, coverage, and the independent timing and usage watermarks. Verify the read-only viewer keeps missing inputs explicit and exposes no raw provider handles, paths, prompts or transcripts.
- [ ] Rebuild the old seed and a later native view in a clean checkout, verify stable old bytes and independent metric refresh, compare board readback for the common view, and prove hosted snapshot freshness and the supported refresh trigger. Start with a supported scope, keep the local fallback available, and retain exact evidence for any unqualified scope.

## Stop conditions

Hold automatic publication when the required producer, scope proof, field authority, replay/fence or readback is missing. A missing Cost source leaves timing available. Promote each measure only after its own qualifying evidence is retained. Slice C completion requires the supported owner contracts and the production replay and hosted readback acceptance in design items 2, 4, 5 and 6.
