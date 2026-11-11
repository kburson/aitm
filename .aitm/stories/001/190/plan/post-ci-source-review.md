# #190 independent source review

**Verdict — accepted.** Signed 2026-11-10 America/Chicago (2026-11-11 UTC) by Codex `/root/pickup186`, independent from the implementer. Off-platform review. Native GitHub approval absent. No actionable blockers for this source revision.

PR #219 targets `trunk` at base `72ca2d2535248844b164014d7817bffec0e9fb7e`. Reviewed head `577ba9382cd8298922a83803aa3e66abdc853fa3`, source and hosted tested tree `4d0144095980203ca7833e3581adac0e32cee6a4`, and hosted tested merge `d7e93ca475bbfb2e54870ddb348fc8e355073dd3`. [PR #219](https://github.com/kburson/aitm/pull/219)

Reviewed `tools/story_dashboard/snapshot.py` and `tools/story_dashboard/tests/test_snapshot.py`, the complete diff against the declared base, against the accepted A05 contract and pickup SHA-256 `160da30673d6beb870a9ab56f7bae2b53238c1fe8304d2056acc8ce6c167d345`. The snapshot serializes the delivered timing and usage projections with canonical units, coverage, provenance and commit-scoped links. It binds the validation report to the exact snapshot bytes.

## Findings resolved

1. `snapshot.py:194` and the estimate serializer preserve a safe basis from the exact selected estimate event. Missing or unsupported basis remains null. The regression covers both outcomes.
2. `snapshot.py:156` admits supported lifecycle states, matching graduation issue identities and shaped document acceptances as progress. The regression confirms malformed later events cannot displace valid progress and a valid acceptance can advance it. The later planning pin retains 515 valid state, 179 graduation and 98 document acceptance events.
3. `snapshot.py:368` and `:380` bind output to a checked directory descriptor and create, replace and clean up temporary files relative to that descriptor. The regression confirms a substituted path cannot redirect output into the other checkout.

## Verification

- Confirmed the clean checkout at the exact reviewed head and tree. The base diff contains only the two accepted additions and `git diff --check` passes. Independently ran all eight focused snapshot tests. Candidate evidence reports all 56 dashboard tests, Ruff checks and formatting checks passing.
- Independently rebuilt the snapshot and validation bytes in memory at as-of `2026-11-11T04:23:16Z` for both retained planning pins and reproduced the two clean reader digests in the verification note. Historical pin `17761cc1928fd916cf32a9c078d4a742bfcb32b8` has 169 stories. Snapshot SHA-256 `e46da18999caf132dcc451e9ae8e7b12dd5517a49113f85931c48d93c5e3772a`, validation SHA-256 `3497de8b8d908759aa0e62bd313de3bced70e4fba6bd82e6aaa2dfa227821ab6`. Later pin `200bae51aa458152f98b98a34a29fdc176c4f6d1` has 179 stories. Snapshot SHA-256 `bcd22bdb3a9150cdd85bdf9c8ba4b723240768dfc630db3371c80fa8b5391b5a`, validation SHA-256 `4f3a8a69369f4a5dd113dd19da04f27388c252f11676f6cb40692d3932774fec`.
- The candidate proof confirms parity for all ten historical direct and inclusive Actual values, with partial coverage. Both reviewed pins preserve #111 implementation elapsed of 774,000 ms and Unknown all-phase elapsed. Cost remains Unknown without a verified selector. The focused selected-report test checks the exact USD decimal and separate Cost cutoff.
- The delivered trunk verifier returned pass for canonical run 42959980651 attempt 1. PR, head, base, tested merge and tree match this review. The signed proof covers `python-base`, `python`, `quality`, `file-checks`, `collect-evidence` and `aitm-ci`. Evidence artifact `13828713322` has archive SHA-256 `227e6068ef93e84737727c356e89faa922f294e51173b5d5036b88c84d2a915f`. [Hosted run](https://github.com/kburson/aitm/actions/runs/42959980651/attempts/1)
