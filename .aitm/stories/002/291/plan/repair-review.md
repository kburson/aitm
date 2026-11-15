# #291 independent premerge SAR for the nominated disposable repair

**Verdict: ACCEPTED for one simulated operator repair on the disposable target.** Signed by OpenAI Codex, independent review agent `/root/review148`. This verdict binds the nomination SHA-256 `4d8e1dc9da0dbd00d414cfc86cb21fe51939dfc7220714a665334b03f684db62`. [Exact repair nomination](repair-nomination.json)

| Evidence | Verified value |
| --- | --- |
| Repository | `kburson/aitm-stl-rehearsal-291`, ID `1458821034` |
| Pull request and target | [PR #1](https://github.com/kburson/aitm-stl-rehearsal-291/pull/1), held default `trunk` |
| Held base | `9a3962d81309e44f08a522b155bf3f83078ec640` |
| Exact repair head | `d094a105a01b771a063bb856eb8c36de93bc3ade` |
| Hosted tested merge | `c64d14e0dd982f141e3a7a55f22c76824e20a05c` |
| Exact repair and tested tree | `bb1b9a683e1c3cf4668a3bdcdcce99c24ee1115b` |
| Green CI | [Run 43718593693, attempt 1](https://github.com/kburson/aitm-stl-rehearsal-291/actions/runs/43718593693/attempts/1), suite `118363475725`, job `132825400991`, Actions app `15368` |

GitHub still reports the nominated PR open and protected `trunk` at the held base. The repair restores `fixture=healthy` and adds a synthetic nomination note. Both workflow blobs are unchanged. The tested merge has the base and the repair head as its ordered parents and the exact repair tree. GitHub's check suite identifies PR #1 and this base and head. The job log verifies checkout of the tested merge and successful execution of `fixture-ci`. The previous repair head `342a7ec0e63dc5d271d93dc52207c7bb28506dc5` failed `fixture-ci`, and the simulated operator merge was refused because the check failed. [Operator red refusal](operator-red-refusal.log)

Normal ruleset `27314376` is active on `refs/heads/trunk`, requires a pull request and a strict `fixture-ci` check from Actions app `15368`, allows merge commits, and lists zero bypass actors. Its GitHub approval count is zero. This signed exact-head SAR supplies the rehearsal's independent review. Hold ruleset `27314377` is active on the same literal ref and restricts updates. The only listed bypass is user `kburson` (`1082467`), for pull requests only. This account's direct push was refused. [Normal rules readback](normal-rules.json) · [Hold rule readback](hold-rule.json) · [Operator push refusal](operator-push-refusal.log)

The ordinary rehearsal job used its repository-scoped Actions token with contents and pull-request write permissions. Its healthy control PR #2 passed the required app's check on exact head `fafa34799c4b3f546813a2ef66a37a8ec36028fe`. The probe created unheld ref `agent-proof-43718586152` at that head. GitHub refused the ordinary push with `GH013` and the ordinary merge with HTTP 405, both explicitly reporting that the protected ref cannot be updated. The ruleset edit returned HTTP 403, `Resource not accessible by integration`. The held branch SHA stayed unchanged. [Ordinary probe run 43718586152, attempt 1](https://github.com/kburson/aitm-stl-rehearsal-291/actions/runs/43718586152/attempts/1)

GitHub grants the simulated operator's exception for eligible pull requests on the held branch. The exact nomination and expected-head merge bound use of that credential to PR #1 at the reviewed head for this experiment. Authority for any later action, real human approval, and production credential separation remain outside this premerge review. The three effective production `trunk` rules matched the baseline. After the simulated repair, the rehearsal still requires proof of hold persistence, stale-evidence refusal and fresh evidence with explicit acknowledgment before any release on the disposable ref. [GitHub ruleset documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository) · [#291](https://github.com/kburson/aitm/issues/291) · [#103](https://github.com/kburson/aitm/issues/103)
