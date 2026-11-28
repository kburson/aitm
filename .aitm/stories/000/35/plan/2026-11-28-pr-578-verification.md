# Exact source qualification for #578

| Evidence | Identity |
| --- | --- |
| Ordered parent 1, base | `e2d6fe48e8512aac5b15966d6b098c71c00c5068` |
| Ordered parent 2, source head | `7ff573234529117942d1da86d0d6e7b9b4826c75` |
| Synthetic merge | `002af43d5bca649dbcb23e70d12bba92528c3857` |
| Tested and independently reviewed tree | `5b7f3c7d4e7f4d8bea30e5449a0816d51747336a` |

[Repository CI](https://github.com/kburson/aitm/actions/runs/46114194674/attempts/1) and [Core CI](https://github.com/kburson/aitm/actions/runs/46114194693/attempts/1) passed before readiness. The trusted verifier ran from the exact base [before readiness](2026-11-28-pr-578-verifier.json) and [with the reviewed tree before merge](2026-11-28-pr-578-premerge-verifier.json). [Independent Grok 4.7 SAR](2026-11-28-pr-578-source-sar.md) passed, and [all seven branch gates](2026-11-28-pr-578-branch-gates.json) passed. [Hosted attempt and collection receipt](2026-11-28-pr-578-hosted.json).

| Full unique Linux collection | Unit | Integration | Total | Strict test |
| --- | ---: | ---: | ---: | --- |
| aitm-core | 1030 | 83 | 1113 | 8300 < 8904 |
| aitm-usage | 1644 | 142 | 1786 | 14200 < 14288 |

Both hosted 92% unit floors passed. One new integration node proves actual installed CLI behavior against a real remote and authoring reservation, including the atomic FUR/capsule publication, interrupted projection recovery, immutable source refusal, stale CAS, capped or disallowed historical evidence, and separate exact acceptance for design and plan. Twenty-four focused unit cases cover authored projection, required-level coverage, applicability, role and identity mapping.
