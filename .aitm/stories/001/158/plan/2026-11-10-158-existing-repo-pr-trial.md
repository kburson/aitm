# #158 Stop the Line PR merge trial in AITM

**Disposition.** GitHub accepted the open-line controls and denied a
fresh synchronous REST merge once the stop rule was effective. In a
separate asynchronous trial, GitHub accepted the merge before the stop,
reported the same request as pending after activation, and then
reported a terminal rule denial. Both target refs stayed fixed during
the stopped attempts. Full #158 qualification remains held and #159
stays blocked. The [synchronous receipt](../attachments/2026-11-10-158-existing-repo-pr-trial.json)
and [asynchronous receipt](../attachments/2026-11-10-158-existing-repo-async-merge-trial.json)
retain candidate identities, timing, provider responses, and protection
snapshots.

## Claude and other automation

GitHub grants the installed Claude app write access to repository code
and pull requests. Its public app manifest subscribes to push, ruleset,
and pull-request events. The coordinator observed a signed-in Claude
Code Pro account with no scheduled tasks and automatic PR creation
off. Auto-fix was on. Anthropic documents auto-fix as monitoring a PR
attached to a Claude session. The fixture PRs were created by the REST
client and none was attached to a Claude session or mentioned Claude. Anthropic's
hosted Code Review feature requires a Team or Enterprise plan.
[Claude app manifest](https://api.github.com/apps/claude) ·
[Claude scheduled tasks](https://code.claude.com/docs/en/routines#supported-events) ·
[Claude auto-fix](https://code.claude.com/docs/en/claude-code-on-the-web#auto-fix-pull-requests) ·
[Claude Code Review](https://code.claude.com/docs/en/code-review#availability).

AITM had one active workflow. It had a `trunk` push trigger and a PR
trigger. The synthetic target and heads contained only `fixture.txt`,
with no workflow or Claude action. GitHub listed only the owner as a
collaborator and reported no repository webhooks or deploy keys. The
trial found zero reviews, issue or inline comments, head or candidate
check runs, or Actions runs on the fixture. Those observations cover
the configured and visible routes. GitHub limits access to the app's
private webhook delivery records to its owner and managers. The trial
did not observe Claude's internal event handling.
[GitHub App webhook delivery access](https://docs.github.com/en/webhooks/testing-and-troubleshooting-webhooks/viewing-webhook-deliveries).

## Synchronous GitHub merge measurements

All three PRs targeted only `aitm-qualify-158/8xxSJX4w/target` in the
existing `kburson/aitm` repository. The same owner OAuth actor made each
REST attempt with the expected head and merge-commit method. The
temporary ruleset `27005608` matched one literal ref and applied
`Restrict updates` with an empty bypass list. The coordinator was
recorded as pending-request custodian before the trial.

| Case | GitHub result |
| --- | --- |
| [Open control #214](https://github.com/kburson/aitm/pull/214) | HTTP 200 and `merged: true`. The landed Git object's ordered parents and tree matched the pinned GitHub test merge. The target advanced to `3987f6cf0aa72e64352b058b910c7a80b1069cb7`. |
| [Fresh merge #215](https://github.com/kburson/aitm/pull/215) | After an effective-rule readback, REST returned HTTP 405 and `Cannot update this protected ref.` GitHub rule suite `5037466737` recorded the failed `update` evaluation. The coordinator observed **Merge is blocked** in the web UI with the merge button disabled. Git and REST readbacks agreed that the target tip stayed fixed. |
| [Already-sent merge #216](https://github.com/kburson/aitm/pull/216) | The client's merge send call completed while the rule was disabled. The client then recorded the stop and sent one exact-rule activation. Activation returned HTTP 200 first. The original merge returned HTTP 405 with the rule violation about 1.06 seconds later. Rule suite `5037489739` recorded a failed evaluation of the active rule. The PR remained open and unmerged until cleanup. Git and REST returned the same unchanged target SHA. |

The terminal response settles the exact synchronous request. The
client's send completion leaves the time GitHub accepted it into merge
processing unobserved.

## Asynchronous GitHub merge measurements

This follow-up used a new temporary target
`aitm-qualify-158/fwFtz9AY/target` in the same repository, with the same
actor and preflight. GitHub's `merge-async` endpoint accepts background
work before it checks rulesets. The trial requested a direct merge
with the expected head and `bypass_rules: false`.
[GitHub async submission](https://docs.github.com/en/rest/pulls/pulls#merge-a-pull-request-asynchronously)
· [GitHub async result](https://docs.github.com/en/rest/pulls/pulls#get-the-result-of-an-asynchronous-merge).

- [Open control #217](https://github.com/kburson/aitm/pull/217) returned
  HTTP 202 and resolved to `merged`. The actual merge's ordered parents
  and tree matched the pinned candidate. It advanced the target to
  `0ece4d4d82e2eb1531b1dea1dfd8dad705a5262f`.
- [Accepted merge #218](https://github.com/kburson/aitm/pull/218) returned
  HTTP 202 and `pending` for request
  `899fa09c-6540-4cf2-b024-2cfbc9e3c1e1` while the rule was disabled.
  The client recorded the simulated stop after receiving that response
  and sent one activation of exact-branch rule `27005821`.
- After GitHub returned HTTP 200 for activation, a result read for the
  same UUID still returned `pending`. The next result read returned
  terminal `failed` with `Cannot update this protected ref.` Rule
  suite `5037587674` recorded the active rule's denial. Git and REST
  agreed that the target stayed at the open control's SHA. The PR
  remained unmerged.

The async trial establishes that this request was accepted by GitHub
before the stop, was still pending after the activation response, and
could no longer commit after the terminal rule denial. It supplies no
timing guarantee for a background job that has already passed the
host's update check when the stop is recorded. The synchronous and
asynchronous REST contracts supply an expected-head input. Exact-base
admission, exclusive normal and repair writers, and the deployed
controller's stop behavior remain unqualified. The [original endpoint
spike](../attachments/github-merge-fence-spike.md) showed the
synchronous endpoint accepting a moved base.
[GitHub synchronous merge contract](https://docs.github.com/en/rest/pulls/pulls#merge-a-pull-request).

## Teardown

The coordinator reconciled each already-sent request and target ref
before any cleanup writes. Both temporary rulesets and all seven test
branch refs were removed. The three rejected PRs were closed unmerged.
The full definitions and effective rules for `trunk` and `planning`
matched across all ten snapshots. Both test namespaces had no branch
refs after cleanup. The [direct-push trial](2026-11-10-158-existing-repo-branch-trial.md)
and original spike remain in the record. #158 stays in Planning and
#159 stays blocked pending a qualified receipt.
