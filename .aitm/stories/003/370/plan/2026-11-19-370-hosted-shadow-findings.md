# #370 hosted Ubuntu shadow findings

**Hold promotion to the required PR gate.** #385 completed the hosted comparison on seven exact PR trees with zero missed failures or outcome mismatches across the five cases that produced a graph assignment. The graph produced no useful narrowing on real repository code, so #385 remains open in Test. Both unavailable cases supplied zero test IDs and had separate full outcomes.

[Declared matrix](../../385/plan/2026-11-19-385-shadow-matrix.md) · [Completed hosted run](https://github.com/kburson/aitm/actions/runs/44558382398/attempts/1) · [Verified evidence and exact node inventories](2026-11-19-370-hosted-shadow-evidence.json)

## Same-tree outcomes and elapsed time

Each row uses one GitHub-hosted Ubuntu 24.04 x64 runner, one exact GitHub-tested merge tree, locked uv 0.10.6 and CPython 3.13.9 in private scratch. Full runs used the 1,525 product/CLI obligations and six configured helper modules on real trees. Product/CLI used three xdist workers there, with reconciled per-node phases. The small fixture ran serially. Each reported duration is seconds. The execution columns exclude setup, queue time, coverage instrumentation, and wheel smoke. The probe column includes collection of both snapshots. The path map took 0.164 seconds in each case. It requested full for every case. Where an assignment was full, its execution and outcome came from the single matching full run on that runner.

| Case | Graph decision and observed outcome | Full suite outcome | Probe | Graph execution | Full execution |
| --- | --- | --- | ---: | ---: | ---: |
| [Grok hook source #386](https://github.com/kburson/aitm/pull/386) | Full | 1,776 passed | 10.488 | shared full | 208.731 |
| [Shared pytest conftest #389](https://github.com/kburson/aitm/pull/389) | Full | 1,776 passed | 11.388 | shared full | 248.742 |
| [Test module rename #391](https://github.com/kburson/aitm/pull/391) | Unavailable | 1,776 passed | 4.421 | — | 204.521 |
| [Package configuration #390](https://github.com/kburson/aitm/pull/390) | Full | 1,776 passed | 11.789 | shared full | 251.899 |
| [Clean static graph #392](https://github.com/kburson/aitm/pull/392) | 9 passed | 16 passed | 3.020 | 0.615 | 1.230 |
| [Seeded regression #387](https://github.com/kburson/aitm/pull/387) | 7 passed, 2 intended failures | 14 passed, same 2 failures | 3.021 | 0.615 | 1.230 |
| [Missing mandatory test #388](https://github.com/kburson/aitm/pull/388) | Unavailable | 15 passed | 1.767 | — | 1.230 |

## Decision evidence

- The real source, shared input, and configuration changes reached graph uncertainties for dynamic imports, unresolved imports, and relative-import context. The map recorded consumer-scope drift for the Grok hook and shared setup for the other two. The real rename exercised a precise refusal. Its five renamed test IDs collected and passed in the full run, but the unchanged suite inventory classifies the original module path only. Both rename paths were unclassified by the map.
- The fixture witnessed the direct test through one import and the transitive test through two. The graph saved 0.615 seconds of execution in each bounded case. Including probe collection, it took about 3.64 seconds versus 1.39 seconds for path-map assignment and full fixture execution. The fixture showed the graph can narrow and preserve outcomes in that bound. It demonstrated no elapsed-time advantage.
- The stale head and wrong tested tree each returned unavailable with no assigned IDs. Removing a mandatory test produced the same empty assignment for the missing inventory case. A truncated full phase receipt failed completeness validation.
- The real source, shared, and configuration cases matched the required CI candidate artifacts' exact path-map decisions, 1,525 product IDs, and passing product outcomes. The required CI run for the rename hit native capture fixture setup errors on both its base and candidate jobs. Its separate shadow full run passed. The shadow artifacts have their own GitHub run, attempt, job, archive digest, PR/base/head/tested identities, image and control hashes.
- The [first shadow run](https://github.com/kburson/aitm/actions/runs/44557441200) used Python under the runner home and failed private ACL checks on the real cases. The completed rerun supplied the exact interpreter path from private scratch and kept all seven PR bindings pinned. Only the experiment harness changed.

The gate, path-map and verifier bytes, pinned #355 runner, live trunk and trunk rules were verified unchanged. The experiment workflow was confined to its dedicated branch. Its result stays advisory. Promotion still needs a representative real change with defensible narrowing and a paired full run.
