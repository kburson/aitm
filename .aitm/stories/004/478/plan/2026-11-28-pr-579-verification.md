# Exact source qualification for #579

| Evidence | Identity |
| --- | --- |
| Ordered parent 1, base | `d50ae9b2bc2731aa8e31aff8d6754c80db1f6f35` |
| Ordered parent 2, source head | `f841e183aa92bd6613cbc90cfd9a7e137d5d6f1b` |
| Synthetic merge | `e18df5d15e6f8c5e1b5ca4b90039aad6a7ec0d85` |
| Tested and independently reviewed tree | `64458f71e55822ce8cc821fcebc181375e78486f` |

[Repository CI](https://github.com/kburson/aitm/actions/runs/46121020618/attempts/1) and [Core CI](https://github.com/kburson/aitm/actions/runs/46121020662/attempts/1) passed before readiness. The trusted verifier ran from the exact base [before readiness](2026-11-28-pr-579-verifier.json) and [with the reviewed tree before merge](2026-11-28-pr-579-premerge-verifier.json). [Independent Grok 4.7 SAR](2026-11-28-pr-579-source-sar.md) passed, and [all seven branch gates](2026-11-28-pr-579-branch-gates.json) passed. [Hosted attempt and collection receipt](2026-11-28-pr-579-hosted.json).

| Full unique Linux collection | Unit | Integration | Total | Strict test |
| --- | ---: | ---: | ---: | --- |
| aitm-core | 1045 | 84 | 1129 | 8400 < 9032 |
| aitm-usage | 1644 | 142 | 1786 | 14200 < 14288 |

Both hosted 92% unit floors passed. The composition includes every reviewed leaf and the exact reviewed tree. C93 adds the sole external contract and one integration node, proving the exact accepted planning tree and source objects against real Git. C27, C72 and C94 add unit proofs only.
