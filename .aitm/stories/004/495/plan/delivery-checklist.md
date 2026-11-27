# #495 delivery checklist

Attempt 1. Codex is the implementing agent and closure owner. [Accepted pickup](2026-11-27-pickup.md) · [Pickup review](2026-11-27-pickup-review.md).

- [x] Published [draft PR #537](https://github.com/kburson/aitm/pull/537) at base `3e08d0b48e884445edee9217b8db9b64cce67afc` and head `1bb35406a1ab9c44c667350e3bae94fb341a5fc6`.
- [x] Locked installed Core passed 99 tests and Ruff. Markdown lint passed. Verified 23 pinned source and test links. Eight pinned legacy test files reported 137 passing cases.
- [ ] Check hosted repository CI and compare Core inputs with the passing hosted baseline under the path filter.
- [ ] Mark ready, obtain Grok 4.7 SAR and run the trusted verifier.
- [ ] Verify landing and record sign-off, Agent Cost and Done.

## Hosted verification

[CI run 45986242634](https://github.com/kburson/aitm/actions/runs/45986242634) passed on base `3e08d0b48e884445edee9217b8db9b64cce67afc`, head `1bb35406a1ab9c44c667350e3bae94fb341a5fc6` and synthetic merge tree `7c5d85baaa6ca8fe7a436041648c53fdfdb6ff65`. The workflow path filter applies hosted repository CI to this Markdown candidate. Core inputs are identical to trunk baseline `8aa608cc1e64ed5986c5b6a8371df5a4c5b3f3e6` with [hosted Core run 45979825833](https://github.com/kburson/aitm/actions/runs/45979825833). The installed local Core suite passed 99 tests and Ruff. The PR left draft and entered Grok 4.7 source SAR on this candidate.
