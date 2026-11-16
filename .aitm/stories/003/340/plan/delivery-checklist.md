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
- Superseded head: `fcd1d745647ca24321b62558e9fd2d3c3c57d1ac` (run https://github.com/kburson/aitm/actions/runs/43824428689, tested merge `8e22acfca5b116dbedb298f0ed62d9de68e1c2de`)
- Head: `a80b4420b9715d3a5716e497293b29322197cb65`
- Hosted run: https://github.com/kburson/aitm/actions/runs/43828790092 attempt 1, conclusion success, event pull_request, head `a80b4420b9715d3a5716e497293b29322197cb65`
- Tested merge: `2e813389fced0787b94410d235f3d1678d34503c` (parents base `755fa2ece56cfa8c70a460b269d947ec6e958b2f` and head `a80b4420b9715d3a5716e497293b29322197cb65`)
- Required jobs, all success: `python-base`, `python`, `quality`, `file-checks`, `collect-evidence`, `aitm-ci`
- Signed candidate `aitm.ci-candidate/v2` on the replacement head: selection mode `full`, source `absent`, 1517 tests, 1516 baseline tests, passed, no failures. `aitm-ci` finished 2026-11-16T08:16:54Z.
- This head still changes the workflow and `tools/ci/`, so the base has no path map. Source `absent` is the control-path result. The base-lane fetch is not executed on this run. The mapped live check is a later pull request whose base contains this map.
- Independent reviewer: separate Grok review. Head `fcd1d745647ca24321b62558e9fd2d3c3c57d1ac` failed on 2026-11-16. Record: `plan/reviews/2026-11-16-head-fcd1d745.md`. Native GitHub review absent. Review of head `a80b4420b9715d3a5716e497293b29322197cb65` passed on 2026-11-16. Record: `plan/reviews/2026-11-16-head-a80b4420.md`. Native GitHub review absent. Trunk `verify_pr` status pass at 2026-11-16T08:26:49Z for reviewed tree `bc7d2e7909177a68325050b45e35a70bc0959345`.
- Merge: https://github.com/kburson/aitm/pull/342 merged 2026-11-16T08:27:35Z as `625b5407978675ac3b906990c8bb0713dcae18fd`
- Merge parents: `755fa2ece56cfa8c70a460b269d947ec6e958b2f` and reviewed head `a80b4420b9715d3a5716e497293b29322197cb65`
- Merge tree: `bc7d2e7909177a68325050b45e35a70bc0959345`, the same tree `verify_pr` reviewed
- Method: merge commit. `origin/trunk` reads back as that commit.

## Checkpoints

- [x] 2026-11-16T07:30:47Z Develop. Branch `story/340-341-path-map` commit `fcd1d745647ca24321b62558e9fd2d3c3c57d1ac`.
- [x] 2026-11-16T07:31:54Z Test. Pull request 342 opened into `trunk`. Head and base read back. Hosted CI run 43824428689 is in progress on that head.
- [x] 2026-11-16T07:39:40Z Required jobs passed on head `fcd1d745647ca24321b62558e9fd2d3c3c57d1ac`. `aitm-ci` finished at that time.
- [x] 2026-11-16T08:08:10Z Review of head `fcd1d745647ca24321b62558e9fd2d3c3c57d1ac` failed. Returned to develop. Replacement head `a80b4420b9715d3a5716e497293b29322197cb65`.
- [x] 2026-11-16T08:16:54Z Required jobs passed on the replacement head. `aitm-ci` finished at that time.
- [x] 2026-11-16T08:26:49Z Review of head `a80b4420b9715d3a5716e497293b29322197cb65` passed. Trunk `verify_pr` status pass for reviewed tree `bc7d2e7909177a68325050b45e35a70bc0959345`.
- [x] 2026-11-16T08:27:35Z Merged to `trunk`. The merge tree is the reviewed tree.
- [x] 2026-11-16T08:39:41Z Mapped proof passed on pull request 343. Run https://github.com/kburson/aitm/actions/runs/43831676598 selected `packages/aitm-usage/tests/test_grok.py` from the base map, ran 33 tests, wrote `base-skip.json`, and passed trunk `verify_pr` at 2026-11-16T08:37:29Z. The proof pull request was closed without merge.
- [x] 2026-11-16T08:40:42Z Retrospective `retro/2026-11-16-delivery.md`.
- [ ] GitHub issue closure read back.
