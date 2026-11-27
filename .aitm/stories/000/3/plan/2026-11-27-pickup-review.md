# #3 Pickup review

Grok 4.7 via Grok Build 1.0.92.

## Round 1

CHANGES REQUIRED

The #3 pickup adds a hosted Core pull-request job and keeps C01’s test-first contract, but the job is not an exact, Linux-only, first-workflow gate that can be required on the draft before Ready without blocking the integration branch or leaving C01’s owned paths.

### Target
The story base is the #470 integration branch, and the draft must record GitHub’s live base and head. The only SHA in the packet is trunk `a5ad6965c1c5b8817c0503dedbf55f576b5ddc67`. That pin is not the integration-branch base the PR is required to use.

### Exact CI evidence and the Linux check
C01’s local proof is Python 3.13.9, a pinned uv lock, and an installed wheel in an isolated child process. The new job only says it “pins Python and uv consistently with current CI” and “runs the locked Core test suite and Ruff.” It never names the runner, the current workflow’s Python or uv pin, or the exact commands. A first hosted Linux Core check is not specified as Linux or `ubuntu-latest`. Read-only permissions, a pull-request event, the synthetic merge candidate, and recording the event base, head, and tested commit are specified.

### First-workflow bootstrapping
The plan requires this new path-filtered job on the #3 draft into the integration branch, then has later story PRs reuse it, while current required suites stay in place. The workflow path is not on that base until #3 lands. A required check that exists only on the draft stays pending for every other pull request into #470. Path limits (Core source, tests, workspace, lock, workflow) make the same check skip with no success result on pull requests that do not touch those paths, so a branch-level requirement does not complete. The packet gives no always-reporting conclusion job and no order that merges the workflow onto #470 before the check becomes required for other stories.

### Scope ownership
C01’s touched-file list and “stated paths” contain package, test, lock, and pyproject files only. The workflow file is outside that contract. The pickup still assigns the job to #3. #69 and #71 keep cross-platform wheel and release workflow scope, but the new job has no single-OS bound, so its runtime scope is not held to a Linux Core suite.

### Delivery sequence
Passing hosted evidence is required before the draft leaves Ready, which matches a pre-Ready check. Independent Grok 4.7 SAR of that same input, including the bootstrap job, is requested only after the PR is taken out of draft. #8 owns final composition and trunk delivery, while #3 closes only after “verified landing,” so integration merge and trunk landing are one close condition.

## Round 2

CHANGES REQUIRED

Bounded C01 source work can start: failing tests, scaffold, typed envelope, ports, lazy catalog, and locked local pytest/ruff on 3.13.9. The new workflow is correctly out of #3, and local green does not count as hosted proof.

The stop is not consistent.

1. Reservation retargets shared `codex/core-470-integration` to trunk `a5ad6965` and then adopts whatever origin returns. Cut the story branch from the verified live integration SHA. Do not move that ref. Stop if the read-back SHA differs from the recorded pickup base.

2. The C01 “Verify and retain” box still completes source review and delivery evidence with the local pytest run. The preamble correctly delays SAR, undraft, and review until a reviewed hosted Core run passes on that exact candidate. Make the checklist the same gate: draft stays in Test until that receipt exists; drift refreshes the receipt before review.

3. Opening the epic promotion PR at the first diff is #8 trunk work and is not held for hosted proof. #3 may open only its own draft PR. Close #3 only after hosted receipt, SAR, delivery on the #470 integration branch, and signed evidence. Trunk promotion stays at #8.

## Round 3

PASS. The revised pickup leaves any existing #470 integration ref untouched, branches #3 only from the read-back SHA, and stops for reconciliation if that base differs. It splits the checklist into local proof, draft/Test, hosted proof, source review, and delivery, and it keeps the draft in Test until the reviewed hosted Core route passes for the exact base and head, with draft removal and SAR only after that receipt. #3 closes only after verified delivery on the #470 integration branch, while trunk promotion stays with #8.

Round 3 plan SHA-256 `da8ee38965a7604b480768e667f54e5b81e5b5c0b8715b8cec3727eb056586a0`.
