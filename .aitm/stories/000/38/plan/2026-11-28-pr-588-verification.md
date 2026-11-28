# Exact source qualification for #588

| Evidence | Identity |
| --- | --- |
| Ordered parent 1, base | `f614c3aa2de3350e0b7a5d741ec60f75d989aac1` |
| Ordered parent 2, source head | `685261dc17bac0a11dd0275f1a379c82fc2a4ae7` |
| Synthetic merge | `a7809d6287d081102428d1ae9563acde3ddc8c63` |
| Tested and independently reviewed tree | `855801e3081cd9024e0848eae4391209a804273f` |

[Repository CI](https://github.com/kburson/aitm/actions/runs/46127727045/attempts/1) and [Core CI](https://github.com/kburson/aitm/actions/runs/46127727043/attempts/1) passed before readiness. The trusted verifier ran from the exact base [before readiness](2026-11-28-pr-588-verifier.json) and [with the reviewed tree before merge](2026-11-28-pr-588-premerge-verifier.json). [Independent Grok 4.7 SAR](2026-11-28-pr-588-source-sar.md) passed, and [all seven branch gates](2026-11-28-pr-588-branch-gates.json) passed. [Hosted attempt and collection receipt](2026-11-28-pr-588-hosted.json).

| Full unique Linux collection | Unit | Integration | Total | Strict test |
| --- | ---: | ---: | ---: | --- |
| aitm-core | 1101 | 87 | 1188 | 8700 < 9504 |
| aitm-usage | 1644 | 142 | 1786 | 14200 < 14288 |

Both hosted 92% unit floors passed. C29 adds eleven unit nodes and one indispensable installed Git contract for production epic mode and terminal route publication against independent code and planning stores.
