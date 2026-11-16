# Functional Test Impact Analysis Implementation Plan

**Goal.** Deliver a required PR check that runs the affected tests for qualified changes, explains the selection, and runs the full applicable suite when impact is uncertain.

**Approach.** Reuse the base-owned path map and pytest evidence from #340 and #341. Independently establish affected consumers first. Keep only mappings whose scope can be justified and use full mode for unresolved shared or runtime dependencies. Bind live evidence to the exact candidate and exercise the mapped check after a successful full run has already been recorded for that PR.

**Inputs.** [#344 story](../story.md), [#133 TIA design, sections 2–3](../../../001/133/design/test-impact-analysis-design.md#2-validation-modes-and-authority), [current PR direction](../../../001/133/plan/2026-11-16-133-pr-feedback-replacement.md), [#340 delivery](../../340/retro/2026-11-16-delivery.md), [#341 delivery](../../341/retro/2026-11-16-delivery.md), and [#339 exact feedback evidence](../../339/plan/2026-11-16-339-exact-pr-feedback-results.md).

## Constraints

- Use the normal protected trunk PR workflow and production trusted verifier. Use unmerged draft PRs in the existing repository for intentional negative controls, with unrelated changes excluded. Revalidate against current trunk at pickup and after delivery. Use the existing three-worker full path and 20-minute budget from the #133 replacement decision.
- The trusted base owns the selector, rules, and test-evidence interpretation. Read the exact candidate's changed paths and test inventory as inputs. A candidate policy change itself receives full validation and independent review before it becomes trusted. Preserve the existing required checks, verified evidence, wheel smoke, and merge rules.
- Preserve the successful-full-run behavior and cancellation from #341. An earlier full result can suppress the extra full run only within the same PR and compatible base, policy, and selection. The current push still requires its own mapped or full result. A fallback push always runs the full suite as its required result.
- Cover ordinary Python PR validation. Scheduled backstop activation, Stop the Line, new runner deployment, and a general-purpose selector are outside scope. #344 stays open until the closeout evidence passes. The parent remains open until its remaining scope is explicitly reconciled.

## Review focus

- A mapped shared module can have consumers absent from its current test list. A matching rule by itself supplies no evidence that the list is complete.
- A former consumer can survive a move or deletion. Account for both paths, and run full if the pre-image or affected inventory cannot be resolved.
- A fixture or resource loaded through a helper or subprocess may be invisible to import analysis. Use an explicit reviewed dependency or full mode.
- A full run on an earlier successful push can hide a missing consumer until the next push restores the stamp. Compare this push with a full run on that same tested tree.
- A selected module that collects nothing, an incomplete path list, or mismatched candidate evidence cannot yield a successful narrowed result.

## Task 1 — Reproduce live behavior and establish the comparison set

- [ ] From current trunk, record the commit and tree, map/selector and workflow blobs, active required checks, and the exact full command and environment used by `.github/workflows/ci.yml`. The delivered reference is `625b5407978675ac3b906990c8bb0713dcae18fd`. #343 is the existing positive case.
- [ ] In a scratch checkout and exact draft candidate, enumerate changed paths with the applicable base and the tested merge tree. Compare selector output, pytest collected IDs and call outcomes, and applicable mandatory subprocess/quality checks. Run the full comparable suite on that same candidate, in a separate fixture root. Keep setup, queue, and test times separate. At pickup, replay the following first case from the source root and retain the exact output. These commands reproduce the known mismatch. The next step establishes the consumer inventory.

  ```sh
  printf '%s\n' packages/aitm-usage/src/aitm_usage/ledger.py |
    python3 tools/ci/path_map.py --map tools/ci/path_map.json --changed-from /dev/stdin
  rg -n 'from aitm_usage\.ledger import|Ledger\.initialize' packages/aitm-usage/tests
  ```

- [ ] Independently list expected test modules and why each is affected. Trace reverse imports and behavior in test bodies, review fixture, shared setup and subprocess declarations, and use `tools/ci/tia/python_graph.py` and the #133 declarations as advisory corroboration where they can resolve edges. Use full green runs and observed coverage to corroborate the separately derived consumer inventory.
- [ ] Record these fixed case classes and expected outcomes. Select actual present paths at the pinned base and record them before the first run.

  | Case | Required outcome |
  | --- | --- |
  | Directly scoped source edit, starting with an existing mapped `aitm_usage/sources/` module | A justified proper subset that contains all independently identified consumers. |
  | Shared source edit to `aitm_usage/ledger.py` | Include `test_scope_admission.py`, `test_ledger.py`, and all other established consumers, or require full with a shared or unresolved dependency reason. |
  | `tests/fixtures/grok/headless.json` | A justified proper subset covering its behavioral consumers, including `test_grok.py`. |
  | Unmapped executable, undeclared runtime dependency, and shared config or map/workflow change | Full suite, with the reason and input path recorded. |
  | Move/deletion with a surviving consumer | Former consumers included, or full with a reason. |
  | Documentation-only change with an explicit trusted no-impact rule | Required non-Python checks run. Unclassified inputs cannot receive this disposition. |

- [ ] Retain baseline evidence under this story’s `plan/` directory with run links and a small case table. For each discrepancy, identify the missing consumer, fallback, or evidence and the smallest owning production component.

## Task 2 — Repair the path policy and retain explainable evidence

- [ ] Add focused red tests in `tools/ci/tests/test_path_map.py` before changing `tools/ci/path_map.json` and `tools/ci/path_map.py`. Pin the Ledger case, one bounded source and one bounded fixture, full mode for an unclassified path alone or mixed with any other changed path, checks-only for explicitly classified no-impact paths, mapped mode for explicit no-impact plus a mapped source path, both sides of a move, missing paths, and stable ordering for a multi-path selection. Retain shared Ledger as full unless the baseline establishes a complete, maintainable set. Use explicit full rules for other insufficiently supported mappings found by the audit. Limit narrowed coverage to reviewed scopes. Include the rule's rationale and the dependency route to the test module. Where the map alone cannot show completeness as the base changes, require a maintained declaration and validate it against relevant consumer changes in CI, or route that scope to full.
- [ ] Keep the `path_map.select(paths, document)` entry point and its `mode`, `tests`, `source`, `key`, and `children` fields. Extend the selection evidence with a deterministic `paths` list keyed by changed path. For each path carry one disposition, the matched rule or fallback reason, and the affected module paths when known. Checks-only requires every changed path to match an explicit positive no-impact rule. A mapped change mixed only with classified no-impact paths keeps the mapped tests. Any unclassified path, including a lone path with a non-executable extension, requires full. Use full for shared setup, controls and incomplete input, or fail the check when full evidence cannot be established.
- [ ] Use one selection contract in both lanes of `.github/workflows/ci.yml`. Verify exact base/tree and complete old and new paths. Handle additions, moves, removals, missing selected files and failed or missing selection evidence via the full path where a trusted complete run can be established. Otherwise the check fails. Preserve existing base-owned compatibility for the first PR changing the controls. Replace the current PR-and-selection cache key with a versioned key that also includes the exact applicable base SHA and the trusted selection-policy digest. Derive the policy digest from the trusted selector and map blobs, and the selection digest from mode and the sorted selected modules. Use an exact restore key and a new namespace so pre-cutover stamps cannot count. Update `test_cache_key_is_exact_and_rejects_unsafe_values` and the workflow key assertion to pin a miss on base, policy, PR or selection changes. Keep the cache save behind successful validation. Changing only file contents while base, policy and selected tests stay the same repeats the short check with no extra full run.
- [ ] Where evidence changes require it, update `tools/ci/python_gate.py`, `tools/ci/verify_pr.py`, and their existing test files. Pair the rule/reason evidence with the collected and executed pytest node IDs for the exact attempt, including parametrizations. Cover a selected module with no executed IDs and stale or incomplete evidence. Keep existing full or legacy receipts readable. Require the per-path evidence once the delivered selector and its map are on the applicable trusted base. The control-changing PR runs with the old trusted selector and full validation. Compare independently derived expected consumers against actual IDs. Include required child checks that the resolved mode entails.
- [ ] Run the focused gate suite from the source root. Then run the normal full check on the control-changing PR, record independent review of the current head and tested tree, and use the trusted verifier before delivery.

  ```sh
  cd packages/aitm-usage
  PYTHONPATH=../../tools/ci uv run --locked pytest -q \
    ../../tools/ci/tests/test_path_map.py ../../tools/ci/tests/test_python_gate.py \
    ../../tools/ci/tests/test_verify_pr.py
  ```

## Task 3 — Prove the delivered PR behavior

- [ ] After the reviewed controls are on trunk, open or refresh exact draft candidates against that base. For the mapped fixture pair, start with an innocuous reordering of the Grok headless rows that the full suite can pass. Confirm the successful full-run stamp. Preserve the same affected paths and inject the known fixture mismatch from #339, after checking the current baseline values. On the later push require the mapped check to fail on the same test and assertion as the full suite on that exact tested tree. Restore the stamp after selection and before running candidate tests, so the red head records the cache hit. A failed candidate must leave the required check red and must never save a stamp or publish passing evidence. Check the Actions steps for the cache hit and the failed test. Run the separate exact-tree full comparison with the same locked environment and retain its matching failure. Keep the negative candidate unmerged and verify it cannot receive trusted acceptance.
- [ ] Repeat the positive proper-subset proof for the direct source case, and repeat the fallback proof for the shared-input case and controlled unmapped/control inputs. Require the workflow to run full where expected. In the same PR, add a qualified input whose consumer modules change the selection set, and prove the full run occurs for the new selection. Exercise a superseded attempt during a push sequence and verify the newer head must supply current evidence. Count already delivered #341 cancellation evidence as context and run the new case against the delivered controls.
- [ ] For each case retain the repository, exact base/head/tested merge commit and tree, changed paths, rules/version or fallback reasons, selected modules, executed IDs, full-suite outcome, run/attempt and artifact links, and the trusted verifier decision. Distinguish the stamp-producing run from the short run and from the exact-tree full baseline. Link the replay commands and expected outputs. Close proof PRs when evidence is retained.
- [ ] Obtain independent review of the delivery evidence. If any case still misses an affected test or cannot establish safe fallback, record it, fix it, and repeat the affected cases. Close #344 only after the live acceptance criteria pass. Return the evidence to #133 for its remaining scope decision.
