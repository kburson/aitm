# Delivery checklist #340

- Story: #340 Make a coarse path map the required PR check
- Implementing agent: Grok, on behalf of kburson
- Closure owner: Grok, on behalf of kburson
- Attempt: 1, 2026-11-16
- Accepted scope: `.aitm/stories/003/340/story.md` and the replacement plan `.aitm/stories/001/133/plan/2026-11-16-133-pr-feedback-replacement.md`
- Dependencies: none
- Parent target: `trunk`
- Pinned base: `755fa2ece56cfa8c70a460b269d947ec6e958b2f`
- Story branch: `story/340-341-path-map`
- Pull request: https://github.com/kburson/aitm/pull/342
- Head: `fcd1d745647ca24321b62558e9fd2d3c3c57d1ac`
- Hosted run: https://github.com/kburson/aitm/actions/runs/43824428689 attempt 1, conclusion success, event pull_request, head `fcd1d745647ca24321b62558e9fd2d3c3c57d1ac`
- Tested merge: `8e22acfca5b116dbedb298f0ed62d9de68e1c2de` (parents base `755fa2ec` and head `fcd1d745`)
- Required jobs, all success: `python-base`, `python`, `quality`, `file-checks`, `collect-evidence`, `aitm-ci`
- Signed candidate `aitm.ci-candidate/v2`: selection mode `full`, source `absent`, 1517 tests, 1516 baseline tests, no failures
- This head changes the workflow and `tools/ci/`, so the base has no path map. Source `absent` is the control-path result. The mapped live check is a later pull request whose base contains this map.
- Independent reviewer: separate Grok review of head `fcd1d745647ca24321b62558e9fd2d3c3c57d1ac`. Verdict fail on 2026-11-16. Record: `plan/reviews/2026-11-16-head-fcd1d745.md`. Native GitHub review absent.
- Replacement head: `a80b4420b9715d3a5716e497293b29322197cb65`. Fresh hosted CI and a new review are required on that head.
- Merge, retrospective, and closure: pending

## Checkpoints

- [x] 2026-11-16T07:30:47Z Develop. Branch `story/340-341-path-map` commit `fcd1d745647ca24321b62558e9fd2d3c3c57d1ac`.
- [x] 2026-11-16T07:31:54Z Test. Pull request 342 opened into `trunk`. Head and base read back. Hosted CI run 43824428689 is in progress on that head.
- [x] 2026-11-16T07:39:40Z Required jobs passed on head `fcd1d745647ca24321b62558e9fd2d3c3c57d1ac`. `aitm-ci` finished at that time.
- [x] 2026-11-16T08:08:10Z Review of head `fcd1d745647ca24321b62558e9fd2d3c3c57d1ac` failed. Returned to develop. Replacement head `a80b4420b9715d3a5716e497293b29322197cb65`.
- [ ] Fresh required jobs on that replacement head.
- [ ] Fresh review verdict on that same passing head.
- [ ] Done after merge, the mapped proof, retrospective, and issue closure.
