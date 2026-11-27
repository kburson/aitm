# #7 delivery checklist

Attempt 1. Codex is the implementing agent and closure owner. [Accepted pickup](2026-11-27-pickup.md) · [Envelope supplement review](2026-11-27-envelope-compatibility-review.md).

- [x] Published [draft PR #533](https://github.com/kburson/aitm/pull/533) at base `a7fd302fc324f263926a885c5599e0d005abf77b` and head `6c5e65bd43b7b74fe990ade480a884ea6fd22ed1`.
- [x] Locked installed Core passed 90 tests and Ruff locally.
- [ ] Check repository and Core CI on the current candidate.
- [ ] Mark ready, obtain Grok 4.7 SAR and run the trusted verifier.
- [ ] Verify landing and record sign-off, Agent Cost and Done.

## Hosted verification

[CI run 45973347426](https://github.com/kburson/aitm/actions/runs/45973347426) and [Core CI run 45973347356](https://github.com/kburson/aitm/actions/runs/45973347356) passed on base `a7fd302fc324f263926a885c5599e0d005abf77b`, head `6c5e65bd43b7b74fe990ade480a884ea6fd22ed1` and synthetic merge tree `0f2a5ec5dc43c979551058974785b3e2593e5794`. Hosted Core ran 90 passing tests and Ruff. The PR left draft and entered Grok 4.7 source SAR on this candidate.

## Recovery authority and rework coverage

The [initial SAR](2026-11-27-pr-533-grok-sar-r1.md) required evidence-only execution scope on every phase and causal rework coverage. The new scope test reproduced an accepted out-of-authority action. Replacement head `97f4f922fbace6acbcaa4b8367c2209d4cde5909` retains each recovery binding's authority by generation, enforces it through deferred result observations, and covers valid and missing rework boundaries plus a mismatched causal operation. Locked installed Core passed 91 tests, Ruff lint and formatting locally.

## Hosted verification

[CI run 45975235479](https://github.com/kburson/aitm/actions/runs/45975235479) and [Core CI run 45975235636](https://github.com/kburson/aitm/actions/runs/45975235636) passed on base `a7fd302fc324f263926a885c5599e0d005abf77b`, head `97f4f922fbace6acbcaa4b8367c2209d4cde5909` and synthetic merge tree `91d3e2740abf0ee18288b500bc9a5a8e2d708b60`. Hosted Core ran 91 passing tests and Ruff. The PR left draft and entered Grok 4.7 source SAR on this candidate.
