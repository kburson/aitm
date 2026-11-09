---
schema: "aitm.review-response/v0"
level: "sar"
story: 2
role: "author"
round: 1
artifact_path: ".aitm/stories/000/2/plan/core-implementation-plan.md"
artifact_base_commit: "f86dd7c1954215585dcbdbcc9bac0e7e490a1956"
artifact_digest: "sha256:07c9ec8e1f51c5c7b78bf4e7390fc50d6d461872f1a027bae884305e235f4765"
patch: "patch-001.diff"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6-astra"
  effort: "xhigh"
author_session: "01a1be2f-9c32-79b1-9385-b18044d32156"
session_identity_kind: "observed-session-id"
started_at: "2026-11-09T06:50:43Z"
submitted_at: "2026-11-09T07:00:04Z"
start_basis: "recorded"
finding_ids: []
answered_finding_ids: ["R1-F001", "R1-F002", "R1-F003", "R1-F004", "R1-F005", "R1-F006", "R1-F007", "R1-F008", "R1-F009"]
---

## Summary

Accepted all nine required findings and both optional suggestions. The plan now has 62 leaves / 194.5 implementation agent-hours (all ≤4 h), with the original 180 h Refine record unchanged. Stable C-keys are preserved; split leaves are inserted at their prerequisite position in the table.

## Finding dispositions

- R1-F001 accepted: C01 declares routing/refresh records and mandatory service ports before use; C54–C56 supply domain schemas/reducers before the backend consumes them. The production composition section names each owner/call site. C06 wires the validation gate, C07/C08 policy/refresh, C14 transaction write authorization, C12 init hooks and C43 sync/action retry, with shared touched paths and normal-entry-point tests. Missing wiring remains unavailable.
- R1-F002 accepted: C22 now precedes C21 and supplies pure build_graduation. C21 graduate_local constructs number, exact draft move, story, reciprocal relations and initial projection identity in one CAS/publication operation. No separate permanent local identity can escape. Failure-between-proposal/construction, shared losing CAS and lost ACK are explicit real-graduate tests; external issued-pending identity remains a distinct case.
- R1-F003 accepted: added full command/options-to-operation/leaf/adapter map. C18 owns Discuss, refresh/index; C26 persists design/plan acceptance; C27 owns attempt reconcile; C16 provides purpose/capability binding, C45 exercises deliverable binding and C61 produces evidence-only authority. C49 tests actual CLI surface rather than helper substitutes; planning validate belongs to C06.
- R1-F004 accepted: C28/C27 explicitly test absent-plan/unbound advisory Develop followed by same-attempt acceptance/binding/reconciliation. New C61 owns unchanged-source evidence-only reopen, new scoped generation, real missing-test admission/rerun, genuine later clock interval, forbidden mutations and stale/superseded generation refusals. C42 separates retained-proof reconstruction with unchanged stopped clock. C49/C50 exercise those public operations.
- R1-F005 accepted: C35 defines LaneAdapter and wires selection to managed executor and doctor/init. C36/C37 return the selected platform adapter; actual installed doctor/init/test under contained policy must prove confinement and receipt assurance or remain pending without fallback. Explicit captured-export policy is tested separately; no host-security change is allowed.
- R1-F006 accepted: split original C02 into envelope dispatch plus C54 lifecycle, C55 attempts/boundaries and C56 evidence/composition; split C24 into portable reconstruction plus C57 topology/assurance and C58 native lineage; split C52 into performance and C59 packaging/CI. Also proactively separate C42 signoff from C61 recovery and C45 spikes from C62 epics, applying the same bounded-deliverable principle. Revised total 194.5 h is a new Plan estimate, not a rewritten Refine estimate or measured actual.
- R1-F007 accepted: qualification commands now select the real collected suite files. Added scenario-to-test map for 8×50, two-clone expansion/test/promote/signoff and actual test-launch refusal, no-child reservation/late review rebuild, local-only admitted target mutation and crash recovery, explicit policy/platform and migration cases. C50 now depends on C35/C38/C42/C61; CI collects the named lanes and reports exclusions honestly. C24 patch replay is explicitly integration work, keeping Git subprocesses out of the pure unit budget.
- R1-F008 accepted: C46 owns real read-only dry-run and MigrationReceiptV1; C48 builds deterministic payload hash excluding its own receipt path and wires fresh-history validation; C51 tests no mutations and forged declaration/receipt/legacy-tail failures. C6 handoff names owner-reconciled freeze, fresh clone/index parity and first GitHub issuance/reconciliation under M2/C6 authority, with no present production change.
- R1-F009 accepted: C53 tests and delivers candidate release workflow/metadata/tutorials first. New C60 subsequently publishes that delivered source under later explicit release-task authority and verifies exact released hash/version on both platforms. C60's evidence harness is not falsely required inside its target release. C5 remains pending until post-publication proof; this task grants no release authority.
- Optional suggestions accepted: eventual issue ledger includes a likely-defect note from each concrete proof; procedure has its absolute local path and current-assignment precedence. The help file's historical stop wording has also already been superseded in its local record, separately from FUR review.

## Changes made

Full decomposition, dependencies, common contracts, CLI/production seams, qualification map and release/migration boundaries updated together. Routine module choices remain builder calls. No accepted design/architecture/master-plan content or original estimate was changed.

## Declined changes and rationale

None. Global policy, expansion/cap interpretation and later hosted/name choices remain open. Production adoption prerequisites are recorded without asking routine clarification.

## Verification

Checked all 62 stable keys, every dependency in topological table order, sum 194.5 h and ≤4 h per leaf, all current relative source links and Markdown whitespace. Reviewed interface ordering and owning CLI call sites against the accepted design. Patch 001 is the complete author delta; no implementation tests are claimed. Round 2 must review the full revised file, including new split leaves and qualification/CLI tables.
