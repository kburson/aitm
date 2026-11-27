# #496 delivery checklist

Attempt 1. Codex is the implementing agent and closure owner. [Accepted pickup](2026-11-27-pickup.md) · [Pickup review](2026-11-27-pickup-review.md).

- [x] Published [draft PR #538](https://github.com/kburson/aitm/pull/538) at base `053a0516b744d898053cee0e0b86c95f6ec605bc` and head `f52aa83b51874387edf0322337b7da6d33e8b637`.
- [x] Locked installed Core passed 99 tests and Ruff. Markdown lint passed. Verified 31 pinned source and test links. Eight pinned legacy test files reported 56 passing cases.
- [ ] Check hosted repository CI and compare Core inputs with the passing hosted baseline under the path filter.
- [ ] Mark ready, obtain Grok 4.7 SAR and run the trusted verifier.
- [ ] Verify landing and record sign-off, Agent Cost and Done.

## Hosted verification

[CI run 45987988842](https://github.com/kburson/aitm/actions/runs/45987988842) passed on base `053a0516b744d898053cee0e0b86c95f6ec605bc`, head `f52aa83b51874387edf0322337b7da6d33e8b637` and synthetic merge tree `88da60727fb3ffbc37b37c0fdff2f75caab3a4ea`. The workflow path filter applies hosted repository CI to this Markdown candidate. Core inputs are identical to trunk baseline `8aa608cc1e64ed5986c5b6a8371df5a4c5b3f3e6` with [hosted Core run 45979825833](https://github.com/kburson/aitm/actions/runs/45979825833). The installed local Core suite passed 99 tests and Ruff. The PR left draft and entered Grok 4.7 source SAR on this candidate.

## Authority rework

[Initial SAR](2026-11-27-pr-538-grok-sar-r1.md) identified twelve findings.
The revision at `a4526e4e71914d5f589cd14720b42e7b38d6b6d0` narrows shelve and resident action behavior,
records partial supersession and both resume paths, qualifies the legacy agent,
project, verb, evidence and hook adapters, and corrects the review source and
test provenance. Markdown lint, 33 pinned links, 99 installed Core tests and
Ruff passed. Fresh repository CI and source SAR apply to this candidate.
