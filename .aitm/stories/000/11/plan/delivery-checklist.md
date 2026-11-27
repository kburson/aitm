# #11 delivery checklist

Attempt 1. Codex is the implementing agent and closure owner. [Accepted pickup](2026-11-27-pickup.md) · [Pickup review](2026-11-27-pickup-review.md).

- [x] Published [draft PR #543](https://github.com/kburson/aitm/pull/543) at base `25b0657dccf471820387402053f1efd1e00c3b52` and head `30cf7f77788f3c28b240fea09c2b5c88c17086f8`.
- [x] Tests-first missing-module failure recorded. All 13 C06 cases, including the installed planning command and the checkout race, and 142 installed Core tests passed, with Ruff lint and format and a clean staged diff.
- [ ] Check exact hosted repository CI and the separately required hosted Core CI.
- [ ] Mark ready, obtain Grok 4.7 SAR and run the trusted verifier.
- [ ] Verify landing and record sign-off, Agent Cost and Done.

## Hosted verification

[CI run 46003645687](https://github.com/kburson/aitm/actions/runs/46003645687) and [Core CI run 46003646004](https://github.com/kburson/aitm/actions/runs/46003646004) passed on base `25b0657dccf471820387402053f1efd1e00c3b52`, head `30cf7f77788f3c28b240fea09c2b5c88c17086f8` and synthetic merge tree `fdafe4babb41d2c016bbcf7b83dfbbff3762c19f`. Hosted Core ran 142 passing tests and Ruff. The PR left draft and entered Grok 4.7 source SAR on this candidate.

## Story operation record rework

[Initial SAR](2026-11-27-pr-543-grok-sar-r1.md) found that story-owned operation
records were only checked for a versioned schema marker. The revised validator
qualifies both store and story operation records by schema, name derived from
operation identity, request digest and introducing parent. Story-owned records
also require the exact owning story. Two new refusal cases failed before the
fix and passed afterward, alongside the positive case and all 145 installed
Core tests with Ruff at head `ac63552b844007eddc9e1191fbc2bd429f30dda6`.
