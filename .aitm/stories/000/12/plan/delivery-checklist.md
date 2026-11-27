# #12 delivery checklist

Attempt 1. Codex is the implementing agent and closure owner. [Accepted pickup](2026-11-27-pickup.md) · [Pickup review](2026-11-27-pickup-review.md).

- [x] Published [draft PR #544](https://github.com/kburson/aitm/pull/544) at base `cce0cb2b033be027f695e3d8f9896edca40de765` and head `79c21d47e493090d9ce7630374ff30c419191a2e`.
- [x] Tests-first missing-module failure recorded. All 28 C07 cases and 173 installed Core tests passed, with Ruff lint and format and a clean staged diff.
- [ ] Check exact hosted repository CI and the separately required hosted Core CI.
- [ ] Mark ready, obtain Grok 4.7 SAR and run the trusted verifier.
- [ ] Verify landing and record sign-off, Agent Cost and Done.

## Hosted policy pin

Before review, added a test that first failed because the local branch could
stand in for the anchored hosted route. The revised service reads the exact
hosted route from a dedicated validated local ref. A fetched candidate does
not change policy before continuity validation and admission. A cached
committed view can remain readable while the checked-out code branch stays
untouched. All 28 C07 cases and 173 installed Core tests passed again, with
Ruff lint and format on head `4221091c9ec68c20472d5e351a95cafa13b86e05`. Both hosted workflows are rerun for
this head while #544 remains draft.

## Repository CI retry

[Repository CI attempt 1](https://github.com/kburson/aitm/actions/runs/46008168418/attempts/1)
failed in `aitm-usage`'s `test_native_inventory_audits_actual_selected_route`
with `Native capture position is unavailable`. The exact candidate diff
leaves `packages/aitm-usage`, `tools/ci` and the workflows untouched.
[Core CI](https://github.com/kburson/aitm/actions/runs/46008168471) passed.
Started a full repository CI rerun at the same head. The PR stays draft
until both required checks pass on the exact candidate.

## Hosted verification

[CI run 46008168418](https://github.com/kburson/aitm/actions/runs/46008168418) and [Core CI run 46008168471](https://github.com/kburson/aitm/actions/runs/46008168471) passed on base `cce0cb2b033be027f695e3d8f9896edca40de765`, head `4221091c9ec68c20472d5e351a95cafa13b86e05` and synthetic merge tree `5d8e19e2f034fa349612f1578251c2657beae92c`. Hosted Core ran 173 passing tests and Ruff. The PR left draft and entered Grok 4.7 source SAR on this candidate.

## Committed policy schema rework

[Initial SAR](2026-11-27-pr-544-grok-sar-r1.md) found that the top-level
policy model discarded unsupported fields. Two tests failed before the fix.
The revised model refuses any unsupported top-level field or table. The
accepted design's four-hour and one-expansion ceilings remain explicit;
added direct tests proving both reject out-of-range values. All 32 C07
tests, all 177 installed Core tests, and Ruff passed at head `26846c77ade5d1d7e4cd06b3c0c2e2d4bf5c0a57`.
