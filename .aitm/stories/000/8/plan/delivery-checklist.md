# #8 delivery checklist

Attempt 1. Codex is the implementing agent and closure owner. [Accepted pickup](2026-11-27-pickup.md) · [Pickup review](2026-11-27-pickup-review.md).

- [x] Published [draft PR #534](https://github.com/kburson/aitm/pull/534) at base `ad6a53ac7741c1640251d4223cdb713f56d7f650` and head `aab53f41336ee444d035b471b571a11a0426cc04`.
- [x] Locked installed Core passed 98 tests and Ruff locally.
- [ ] Check repository and Core CI on the current candidate.
- [ ] Mark ready, obtain Grok 4.7 SAR and run the trusted verifier.
- [ ] Verify landing and record sign-off, Agent Cost and Done.

## Hosted verification

[CI run 45977405090](https://github.com/kburson/aitm/actions/runs/45977405090) and [Core CI run 45977405329](https://github.com/kburson/aitm/actions/runs/45977405329) passed on base `ad6a53ac7741c1640251d4223cdb713f56d7f650`, head `aab53f41336ee444d035b471b571a11a0426cc04` and synthetic merge tree `12ff6666712ed83d9bf6df63ef88e994b547c0df`. Hosted Core ran 98 passing tests and Ruff. The PR left draft and entered Grok 4.7 source SAR on this candidate.

## Action result provenance rework

The [initial Grok 4.7 SAR](2026-11-27-pr-534-grok-sar-r1.md) found that a later result could overwrite a retained unavailable action outcome. The same-operation conflict fixture failed before the correction. The accepted design permits a new recovery operation under the same stable action key. The revised reducer retains each operation's result, rejects conflicting results for the same operation, and protects a completed result. A valid later retry adds its new outcome while keeping the original unavailable record. Exact duplicate events remain idempotent.

Replacement head `8508651997ada2e7fb3b03d3270e48cbac47c8f9` passed 99 locked installed Core tests and Ruff locally.

## Hosted verification

[CI run 45978723190](https://github.com/kburson/aitm/actions/runs/45978723190) and [Core CI run 45978723079](https://github.com/kburson/aitm/actions/runs/45978723079) passed on base `ad6a53ac7741c1640251d4223cdb713f56d7f650`, head `8508651997ada2e7fb3b03d3270e48cbac47c8f9` and synthetic merge tree `d3cc0f30a7e1483ae16e28c327d48d8a3240c217`. Hosted Core ran 99 passing tests and Ruff. The PR left draft and entered Grok 4.7 source SAR on this candidate.
