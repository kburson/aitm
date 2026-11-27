# M2, M7 and M8 XPR and sizing

Accepted designs from planning publication [`4db85c4b`](https://github.com/kburson/aitm/commit/4db85c4b31b8a091716bc97303cb3538a31a2a57). Claude Opus 5.5 issued all three native XPR decisions. The estimates are preliminary implementation agent-hours including verification and review.

| Rank | Milestone | Size | Estimate | XPR |
| ---: | --- | --- | ---: | --- |
| 250 | [#524 M2 GitHub provider](https://github.com/kburson/aitm/issues/524) | XL | 44.5 h | [Accepted](https://github.com/kburson/aitm/blob/4db85c4b31b8a091716bc97303cb3538a31a2a57/.aitm/stories/005/524/design/reviews/spec/2026-11-27-github-extension-design-review-a9af7c6091f4f1719529a371c02f6f77/review-a9af7c6091f4f1719529a371c02f6f77-review-manifest.md) |
| 260 | [#522 M7 History import](https://github.com/kburson/aitm/issues/522) | Feature | 18.5 h | [Accepted](https://github.com/kburson/aitm/blob/4db85c4b31b8a091716bc97303cb3538a31a2a57/.aitm/stories/005/522/design/reviews/spec/2026-11-27-history-import-design-review-da800297e0b0c147b91cbdf5f1aad338/review-da800297e0b0c147b91cbdf5f1aad338-review-manifest.md) |
| 270 | [#523 M8 Estimation rubric](https://github.com/kburson/aitm/issues/523) | Feature | 21.5 h | [Accepted](https://github.com/kburson/aitm/blob/4db85c4b31b8a091716bc97303cb3538a31a2a57/.aitm/stories/005/523/design/reviews/spec/2026-11-27-rubric-design-review-e3cc08fe8be7c89350666f9039583e47/review-e3cc08fe8be7c89350666f9039583e47-review-manifest.md) |

The first independently landable work is #525 (S, 3.75 h, included in M2). After #72, it can ship with the source capability alone. M7 consumes the qualified read adapter and hands off a sealed, validated corpus. M8 consumes that corpus, Core lineage and qualified Actual. Activation of a live learned model has separate data and evaluation gates.

[Native board and dependency readback](2026-11-27-m2-m7-m8-xpr-and-sizing.json).
