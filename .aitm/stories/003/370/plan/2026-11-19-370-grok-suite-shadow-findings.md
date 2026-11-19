# #370 Grok suite hosted Ubuntu qualification

**Pass for the declared Grok replay test-body boundary.** #393 exercised four exact GitHub PR trees. The bounded edit selected the complete 33-test Grok ingestion and replay suite, matching its outcomes in the 1,776-test full run. The bounded lane took 3.564 seconds including locked environment setup and suite selection, versus 274.003 seconds for the full lane on the same runner. The measured saving was 270.439 seconds, or 98.7%.

[Hosted run](https://github.com/kburson/aitm/actions/runs/44588398041/attempts/1) · [Declared matrix](../../393/plan/2026-11-19-393-grok-suite-matrix.md) · [Exact outcomes and timing](2026-11-19-370-grok-suite-shadow-evidence.json) · [Versioned shadow harness](https://github.com/kburson/aitm/tree/881c2ca8827429058976008d3e820540622a54d1/shadow-393)

| Exact tested PR | Suite decision and outcome | Full outcome | Suite lane seconds | Full lane seconds | Path-map lane seconds |
| --- | --- | --- | ---: | ---: | ---: |
| [#394 Bounded replay assertion](https://github.com/kburson/aitm/pull/394) | 33 passed | 1,776 passed | 3.564 | 274.003 | 274.167 |
| [#397 Seeded corroboration mismatch](https://github.com/kburson/aitm/pull/397) | 32 passed, one intended failure | 1,775 passed, same failure | 3.962 | 263.368 | 263.532 |
| [#395 Shared headless fixture](https://github.com/kburson/aitm/pull/395) | Full | 1,776 passed | 247.965 | 247.851 | 248.015 |
| [#396 Shared Grok adapter](https://github.com/kburson/aitm/pull/396) | Full | 1,776 passed | 324.971 | 324.833 | 324.997 |

Each row compares workloads on one hosted Ubuntu 24.04 x64 runner using uv 0.10.6, private CPython 3.13.9, the locked environment, independent pytest processes, and three product workers. Full includes 1,525 product and CLI IDs and 251 helpers. All timings include locked environment setup. Each selection lane additionally includes its selector time. These measurements exclude job queue and startup, interpreter provisioning, coverage instrumentation, and wheel smoke. The current base-owned path map selected full on every row. Each full decision reused the corresponding full execution result in the timing comparison.

The bounded edit strengthened the existing replay test to verify two distinct observations and equivalent observations with and without valid headless corroboration. Snapshot comparison proved the bytes outside that declared test body unchanged. Pytest resolved 33 IDs at execution time, and independent reconciliation matched that set exactly against the full run's IDs for the target. The seeded mismatch perturbed the corroborating row before the existing positive assertion. Selected and full runs failed the same test and produced zero missed failures or mismatched outcomes.

Other modules import the shared Grok fixture or consume the product adapter. Both shared edits therefore selected full. The existing path map also selected full for the headless fixture because its audited consumer digest had drifted. The result qualifies the declared test-body boundary. Changes to shared product code, shared fixtures, or unclassified inputs retain conservative fallback.

The experiment reused #383's Git resolver, verified the literal base, head, tested merge and tree for every case, and rechecked the snapshots after execution. Wrong tested tree and stale head returned unavailable. An incomplete phase receipt failed validation. The stored outcomes bind the workflow attempt, exact Git identities, runner image, controls and artifact digests. Trunk, required gate bytes, branch rules, and the pinned #355 entry point were verified unchanged. The shadow result carries advisory authority.
