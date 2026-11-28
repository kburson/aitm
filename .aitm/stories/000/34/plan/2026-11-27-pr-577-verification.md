# Exact source qualification for #577

| Evidence | Identity |
| --- | --- |
| Ordered parent 1, base | `0d3846b6587bd1b5889ac4080963877e003a7433` |
| Ordered parent 2, source head | `c718debe5d2cf7dd508c3607abdfaed748a7819d` |
| Synthetic merge | `be50940f50d2bb870ba0b39f5efd8af1d785da80` |
| Tested and independently reviewed tree | `82dd4b69b1b2d3371cf4d7545813e2a93ef88664` |

[Repository CI](https://github.com/kburson/aitm/actions/runs/46112297369/attempts/1) and [Core CI](https://github.com/kburson/aitm/actions/runs/46112297391/attempts/1) passed before readiness. The trusted verifier ran from the exact base [before readiness](2026-11-27-pr-577-verifier.json) and [with the reviewed tree before merge](2026-11-27-pr-577-premerge-verifier.json). [Independent Grok 4.7 SAR](2026-11-27-pr-577-source-sar.md) passed, and [all seven branch gates](2026-11-27-pr-577-branch-gates.json) passed. [Hosted attempt and collection receipt](2026-11-27-pr-577-hosted.json).

| Full unique Linux collection | Unit | Integration | Total | Strict test |
| --- | ---: | ---: | ---: | --- |
| aitm-core | 1006 | 82 | 1088 | 8200 < 8704 |
| aitm-usage | 1644 | 142 | 1786 | 14200 < 14288 |

Both hosted 92% unit floors passed. One new integration case drives a real installed CLI, write reservation through the planning Git store, uncommitted authored bytes, predecessor and hash refusals, immutable response retry, exact patch replay, and idempotent completion. Eighteen unit cases cover timing basis, missing or partial coverage, exclusions, overlapping actors, wall union, and attribution. Both old integration lanes remain unchanged.
