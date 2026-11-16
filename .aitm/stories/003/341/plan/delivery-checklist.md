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
- Head: `fcd1d745647ca24321b62558e9fd2d3c3c57d1ac`
- Hosted run: https://github.com/kburson/aitm/actions/runs/43824428689
- The workflow cancels a superseded pull-request run. A narrowed selection saves a full-suite stamp only after the full suite passes, and a later push with the same key does not start that suite. This head is mode full because the base has no map, so the stamp path is not exercised here.
- Independent reviewer: pending a green exact head
- The live full-once proof is a follow-up pull request after this candidate is on `trunk`.

## Checkpoints

- [x] 2026-11-16T07:30:47Z Develop, shared with #340.
- [x] 2026-11-16T07:31:54Z Test. Pull request 342 is the candidate. Hosted CI is in progress.
- [ ] Review after the required jobs pass on this head.
- [ ] Done after the amended-head proof, retrospective, and issue closure.
