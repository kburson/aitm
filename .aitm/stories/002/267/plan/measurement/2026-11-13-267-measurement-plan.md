# #267 local advisory measurement plan

Pin the two-profile #143 pytest workload to AITM commit `766504a02aaeb9dda339d588172dd7d5bdbd2b3f`. Use CPython 3.13.9, uv 0.10.6, the repository lock, and pytest-testmon 2.3.0 (an isolated extra). Exercise the real #143 module entry point and compare the actual selected IDs with pytest-testmon's dependency-based selection and serial reference runs.

## Predeclared fixture seeds

Each seed is applied separately to the exact checkout. The stated expected set is a source-based lower bound for counting misses. Any observed pass-to-fail delta is added separately as outcome evidence.

| Seed | Disposable change | Expected IDs | Expected behavior |
| --- | --- | --- | --- |
| CLI Python | Change the argparse program name in `packages/aitm-usage/src/aitm_usage/cli.py` from `aitm-usage` to `aitm-267-usage`. | `tools/ci/tests/test_cli_evidence.py::test_usage_console_help` | Actual CLI smoke should fail. The declared subprocess edge gives TIA the expected case, subject to other conservative fallback causes. Testmon can miss work performed in a native child. |
| Non-code | Append an inert documentation paragraph to root `README.md`. | Empty | No changed outcome is expected. Record actual #143 mode for the unclassified path rather than assuming a no-tests decision. |
| Uncertain fixture | Change the first synthetic `requestId` in `packages/aitm-usage/tests/fixtures/grok/headless.json` to a distinct synthetic ID. | `packages/aitm-usage/tests/test_grok.py::test_headless_projection_is_only_corroboration` | Its lookup should fail. The pinned manifest has no fixture edge, so #143 should use full fallback. Testmon's Python instrumentation may miss the external JSON input. |
| Unavailable history | Re-run the CLI seed with a fresh path for the testmon dependency database. Invoke #143 with a deliberately unresolvable base name. | Same CLI smoke ID | Record testmon's cold selection and #143's actual unavailability. The pinned revision remains the serial oracle. |

Use the existing evidence observer to capture exact IDs, test phases and required native children. Seed testmon history with all tests on the unchanged checkout. Restore the same frozen history for each warm measurement so runs cannot contaminate one another. Use separate serial profile invocations with private temporary paths, disable plugin auto-discovery and cache generation, and keep reports and dependencies outside the source. Record wall time separately for history creation, plan and execution. The measurement draws no authority for merge, coverage qualification or production execution from advisory results.
