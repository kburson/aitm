# #172 Advisory testmon trial on AITM tests

This local trial used PR #197 head `2dd98bb7f5029188cf693e7c1317dd5fc0675e2b`
and tree `35ad17ad3121728482ba9acdfcdd8e724c56289f`. It is a representative
sample for #172, which remains in Backlog. The hosted workflow and
production suite policy retain their existing behavior.

## Method

Two separate scratch copies of the exact tree used Python 3.13.9,
pytest 9.2.0, pytest-xdist 3.8.0, pytest-testmon 2.3.0, and Coverage.py
7.17.2. On a host with ten available cores, `-n 8 --dist worksteal`
ran the 80% local setting. Each copy seeded its own testmon history with
`--testmon --testmon-noselect`, using 47 TIA inventory tests and five
`aitm-usage` Grok pricing tests. The changed copies ran testmon selection
and then a complete 52-test reference run. A local observer captured
the exact test IDs and outcomes from the xdist controller.

| Scratch-only change | Testmon selection | Full sample |
| --- | --- | --- |
| `pricing.py`, behavior-neutral keyword argument in `load_monitor_rate_card` | Three tests selected and passed | 52 passed |
| `rates/monitor/2026-11-10.json`, change uncached input rate from `2` to `3` | Zero selected, CLI exited 0 | 51 passed, one failed |

The asset failure was
`packages/aitm-usage/tests/test_grok_pricing.py::test_grok_rate_classes_do_not_use_claude_defaults`.
That test calls `load_monitor_rate_card`, which reads the changed JSON
resource. The testmon-selected run missed this dependency and the
resulting failure. The advisory run with `--testmon-noselect` also ran
all 52 tests and surfaced the failure.

## Suite organization

The Python edit selected these tests in
`packages/aitm-usage/tests/test_grok_pricing.py`.

- `test_grok_card_rejects_unproven_rate_classes_and_models`
- `test_grok_rate_classes_do_not_use_claude_defaults`
- `test_unknown_grok_rate_and_provider_ticks_remain_separate`

The reviewed `suites.json` already maps all three to owner `aitm-usage`,
suite `unit`, and isolation group `grok-pricing`. The five pricing tests
contain four unit tests and one integration test. The 47 inventory
tooling tests sit outside the current #103 product and helper profiles.
The observed cluster supports the existing group. Classification and
shard assignment still come from the reviewed policy.

## Disposition

Testmon can suggest Python dependencies or test ordering. For #172, compare
those suggestions with the trusted selection and full reference results.
The sample's worker startup dominated elapsed time, so this trial provides
selection and missed-impact evidence. It does not establish a speedup.
Unknown dependency impact continues to trigger the full applicable suite.
