# #423 refinement

As the maintainer of test automation, I want a measured estimate of what suite-level TIA misses, over-selects, and saves so I can judge the advisory selector on evidence from real repository changes.

**Size L. Estimate 3.5 agent-hours. Priority P2.** Allow 0.75 hours for matrix design and plan review, 1.0 for candidate and hosted harness setup, 1.0 for validating and interpreting receipts, and 0.75 for independent results review and archival. Hosted queue and execution affect elapsed time. The estimate is for engaged agent work, including active supervision. The spike stays within the four-hour leaf bound.

The prerequisite is satisfied by [#422’s sign-off](../../422/retro/2026-11-24-422-sign-off.md). Its baseline is `45db935ac73911b95320a3e38d19f177cedd4fd2`, from the owner-directed merge of #424. Use that exact tree and a fresh disposable draft. Limit delivery to the research record on planning. All experiment branches and the draft are outside the production delivery path.

Acceptance is complete, reproducible evidence for each scenario in #423 with a separate full oracle, independently declared expectations, clean and seeded controls, hosted advisory receipts, and independent review. A measured miss or bounded inconclusive result is a research finding. Missing provenance or unexecuted minimum comparisons leave the deliverable incomplete.
