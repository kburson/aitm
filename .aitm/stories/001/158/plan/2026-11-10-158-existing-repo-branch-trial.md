# #158 Stop the Line trial in the AITM repository

**Bounded evidence.** GitHub enforced an exact-branch stop for a fresh
direct push after rule activation. The same repository actor could
advance the branch before activation. Full #158 qualification remains
held and #159 stays in Backlog. The [approved trial
scope](2026-11-10-158-existing-repo-qualification-proposal.md) is pinned
by the raw SHA-256 in the [measurement receipt](../attachments/2026-11-10-158-existing-repo-branch-trial.json).

## Hosted result

| Step | Observation |
| --- | --- |
| Open | In repository `kburson/aitm` (ID `1450406435`), `kburson` advanced the temporary ref `refs/heads/aitm-qualify-158/ND9aWlcq/target` by a normal fast-forward Git push. Git and REST returned the new tip `81a9e37cc168236e47f8e148a5e39e24f19581dd`. The synthetic history held one inert text file and no workflows. |
| Activate | A local simulated scheduled-failure marker preceded the ruleset create call. GitHub returned HTTP 201. Active ruleset `27005244` matched that exact ref and applied `Restrict updates` with an empty bypass list. GitHub's effective-rules API returned that rule on the temporary ref. |
| Deny | The same actor attempted the same kind of fast-forward with candidate `adae824bd3bdc1f176e0c619c74e16528cfc6ded`. GitHub returned `GH013` and `Cannot update this protected ref.` Rule suite `5037309333` recorded a failed `update` evaluation from ruleset `27005244` and the exact attempted transition. Git and REST confirmed the tip stayed at `81a9e37cc168236e47f8e148a5e39e24f19581dd`. |
| Teardown | The ruleset delete returned HTTP 204. Git confirmed deletion of the temporary ref, and the API reported zero effective rules for it. The full `trunk` and `planning` ruleset definitions and their effective rules matched before activation, while active, and after teardown. The two production ref tips moved during concurrent work. The trial's Git writes named only the temporary ref. |

The authenticated installation settings showed code write access for both
Claude and the ChatGPT Codex Connector. AITM's only active Actions workflow
had a `trunk` push trigger and a pull-request trigger. The repository
webhook and deploy key lists were empty. The branch-only trial created no
PR and Actions listed zero runs for the trial branch.

**Preflight deviation.** The coordinator proceeded with branch and
ruleset writes based on the published Claude scheduled-task trigger list,
which covers pull requests, releases, and issues. Claude's public GitHub
App manifest also subscribes to `push` and `repository_ruleset` and has
contents write access. Those subscriptions apply to the types of events
used in the trial. Actual app-side behavior for those events and for PRs
was unverified. The approved procedure called for holding setup under
that uncertainty. The direct-push measurement remains evidence of the
GitHub rule evaluation, with qualification held. [Claude scheduled-task
triggers](https://code.claude.com/docs/en/routines#supported-events)
· [Claude app manifest](https://api.github.com/apps/claude)
· [GitHub rule suites](https://docs.github.com/en/rest/repos/rules#get-a-repository-rule-suite).

## Qualification still outstanding

The coordinator ran and verified teardown after the terminal push denial.
The preflight record lacks an explicit pending-request custodian designation.

The simulated failure marker records a test input. It exercised no
deployed AITM admission, repair, or restart logic. Web and REST PR
merges, a separate automation identity, and an already-sent merge were
unrun. An already-sent merge needs host evidence of when it committed
or when the exact request became incapable of committing. The time
between a scheduled failure and effective rule activation remains
unqualified. Auto-merge was disabled and no merge queue rule applied.

The one-time [earlier spike](../attachments/github-merge-fence-spike.md)
and [verified cleanup](disposable-fixture-teardown.json) remain in
the record. That spike showed the REST merge endpoint rejecting a stale
head and accepting a stale base even when the candidate tree was
unchanged. The existing-repository push result leaves exact PR merge
admission, exclusive ordinary-writer control, and in-flight ordering
open. This trial used the existing AITM repository throughout.
