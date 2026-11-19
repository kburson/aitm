# #376 portable launcher delivery

[PR #369](https://github.com/kburson/aitm/pull/369) merged at `1decd7c613898eb9442a96a4e0163e87c4eca6cc`. Its [Ubuntu trunk run](https://github.com/kburson/aitm/actions/runs/44525506404) and exact Darwin advisory replay passed before #355 closed. [#355 sign-off](../../355/retro/2026-11-19-355-delivery.md).

1. Verify private mode bits, `O_NOFOLLOW`, and exclusive rename in scratch without executing candidate product Python in the controller. Resolve Git on PATH and preserve the snapshot reader's mandatory offline controls.
2. Use a portable suite covering the current product modules and all six Ubuntu helper test targets. Keep Darwin's exact procfs skip handling local and scoped by node and reason. Remove the retired firmlink skip from hosted policy.
3. Read the Ubuntu baseline runtime and image from authenticated evidence. Keep historic Darwin evidence support. Preserve a reported filesystem value if the raw authenticated capability records one. The frozen #377 workflow records OS, runtime and image and omits filesystem. Do not infer the runner filesystem from a separate machine.
4. Keep the hosted workflow and selector bytes, and review the exact changes that preserve the #354 anchor and release scope. Verify the actual launcher and #355 advisory on both platforms, run trusted CI, then replay the delivered trunk commit before closing #376 and its parent.

## Hosted verification

[PR #382 attempt 1](https://github.com/kburson/aitm/actions/runs/44527861244/attempts/1) passed both Python lanes, quality and file checks. The base used `ubuntu24:20261116.133.1` and the candidate used `ubuntu24:20261111.370.1`. Replaying the collector on the original artifacts reproduced the sole failure `missing or drifted trusted base identity`. The two selection documents were identical. Product coverage was 14,738 of 16,252 lines and helper coverage was 1,042 of 1,114. The full workflow was rerun on the same refs to obtain fresh producer evidence without weakening the identity check.

[Attempt 2](https://github.com/kburson/aitm/actions/runs/44527861244/attempts/2) passed all test and quality jobs and again held only on runner image. The base used `ubuntu24:20261111.370.1` and the candidate used `ubuntu24:20261111.127.1`. [Attempt 3](https://github.com/kburson/aitm/actions/runs/44527861244/attempts/3) passed 1,524 candidate behavior tests and failed the unchanged `test_committed_pair_conflict_stalls_affected_source_without_regressing_history[v4-proposal]` with a native source custody error. Both earlier candidate attempts passed that case. A targeted Ubuntu run passed it on both exact base and head. The entire product subtree is identical across the two commits. Attempt 4 repeats the canonical workflow on the same refs.
