# #370 suite-level affected-test plan

Use independently runnable pytest suites as the unit of TIA selection. Keep one Python implementation. Ubuntu is the hosted reference and macOS remains a portability cross-check for the shared snapshot implementation. The hosted work in [#393](../../393/story.md) qualifies one suite.

## Why the plan changed

[#385](../../385/story.md) completed seven matched hosted Ubuntu comparisons. The file-level probe caught both seeded failures with a narrow fixture assignment. It produced full or unavailable decisions on every real tree. The real rename exposed the cost of binding inventory classification to individual filenames. The experiment is complete and promotion to the required gate stays on hold. [Findings and timings](2026-11-19-370-hosted-shadow-findings.md)

## Selection model

1. Reuse the exact Git snapshot resolver delivered by #383 for staged index, HEAD, and PR tested trees. The pilot uses PR mode. Compare the literal base with the tested tree and preserve the PR head, ordered merge parents, and identity rechecks. [#383 delivery](../../383/retro/2026-11-19-383-delivery.md)
2. Declare each suite's pytest target and the source, fixture, dependency, configuration, and runtime inputs that can affect it. Audit shared and downstream consumers and record why each input selects a suite. Inputs established as shared select all affected suites. The one-suite pilot requests full when an input can reach work beyond its qualified boundary. Unknown input falls back to full. Invalid identity or incomplete required evidence returns unavailable.
3. Let pytest discover node IDs from the selected target during execution. Use those IDs and their outcomes to verify coverage of the assignment. Selecting suites avoids the pilot's dependence on an exhaustive per-node inventory for both snapshots. Renames or deletions that change an unqualified target or boundary fail closed.
4. Compare the suite assignment, the current path-map decision, and complete full-suite outcomes for the same hosted Ubuntu PR tree. Measure setup, selection, execution, and elapsed time. Require a defensible real narrowing with useful elapsed-time savings and zero missed failures in the declared cases. Shared-input fallback and invalid identity must be exercised.

## Completed qualification

[#393](../../393/story.md) qualified the existing Grok ingestion and replay suite for a change confined to a declared test body across four exact hosted Ubuntu PR trees. The bounded lane passed 33 tests in 3.564 seconds including setup and selection. Its same-runner full reference passed 1,776 tests in 274.003 seconds. Both lanes caught the same seeded failure. Shared fixture and adapter changes selected full. [Findings](2026-11-19-370-grok-suite-shadow-findings.md)

[#398](../../398/story.md) qualified the exact decoder refactor and seeded control on one pinned base. The positive edit took 4.316 seconds for the replay suite versus 338.504 seconds for the exact full run. Both lanes caught the seeded failure. Shared changes selected full. [Findings](2026-11-19-370-bounded-production-shadow-findings.md)

## Hosted integration decision and next story

The [integration decision](2026-11-19-370-suite-hosted-integration-decision.md) continues isolated hosted shadow and holds routine integration. [#402](../../402/story.md) will qualify a reusable suite declaration for a fresh production edit and across an unrelated base advance. Changes that invalidate the declaration must yield full or unavailable. The required workflow, path map, gate, verifier, branch rules and #355 command retain their current roles.
