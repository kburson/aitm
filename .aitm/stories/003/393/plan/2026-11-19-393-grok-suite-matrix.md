# #393 Grok ingestion and replay suite matrix

Qualify the existing `packages/aitm-usage/tests/test_grok.py` pytest target on hosted Ubuntu with an isolated, read-only shadow run. Reuse #383's `ProbeRequest` and snapshot resolver to inspect the base and exact tested merge. Bind the literal PR base, head, tested commit, tested tree and ordered parents. Recheck snapshot digests after execution. Use the base-owned path map as a read-only comparator.

## Input ownership

`test_grok.py` imports `Evidence` from `test_monitor_adapters.py` and exercises `aitm_usage.sources.grok`, the shared adapter, ledger, and type definitions. Its `grok_source` reads `fixtures/grok/{headless.json,updates.jsonl,usage.json}` and is imported and executed by `test_monitor_grok_capture.py`. Coverage, enrollment, inventory, journal, qualification, scope and hook tests import constants or fixture paths from the same module. Product adapter code serves additional capture and delivery paths. Those inputs are shared. Pytest configuration, conftest, tooling, dependencies and interpreter changes also require full. Unknown input, mixed changes, file moves, and unverified module ownership require full. Invalid identity or incomplete receipts hold the result.

The bounded input is an edit confined to the body of the existing `test_headless_projection_is_only_corroboration` function. Repository-wide reference search found only its definition. The versioned declaration requires the same file mode and uses a structural comparison to verify that the module, imports, shared helpers and fixtures, function name, signature and decorators are unchanged outside that body. The selected assignment is the full pytest module. IDs come from actual pytest execution.

| Case | Exact candidate change | Expected |
| --- | --- | --- |
| bounded | Strengthen the live replay test to assert that a forged headless row does not suppress the unaffected prompt | Select the existing suite. Full and selected outcomes agree. Measure material savings including setup and selection. |
| seeded | Feed a mismatched headless row during the positive replay before any expected conflict | Select the suite. Its existing baseline assertion fails. Full catches exactly the same seeded failure. |
| shared-fixture | Change whitespace in the tracked headless fixture loaded by multiple suites | Full. Identify the other consumers despite the narrowly named fixture. |
| shared-source | Clarify the Grok adapter module docstring | Full. The adapter has consumers in multiple suites. |
| identity and evidence controls | Wrong tested tree, stale head, truncated receipt | Unavailable or held with no qualified assignment. |

Use comparable runner environments per case, the same locked dependencies, independent test observations, retained exact outcomes, and timing for suite assignment and execution versus full. The full inventory includes product, CLI and the six established helper modules. Keep the required workflow, path map, evaluator, verifier, branch rules and #355 unchanged.
