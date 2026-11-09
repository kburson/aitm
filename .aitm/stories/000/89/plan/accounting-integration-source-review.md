# U05 accounting integration verification

Integration base `bf350c0a655892994c725d01e86552d0b15293ef`. Independently accepted exact head `296c6c314453c9682df62f1174d5a999d81795c9`. [Original source review](source-review.md) retained.

The locked package suite passed 351 tests on the exact integration source. Ruff and diff checks passed.

Independent exact spec PASS and quality PASS. Twelve focused reviewer cases covered exact terminal reconciliation, split commits and reopen, sparse omissions versus explicit nonstandard and invalid modes, late previously priced records and preserved original scope. Native 19 and 26 Standard requests still reconcile. Only the Claude adapter and its tests changed. A contradicted request retains measured usage with Unknown current API-equivalent cost. Earlier as-of price remains available.
