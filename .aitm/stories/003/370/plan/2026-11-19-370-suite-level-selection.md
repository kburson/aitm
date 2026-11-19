# #370 suite-level affected-test plan

Use independently runnable pytest suites as the unit of TIA selection. Keep one Python implementation. Ubuntu is the hosted reference and macOS remains a portability cross-check for the shared snapshot implementation. The hosted work in [#393](../../393/story.md) qualifies one suite.

## Why the plan changed

[#385](../../385/story.md) completed seven matched hosted Ubuntu comparisons. The file-level probe caught both seeded failures with a narrow fixture assignment. It produced full or unavailable decisions on every real tree. The real rename exposed the cost of binding inventory classification to individual filenames. The experiment is complete and promotion to the required gate stays on hold. [Findings and timings](2026-11-19-370-hosted-shadow-findings.md)

## Selection model

1. Reuse the exact Git snapshot resolver delivered by #383 for staged index, HEAD, and PR tested trees. The pilot uses PR mode. Compare the literal base with the tested tree and preserve the PR head, ordered merge parents, and identity rechecks. [#383 delivery](../../383/retro/2026-11-19-383-delivery.md)
2. Declare each suite's pytest target and the source, fixture, dependency, configuration, and runtime inputs that can affect it. Audit shared and downstream consumers and record why each input selects a suite. Inputs established as shared select all affected suites. The one-suite pilot requests full when an input can reach work beyond its qualified boundary. Unknown input falls back to full. Invalid identity or incomplete required evidence returns unavailable.
3. Let pytest discover node IDs from the selected target during execution. Use those IDs and their outcomes to verify coverage of the assignment. Selecting suites avoids the pilot's dependence on an exhaustive per-node inventory for both snapshots. Renames or deletions that change an unqualified target or boundary fail closed.
4. Compare the suite assignment, the current path-map decision, and complete full-suite outcomes for the same hosted Ubuntu PR tree. Measure setup, selection, execution, and elapsed time. Require a defensible real narrowing with useful elapsed-time savings and zero missed failures in the declared cases. Shared-input fallback and invalid identity must be exercised.

## Next story

[#393](../../393/story.md) starts by auditing the existing Grok ingestion and replay target, `packages/aitm-usage/tests/test_grok.py`. Its existing fixture inputs give the pilot a concrete boundary to validate. Any source or fixture with other consumers must retain conservative selection. Finish the Ubuntu comparisons and record the result here before considering broader suite coverage or finer selection.

The required workflow, hosted path map, gate, verifier, branch protection, and pinned #355 command keep their current roles. Promotion requires a separate decision.

#393 qualified the declared Grok test-body boundary on hosted Ubuntu. [Findings](2026-11-19-370-grok-suite-shadow-findings.md)
