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
