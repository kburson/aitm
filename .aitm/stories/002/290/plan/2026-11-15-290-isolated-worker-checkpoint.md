# #290 Isolated worker checkpoint

The first shared-volume retry passed all 1,817 baseline tests. Its projected cohort ended with 1,202 passes and one native-source discovery setup error. The error trace showed discovery returned no native candidate. The shared temporary directory's change time moved during that test session. The specific invalidating change remains unverified. [Retained traceback](second-layout-projected.log)

A dedicated APFS disk image keeps temporary test namespaces separate from the shared system temp directory. Coverage outputs and fixture roots remain siblings. The sampled common ancestor change times stayed stable through both three-worker test sessions. [Ancestor observations](first-worker-ancestor-events.jsonl)

Both three-worker cells verified all 3,020 modeled assignments and captured the required native subprocess coverage, including per-PID evidence. Per-file executed line sets, branch sets and denominators exactly matched between these two sample cells.

| Three-worker cell | Dependency setup | Measured elapsed |
| --- | ---: | ---: |
| Cold | 1.094 s | 521.355 s |
| Warm | 0.076 s | 545.036 s |

The waits, checkout and dependency-cache state differ from real hosted PR CI. The serial reference remains in progress on the same volume. [Cold receipt](isolated-workers-3-cold.json) · [Warm receipt](isolated-workers-3-warm.json)
