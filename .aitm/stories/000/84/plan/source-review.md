# Source verification and review

Source base `4e896e049370df58fe870dc80790401056218b97`. Reviewed head `0df428e4fa5df25fac97409872bec3d672f45bf1`.

## Observed verification

The locked package suite passed 69 tests on Python 3.13 on the exact integration head. Ruff and diff checks passed. The implementer also verified a fresh wheel installation and its CLI version and help entry points. The RED record covered 33 earlier failures, two edge cases, and six physical-overlap cases on the prior source. Observed implementer intervals total 24 minutes and 54 seconds across original development and both repairs. The four-hour leaf cap remains in force.

## Independent source review

The first source review reproduced ACL exposure, lock replacement, stale cursor writes, a constraint-free schema, credential-like metadata and foreign references. The approved amendment resolved cross-leaf ownership. The first repaired head fixed those cases but admitted a second writer under an APFS firmlink alias. The final independent reviewer accepted specification compliance and code quality on this exact head. Twelve independent overlap probes refused existing and missing roots across equality and both ancestry directions without creating private state. A legitimate alias remained usable and a competing process received writer-active. The earlier independent regression matrix remains verified.

The reviewed source is staged on the #83 integration branch.
