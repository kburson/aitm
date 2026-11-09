# Source verification and review

Source base `0df428e4fa5df25fac97409872bec3d672f45bf1`. Reviewed head `67e888d720e67cb99e6e019fa1f0b6dc7510f40e`.

## Observed verification

The exact integration head passed 101 locked package tests on Python 3.13, plus Ruff and diff checks. The implementer retained RED/GREEN for 32 scope tests, including actual CLI publication under an active writer lease, pending and final dispositions, conflict, owner reassignment, concurrent publication and acknowledgment, and earlier as-of history. Observed implementation intervals total 24m 24s across the original candidate and two fixes.

## Independent source review

The independent reviewer accepted specification compliance and code quality at the exact staged head. The first review exposed plain development defaults, generation order across streams, delayed pending-location loss and a scope-only dispatch. The first repair fixed those cases and revealed a lineage edge when later provider rows add request or message IDs. The final repair preserves pre-rebind observations by admitted immutable key and leaves new old-stream work and ambiguous identities Unknown. Provider ordering remains fixture-proven. U03–U05/U08 own real provider admission and U12 owns the separate-process crash proof.

The reviewed source is staged on the #83 integration branch.
