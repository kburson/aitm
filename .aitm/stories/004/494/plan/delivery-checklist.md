# #494 delivery checklist

Attempt 1. Codex is the implementing agent and closure owner. [Accepted pickup](2026-11-27-pickup.md) · [Pickup review](2026-11-27-pickup-review.md).

- [x] Published [draft PR #535](https://github.com/kburson/aitm/pull/535) at base `8aa608cc1e64ed5986c5b6a8371df5a4c5b3f3e6` and head `dc3b6a7b7ecf0abfb89908c5ff17aed9cf8dfe56`.
- [x] Locked installed Core passed 99 tests and Ruff. Markdown lint passed. Reconstructed all 51 registrations, verified 94 pinned links, and executed 105 pinned legacy cases.
- [ ] Check repository CI on the current candidate and verify matching Core inputs under the established path filter.
- [ ] Mark ready, obtain Grok 4.7 SAR and run the trusted verifier.
- [ ] Verify landing and record sign-off, Agent Cost and Done.

[Core CI applicability and baseline](2026-11-27-hosted-ci-applicability.md).

## Hosted verification

[CI run 45982804504](https://github.com/kburson/aitm/actions/runs/45982804504) passed on base `8aa608cc1e64ed5986c5b6a8371df5a4c5b3f3e6`, head `dc3b6a7b7ecf0abfb89908c5ff17aed9cf8dfe56` and synthetic merge tree `42c0a097868132e4ca8db9b019c1ae996095bdfc`. The workflow path filter applies hosted repository CI to this Markdown candidate. Core inputs are identical to trunk baseline `8aa608cc1e64ed5986c5b6a8371df5a4c5b3f3e6` with [hosted Core run 45979825833](https://github.com/kburson/aitm/actions/runs/45979825833). The installed local Core suite passed 99 tests and Ruff. The PR left draft and entered Grok 4.7 source SAR on this candidate.
