# #2 governed PR and working-branch lifecycle SAR closure

**Verdict — Accepted at the exact digests below.** SAR-PR-03 is resolved. SAR-PR-01, SAR-PR-02, SAR-PR-04 and SAR-PR-05 remain resolved.

## Reviewed revision

I read both revised artifacts in full, design first. The worktree `/Users/kpburson/.codex/worktrees/aitm-158-evidence/trunk` resolved to `123e08304bdfe94ae4eac83f6b93a9a3e2822c79`. Both SHA-256 digests match the review assignment.

| Artifact under `.aitm/stories/000/2/` | SHA-256 |
| --- | --- |
| `design/2026-11-11-2-governed-pr-and-branch-lifecycle-design.md` | `2829a591189907906757716138d9dfa9806a552c1194e422823fa507e1cd5db4` |
| `plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md` | `7596974f583018af5de1e7a50f208bc360ad1d3c9de4d8ecd4a6335ce2dca258` |

## SAR-PR-03 · Resolved

Design lines 28–35 and plan lines 35–48 keep the declared integration delivery on an ordinary story with its own attempt and leave C62 aggregate epics on their existing path. Plan lines 50–67 supply the missing path through C76 for clean child-only integration. The typed receipt is confined to the designated integration story and binds its current attempt and parent to the pinned default-target baseline, exact integration head and tree, and verified C39–C41 child-to-integration deliveries. It requires a nonempty and completely explained delta, including after a base refresh, and re-evaluation on source or baseline changes.

The receipt proves Develop-exit source eligibility. The integration attempt still needs its own current Test result, independent review and exact C41 admission. The ordinary C76 source rule remains applicable to other stories and defects. This resolves the earlier case where a clean child-only head could pass test and review in principle but lacked a qualifying integration-story source commit for Develop exit.

Plan lines 220–225 assign the change to a bounded Core leaf before hosted integration delivery. The proof matrix at lines 263–265 connects the exact child deliveries to the real Develop-exit guard and separately reviewed default-target delivery. It rejects missing, stale, unrelated, empty or unexplained source and checks that child evidence alone cannot admit the merge.

This acceptance covers the planning artifacts. The Core leaf and hosted qualification retain their own evidence and authorization requirements.
