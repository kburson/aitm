# #363 Scheduled sweep identity implementation plan

**Goal**

Deliver a research receipt identifying the production run and the input rules the flag writer can rely on.

**Scope**

[Story](../story.md), [epic plan](../../362/plan/2026-11-21-362-delivery-plan.md), [#361 sign-off](../../361/retro/2026-11-21-361-sign-off.md). Target `planning`. Deliver the receipt and fixtures as planning evidence. The writer consumes the accepted contract in #365.

## Tasks

- [ ] Recheck GitHub's repository ID `1450406435`, default branch `trunk`, workflow ID `425235652`, path `.github/workflows/category-full-sweep.yml`, and the branch and event filters. Retrieve the exact attempt via `gh api repos/kburson/aitm/actions/runs/44864075824/attempts/1`. Compare the run and attempt IDs, `run_number` (4), event, source SHA and timestamp with #361. Record the exact attempt `reconcile` job and how a success is verified. Record a manual rehearsal and another workflow as negative examples.
- [ ] Define what #365 can accept. The proposed rule uses the original attempt of each distinct scheduled run, so a manual rerun cannot clear the warning. Order by the pinned workflow's `run_number` after validating run ID and attempt identity. Document the timestamp source and meaning. Set the activation floor using the verified #361 baseline. Specify how a newer qualifying failure refreshes an existing warning and how publisher events are rejected. Assess failure and timeout as warning candidates, and require successful same-attempt reconciliation for clearance. Record how cancellation, pending runs, missing slots, mismatched or absent evidence, and unknown conclusions are handled. Check that the contract survives normal retention and API errors.
- [ ] Write a small outcome table with authentic successful evidence and synthetic failure, late delivery, rerun, incomplete and unrelated cases. Note any constraints from the [workflow runs API](https://docs.github.com/en/rest/actions/workflow-runs) and [workflow jobs API](https://docs.github.com/en/rest/actions/workflow-jobs). Resolve the exact evidence and ordering policy in the receipt.
- [ ] Open the receipt PR. Obtain independent Grok PR review on its current head and record accepted delivery before #365 starts.
