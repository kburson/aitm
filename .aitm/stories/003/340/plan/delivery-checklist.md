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
- Hosted run: https://github.com/kburson/aitm/actions/runs/43824428689
- Required jobs: `python-base`, `python`, `quality`, `file-checks`, then `collect-evidence` and `aitm-ci`
- This head changes the workflow and `tools/ci/`, so the base has no path map. The run records selection source `absent` and must pass the full suite. That is the control-path result. The mapped live check is a later pull request whose base contains this map.
- Independent reviewer: pending a green exact head
- Merge, retrospective, and closure: pending

## Checkpoints

- [x] 2026-11-16T07:30:47Z Develop. Branch `story/340-341-path-map` commit `fcd1d745647ca24321b62558e9fd2d3c3c57d1ac`.
- [x] 2026-11-16T07:31:54Z Test. Pull request 342 opened into `trunk`. Head and base read back. Hosted CI run 43824428689 is in progress on that head.
- [ ] Review after the required jobs pass on this head.
- [ ] Done after merge, the mapped proof, retrospective, and issue closure.
