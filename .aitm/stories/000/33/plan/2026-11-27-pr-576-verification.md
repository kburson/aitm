# Exact source qualification for #576

| Evidence | Identity |
| --- | --- |
| Ordered parent 1, base | `c49b535d522f7fca1b8e5c6038b1783993e1c012` |
| Ordered parent 2, source head | `624f09c37d449fedfcf889658efc692bcee87d97` |
| Synthetic merge | `ce3bf214bf20ed440f9c781adfb1de87c535db88` |
| Tested and independently reviewed tree | `c4728bf59277cbc6ed63dbcf8a5f5b12e4aa7bc5` |

[Repository CI](https://github.com/kburson/aitm/actions/runs/46110731549/attempts/1) and [Core CI](https://github.com/kburson/aitm/actions/runs/46110731550/attempts/1) passed before readiness. The trusted verifier ran from the exact base [before readiness](2026-11-27-pr-576-verifier.json) and [with the reviewed tree before merge](2026-11-27-pr-576-premerge-verifier.json). [Independent Grok 4.7 SAR](2026-11-27-pr-576-source-sar.md) passed, and [all seven branch gates](2026-11-27-pr-576-branch-gates.json) passed. [Hosted attempt and collection receipt](2026-11-27-pr-576-hosted.json).

| Full unique Linux collection | Unit | Integration | Total | Strict test |
| --- | ---: | ---: | ---: | --- |
| aitm-core | 988 | 81 | 1069 | 8100 < 8552 |
| aitm-usage | 1644 | 142 | 1786 | 14200 < 14288 |

Both hosted 92% unit floors passed. One new integration case checks public native source and blob digests against real Git patch replay, preserves the separate revision and finalization commits, and verifies claim and predecessor timing without rewriting originals. Twelve unit cases cover unknown, stale and cross-participant timing and nonaccepting native status. The affected local suites passed 81 tests and the separate tooling check. Two actual retained native Core design archives replayed and validated under explicit fixture policies.
