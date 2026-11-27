# #471 legacy qualification delivery checklist

[Accepted epic pickup](2026-11-27-integration-pickup.md) · [Pickup review](2026-11-27-integration-pickup-review.md).

[Draft trunk PR #536](https://github.com/kburson/aitm/pull/536) composes the verified
leaf deliveries below. The exact trunk base is `8aa608cc1e64ed5986c5b6a8371df5a4c5b3f3e6`, integration head
is `98b73279746d0626f4d4faa5dbabe12d75171e61`, and synthetic merge tree is `80f3e9a6b602041769fc7b7502ffa357fc9361b2`. The candidate
contains only the four accepted Markdown documents. #497 remains in Review
until exact trunk delivery.

- PR #535 landed at `3e08d0b48e884445edee9217b8db9b64cce67afc` on reviewed tree `9c6b257f8a64ebbea34db865c38f7f42eca861ea`.
- PR #537 landed at `053a0516b744d898053cee0e0b86c95f6ec605bc` on reviewed tree `7c5d85baaa6ca8fe7a436041648c53fdfdb6ff65`.
- PR #538 landed at `7f5b3fb62a83f3f04fea6c5a5ceb1bdaeb04ef32` on reviewed tree `eee5fb74670fa4ca72619c93a37d05cd75298859`.
- PR #539 landed at `98b73279746d0626f4d4faa5dbabe12d75171e61` on reviewed tree `80f3e9a6b602041769fc7b7502ffa357fc9361b2`.

- [x] Verified all leaf merges are ancestors of the candidate. Each matches its reviewed head, base and tree.
- [x] Verified 19 typed design decision vectors, evidence links, Markdown lint, 99 installed Core tests and Ruff.
- [ ] Require exact hosted repository CI and compare exact Core inputs to the passing Core baseline.
- [ ] Remove draft, run fresh Grok 4.7 source SAR and verify the exact candidate.
- [ ] Verify trunk landing and sign off #497 and #471.

## Hosted verification

[CI run 45993218161](https://github.com/kburson/aitm/actions/runs/45993218161) passed on base `8aa608cc1e64ed5986c5b6a8371df5a4c5b3f3e6`, head `98b73279746d0626f4d4faa5dbabe12d75171e61` and synthetic merge tree `80f3e9a6b602041769fc7b7502ffa357fc9361b2`. The workflow path filter applies hosted repository CI to this Markdown candidate. Core inputs are identical to trunk baseline `8aa608cc1e64ed5986c5b6a8371df5a4c5b3f3e6` with [hosted Core run 45979825833](https://github.com/kburson/aitm/actions/runs/45979825833). The installed local Core suite passed 99 tests and Ruff. The PR left draft and entered Grok 4.7 source SAR on this candidate.

## Backlog guard follow-up

[Initial SAR and coordinator evidence](2026-11-27-pr-536-grok-sar-r1.md) record the omitted
Backlog profile block and the parsed proof for the existing exit guard.
A fresh independent source review of the same exact candidate gets the
complete accepted state definition. Approval and merge remain pending.
