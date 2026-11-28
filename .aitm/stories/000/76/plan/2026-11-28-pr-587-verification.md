# Exact source qualification for #587

| Evidence | Identity |
| --- | --- |
| Ordered parent 1, base | `961eeadea49af380f99a5903bcec6a0b81e50fba` |
| Ordered parent 2, source head | `690a2cd9bcbdea543dca18030fecb82ed891d7f1` |
| Synthetic merge | `b097d972bd48e36313dfd3fd7e9c97450f38cc34` |
| Tested and independently reviewed tree | `ceddf175f1e85672a9c05bff6ade24d2219f9e7f` |

[Repository CI](https://github.com/kburson/aitm/actions/runs/46126590372/attempts/1) and [Core CI](https://github.com/kburson/aitm/actions/runs/46126590384/attempts/1) passed before readiness. The trusted verifier ran from the exact base [before readiness](2026-11-28-pr-587-verifier.json) and [with the reviewed tree before merge](2026-11-28-pr-587-premerge-verifier.json). [Independent Grok 4.7 SAR](2026-11-28-pr-587-source-sar.md) passed, and [all seven branch gates](2026-11-28-pr-587-branch-gates.json) passed. [Hosted attempt and collection receipt](2026-11-28-pr-587-hosted.json).

| Full unique Linux collection | Unit | Integration | Total | Strict test |
| --- | ---: | ---: | ---: | --- |
| aitm-core | 1090 | 86 | 1176 | 8600 < 9408 |
| aitm-usage | 1644 | 142 | 1786 | 14200 < 14288 |

Both hosted 92% unit floors passed. C71 adds thirteen unit nodes and one indispensable installed Git contract for atomic scope-file publication, transition and kind invalidation.
