# #158 independent review of the merge boundary trial

**Disposition.** Accepted for publication as bounded counterexamples
and named-writer evidence. Full #158 qualification stays held and #159
remains blocked.

| Reviewed artifact | SHA-256 |
| --- | --- |
| [Measurement receipt](../../attachments/2026-11-11-158-merge-boundary-trial.json) | `4b7d3cd5fcb87b907c733a6557e2e94f36694cc242d6e0d34a61c2d583ff4554` |
| [Trial report](../2026-11-11-158-merge-boundary-trial.md) | `83ccde596ce68595dcf21ccb8b7168e6e115f4e522477290e8b21dd24e447bd4` |
| [Story record](../../story.md) | `18c5d3e63dd97ca4f3bbb927d368b09db1e352825e5cf99060dcf7b35009e23e` |

The reviewer checked the five UUID-attributed async traces, four
landed Git objects, both ancestor-base transitions, status and writer
controls, seven rule suites, five protection snapshots, and teardown.
The moved first parent and head-status fallback matched the recorded
controls. The connector and CLI resolved to the same user. The
explicit PR-only exception succeeded and the tested direct and
ordinary routes were denied. The public API evidence supports
leaving the post-check case unrun.

The report clarifies that terminal results preceded teardown in each
test phase. The original spike, earlier trials, and #159 were outside
the staged diff. No publication findings remain.

Reviewer: independent Codex agent `review158_pr_trial`.
