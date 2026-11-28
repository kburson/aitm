# Exact source qualification for #573

| Evidence | Identity |
| --- | --- |
| Ordered parent 1, base | `8a62c860a8662156de26329d07baf09c92bd9ea9` |
| Ordered parent 2, source head | `5151beaed72122410e4e794f8c09b358be56b161` |
| Synthetic merge | `25d265760406f97de7afca12f5a0d8b2b010f364` |
| Tested and independently reviewed tree | `5b7f3c7d4e7f4d8bea30e5449a0816d51747336a` |

[Repository CI](https://github.com/kburson/aitm/actions/runs/46114882928/attempts/1) and [Core CI](https://github.com/kburson/aitm/actions/runs/46114882915/attempts/1) passed before readiness. The trusted verifier ran from the exact base [before readiness](2026-11-28-pr-573-verifier.json) and [with the reviewed tree before merge](2026-11-28-pr-573-premerge-verifier.json). [Independent Grok 4.7 SAR](2026-11-28-pr-573-source-sar.md) passed, and [all seven branch gates](2026-11-28-pr-573-branch-gates.json) passed. [Hosted attempt and collection receipt](2026-11-28-pr-573-hosted.json).

| Full unique Linux collection | Unit | Integration | Total | Strict test |
| --- | ---: | ---: | ---: | --- |
| aitm-core | 1030 | 83 | 1113 | 8300 < 8904 |
| aitm-usage | 1644 | 142 | 1786 | 14200 < 14288 |

Both hosted 92% unit floors passed. The complete composition proves all five verified leaf landings with no unrelated changes, the upstream trunk receipts, and the exact reviewed tree. Four added integration nodes prove real Git apply for portable reconstruction, public native lineage and source bytes against Git replay, installed live timing against the Git planning store, and transactional review import and acceptance through an installed CLI. C57 proves policy and topology in unit cases and adds no integration nodes.
