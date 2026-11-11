# #158 Exact base, merge writers, and the Stop the Line boundary

**Disposition.** The native async merge route failed exact-base
enforcement. A PR-only rule distinguished allowed and denied routes
for a named user. The trial left distinct-writer enforcement and the
host's post-check interval unqualified. #158 stays in Planning and
#159 remains blocked. The [measurement receipt](../attachments/2026-11-11-158-merge-boundary-trial.json)
records the exact commits, responses, rule evaluations, and cleanup.

## Exact base

| Case | GitHub result |
| --- | --- |
| [#223 · Native async merge](https://github.com/kburson/aitm/pull/223) | The target advanced from `5d3b8ba` to `cce149d`, an ancestor of the unchanged head `49bcf60`. GitHub generated the same tree on both bases. The head-conditioned async request returned 202 and then `merged`. Git proved the landed first parent was `cce149d`, the moved base. |
| [#224 · Strict required status check](https://github.com/kburson/aitm/pull/224) | A fixture-only passing status on the old test-merge commit did not satisfy the strict rule after the target moved to an ancestor of the same head. The async request failed and the target stayed fixed. With the same rule still active, a passing status on the unchanged head allowed the merge even though the current test-merge commit had no passing status in that context. |
| [#225 · Status on the current test-merge commit](https://github.com/kburson/aitm/pull/225) | The coordinator published the synthetic status on the current test-merge commit and verified it was absent on the head. The synchronous connector merge still returned HTTP 405 for the missing required check. The test-merge ref later had a different commit with the same ordered parents and tree. This case did not establish a usable exact-test-merge status route. |

The strict setting checks whether the head includes the current base.
It permits the documented head-status fallback when the current
test-merge commit has no status. The fixture check came from the
repository owner, with no dedicated status publisher. The async
request and GitHub's live GraphQL merge input expose an expected
head. Neither exposes an expected base.
[GitHub async merge contract](https://docs.github.com/en/rest/pulls/pulls#merge-a-pull-request-asynchronously)
· [GitHub status selection](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks#conflicts-between-head-commit-and-test-merge-commit).

## Exclusive merge writers

GitHub attributed the connector's successful open merge of #225 to
`kburson`. The CLI authenticated as the same user, and the repository
listed no other collaborator. The test exercised distinct routes
under one principal.

A temporary `Restrict updates` ruleset for the one literal target
named `kburson` as its sole PR-only exception. On [#226](https://github.com/kburson/aitm/pull/226),
GitHub refused the direct Git push with GH013 and the direct REST
ref update with HTTP 422. Both carried the pinned test-merge commit.
An async PR merge with `bypass_rules: false` also failed and the ref
stayed fixed. The explicit PR-only merge succeeded with the approved
parents and tree. Rule suite `5045391981` recorded the bypass.
Independent enforcement against a second write-capable principal
remains untested. [GitHub PR-only exceptions](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository).

## After GitHub's update check

**Unrun.** No public surface examined exposes a checkpoint for an
identified request after it passes GitHub's final ref-update check
and before it can commit. Async acceptance occurs before the rules
run. The async result returns `pending` or a terminal result without
a check-stage field. The live GraphQL fields and timeline expose
mergeability and completed merge information. The ruleset records
observed in this trial are outcomes of attempts. An activation timed
only against any of those signals could not establish the requested
ordering.

The [prior async trial](2026-11-10-158-existing-repo-pr-trial.md)
proved that one accepted pending request reached the active rule and
failed. Its denial leaves the later interval unverified.
[GitHub async result](https://docs.github.com/en/rest/pulls/pulls#get-the-result-of-an-asynchronous-merge)
· [GitHub rule insights](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/managing-rulesets-for-a-repository#viewing-insights-for-rulesets).

## Scope and cleanup

The four PRs and two rulesets used one temporary target in the
existing AITM repository. The coordinator rechecked Claude's visible
settings before setup. There were no scheduled tasks. Auto-fix was
enabled and none of the fixture PRs was attached to a Claude session.
The fixture emitted only synthetic test statuses and showed no
app reviews or comments, head check runs, or Actions runs in the
post-trial readback.

All five async requests reached terminal results before teardown of
their respective test phases. The four PRs were closed by their
measured merges. Both exact-target
rulesets and all five test branch refs were removed. The full
ruleset definitions and effective rules for `trunk` and `planning`
matched across five snapshots. The original spike and prior
same-repository trials remain in the record.
