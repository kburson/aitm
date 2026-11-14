# #286 independent Core testing standard review

**Verdict: ACCEPTED for planning publication.** Signed by OpenAI Codex, independent review agent `/root/review148`. Reviewed standard SHA-256 `7d8a9c7739611b9cdb408918ee71002f98572ff91f55d2abe36ac7ce26af6621`. [#286](https://github.com/kburson/aitm/issues/286)

I verified the examples and test layers against the accepted Core design and leaf map in protected planning revision `88a8380b27c48dff39eab1c8131f7ac788c3afdb`. From the publication directory `.aitm/stories/002/286/plan/`, the standard's relative link resolves to `.aitm/stories/000/2/design/core-design.md`, existing Git blob `3b83c1b5858036702f0993bfb7b48b21800d4a2f`. [Core design](https://github.com/kburson/aitm/blob/88a8380b27c48dff39eab1c8131f7ac788c3afdb/.aitm/stories/000/2/design/core-design.md) · [Core leaf map](https://github.com/kburson/aitm/blob/88a8380b27c48dff39eab1c8131f7ac788c3afdb/.aitm/stories/000/2/plan/leaf-stories.md)

- C28/#37 supports the enforce-mode refusal example. The revised walkthrough correctly distinguishes a recorded advisory guard failure on a legal edge from the integrity refusal on an illegal edge. C78/#81 exercises installed `explain` against the same pinned guard evaluator and exposes unavailable required evidence.
- C18/#23 and the event-folding contract support equivalent reads without a prior index. The publication and reconciliation contract and C50/#60 support replay by stable operation ID, persisted readback, same-story conflict and permitted disjoint replay.
- The extension example targets policy-selected guard invocation and attributable outcomes. The design explicitly handles an unavailable required extension guard and preserves the enforce/advisory distinction.

The standard turns the cases into practical review steps that name the normal entry point, assertion boundary, relevant regression, native fidelity and selection fallback. It distinguishes independent review judgment from automated authorization and leaves #103 and its validation policy unchanged. The evidence in this review covers the standard's exact bytes and source-backed walkthroughs. [#103](https://github.com/kburson/aitm/issues/103)
