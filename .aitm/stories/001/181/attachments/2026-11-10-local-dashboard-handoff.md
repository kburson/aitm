# #181 local story dashboard handoff

Slices A and B are delivered through all eight child issues. The scoped planning status, GitHub Closed Completed and AITM-PY Done were verified for each child.

| Story | Board | Direct Actual (ms) | Coverage | Admitted timing receipts |
| --- | --- | ---: | --- | ---: |
| [#186](https://github.com/kburson/aitm/issues/186) | Done | 4,087,308 | Partial | 1 |
| [#187](https://github.com/kburson/aitm/issues/187) | Done | 1,880,699 | Partial | 1 |
| [#188](https://github.com/kburson/aitm/issues/188) | Done | 1,494,000 | Partial | 5 |
| [#189](https://github.com/kburson/aitm/issues/189) | Done | 602,000 | Partial | 4 |
| [#190](https://github.com/kburson/aitm/issues/190) | Done | 776,000 | Partial | 3 |
| [#191](https://github.com/kburson/aitm/issues/191) | Done | 294,901 | Partial | 4 |
| [#192](https://github.com/kburson/aitm/issues/192) | Done | 1,160,677 | Partial | 4 |
| [#193](https://github.com/kburson/aitm/issues/193) | Done | 296,372 | Partial | 3 |

[Final dashboard planning pin](https://github.com/kburson/aitm/commit/3a28d392ad0c5782b1898b387a4ecbc8e694ecb1) and cutoff `2026-11-11T05:33:20Z` produced snapshot SHA-256 `f500e9725452af95d8fb4e58ec613a786b95534071b85e17f51eb06e4679c510` and standalone dashboard SHA-256 `0fad4c852595a17c7909ea6f12f77ed78bddd79f29e240d1b872f1de025d7a1b`. In this pin #181 records 13,754 ms of direct orchestration and 10,591,957 ms of descendant work, totaling 10,605,711 ms of partial Actual. The local HTML was opened with its filters and both drilldowns in an offline browser with zero automatic web requests. For exact refresh commands, see the [quick start](https://github.com/kburson/aitm/blob/bc8063b66522ed3a27c95d1bb0546f1e73249612/tools/story_dashboard/README.md).

B02 independently qualified [the historical seed](https://github.com/kburson/aitm/commit/17761cc1928fd916cf32a9c078d4a742bfcb32b8) and [the manual board pilot](https://github.com/kburson/aitm/commit/527dce9bd7847181a67dc23c6bb2c9844f15c87f). The #191 board sample read back 0.0014 h with Partial coverage and blank Cost. Owner wait in that pinned sample is Unknown because the response boundary was missing. Estimate calibration uses complete Actual for the same phase and agent scope.

Slice C remains the #181 production integration checkpoint with Core #2 and Usage Monitor #100. Its reviewed [coordination boundaries](timing-and-usage-coordination.md) preserve the contracts for provider-independent timing, usage and pricing.
