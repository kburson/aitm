# #2 governed PR and working-branch lifecycle SAR closure

**Verdict — Changes requested.** Four findings are resolved at the reviewed digests. SAR-PR-03 remains open at P1.

## Reviewed revision

I read both revised artifacts in full, design first. The physical worktree `/Users/kpburson/.codex/worktrees/aitm-158-evidence/trunk` resolved to `ff09e06bdc96619ac13eb11e15aafb4495056432`. The following SHA-256 digests match the review assignment.

| Artifact under `.aitm/stories/000/2/` | SHA-256 |
| --- | --- |
| `design/2026-11-11-2-governed-pr-and-branch-lifecycle-design.md` | `11ea2e95327da0834648447721eec72430e3606ea9e54252cd7a3b45e9b69c4c` |
| `plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md` | `55642beeeed874ddf990f87d557186581b021c26f3253b13069e46abf4605db6` |

## Finding dispositions

| Finding | Disposition and source evidence |
| --- | --- |
| SAR-PR-01 · P1 | **Resolved.** Design lines 43–49 and plan lines 176–197 put retirement and dependent admission in the same durable order, keep the ref for the winning dependent, and hold deletion for uncontrolled routes or unresolved admitted effects. Plan line 238 calls for both race outcomes with unchanged parent OID. |
| SAR-PR-02 · P1 | **Resolved.** Design lines 20–27 and 54–60 and plan lines 63–102 distinguish the stable resource incarnation from C16 session recovery, separate pre-pickup and terminal service claims, require per-effect dispatch ownership and positive attribution, and fence replay. The scrap receipt preserves recoverable source independently of the ref. Plan lines 237–238 exercise rebind, lost effects, collision and stale cleanup. |
| SAR-PR-03 · P1 | **Open.** Design lines 28–33 and plan lines 35–49 establish a real ordinary story owner and keep the C62 aggregate separate. The ordinary story's source-eligibility gap below prevents acceptance of the positive trace in plan lines 242–243. |
| SAR-PR-04 · P2 | **Resolved.** Design lines 66–77 and plan lines 141–152 order promotion at the exact provider transition, explain an earlier committed promotion, preserve merge denial, require terminal reconciliation, and disable unqualified routes. Plan line 241 covers hold, head, retarget and ambiguity races. |
| SAR-PR-05 · P2 | **Resolved.** Plan lines 207–222 give the adapter and #158 integration separate proof boundaries. Lines 225–244 specify finite fixtures, outcomes and retained receipts. The plan calls for a positive non-default delivery under hold and gives an unavailable result denial credit only. |

## SAR-PR-03 · P1 · The integration delivery still needs a path through C76

**Locations** Revised plan lines 38–48, 201–206 and 242–243. Revised design lines 28–33. Accepted `design/core-design.md` lines 409–411 and 423–434. Accepted `plan/core-implementation-plan.md` C76, especially line 1205.

The revised plan provisions an ordinary integration delivery story in Backlog and later binds its attempt to the resulting head after child deliveries. An epic can reach that point with all child changes merged cleanly, with source commits attributed to the child stories and no nonempty source change carrying the integration story's ID. That head can be independently reviewed and tested, but the ordinary integration story still needs C76's Develop exit proof before its review can become effective for C41. C76 checks the exact story prefix on qualifying changes since the pinned baseline. The content-free bootstrap cannot supply that proof. The proposed positive hosted trace asserts final delivery without naming the source evidence that admits it.

Specify the exact pinned baseline and source-evidence contract for an integration delivery that consists of already-verified child changes. If it uses the existing C76 guard, identify the genuine integration-story change that qualifies and state how the clean aggregation case is handled. If the clean case uses equivalent source-mapping evidence under a revised guard, name the Core leaf that owns the change and bind its proof to the exact child deliveries, integration head, baseline and independent review. Exercise the clean child-only case through installed Develop exit, effective review and C41 admission. Retain an explicit refusal for empty bootstrap, child review alone and stale mapping. This closes the existing finding without changing the resolved retirement, provider or promotion contracts.

The dispositions assess the exact draft bytes. Provider and runtime behaviors remain qualification work under the reviewed plan.
