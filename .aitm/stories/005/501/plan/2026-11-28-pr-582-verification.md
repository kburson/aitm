# Exact source qualification for #582

| Evidence | Identity |
| --- | --- |
| Ordered parent 1, base | `faa339e76a6fdd5b9aec026fe5594635cb4c123d` |
| Ordered parent 2, source head | `bf44d734d536d210f840923903803764b3843b44` |
| Synthetic merge | `298d6b753258287ac8584dc10acef4f600ea70e5` |
| Tested and independently reviewed tree | `f860803aa120568ecc60b7250d45893da0382afa` |

[Repository CI](https://github.com/kburson/aitm/actions/runs/46119724387/attempts/1) and [Core CI](https://github.com/kburson/aitm/actions/runs/46119724344/attempts/1) passed before readiness. The trusted verifier ran from the exact base [before readiness](2026-11-28-pr-582-verifier.json) and [with the reviewed tree before merge](2026-11-28-pr-582-premerge-verifier.json). [Independent Grok 4.7 SAR](2026-11-28-pr-582-source-sar.md) passed, and [all seven branch gates](2026-11-28-pr-582-branch-gates.json) passed. [Hosted attempt and collection receipt](2026-11-28-pr-582-hosted.json).

| Full unique Linux collection | Unit | Integration | Total | Strict test |
| --- | ---: | ---: | ---: | --- |
| aitm-core | 1038 | 84 | 1122 | 8400 < 8976 |
| aitm-usage | 1644 | 142 | 1786 | 14200 < 14288 |

Both hosted 92% unit floors passed. C93 adds one indispensable real Git integration node. It proves exact Git planning reads and source commit/tree identity across all three bases and stale or foreign evidence. C93 adds no other integration contract.
