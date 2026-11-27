# #6 Delivery checklist

Attempt 1. Codex is the implementing agent and closure owner. [Accepted pickup](2026-11-27-pickup.md) · [Pickup review](2026-11-27-pickup-review.md).

- [x] Published [draft PR #532](https://github.com/kburson/aitm/pull/532) against #470 integration base `7a378bb8b816020186bf30c5669f2170fcebc4cc`, head `98a4851fa58847a520a387d26f3641412118a06a`.
- [x] Locked installed Core suite and Ruff passed locally. 62 tests passed.
- [ ] Verify repository and Core CI against the exact current base, head and tree.
- [ ] Mark ready, obtain independent Grok 4.7 SAR, and run the repository verifier.
- [ ] Merge to #470, verify the landing, and record sign-off, Agent Cost and Done.

## Hosted verification

[CI run 45969083239](https://github.com/kburson/aitm/actions/runs/45969083239) and [Core CI run 45969083245](https://github.com/kburson/aitm/actions/runs/45969083245) passed on base `7a378bb8b816020186bf30c5669f2170fcebc4cc`, head `98a4851fa58847a520a387d26f3641412118a06a` and synthetic merge tree `5316d35f7d63263dcd9534878a5424effa49ff04`. Hosted Core ran 62 passing tests and Ruff. The PR left draft and entered Grok 4.7 source SAR on this candidate.

## Story-scope and sign-off rework

The [first SAR](2026-11-27-pr-532-grok-sar-r1.md) required pinning the lifecycle domain to its own story and folding typed sign-off by the signing agent independently of the recording actor. Cross-story and signer fixtures failed before the fix. The replacement head `49fd26b15980c8a1771df3fd63f32eb221a0f99b` passed 67 locked Core tests and Ruff locally and awaits hosted evidence.
