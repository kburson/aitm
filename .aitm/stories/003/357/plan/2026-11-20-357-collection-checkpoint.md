# #357 Collection checkpoint

Trunk commit `9843874bd00ffa1255b3595987106d5af51dceb3`, tree `b8ca66991842e6b360cf09f0e36b25c693d48390`. Darwin arm64, CPython 3.13.9, uv 0.10.6, pytest 9.2.0, locked package environment. Each profile returned zero twice with identical ordered node IDs. The profiles contain 2,314 disjoint IDs across 71 source files. [Exact node IDs](../attachments/2026-11-20-357-collected-nodeids.tsv) · SHA-256 `fde21675b90b5d9a4a4d2d733d7d3a0289fee540b0457d03daf8bb44d166d9f2`.

| Profile | Root | IDs |
| --- | --- | ---: |
| product | `packages/aitm-usage/tests` | 1,519 |
| ci | `tools/ci/tests` | 706 |
| board | `tools/board_sync/tests` | 13 |
| dashboard | `tools/story_dashboard/tests` | 61 |
| native | `packages/aitm-usage/native-tests` | 15 |

## Reproduce from the repository root

Run each target independently. Set `target` to the table entry and `receipt` to a distinct path outside the checkout.

```sh
export PYTHONPATH="$PWD:$PWD/tools/ci"
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
if [ "$target" = packages/aitm-usage/native-tests ]; then
  export PYTHONPATH="$PWD:$PWD/tools/ci:$PWD/packages/aitm-usage/tests"
fi
AITM_CI_PYTEST_EVIDENCE="$receipt" uv run --project packages/aitm-usage \
  --locked --python 3.13.9 python -m pytest -c packages/aitm-usage/pyproject.toml \
  --rootdir "$PWD" -p no:cacheprovider -p pytest_evidence --collect-only -q "$target"
```

An initial direct tools collection could not import the repository namespace. The corrected invocation sets the repository root on the module path. The opt-in Darwin watch module separately imports shared helpers from `test_host_watch`; the native invocation includes the product tests directory to resolve it. These are collection prerequisites for the experiment and inputs to #358.

## First provisional classifications

- `packages/aitm-usage/tests/test_grok_pricing.py::test_grok_rate_classes_do_not_use_claude_defaults` — Unit. Direct rate-card/accounting calls check that provider rates stay distinct. Fast/slow placement awaits timing.
- `packages/aitm-usage/tests/test_grok_pricing.py::test_grok_preserves_legacy_rate_digest_and_fixed_export` — Local integration. Uses the real packaged rate card and temporary export path to verify compatibility.
- `packages/aitm-usage/tests/test_service_process.py::test_real_service_crash_enrollment_and_private_state` — Systems integration. The installed command and separately running service exercise enrollment, crash and durable ownership through real processes.
- `packages/aitm-usage/native-tests/test_darwin_watch.py::test_darwin_start_failure_retires_owned_resources` — Systems integration. Intercepts selected native calls around FSEvents handle ownership and requires a Darwin host.

The full witness register, unit timing threshold validation, Ubuntu collection and final exception list are still open. The collection receipt establishes which nodes were discovered on this host. Execution outcomes and parity still need evidence.
