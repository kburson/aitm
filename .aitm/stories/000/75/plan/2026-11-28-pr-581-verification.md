# Exact source qualification for #581

| Evidence | Identity |
| --- | --- |
| Ordered parent 1, base | `765b99d23e4e407d98e83e76d5b6b325e9b9048a` |
| Ordered parent 2, source head | `24b681ee6819f3e3fb3550c58bf95b1b2e8e9e42` |
| Synthetic merge | `28675f8e4574fc76cfe3f1641ed63f23a4b3fe7f` |
| Tested and independently reviewed tree | `e192ebbf16bd052fd61c37c98efad1c034761db2` |

[Repository CI](https://github.com/kburson/aitm/actions/runs/46118743396/attempts/1) and [Core CI](https://github.com/kburson/aitm/actions/runs/46118743340/attempts/1) passed before readiness. The trusted verifier ran from the exact base [before readiness](2026-11-28-pr-581-verifier.json) and [with the reviewed tree before merge](2026-11-28-pr-581-premerge-verifier.json). [Independent Grok 4.7 SAR](2026-11-28-pr-581-source-sar.md) passed, and [all seven branch gates](2026-11-28-pr-581-branch-gates.json) passed. [Hosted attempt and collection receipt](2026-11-28-pr-581-hosted.json).

| Full unique Linux collection | Unit | Integration | Total | Strict test |
| --- | ---: | ---: | ---: | --- |
| aitm-core | 1038 | 83 | 1121 | 8300 < 8968 |
| aitm-usage | 1644 | 142 | 1786 | 14200 < 14288 |

Both hosted 92% unit floors passed. C72 adds no integration nodes or external contracts. Its MemoryBackend cases exercise typed descriptors, graph refusal, stable identity and current C26 applicability.
