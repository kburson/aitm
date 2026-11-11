# #2 Governed PR and working branch lifecycle · manual SPR acceptance

**Verdict — Accepted at the exact source digests below.** SPR-PR-04 is resolved. SPR-PR-01, 02, 03, 05 and 06 remain resolved.

## Exact reviewed inputs

I read the complete current 107-line specification followed by the complete current 338-line plan in contiguous ranges. I verified both raw SHA-256 digests in the physical review worktree `/Users/kpburson/.codex/worktrees/aitm-158-evidence/trunk`. Its checked-out branch pointer resolved to the assigned source commit `e88f064b67396c4682e5e63940b9fd9f2d17f650`.

| Artifact under `.aitm/stories/000/2/` | Raw SHA-256 |
| --- | --- |
| `design/2026-11-11-2-governed-pr-and-branch-lifecycle-design.md` | `71dae425e57507082796dc4e8f475eadb4201de4eb0ead5d74c64942e6be419c` |
| `plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md` | `b1a1f71f42fd39d9b03ce04b9971c5ed519275515731452f88efe00ff1698f8c` |

## Final finding dispositions

| Finding | Review disposition |
| --- | --- |
| SPR-PR-01 | Resolved. Managed readiness uses broker dispatch order, reconciles already-sent or ambiguous effects and has separate qualification from #158 host merge enforcement. Managed repair requires both. |
| SPR-PR-02 | Resolved. One semantic lifecycle slot and exclusive literal host-resource ownership prevent duplicate provision and unsafe identity reuse. |
| SPR-PR-03 | Resolved. The target policy controls every write route to a dual-role ref, including attempted generic owner pushes. |
| SPR-PR-04 | Resolved. The graph keeps the integration owner in required scope, uses its separately declared upstream, and prevents premature closure. The composed-source guard and C41 admission now use that exact upstream. |
| SPR-PR-05 | Resolved. Synthetic #158 host proof and actual integrated #133 CI proof have separate producers, prerequisites and receipts. |
| SPR-PR-06 | Resolved. Retarget requires verified redraft, terminal reconciliation of ambiguity and fresh admission and CI for the actual target. |

Design lines 29–41 and plan lines 31–64 distinguish the integration delivery owner, required epic scope and literal upstream target. Plan lines 66–86 bind composed-source eligibility to the literal upstream ref, applicable identity and incarnation, pinned upstream baseline, exact integration head and tree, and verified component receipts. The current integration attempt must still pass its own Test and independent source review and obtain C41 admission to the exact same upstream. The #158 policy applies when that upstream is the protected default target. The deterministic fixture at plan line 335 proves a nested upstream whose baseline differs from default and rejects default or sibling substitution.

This is an independent manual same-provider review of these planning artifacts. It grants no hosted test, production-protection, implementation, or #159 pickup authority.
