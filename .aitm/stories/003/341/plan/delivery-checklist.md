# Delivery checklist #341

- Story: #341 Run the short check on every push and the full suite once
- Implementing agent: Grok, on behalf of kburson
- Closure owner: Grok, on behalf of kburson
- Attempt: 1, 2026-11-16
- Accepted scope: `.aitm/stories/003/341/story.md`
- Dependency: #340, same candidate
- Parent target: `trunk`
- Pinned base: `755fa2ece56cfa8c70a460b269d947ec6e958b2f`
- Story branch: `story/340-341-path-map`
- Pull request: https://github.com/kburson/aitm/pull/342
- Superseded head: `fcd1d745647ca24321b62558e9fd2d3c3c57d1ac`
- Head: `a80b4420b9715d3a5716e497293b29322197cb65`
- Hosted run: https://github.com/kburson/aitm/actions/runs/43828790092 attempt 1, conclusion success, head `a80b4420b9715d3a5716e497293b29322197cb65`
- Tested merge: `2e813389fced0787b94410d235f3d1678d34503c`
- The workflow cancels a superseded pull-request run. A narrowed selection saves a full-suite stamp only after the full suite passes, and a later push with the same key does not start that suite. This head is mode full because the base has no map, so the stamp path is not exercised here. The full-once steps on run 43828790092 were skipped.
- Independent reviewer: the same off-platform fail on head `fcd1d745647ca24321b62558e9fd2d3c3c57d1ac`. Record: `../../340/plan/reviews/2026-11-16-head-fcd1d745.md`. Native GitHub review absent. A new review of the replacement head started 2026-11-16T08:17:36Z. Verdict pending.
- The live full-once proof is a follow-up pull request after this candidate is on `trunk`.

## Checkpoints

- [x] 2026-11-16T07:30:47Z Develop, shared with #340.
- [x] 2026-11-16T07:31:54Z Test. Pull request 342 is the candidate. Hosted CI is in progress.
- [x] 2026-11-16T07:39:40Z Required jobs passed on the shared head.
- [x] 2026-11-16T08:08:10Z Shared review of head `fcd1d745647ca24321b62558e9fd2d3c3c57d1ac` failed. Returned to develop.
- [x] 2026-11-16T08:16:54Z Required jobs passed on replacement head `a80b4420b9715d3a5716e497293b29322197cb65`.
- [ ] Fresh review verdict on that same head.
- [ ] Done after the amended-head proof, retrospective, and issue closure.
