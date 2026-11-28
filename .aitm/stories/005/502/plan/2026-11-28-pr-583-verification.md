# Exact source qualification for #583

| Evidence | Identity |
| --- | --- |
| Ordered parent 1, base | `e448e077f3f8358f0285ff85546e2e53df470ed3` |
| Ordered parent 2, source head | `e47e576341e5dcba70c9a4d1d5886545bb7295e0` |
| Synthetic merge | `436c1cf58db2f4c2e8b42b5de369e17dfa807aef` |
| Tested and independently reviewed tree | `64458f71e55822ce8cc821fcebc181375e78486f` |

[Repository CI](https://github.com/kburson/aitm/actions/runs/46120523944/attempts/1) and [Core CI](https://github.com/kburson/aitm/actions/runs/46120523850/attempts/1) passed before readiness. The trusted verifier ran from the exact base [before readiness](2026-11-28-pr-583-verifier.json) and [with the reviewed tree before merge](2026-11-28-pr-583-premerge-verifier.json). [Independent Grok 4.7 SAR](2026-11-28-pr-583-source-sar.md) passed, and [all seven branch gates](2026-11-28-pr-583-branch-gates.json) passed. [Hosted attempt and collection receipt](2026-11-28-pr-583-hosted.json).

| Full unique Linux collection | Unit | Integration | Total | Strict test |
| --- | ---: | ---: | ---: | --- |
| aitm-core | 1045 | 84 | 1129 | 8400 < 9032 |
| aitm-usage | 1644 | 142 | 1786 | 14200 < 14288 |

Both hosted 92% unit floors passed. C94 adds seven unit nodes, zero integration nodes and zero external contracts. It preserves the existing C93 Git contract.
