# #147 delivery checklist addendum — policy reconciliation

This continues the [attempt 1 checklist](delivery-checklist.md) and [previous replacement addendum](delivery-checklist-r2.md). Exact formal SAR held the prior candidate. Review → Develop was recorded at planning `df9eed6afc6876b337c99072e8747df389af3e0b`. Accepted Plan and JIT still apply. The estimate remains 3.5 implementation agent-hours.

- Existing [PR #261](https://github.com/kburson/aitm/pull/261) targets `trunk`. Pinned base `71aa5c880fc6a1db1cf676dfc663373f02ef7b16`. Replacement head `96fdc4d34c3645fee7f13ef68527f9b6486c316b`, tree `8671a77850794d4de78f6c2250b75aa9bf6c5c50`. Both prior heads remain in ancestry.
- [Prior run 43142104151 attempt 1](https://github.com/kburson/aitm/actions/runs/43142104151/attempts/1) and its trusted verifier and owner disposition apply to `0d8f8ea` only. The [formal SAR](reviews/147-formal-sar-r1.md) held that source for incomplete reconciliation against policy.
- The correction reconciles anchor and successor obligations against the exact independently supplied policy byte pairs using T02 projection. The local candidate passed 63 focused and 239 combined tests, Ruff and Git whitespace checks. [Replacement local proof](local-validation-r3.md)

- [ ] Push the replacement through the existing PR. Read back current head, applicable base and Test. Refresh the exact candidate if the applicable base moves.
- [ ] Require fresh authenticated exact #103 jobs, ordered test-merge parents and tree, current owner tree disposition and trusted verifier result.
- [ ] Obtain fresh independent SAR for the same passing candidate, then complete normal delivery mapping, signed implementer retrospective and closure.
