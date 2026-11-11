# #158 proposed qualification in the existing AITM repository

**Draft for owner review before implementation.** This proposal replaces
the disposable-repository route for #158 after acceptance and independent
review. The [earlier spike report](../attachments/github-merge-fence-spike.md),
[rules and request evidence](../attachments/github-merge-fence-rules.json),
[independent review](reviews/spr-2026-11-10-endpoint-evidence.md) and
[teardown receipt](disposable-fixture-teardown.json) remain part of the record.
The observed merge API rejected a stale PR head and accepted a moved
target base. The proposed qualification must account for both results.

## Scope

Use the existing public kburson/aitm repository with a short-lived
test target and test PR heads under aitm-qualify-158/<run-id>/.
Seed only inert, synthetic Git history. Publish no credentials,
private traces, or production test data. Before creating a branch or
PR, check which Actions workflows and integrations could react to
the test events. Hold setup if an integration can write outside the
fixture or its behavior is unknown. Use a small local test driver
and recorded fixture results for the simulated scheduled failure.
The actual GitHub
branch update decisions must come from the host.

Keep all hosted writes within the named test refs, their PRs, and
temporary rulesets that match the **exact** test target. Snapshot the
effective protections and rule IDs for the test target, trunk, and
planning before the run, after installing the temporary rulesets,
and after teardown. Reject a rule with a broader pattern or one that
touches either production ref. Check for repository automation that
could write outside the fixture before proceeding. Record fixture
repository and ref identities on every request. The experiment's
write scope excludes trunk, planning, existing workflows, and
repository-wide settings.

The proposed approach begins with the existing rules administrator and
existing repository identities. It requires an ordinary identity that
can merge a passing fixture PR while the target is open, so its later
refusal exercises the stop. Before using a denial as evidence,
establish that the same actor and route could complete an equivalent
operation while open, with any required check and review supplied
by approved existing identities. Record an already-denied route
as a baseline denial and missing actors or evidence as unrun. For
this first stage, use a temporary ruleset restricted to the exact
test target, with **Restrict
updates** and an empty bypass list. Activate it for the stop. This
tests whether GitHub itself refuses updates on a protected test ref.
[GitHub rule targeting and bypass](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository)
· [Restrict updates](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets#restrict-updates).

## Acceptance cases

| Case | Evidence and decision |
| --- | --- |
| Open line | A passing test PR follows the allowed normal path. Establish the ordinary identity's ability to update the test target before the stop and pin the PR head, target base, and expected merge tree. |
| Stop before dispatch | Feed the simulated scheduled full-suite failure to the driver. Hold a green PR at the final send boundary. Verify the stop invalidates its admission and that zero outbound merge requests leave after the stop. |
| Stop enforced by GitHub | Verify the new rule is active on the exact test target. Exercise an already-green PR through web and API, direct push, and any available automation. Record each host refusal and confirm the target SHA stayed fixed. Establish queue availability separately and mark unavailable cases explicitly. |
| Merge already sent | Use a controlled send barrier and durable request record. Determine whether GitHub had committed before the recorded stop, or provides conclusive evidence that the in-flight request could no longer commit. A timeout, a delayed response, or readback of an active ruleset alone leaves the case unresolved. Any ordinary merge landing after the recorded stop fails this route. |
| Base or head moves | Preserve the earlier stale-base case as a control. Repeat the condition against any proposed permitted merge route. Require exact admission and result identity at the host, with the approved base and head as the ordered parents and the tested tree as the result. |
| Repair and restart | Exercise the driver decisions with fixture evidence. Only the incident-bound repair with a complete passing suite and independent review can be eligible. Resume ordinary work after fresh full-suite success on the repaired target and verified updates from all enrolled test workspaces. A live repair merge requires a host path that preserves the stop for ordinary writers. |

## Qualification boundary and closeout

This first stage can establish same-repository GitHub enforcement once
the stop rule is active and exercise controller admission and restart
with test inputs. Full #158 qualification still requires proof of the
approved tree at the actual merge, exclusive control of ordinary target
updates, and ordering of a stop with a merge GitHub has already received.
The temporary rule toggle is a hypothesis for those guarantees. Keep the
original stop boundary and account for the time between recording a stop
and host enforcement. The only permitted write while an already-sent
request is unresolved is the named administrator's one planned
activation of the exact test target's stop rule. Record the stop
before activating that rule. Hold further experiment writes,
including repair, retry and teardown, until readback resolves the
request. Require a
host-observed ordering event or a terminal result tied to the exact
request. A client barrier and a provider request ID alone do not
prove a still-committable operation overlapped the stop.

Record a qualified receipt only if all required guarantees are
established. A demonstrated violation supports a refusal. A run
that proves only post-activation denial produces a bounded evidence
receipt. Missing setup or an inconclusive ordering test keeps full
qualification on hold. #159 stays held without a qualified receipt.

A dedicated GitHub App is deferred for this proposal. If a qualified
normal or repair path needs an exclusive writer identity, bring that
design back for review. A GitHub App installation token can cover
repository contents, so an exact branch ruleset alone does not make
such a token test-branch scoped. A later proposal must establish a
credible credential boundary before any grant. [GitHub installation authentication](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app-installation)

Capture exact rule readbacks, allowed and denied attempts, request and
ref identities, and the reason for every unrun case. Preserve the earlier
spike artifacts. Close only the test PRs and remove the exact temporary
rulesets and refs after all requests are terminal. Verify the original
trunk and planning protections by authenticated readback and retain
an independently reviewed evidence receipt on planning. Before the
trial, name the custodian who keeps the test branch fenced if a
request remains unresolved or rule scope drifts. Retain the fixture
until the custodian can verify terminal requests and safe cleanup.
Production cutover and successor pickup require their own acceptance.
