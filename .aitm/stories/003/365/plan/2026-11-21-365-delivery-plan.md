# #365 Scheduled failure flag writer implementation plan

**Goal**

Persist the latest qualifying scheduled sweep decision, with a durable watermark that makes repeat or delayed notification safe.

**Scope**

[Story](../story.md), [epic plan](../../362/plan/2026-11-21-362-delivery-plan.md), and the accepted #363 and #364 receipts when available. Target `trunk`. This plan proposes file names and an implementation around the dedicated-issue store. Resolve the receipt-dependent decisions at JIT before editing source or provisioning the store.

**Files**

- `tools/ci/scheduled_sweep_flag.py` for provider reads, pure decision logic, record validation and the writer entry point.
- `tools/ci/tests/test_scheduled_sweep_flag.py` for decision, provider, persistence and workflow boundary checks.
- `.github/workflows/scheduled-sweep-flag.yml` for the separate publisher.
- `tools/ci/category_sweep_catalog.tsv` for exact node IDs and host classification.
- `docs/ci.md` for operator reconciliation, limitations and recovery.

## Tasks

- [ ] Verify both receipt PRs landed after Grok review, and reconcile their evidence and storage contracts for the ordering key, baseline and unavailable-state behavior. Pin those contracts, the live target, branch and canonical CI route. Define a pure transition that accepts an existing validated record and authenticated ordered run evidence and returns a replacement or no change. Expose record parsing and URL derivation for #366. Confirm the trusted `GitHub` read helpers in `tools/ci/verify_pr.py` are reusable without inheriting #103-specific authority.
- [ ] Write tests for a first failure, newer failure, later verified scheduled success, same-run rerun, older delivery after clear, duplicate delivery, missing or contradictory attempt evidence, cancellation and wrong repository/workflow/event/branch. Run `uv run --project packages/aitm-usage --locked --python 3.13.9 python -m pytest tools/ci/tests/test_scheduled_sweep_flag.py -q` in the repository's CI tools environment and observe the expected implementation failures.
- [ ] Implement authenticated history reconciliation. Under one writer concurrency group shared by completion and manual events, re-read the persisted watermark and verify candidate run identity via the Actions REST API. Compute the latest eligible decision from the complete relevant range rather than taking the trigger's arrival order as authoritative. A newer known non-decisive result preserves the prior verified decision. If a newer candidate or range cannot be authenticated, fail the write and leave the stored record intact. Keep a watermark on clear. Provision the agreed issue once with an explicit uninitialized marker and pin its number and immutable ID in the workflow contract. Refuse writes to an unexpected target, and reconcile a lost response by readback before any retry.
- [ ] Add a separate `workflow_run: completed` listener for the named workflow and an operator `workflow_dispatch` reconciliation from trusted `trunk`. Treat the event as a wake-up hint. Use explicit minimal permissions, trusted default-branch code, fixed API routes and a dedicated write target. Keep privileged execution away from watched-run code and downloaded artifacts. Have the job visibly report publication failures. Demonstrate that a dropped completion can be recovered by the next reconcile or operator invocation, and document the interval during which the previous result may still be shown.
- [ ] Run the focused tests, `actionlint` on the publisher, category catalog reconciliation for changed tests on both profiles and a controlled provider/store replay using an isolated record and no production write. Cover history pagination or concurrent change, missing or malformed record, failed or ambiguous write, stale watermark and readback. Record the focused test result separately from the canonical CI result because the governed helper lane enumerates its modules. Verify the existing CI and sweep routing through file review and canonical PR validation.
- [ ] Open the story PR. Require canonical CI, the trusted verifier and independent Grok PR review for the exact current candidate. After merge, validate deployed reconciliation and record readback using existing authentic eligible scheduled history. Record the actual trigger and source of the readback. Controlled replay supplies the evidence for failure then clear without intentionally failing the live sweep. Sign off and close before #366 enters Dev.
