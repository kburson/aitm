# Exact source qualification for #580

| Evidence | Identity |
| --- | --- |
| Ordered parent 1, base | `33516757c6bb3ee2397a5827dc249184d6bfc835` |
| Ordered parent 2, source head | `ab5d9c4d00d7648b978cf4c780277138cf7914f6` |
| Synthetic merge | `b0a3466398820a822264c77fac2129451ca7ab6d` |
| Tested and independently reviewed tree | `fd705f42963691ecfc8f82eabffa9d69e59eeaf9` |

[Repository CI](https://github.com/kburson/aitm/actions/runs/46117807950/attempts/1) and [Core CI](https://github.com/kburson/aitm/actions/runs/46117808050/attempts/1) passed before readiness. The trusted verifier ran from the exact base [before readiness](2026-11-28-pr-580-verifier.json) and [with the reviewed tree before merge](2026-11-28-pr-580-premerge-verifier.json). [Independent Grok 4.7 SAR](2026-11-28-pr-580-source-sar.md) passed, and [all seven branch gates](2026-11-28-pr-580-branch-gates.json) passed. [Hosted attempt and collection receipt](2026-11-28-pr-580-hosted.json).

| Full unique Linux collection | Unit | Integration | Total | Strict test |
| --- | ---: | ---: | ---: | --- |
| aitm-core | 1034 | 83 | 1117 | 8300 < 8936 |
| aitm-usage | 1644 | 142 | 1786 | 14200 < 14288 |

Both hosted 92% unit floors passed. C27 adds no integration nodes or external contracts. Its normal transaction and preflight refusal are covered by the in-process MemoryBackend proof.
