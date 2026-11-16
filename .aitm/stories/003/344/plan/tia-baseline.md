# #344 baseline and consumer audit

## Hosted baseline

[Draft #345](https://github.com/kburson/aitm/pull/345) adds a comment to `packages/aitm-usage/src/aitm_usage/ledger.py` with no other changed paths. Base `625b5407978675ac3b906990c8bb0713dcae18fd`, head `e8decd2385f6d6d9e049bce8e0fe98c89776dd45`, tested merge `11b201ef7159e4c2518fb4c1efe2a9d3f40595ed`, and tree `278f9985aacf9788838a42673bcba7e7b8318586`. The tip and tested merge have identical trees.

[CI run 43873943696, attempt 1](https://github.com/kburson/aitm/actions/runs/43873943696) passed all six canonical jobs. The trusted base map chose `test_ledger.py` and executed 69 tests in 2.88 seconds. The same job then ran the full comparison on the same tree with Python 3.13.9, uv 0.10.6, macOS 26 / APFS and three pytest-xdist workers. All 1,517 tests passed in 270.13 seconds. Python started at 13:14:58 UTC, five seconds after the canonical run was created, and ended at 13:20:38 UTC. The named tests exclude helper coverage and wheel validation.

The delivered verifier held that first attempt because the provider's attempt creation time was 13:14:54 UTC and its canonical run creation time was 13:14:53 UTC. Run ID, attempt, suite and start time agreed. Subsequent treatment keeps the exact checks and handles the observed one-second persistence difference. Local full comparisons on the same tree were attempted twice. The first encountered an archive-path test artifact and a native fixture setup error. The second reproduced two different native fixture failures. The hosted run above supplies the successful exact-tree comparison. [Attempt 2](https://github.com/kburson/aitm/actions/runs/43873943696/attempts/2) passed the [delivered verifier](baseline-verifier.json) for the same base, head and tree.

The live trunk ruleset requires a pull request and protects against deletion and non-fast-forward writes. The ruleset has no configured GitHub required-status context. For #344 delivery, the canonical signed `aitm-ci` result and the trusted verifier are the AITM merge gate. The existing ruleset was observed through GitHub's API.

## Independently identified consumers

| Input | Expected behavior and supporting observations |
| --- | --- |
| `src/aitm_usage/ledger.py` | Full. The baseline map selects Ledger's unit module. Admission, registry, monitor delivery, export and service tests also import, initialize or exercise Ledger through their fixtures. These consumers include `test_scope_admission.py`, `test_service.py`, `test_monitor_ledger_version.py` and `test_monitor_delivery.py`. The audit found 37 test modules matching the direct import, module import or initialization search. The broad runtime dependency is treated as full. |
| `src/aitm_usage/sources/grok_scope_hook.py` | Mapped to `test_grok_scope_receipts.py`. This file exercises the hook's `main` and process-ancestry checks directly. The production reverse call to `_has_process_ancestor` comes from `scope_admission.bind_grok_prompt`, which the reviewed receipt tests invoke. The installed CLI evidence test checks `aitm-usage --help` and never launches the scope hook. Unqualified consumers and any audited inventory drift force full. |
| `tests/fixtures/grok/headless.json` | Mapped to `test_grok.py`. This is the product suite's reader of the fixture, under its own Grok fixture root. It reconciles supplied request IDs and totals with native observations. #339 demonstrated that a mismatched total fails `test_headless_projection_is_only_corroboration`. |
| Unknown inputs, root or package discovery controls, renamed or deleted inputs | Full. The selector preserves each old and new path through exact-tree comparison. Shared controls also expire an audited mapping when they change in a later base. |
| `README.md` or `docs/blocked-by.md` | Checks-only for ordinary content-only edits, based on the two explicit non-runtime documentation rules. Lint and wheel smoke still run. |

The reviewed declarations are deliberately limited to the two verified consumer scopes. The consumer digest binds the tracked package, canonical pytest observation and CLI files, shared setup names and workflow. If that input set changes, the rule falls back until its consumers are re-audited. CI compares the two trusted selection results and the verifier reconstructs the selection from the exact source trees.

## Replay

Check out the named base and inspect the mapping and its consumers.

```sh
printf '%s\n' packages/aitm-usage/src/aitm_usage/ledger.py |
  python3 tools/ci/path_map.py --map tools/ci/path_map.json --changed-from /dev/stdin
rg -n 'from aitm_usage\.ledger import|from aitm_usage import .*ledger|Ledger\.initialize' packages/aitm-usage/tests
rg -n 'bind_grok_prompt|grok_scope_hook|headless\.json' packages/aitm-usage tools/ci
```
