---
schema: "aitm.review-response/v0"
level: "sar"
story: 2
role: "reviewer"
round: 1
artifact_path: ".aitm/stories/000/2/plan/core-implementation-plan.md"
artifact_base_commit: "f86dd7c1954215585dcbdbcc9bac0e7e490a1956"
artifact_digest: "sha256:5c5103a8f9138e3e893cc9546d58f17f46078ab06911391e73e89d6919548ff7"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6.1-sol"
  effort: "high"
reviewer_session: "01a1bf0f-9ac0-7603-911d-3fb4bd37d3e7"
session_identity_kind: "observed-session-id"
started_at: "2026-11-09T06:47:14.618Z"
submitted_at: "2026-11-09T06:50:17.397Z"
start_basis: "recorded"
finding_ids: [R1-F001, R1-F002, R1-F003, R1-F004, R1-F005, R1-F006, R1-F007, R1-F008, R1-F009]
answered_finding_ids: []
---

## Summary

**Revisions requested.** I read the complete 933-line candidate and the accepted core design, parent architecture, published master-plan SAR, owner and core draft decisions, original Refine record, planning layout, and interim review procedure. I verified the raw input digest and compared the parent design and master-plan digests with their manifests. The table sums to 172 h over 53 leaves, and its declared dependency edges form a topological order. The worker thread ID matches its recorded Codex session metadata, and its turn context records the selected model, effort, and start. This is manual SAR with declared-manual assurance. The recorded interval is an elapsed turn span.

The plan assigns the major subsystems and preserves the release/adoption boundary and open policy choices. The required revisions concern ownership of normal entry points, atomicity and integration prerequisites, bounded leaves, and verifiable acceptance.

## Findings

### R1-F001 — High — Specify the production composition seams and executable dependencies

The contract ownership on plan lines 60–62 gives C07 ownership of StoreAnchor, but C06's public validation contract already consumes it and C07 waits for C06. C07 likewise consumes RefreshResult before the C08 fetch leaf exists, without a named earlier owner for that observation type. C05 declares a mandatory ValidationGate but the plan leaves unclear which leaf actually wires its production implementation. Similar gaps arise where C14 must enforce extension ownership at every transaction boundary, C43 must retry on sync, and C12 must complete init wiring. Those leaves own isolated modules and tests but do not name the owning call site, a predeclared extension seam, or an allowed shared-path update. An implementer could deliver a working helper while the normal command bypasses it. The design makes these rules apply to the real writer and normal entry points (core design lines 139–149, 151–174, 293–312, 467 and 568–578).

Move shared type ownership earlier or introduce a defined prerequisite, then identify the owner, touched paths and dependency order for production composition. Cover at least the committed-policy/fetch and validation gate, constrained extension write ingress, init wiring and sync/action retries. Make an integration test drive a real entry point where each rule matters, including a transaction-boundary rejection and pending-action recovery. Reconcile table, leaf prerequisites and parallel groups; a future implementation of an already consumed type or call site cannot be a prerequisite supplied by guesswork.

### R1-F002 — High — Keep local numbering and story finalization atomic

C21 (lines 414–426) exposes allocate_local returning IdentityResult and tests that a local CAS exposes a permanent ID. C22 (lines 428–440) separately owns finalize_graduation, the draft move, numbered story creation and reciprocal links, and depends on C21. The proposed boundary can deliver permanent local allocation before the story exists and provides no callable finalization contract to C21. The local provider specifically requires allocation and initialization in one authority transaction; shared candidates are unissued until that transaction is verified in publication (core design lines 541–545). An externally issued, retained but not yet finalized number is a distinct case.

Name the shared pure construction or operation seam and order its delivery so neither leaf needs an undeclared forward dependency. Test the actual local graduation transaction in local-only and shared modes, including a failure between proposed allocation and story construction, a losing CAS/reallocation, and lost acknowledgement. Assert that number, draft move, initialized story, relationships and initial projection identity appear together, with no separately exposed local ID or workable numbered story before the required authority result.

### R1-F003 — High — Assign complete CLI paths before the qualification walk

The plan promises every named command has an owning leaf and C49 only audits existing adapters (lines 62 and 820–832). It names modules but leaves required routes without a concrete owner or proof. For example, no leaf defines the Discuss context/command exporter; C27 exposes JIT and estimates but no same-attempt attempt reconcile route; C16's bind tests do not specify bind --deliverable or bind --evidence while C42 and C45 lack an explicit bind adapter update/seam. C26 names an acceptance evaluator and review import CLI but no persisted design accept/plan accept operation or owner for its adapters. The core design requires these routes and distinguishes successful import/evaluation from a persisted acceptance or new binding authority (lines 397–403, 418–428, 461, and 582–595). The existing CLI walk's prose could pass using direct helper calls or without explicitly exercising those transitions.

Provide a command/subcommand and option-to-leaf map against the entire accepted CLI table, with owning operations, adapter paths and representative end-to-end commands. Include persisted acceptance, provisional-attempt reconciliation, both scoped binding routes, Discuss, read refresh/index rebuild and planning validate. If another leaf owns a shared adapter, pin the integration seam and prerequisite. Have C49 verify command coverage and use the real CLI for required workflows, while keeping missing behavior with its owner.

### R1-F004 — High — Make the provisional and evidence-only paths explicit in executable acceptance

C27 mentions preserving the provisional budget only in its risk note, C28 tests generic advisory advancement, and C42's recovery test omits the separate scoped binding/admission and the timing outcomes. C49 lists a nominal walk and unspecified advisory recovery. A builder can satisfy those descriptions without proving that an advisory Develop entry with missing plan and binding keeps its attempt identity, or that recovery of unchanged Done/unverified work obtains only the authority it needs. The accepted design requires both recovery paths with retained prior evidence and time (core design lines 397–403, 449–453, and 633, 641).

Assign the producers and targeted assertions. Exercise advisory Develop with an absent plan and missing implementation binding, then attach current accepted plan/binding without resetting attempt, clock or allowance. Exercise real missing-test recovery from Done/unverified: retain the old disposition/waivers, use the new evidence-only binding and managed admission, activate only after valid prerequisites, sign off, and prove old or superseded generations cannot act. Prove recovery cannot edit implementation, expand or authorize new target mutation, and distinguish a genuine rerun's later eligible interval from reconstruction of an already valid receipt. Include the shared-store ordering proof where applicable.

### R1-F005 — High — Verify containment through the actual executor and readiness paths

C35 defines captured-export execution. C36 and C37 add platform probe/profile modules, but their touched paths do not include the C35 runner or C11/C12 readiness routes and no profile-to-executor contract is named. C52's installed smoke and C49's earlier captured-export walk do not close that seam. Both platform adapter tests could pass on their own yet a contained policy would still launch an unconfined process, report the wrong assurance, or never work via normal commands. The design requires the selected lane in init/doctor and authoritative verification, with contained proof where supported and a truthful unavailable result otherwise (lines 434–447, 641).

Name the platform-neutral selection/dispatch interface, its production wiring owner and dependency order. Require real installed commands under selected contained policy to report probe readiness and run the actual managed process tree through its profile on supported macOS/Linux lanes, with read/write/network/descendant assertions and receipt assurance. A failing/unavailable probe must keep authoritative verification pending without a captured-export fallback; a separately committed captured-export policy must still permit its bounded nominal walk. Preserve existing no-host-security-change boundary.

### R1-F006 — High — Decompose known large or compound leaves before issuing them

C02 allocates 3.5 h to defining all accepted event families and building the full causal reducer with clock validation, although several domain boundaries need later types. C24 puts portable schemas, patch replay and escape controls, topology and assurance validation, and native lineage mapping in one 4 h leaf. C52 puts distinct full-entrypoint timing, unit isolation, dual-platform wheel installation and CI wiring in one 3.5 h leaf. Those obligations each include a failing test, implementation, affected contract checks and effective source review on an empty baseline. The plan provides no independent deliverable cut or capacity rationale for these already identifiable groups. Its JIT fallback (line 41) handles new uncertainty but would shift known decomposition work until after the plan creates issues from these rows.

Split compound work into bounded deliverables with concrete prerequisites and tests, or provide a credible bounded basis tied to already-delivered helpers and separate test/review engagement for each disputed leaf. For example, freeze event envelope and reducer invariants first and define/test domain reducers in bounded groups; separate portable reconstruction from native mapping and topology where needed; separate performance proof from cross-platform install/CI qualification. Update leaf count, bottom-up estimate, dependencies, coverage and stable keys consistently. Preserve the historical 180 h Refine estimate and keep JIT as the check on later uncertainty.

### R1-F007 — Medium — Assign executable qualification suites and close their prerequisite and proof gaps

C49–C52 list separate suite files but the required pytest commands select only test_c49.py through test_c52.py. Nothing connects those entry points to the other listed suites or requires their collection. C50 claims trip/target/expansion races and shared recovery but omits a dependency on C42 for sign-off races; it inherits C35 transitively, but does not identify an actual shared test-command launch refusal as a required scenario. Its proposed test could pass using only low-level operation doubles. The broad matrix in lines 898–915 associates topics with leaves but does not ensure that required combinations are run, such as a lost issue response and no-child resolution followed by full event rebuild, an enforce-mode stop winning a shared test command before launch, or local-only core-run delivery with publication explicitly not applicable (core design lines 597 and 632–646).

Give each qualification suite exact collected test paths or one clear executable aggregator and a scenario-to-test map for the accepted design's required combinations and proofs. Assign prerequisites for the public operations each scenario executes. Include actual two-clone expansion/test/promote/sign-off fencing, reconstruction of no-child reservation and late review clock facts without private state, and successful local-only core-run delivery plus checked-out/invalidated refusals. Use explicit lanes for platform or release cases and show the required suites in CI evidence.

### R1-F008 — Medium — Specify the migration receipt, dry-run and adopted-readiness proof

C46–C48 and C51 preserve review snapshots, bound the legacy declaration and cover competing apply. They do not assign receipt construction/validation for the deterministic payload tree excluding its own receipt path, or prove that fresh validation rejects a forged extension of the bounded legacy segment. C51's statement to compare hashes is not an explicit read-only dry-run manifest proving no allocation or ref mutation. The production sequence in lines 919–925 has no post-cutover index rebuild/verified new GitHub issuance checkpoint or explicit owner reconciliation if unrelated live authoring prevents freeze. The design and master checkpoints require these distinctions (core design lines 168–172, 608–624; master plan identity continuity and C4/C6).

Identify dry-run CLI/manifest ownership, receipt schema/payload validation and their validator touch points. Test complete input/output and deviation inventory with no ref/identity mutation; fresh verification after cutover and a negative altered-declaration/receipt case; and replay through exact declared prefix, reviewed raw snapshots and regenerated views. In the separately authorized C6 handoff, name safe freeze preconditions and the readiness evidence including fresh clone/index rebuild and the master plan's first post-cutover GitHub issuance/reconciliation checkpoint. Keep that live provider proof in M2/C6 and leave the current task limited to planning and disposable fixtures.

### R1-F009 — Medium — Sequence release qualification around the delivered artifact

The common cycle requires a leaf's tests before its implementation commit and passing source review (lines 68–76), while C53's test names the built/released artifact and its touched files introduce the release workflow and package metadata that produce it (lines 876–888). The plan distinguishes local wheel smoke from actual release evidence (line 917) but gives no executable order separating the two proofs. A leaf cannot require the release containing its own workflow as a pre-delivery test artifact.

Separate C53's source-delivery checks on a candidate artifact from later authorized publication and post-publication qualification. Name the owner and evidence for testing the exact released hash/version from a clean disposable consumer on the required platforms, with replay of the applicable scenarios. State that the released package checkpoint stays pending until that result and delivered tutorial/rationale are recorded. This is planning of the release gate; it supplies no present release or adoption authority.

## Required changes

Address R1-F001 through R1-F009 in the plan and keep the table, leaf details, execution order and acceptance coverage consistent. Preserve the owner-open choices, original Refine history and separate M1 release/C6 adoption authority.

## Optional suggestions

- Carry a short likely-defect note into the eventual issue ledger when a leaf's existing risk note is broader than the failure it is meant to catch. The accepted plan need only provide that information once per leaf.
- Cite the current applicable procedure by its documented local path and precedence. The interim strategy retains a historical pre-XPR stop instruction for the core design; the current scoped assignment separately authorizes the plan's ordered levels.

## Decision

**revisions-requested**

The next round reviews the full revised candidate and every author disposition.
