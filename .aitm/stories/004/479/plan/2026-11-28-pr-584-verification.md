# Exact source qualification for #584

| Evidence | Identity |
| --- | --- |
| Ordered parent 1, base | `4ad5d16a49c1af8f5a812c60bc27098f8c7ce445` |
| Ordered parent 2, source head | `388cb834ccb263ef34f55a8be7621d20aa52230b` |
| Synthetic merge | `ba19b589ca3fa679f26611dbbd81d84357caad4b` |
| Tested and independently reviewed tree | `9e0d32c2946893f6a1177beef91e08a15479391f` |

[Repository CI](https://github.com/kburson/aitm/actions/runs/46128524295/attempts/1) and [Core CI](https://github.com/kburson/aitm/actions/runs/46128524335/attempts/1) passed before readiness. The trusted verifier ran from the exact base [before readiness](2026-11-28-pr-584-verifier.json) and [with the reviewed tree before merge](2026-11-28-pr-584-premerge-verifier.json). [Independent Grok 4.7 SAR](2026-11-28-pr-584-source-sar.md) passed, and [all seven branch gates](2026-11-28-pr-584-branch-gates.json) passed. [Hosted attempt and collection receipt](2026-11-28-pr-584-hosted.json).

| Full unique Linux collection | Unit | Integration | Total | Strict test |
| --- | ---: | ---: | ---: | --- |
| aitm-core | 1103 | 87 | 1190 | 8700 < 9520 |
| aitm-usage | 1644 | 142 | 1786 | 14200 < 14288 |

Both hosted 92% unit floors passed. C91 added pure placement and obligation cases. C28, C71 and C29 added one indispensable real Git contract each for installed transition and authored sync, atomic split publication, and installed kind and terminal routing. C105 added two composed-profile unit nodes.
