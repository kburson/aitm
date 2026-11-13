# #267 local TIA and pytest-testmon advisory measurement

AITM `766504a02aaeb9dda339d588172dd7d5bdbd2b3f` on Darwin 26.6.2 arm64 with APFS and native ACL support. One worker per profile, Python 3.13.9, pytest 9.2.0, uv 0.10.6, coverage 7.17.2 and pytest-testmon 2.3.0.

The unchanged serial reference observed 1,412 test IDs in 359.66s. The unchanged Testmon history run observed 1,412 IDs in 604.59s. Both profiles in the history run used a fresh database with selection disabled. Each warm case started from a copy of the corresponding unchanged history.

## Baseline diagnostics

The unchanged serial reference retained 1 failure(s). The unchanged full Testmon history run completed cleanly on the same inventory. The evidence includes 3 isolated unchanged rechecks and the original baseline failure phase.

- `packages/aitm-usage/tests/test_monitor_journal.py::test_pair_preserves_frontiers_when_one_native_completion_is_invalid[repeated-counter-rival]` failed during setup.

## Seed measurements

| Seed | Serial IDs / wall | Expected IDs | Serial pass-to-failure IDs | #143 plan / IDs / wall | #143 expected misses / expected extras / observed misses | Testmon IDs / wall | Testmon expected misses / expected extras / observed misses |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| cli | 1412 / 323.46s | 1 | 18 | full / 1412 / 15.62s | 0 / 1411 / 0 | 136 / 17.52s | 1 / 136 / 10 |
| non-code | 1412 / 374.20s | 0 | 0 | full / 1412 / 15.62s | 0 / 1412 / 0 | 0 / 1.00s | 0 / 0 / 0 |
| uncertain | 1412 / 363.33s | 1 | 1 | full / 1412 / 15.56s | 0 / 1411 / 0 | 0 / 1.01s | 1 / 0 / 1 |
| unavailable | 1412 / 323.46s | 1 | 18 | unavailable / 0 / 0.12s | 1 / 0 / 18 | 1412 / 548.84s | 0 / 1411 / 0 |

Expected misses are predeclared IDs omitted by the method. Expected extras are selected IDs outside that predeclared lower bound. Observed misses are IDs whose serial outcome changed from pass to failure and which the method omitted. A full fallback's extras include every full-run obligation outside the lower bound. The unavailable case reuses the full CLI-seed reference. Wall time sums the two profiles for direct serial and Testmon. The #143 plan wall includes dependency setup, snapshot verification and collection.

## Method observations

- **cli.** #143 plan exited 0. It reported `uncertain impact for 1 changed path(s): dynamic-import, unresolved-import`. `--run` exited 1 with status `failed` after 340.73s command wall and 325.50s execution stage. It recorded 1,412 executed IDs. Testmon recorded ci-helpers exit 0 (0 selected), product-cli exit 1 (136 selected).
- **non-code.** #143 plan exited 0. It reported `uncertain impact for 1 changed path(s): dynamic-import, unresolved-import`. Testmon recorded ci-helpers exit 0 (0 selected), product-cli exit 0 (0 selected).
- **uncertain.** #143 plan exited 0. It reported `uncertain impact for 1 changed path(s): dynamic-import, unresolved-import`. Testmon recorded ci-helpers exit 0 (0 selected), product-cli exit 0 (0 selected).
- **unavailable.** #143 plan exited 2. It reported `base-ref: cannot resolve a commit`. `--run` exited 2 with status `refused` after 0.11s command wall and 0.00s execution stage. It recorded 0 executed IDs. Testmon recorded ci-helpers exit 1 (196 selected), product-cli exit 1 (1216 selected).

## Evidence

The sanitized machine-readable evidence has SHA-256 `7edc9e3e109786b5fb00eb11961dd3c4947898886642196e94e4d005cfff11c5`. It binds the fixture patches and raw diagnostic files by digest and lists exact selected, omitted, extra and failed node IDs, plus phase outcomes. Raw tracebacks and full history databases are retained in private scratch. The [recipe](recipe.md) and [implementer notes](benchmark-notes.md) record fixture conditions and the baseline diagnostic.

Use these results for advisory TIA evaluation. #103 remains the merge gate.

Signed `codex-collaboration:/root/measure267`.
