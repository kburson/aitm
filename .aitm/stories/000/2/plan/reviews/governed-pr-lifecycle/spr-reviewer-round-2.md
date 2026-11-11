# #2 Governed PR and working branch lifecycle · manual SPR closure check

**Verdict — Changes requested.** SPR-PR-01, 02, 03, 05 and 06 are resolved. SPR-PR-04 has one remaining source-eligibility scope contradiction.

## Exact reviewed inputs

I read the complete current 106-line specification followed by the complete current 333-line plan in contiguous ranges. I verified the raw SHA-256 digests in the physical review worktree `/Users/kpburson/.codex/worktrees/aitm-158-evidence/trunk`. Its checked-out branch pointer resolved to the assigned source commit `73bcd9ed37fc3f6967a9af5bc4aafb50c0480271`.

| Artifact under `.aitm/stories/000/2/` | Raw SHA-256 |
| --- | --- |
| `design/2026-11-11-2-governed-pr-and-branch-lifecycle-design.md` | `c1a9e4b6122871a66e02aac1b9ad9f762df2f52b6ba848d035f354e4f066370f` |
| `plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md` | `56bf58bd263c5e451dfa30e02d74cf8050b0a7bd68ff18dbb958da21c61fd3bc` |

## Finding dispositions

| Finding | Review disposition |
| --- | --- |
| SPR-PR-01 | Resolved. Design lines 76–89 and plan lines 186–215, 287–304, 328 and 331 distinguish ordered managed ready dispatch from host-enforced merge. They define already-sent and uncertain outcomes, qualify the separate readiness route and gate managed repair on it. |
| SPR-PR-02 | Resolved. Design lines 20–28 and 61–70 and plan lines 98–149 and 324 define a semantic lifecycle CAS, exclusive host identity, sent/unsent distinction and no unsafe same-ref reuse. |
| SPR-PR-03 | Resolved. Design lines 35–37 and plan lines 217–240, 291–292 and 329 apply target policy to all writers of a dual-role ref and test generic owner push refusal, approved refresh and policy-permitted direct work. |
| SPR-PR-04 | Changes still requested. Plan lines 31–64 resolve the graph, upstream selection, early provisioning and C62 closure/replacement. The remaining contradiction is the C76 receipt's default-only binding at lines 66–83. See below. |
| SPR-PR-05 | Resolved. Plan lines 295–304 and 331–332 separate #158 synthetic host qualification from end-to-end #133 actual CI and preserve later authorization boundaries. |
| SPR-PR-06 | Resolved. Design lines 79–86 and plan lines 203–215 and 328 require verified redraft before target change, reconcile ambiguity and require fresh authorization and CI for the actual target. |

## SPR-PR-04 · P1 retained · Bind composed source eligibility to the literal upstream target

The revision resolves the issue and delivery graph. Plan lines 42–57 define the integration story's explicit upstream, with default branch used for a top-level epic. This permits a nested integration to target its enclosing integration branch. Plan lines 71–83 then require the child-only integration receipt to use a pinned default-target baseline and require C41 admission for default-target delivery. A nested integration based on a non-default branch with its own changes would either fail eligibility despite valid component receipts or be assessed against the wrong branch. This also conflicts with the plan's statement that non-default delivery uses its own base and policy.

Bind the receipt and its independent C41 admission to the integration story's literal upstream ref, pinned upstream baseline and resolved upstream identity/incarnation where applicable. Apply default-only policy only when that literal upstream is the protected default target. Add a nested non-default fixture whose upstream baseline differs from the default branch and show that the correct proof passes while default or sibling substitution fails. Keep the same required-scope and independent Test/Review obligations.

Return the revised source digests for narrow closure. No hosted qualification, implementation, gate change or #159 pickup authority follows from this planning review.
