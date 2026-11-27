# #470 Core records and reducers slice admission

At `2026-11-27T10:10:49.503Z` the six child merges and hosted Core CI prerequisite were observed on the current [slice PR #529](https://github.com/kburson/aitm/pull/529) head `8912327b311b66fa2f557fa0e04c34ecf1d5afe1`. The base is `a5ad6965c1c5b8817c0503dedbf55f576b5ddc67` on trunk. Git ancestry linked every reviewed child landing and the slice diff had 49 files within their verified union.

- [PR #528](https://github.com/kburson/aitm/pull/528) · `34fd11588a1fecf3d04f16a311f1be9bd2f33c3b`
- [PR #526](https://github.com/kburson/aitm/pull/526) · `a97c9952f32e6af44ff0cc1e00f9d60263a5dce1`
- [PR #530](https://github.com/kburson/aitm/pull/530) · `3ee8b2cbd0aedc0bb9b2fce0f01631ae9730c644`
- [PR #531](https://github.com/kburson/aitm/pull/531) · `7a378bb8b816020186bf30c5669f2170fcebc4cc`
- [PR #532](https://github.com/kburson/aitm/pull/532) · `a7fd302fc324f263926a885c5599e0d005abf77b`
- [PR #533](https://github.com/kburson/aitm/pull/533) · `ad6a53ac7741c1640251d4223cdb713f56d7f650`
- [PR #534](https://github.com/kburson/aitm/pull/534) · `8912327b311b66fa2f557fa0e04c34ecf1d5afe1`

[C56 source SAR](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/8/plan/2026-11-27-pr-534-grok-sar.md) and trusted repository CI verification passed on the #8 child. Its integration merge tree `d3cc0f30a7e1483ae16e28c327d48d8a3240c217` was verified at the head of this slice. The installed Core suite passed 99 tests including deterministic configured-workflow and causal attempt replay, historical state/capability recovery, typed evidence, and opaque extension preservation. The installed CLI entry point and JSON Schema were checked. All five prerequisite story records read back Done.

The slice candidate is in Test while its own repository and Core runs complete. Draft removal, Grok 4.7 aggregate source review, repository verifier and trunk merge require the exact tested tree. #8's final delivery and #470 Done follow the verified trunk landing.

## Hosted verification

[CI run 45979825835](https://github.com/kburson/aitm/actions/runs/45979825835) and [Core CI run 45979825833](https://github.com/kburson/aitm/actions/runs/45979825833) passed on base `a5ad6965c1c5b8817c0503dedbf55f576b5ddc67`, head `8912327b311b66fa2f557fa0e04c34ecf1d5afe1` and synthetic merge tree `d3cc0f30a7e1483ae16e28c327d48d8a3240c217`. Hosted Core ran 99 passing tests and Ruff. The PR left draft and entered Grok 4.7 source SAR on this candidate.
