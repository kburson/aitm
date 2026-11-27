# #497 initial pickup review

Grok 4.7 Build Fast reviewed the pinned pickup.

CHANGES REQUIRED

The Markdown scope, sibling admission, eight-set coverage, typed acceptance/refusal fixtures, and policy boundary match the accepted #471 plan. Two trunk-qualification rules are narrower than that plan.

1. **Docs-only Core exclusion proof.** When Core CI filters out the Markdown PR, qualify the exact candidate by comparing the Core package, root inputs, and workflow bytes with the latest passing hosted Core baseline, and re-evaluate hosted CI if any of those inputs differ. The pickup only requires proof that Core inputs are unchanged against a hosted baseline.

2. **SAR target.** Require a fresh Grok 4.7 source SAR on the non-draft #497 story PR and on the final trunk PR. “Standalone” SAR for the leaf and aggregate PRs does not state that source review or those two PR targets.
