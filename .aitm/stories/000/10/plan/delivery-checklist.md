# #10 delivery checklist

Attempt 1. Codex is the implementing agent and closure owner. [Accepted pickup](2026-11-27-pickup.md) · [Pickup review](2026-11-27-pickup-review.md).

- [x] Published [draft PR #542](https://github.com/kburson/aitm/pull/542) at base `48666e85daf2bd3f42a3e09849603d0329e61cf8` and head `eb9ace4d9461b3222b1f48d5d55d71f300cc1b3e`.
- [x] Tests-first missing-module failure recorded. All 17 C05 cases, including the reused C04 contract on temporary Git, and 127 installed Core tests passed, with Ruff lint and format and a clean staged diff.
- [ ] Check exact hosted repository CI and the separately required hosted Core CI.
- [ ] Mark ready, obtain Grok 4.7 SAR and run the trusted verifier.
- [ ] Verify landing and record sign-off, Agent Cost and Done.

## Hosted verification

[CI run 45999381334](https://github.com/kburson/aitm/actions/runs/45999381334) and [Core CI run 45999381936](https://github.com/kburson/aitm/actions/runs/45999381936) passed on base `48666e85daf2bd3f42a3e09849603d0329e61cf8`, head `eb9ace4d9461b3222b1f48d5d55d71f300cc1b3e` and synthetic merge tree `51583481a50d6c6722cca817089f1df57c45cb5b`. Hosted Core ran 127 passing tests and Ruff. The PR left draft and entered Grok 4.7 source SAR on this candidate.

## Git outcome rework

[Initial SAR](2026-11-27-pr-542-grok-sar-r1.md) identified the distinction
between post-CAS advancement and pre-commit validation denial. It also
identified missing expected snapshots incorrectly reported as unavailable.
The two regression tests first failed on the reviewed source, then passed at
head `497ae465839a20c8454c5b794c90d7638de11f91`. The installed suite passed 129 cases with Ruff and formatting
checks. Fresh repository and separate Core hosted CI apply before ready
status and the follow-up Grok 4.7 source SAR.
