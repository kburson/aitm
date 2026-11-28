# Exact source qualification for #585

| Evidence | Identity |
| --- | --- |
| Ordered parent 1, base | `ca885a382eef28d4491461661243612269d18acc` |
| Ordered parent 2, source head | `56f2717055c3d41115b10bb98390525c2f0912c2` |
| Synthetic merge | `02962b254bce27b35ea89be5473242943e3dcd22` |
| Tested and independently reviewed tree | `f2bba1a9a67049515ae8d4981b0caf128e7bf2ab` |

[Repository CI](https://github.com/kburson/aitm/actions/runs/46122372201/attempts/1) and [Core CI](https://github.com/kburson/aitm/actions/runs/46122372299/attempts/1) passed before readiness. The trusted verifier ran from the exact base [before readiness](2026-11-28-pr-585-verifier.json) and [with the reviewed tree before merge](2026-11-28-pr-585-premerge-verifier.json). [Independent Grok 4.7 SAR](2026-11-28-pr-585-source-sar.md) passed, and [all seven branch gates](2026-11-28-pr-585-branch-gates.json) passed. [Hosted attempt and collection receipt](2026-11-28-pr-585-hosted.json).

| Full unique Linux collection | Unit | Integration | Total | Strict test |
| --- | ---: | ---: | ---: | --- |
| aitm-core | 1064 | 84 | 1148 | 8400 < 9184 |
| aitm-usage | 1644 | 142 | 1786 | 14200 < 14288 |

Both hosted 92% unit floors passed. C91 adds 19 pure unit nodes for typed graph and capability validation. The predecessor Git contract and other external integration contracts carry forward.
