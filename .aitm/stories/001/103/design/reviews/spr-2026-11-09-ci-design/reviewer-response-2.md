# #103 manual independent Codex design SPR — round 2

Submitted UTC `2026-11-10T02:45:10Z`.

**Verdict: accepted. No required changes remain.**

## Review identity and coverage

- This is the declared independent, same-provider manual SPR, continuing round 1 in the same reviewer session. The separate native reviewer attempt failed with `APR_CODEX_HOOK_INVALID`. This verdict is a manual record and supplies no native approval.
- Reviewer context is Codex Desktop, `openai`, `gpt-6.1-sol`, high effort. The provider-qualified session fingerprint was independently rederived in this reviewer environment and matches round 1, `sha256:a3bb437a4264b6ad468ee66ea2fa72d26913b9712e2db7f6ecbf105ed0bbd287`. The digest input was the exact prefix `ai-peer-review.session/v1\nopenai\n` followed by the active reviewer session handle without an added newline. Model and effort are the recorded reviewer context, with no fresh native join attestation.
- Artifact is `.aitm/stories/001/103/design/github-ci-quality-gates-design.md`. Source commit `4e7d5708bb5628d7a6767d295fbf4eeacc72670b`. Raw SHA-256 `2506b3bb129e98ca936677c825513fee65f838a65e1c7625087ec091fba5a02e` matches both the file and the pinned commit. I reread contiguous lines 1–20, 21–40 and 41–48 to EOF with no omissions, and checked the durable round-one findings.

## Finding dispositions

1. **SPR-CI01 resolved.** Lines 15–17 bind passing evidence to the repository and expected workflow identity, PR, event and target, exact base/head and tested commit, run ID and attempt, and each required job. The aggregate must actually succeed in that same completed successful attempt. Skipped, neutral, cancelled, missing, ambiguous and wrong-workflow evidence stays open. A whole-workflow retry produces a complete attempt. Lines 45–46 require positive identity evidence and negative cases. Any later check-source enforcement remains separately authorized. [GitHub required checks](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)
2. **SPR-CI02 resolved.** Line 19 requires exact ordered merge parents and a live head/target comparison both before review and before merge. It names the retarget `edited` activity and a story-branch update plus `synchronize` when the same base advances without an event. Old-event reruns and trunk-push evidence do not satisfy a fresh PR gate. Lines 23 and 45 require evidence on trunk and a representative declared integration target and a demonstrated fresh event after drift. [GitHub PR events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request) · [GitHub rerun identity](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs)
3. **SPR-CI03 resolved.** Line 40 pins a hosted Darwin runner label and requires documented capabilities for ACL, exclusive publication, writer lease and restart proof. Predeclared capability-dependent skips are distinguishable from skipped required evidence. An unexercised required case or unexpected skip blocks the aggregate even when all other lanes pass. A policy disposition records the gap without supplying a pass. Lines 23 and 46 limit bootstrap authorization to Before Develop preflight and require genuine Actions, at least 90% measured coverage, independent review and a missing-capability negative case. The story checklist still governs Review and merge.

## Remaining design assessment

- Lines 7–11 and 25–34 keep CI scoped to source PRs, the current Python package and document validation. TypeScript activates with the first actual package. Core wheel and release contracts and operational deployment/provider proof remain separate.
- Lines 38–41 and 47 retain the unrounded 90% product-line floor per active package, including unimported modules. The first gate requires meaningful behavior and recovery coverage. The full serial Darwin baseline, explicit test inventory, same-candidate coverage and measured cold/warm queue, setup, test and total durations give the later parallel work a comparison point.
- Lines 45–48 tie the evidence to individual review, merge and closure. This acceptance applies to the exact design bytes. Runner setup, actual CI execution and ruleset enforcement remain delivery evidence.
