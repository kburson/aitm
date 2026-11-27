# #497 delivery checklist

Attempt 1. Codex is the implementing agent and closure owner. [Accepted pickup](2026-11-27-pickup.md) · [Pickup review](2026-11-27-pickup-review.md).

- [x] Published [draft PR #539](https://github.com/kburson/aitm/pull/539) at base `7f5b3fb62a83f3f04fea6c5a5ceb1bdaeb04ef32` and head `a02e7248fd2a88b9e113ddca980607f2f01f746f`.
- [x] Locked installed Core passed 99 tests and Ruff. Markdown lint passed for all four documents. Verified 19 typed decision vectors across eight groups and the source and review references.
- [ ] Check hosted repository CI and compare Core inputs with the passing hosted baseline under the path filter.
- [ ] Mark ready, obtain Grok 4.7 SAR and run the trusted verifier.
- [ ] Verify the story landing and the aggregate trunk admission in PR #536, then record sign-off, Agent Cost and Done.

## Hosted verification

[CI run 45991314542](https://github.com/kburson/aitm/actions/runs/45991314542) passed on base `7f5b3fb62a83f3f04fea6c5a5ceb1bdaeb04ef32`, head `a02e7248fd2a88b9e113ddca980607f2f01f746f` and synthetic merge tree `99e589490afe01229f65a3c3f39ebe18355e975f`. The workflow path filter applies hosted repository CI to this Markdown candidate. Core inputs are identical to trunk baseline `8aa608cc1e64ed5986c5b6a8371df5a4c5b3f3e6` with [hosted Core run 45979825833](https://github.com/kburson/aitm/actions/runs/45979825833). The installed local Core suite passed 99 tests and Ruff. The PR left draft and entered Grok 4.7 source SAR on this candidate.

## Decision vector rework

[Initial SAR](2026-11-27-pr-539-grok-sar-r1.md) requested two fixture
clarifications. At head `c7ec0f5a2047c25a96dd45253f8dcb85ce21da96`, the accepted resource case explicitly has
three outstanding sibling deliveries and satisfied provisioning prerequisites.
The refusal identifies the exact mismatch in the local verification receipt.
All 19 vectors, Markdown lint, 99 local installed Core tests and Ruff passed.
Fresh hosted repository CI and source SAR apply.

## Hosted verification

[CI run 45992346359](https://github.com/kburson/aitm/actions/runs/45992346359) passed on base `7f5b3fb62a83f3f04fea6c5a5ceb1bdaeb04ef32`, head `c7ec0f5a2047c25a96dd45253f8dcb85ce21da96` and synthetic merge tree `80f3e9a6b602041769fc7b7502ffa357fc9361b2`. The workflow path filter applies hosted repository CI to this Markdown candidate. Core inputs are identical to trunk baseline `8aa608cc1e64ed5986c5b6a8371df5a4c5b3f3e6` with [hosted Core run 45979825833](https://github.com/kburson/aitm/actions/runs/45979825833). The installed local Core suite passed 99 tests and Ruff. The PR left draft and entered Grok 4.7 source SAR on this candidate.
