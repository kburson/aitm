# #104 GitHub binding probe · Attempt 1

**Disposition: binding failed. Return to Planning.** The hosted diagnostic completed successfully. GitHub's authenticated run and check records associated that attempt with the PR head. The observed fields did not independently bind the attempt to the synthetic merge tested by an ordinary PR workflow.

## Exact observed candidate

- [Bootstrap PR #107](https://github.com/kburson/aitm/pull/107), same repository and target `trunk`. Head `d34921e0dd604abb2af5b710031d8e4a85c76cee`. The only change is the diagnostic workflow. The PR is preserved as an open draft, unmerged.
- [Actions run 42749926303, attempt 1](https://github.com/kburson/aitm/actions/runs/42749926303/attempts/1). Workflow `412848571` at `.github/workflows/ci.yml`, event `pull_request`, check suite `115780508375`, diagnostic [job 129610875115](https://github.com/kburson/aitm/actions/runs/42749926303/job/129610875115).
- GitHub recorded run creation at `2026-11-10T03:30:52Z`, job start at `03:30:56Z` and completion at `03:31:00Z`. The hosted image was `macos-26-arm64` `20261102.0473.1`, macOS 26.7.2, Xcode 26.6 build 17F113. The diagnostic establishes basic runner availability. Full Darwin behavior qualification and the production tests were outside this attempt.
- Live base `f80f22645e2008c4cac9dc6e4003640bba976b5f`. The current PR merge ref and PR `merge_commit_sha` both named `e092c5f387db77d8eb7ac897f801f442097f6b6c`. The authenticated raw merge object has that base as first parent and the PR head as second parent. Its tree is `6f1c0801e6e63ae8706707393faf9fbdb076b13c`.

## Trust boundary

| Evidence read | Observation |
| --- | --- |
| REST run and exact attempt | `head_sha` and `head_commit.id` are the PR head. The associated same-repository PR number and event base/head agree with the live target/head. |
| REST check suite, attempt jobs and GitHub Actions check run | Every `head_sha` is the PR head. The attempt has one successful `binding-observation` job. |
| GraphQL check suite | `commit.oid` is the PR head. Its linked workflow run and attempt match the REST identities. |
| REST check suites and check runs queried on the synthetic merge SHA | Zero results for both. The equivalent head check query returned the diagnostic check. |
| Current PR and Git data | PR merge field and merge ref agree and the raw ordered parents match. These current values and the commit object do not identify which merge the selected attempt tested. |
| Candidate workflow output | `GITHUB_SHA` and `GITHUB_WORKFLOW_SHA` reported the same synthetic merge SHA. The event payload recorded the exact head and base and a null `pull_request.merge_commit_sha`. A candidate-authored log can corroborate the merge SHA. It cannot establish an independent binding. |

The runtime behavior and REST identities are separate pieces of evidence. GitHub documents the merge-ref meaning of `GITHUB_SHA` for ordinary PR workflows, while its check and run records observed here key this attempt to the PR head. The positive job result therefore has no `aitm-ci` meaning. [GitHub pull request event behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request) · [GitHub attempt job API](https://docs.github.com/en/rest/actions/workflow-jobs#list-jobs-for-a-workflow-run-attempt).

## Planning handoff

The unresolved requirement is an immutable, provider-owned association of the selected run ID and attempt with the exact tested merge. To resume, review any proposed replacement evidence route against that trust boundary, including stale target or head and rerun behavior. Refresh #104's JIT against the resulting reviewed plan before another Develop attempt.

Trunk stayed at its pinned commit. No production CI helpers, wheel, aggregate, integration proof refs or dependent leaf work began. The 90% line floors and meaningful behavioral-test requirement stay in the accepted scope.
