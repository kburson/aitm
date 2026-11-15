# #291 Human-operated trunk hold rehearsal

Rehearse a trunk-only merge hold on a disposable GitHub repository with synthetic fixture content. The available private test repository cannot use GitHub rulesets on its current plan. Use a newly created public disposable target containing only the rehearsal fixture and workflows. Preserve the repository and exact provider logs as evidence. All production repository settings remain as deployed.

## Provider experiment

- [ ] Establish normal pull-request and mandatory CI rules for the disposable `trunk`. Validate one intentionally failing repair through the normal path, then validate the exact nominated repair candidate and get an independent agent review of its source, CI and evidence binding.
- [ ] Add a separate `trunk`-only restrict-updates ruleset. Give only the designated rehearsal operator account a pull-request-only exception. Run the ordinary client under a repository-scoped GitHub Actions token without administration. Prove native refusals for a direct push, an ordinary merge, and a rule edit. Prove the same credential can update an unheld ref.
- [ ] Bind the simulated operator's one authorization to the exact repair PR and head. Use the disposable repository's normal CI and independent review. Test that the hold persists after the repair and an ordinary merge remains refused. The experiment's administrative operator and workflow client are separate credential roles. No claim of a real human approval or of production credential separation follows from the simulated operator action.
- [ ] Exercise stale green versus the repaired SHA using the existing #279 shadow recovery store. Even exact current green requires explicit operator acknowledgment. Record the stale refusal, fresh run and removal of the hold on the disposable ref only.
- [ ] Get independent review of the verified branch outcomes, exact repair, actor separation, stale evidence and protection snapshot. Use those findings for the separately reviewed production cutover decision in #294.

[GitHub repository rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets) · [Protected PR-only bypass](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository)
