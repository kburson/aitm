# Exact source qualification for #586

| Evidence | Identity |
| --- | --- |
| Ordered parent 1, base | `8f37406e1a68b49bfbd4072a8abb2d2da646011a` |
| Ordered parent 2, source head | `6a8d8db3b9f6460847804620e0f1dc764473e85f` |
| Synthetic merge | `8c044849af911c99be1f914fda09b0968f81cb2a` |
| Tested and independently reviewed tree | `971a3c8c333260c32a70232ee5e72b6855436f88` |

[Repository CI](https://github.com/kburson/aitm/actions/runs/46125354437/attempts/1) and [Core CI](https://github.com/kburson/aitm/actions/runs/46125354323/attempts/1) passed before readiness. The trusted verifier ran from the exact base [before readiness](2026-11-28-pr-586-verifier.json) and [with the reviewed tree before merge](2026-11-28-pr-586-premerge-verifier.json). [Independent Grok 4.7 SAR](2026-11-28-pr-586-source-sar.md) passed, and [all seven branch gates](2026-11-28-pr-586-branch-gates.json) passed. [Hosted attempt and collection receipt](2026-11-28-pr-586-hosted.json).

| Full unique Linux collection | Unit | Integration | Total | Strict test |
| --- | ---: | ---: | ---: | --- |
| aitm-core | 1077 | 85 | 1162 | 8500 < 9296 |
| aitm-usage | 1644 | 142 | 1786 | 14200 < 14288 |

Both hosted 92% unit floors passed. C28 adds thirteen unit nodes and one indispensable external-Git integration node. The installed proof exercises remote authored-sync custody, attempt preflight, the provisional attempt clock, and preservation of separate authored writes on refusal and conflict.
