# #575 exact source qualification

| Identity | Git object |
| --- | --- |
| Base and first parent | `2dfbe56bff0eefdb1f8d156f350da42899730ed0` |
| Source head and second parent | `5d9346f81363c55647abb48acb947a5c750812eb` |
| Hosted synthetic merge | `8cf065f9bb9d1ae53cb2688ee61edc52f0f67840` |
| Tested and reviewed tree | `2eed80405a1800cd820ebe29a71e1ae52c48991d` |

[Repository CI](https://github.com/kburson/aitm/actions/runs/46106458982/attempts/1) and [Core CI](https://github.com/kburson/aitm/actions/runs/46106458975/attempts/1) passed before readiness. The Core job printed and checked the exact candidate, ran all 1,056 product tests, ran the separate tooling check and passed Ruff. Repository CI retained 18,749/20,685 product line coverage and 1,060/1,133 helper line coverage. [Hosted candidate and collection receipt](2026-11-27-pr-575-hosted.json).

| Linux full unique collection | Unit | Integration | Total | Strict integer gate |
| --- | ---: | ---: | ---: | --- |
| aitm-core | 976 | 80 | 1056 | 8000 < 8448 |
| aitm-usage | 1644 | 142 | 1786 | 14200 < 14288 |

Both hosted 92% unit floors passed. The 36 new Core unit cases exercise the C57 policy against in-memory evidence. C57 adds zero integration cases and changes no classifications. The inherited C24 Git apply case remains covered in the Core integration lane.

Local non-editable verification passed the 68 focused C24/C57 cases and the separate tooling check. The earlier editable invocation exposed the tooling fixture's deliberate prohibition on source paths in `sys.path`. The hosted-style rerun passed. The original full local macOS run was interrupted during a subprocess wait. Hosted Linux ran the full product suite. Local replay of the archived Core design manual SPR and portable native-consensus XPR validated both under explicitly configured fixture policies.

The [first source SAR](2026-11-27-pr-575-source-sar-r1.md) requested changes. The trusted verifier ran from the clean exact base [before readiness](2026-11-27-pr-575-verifier.json) and [again with the reviewed tree before merge](2026-11-27-pr-575-premerge-verifier.json). The [independent SAR](2026-11-27-pr-575-source-sar.md) passed on the exact candidate. GitHub reported a clean merge state and [all seven successful checks](2026-11-27-pr-575-branch-gates.json).
