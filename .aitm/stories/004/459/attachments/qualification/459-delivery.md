# Story #459 delivery and C44 fixture parity

[PR #463](https://github.com/kburson/aitm/pull/463) merged to protected trunk at `a5ad6965c1c5b8817c0503dedbf55f576b5ddc67`. The ordered merge parents and delivered tree matched the exact reviewed candidate. The plan reached [sealed XPR consensus](https://github.com/kburson/aitm/blob/e2478a2815c28c75a529dc0c20151ef484ebbf69/docs/peer-reviews/plan/2026-11-26-2026-11-26-core-cost-fixture-plan-review-267e823be939722787b850589663a74b/review-267e823be939722787b850589663a74b-review-manifest.md). Independent source review and all hosted checks passed. [Source review](459-linux-first-source-review.md) · [Trusted CI](459-linux-first-ci.json) · [Portability](459-linux-first-platform-checks.json).

## Delivered producer

The portable wheel runs `aitm-effort story-core-export`. It reopens the exact #458 report, reproduces it from the pinned planning commit and reviewed rate bytes, and emits the existing `aitm.usage.export/v1` receiver files plus independently bound provenance. The fixture is unchanged at blob `9257c7ec948468e8251dcc987ae89bea52f495f5` and SHA-256 `eb1da4e1441bdad0d436b9282d5b67e1e6b3dad8e3215e77443de5e211b91c74`.

## Live input through disposable fixture storage

The #461 run used exact artifact commit `52e57ed3c7ea54c473fe6b223d09000269856f2e`, report ID `0feeb1478d08640faee709e4fff72b4e60d5cf39191eba36a9ca99baa0f0c40e`, and planning input pin `b17d26a9e1336bd51d239ae3c02b5906c74e3c69`. Two fresh commands using the delivered wheel reproduced identical bytes and matched the source receipts and rate digest. The pinned report gives a known **$0.1754084** Sol Standard API-equivalent subtotal.

The unchanged C44 fixture imported three pending rows and accepted zero scoped rows. After reopening the same SQLite database, replay returned duplicate and left the three pending rows intact. Story Cost stayed held because admission is open and unattributed coverage is unknown. [Exact normalized bundle](459-live-461-core-bundle.json) · [Digest and fixture readback](459-fixture-parity.json).

## Synthetic contract outcomes

| Case | Observed fixture outcome |
| --- | --- |
| Closed complete scope and exact digest | Accepted one immutable row. Its stored digest matched the provenance sidecar. |
| Lost acknowledgement after commit | A fresh client read the exact accepted digest. Replaying the same row returned duplicate. |
| Controlled rollback | A fresh client verified no accepted or pending row. Identical retry imported once. |
| Missing, mismatched or pending readback | Held in the fixture exercise. |
| Same-cutoff repricing | New rate basis imported with one reconciliation item. The original accepted receipt stayed intact. |
| Late observation and corrected revision | Original source identity stayed stable, the change reconciled, and the late unscoped source remained pending. |
| Changed private scope key at the same cutoff | Rejected as a conflicting usage projection. |
| Disputed omission | Original receiver acceptance remains immutable. The sidecar exposes the hold for the consumer. |
| Ambiguous scope, private key and forged artifact controls | Unknown scope remains pending. Private paths and values stay out of the bundle. Foreign pins and internally consistent forged reports hold. |

The local exact-candidate suite passed 1,780 tests with one skip. The Linux installed-wheel job passed 236 effort fixtures, including the positive and adversarial Core export cases. The focused Windows job passed three canonical byte and CLI tests. The revised Linux-first policy selected no hosted macOS job for this change. The verified fixture tests are in `packages/aitm-usage/tests/test_effort_core_export.py`.

## Core handoff

[#230](https://github.com/kburson/aitm/issues/230) owns live receiver qualification with #51. Retain the two exact v1 files with their provenance sidecar and receipt/report selectors. Authorize one project, story and window per fixture lane and retain the same private scope key across retry and repricing. For ambiguous disposition, establish the original receiver identity and verify the exact stored digest or controlled absence before action. A disputed omission conveys a hold through provenance. The fixture itself retains prior acceptance. Actual and aggregate Cost retain their independent authority.
