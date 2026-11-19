# #383 exact-input qualification

The independent qualification exercised tool head `eb444ad05b8b08b2bd3cbab64e2f110f5f979cae`, tree `875bb2e29df63abaa39c874215658bf3f9c9f6c8`, from [PR #384](https://github.com/kburson/aitm/pull/384). Both hosts used CPython 3.13.9 and uv 0.10.6. The reference was non-root Ubuntu 24.04 arm64. The [machine receipt](2026-11-19-383-qualification.json) records the exact input identities, expected inventories, comparison decisions, and controlled witnesses. Its SHA-256 is `eb52b772b59897d9d1a5234998c6371b823ab136e1902cc2dd5e2b7e239d0fee`.

## Actual repository tree

One scratch comment edit to the Grok scope hook on trunk `5023860969b719989575ad2a07666a91c909ec12` made scratch HEAD `e199b1608cbba73d59a7f3717328d796e64714fd`. The staged index, HEAD, and synthetic PR commit `be39d49ccf6d5e48dc1f10b2b2ff8d4606efc12b` represented the same tree `d39c32b176442180a287a664c105c37778ae2d1a`. The probe emitted equal changed paths and exact test IDs across the three modes on each host. Dynamic, relative, and unresolved import evidence correctly selected the full inventory.

- Ubuntu's isolated full run on that tree passed 1,525 product/CLI and 251 helper tests with zero failures, errors, or skips. Each probe list matched those 1,776 observed IDs. Two earlier shared-container runs encountered native journal setup errors. The independently isolated run completed cleanly with reconciled pytest observer outcomes.
- macOS's independent full collection found 1,520 product/CLI and 251 helper IDs. Each probe matched all 1,771. Ubuntu has five extra inotify tests, and two errno parameter cases use platform-specific numbers.
- Staged and HEAD decisions excluded the unstaged and untracked sentinels. The index, working bytes, and HEAD survived the read-only probe. The PR probe refused the wrong tree and reversed parents.
- The same CLI also bound the actual GitHub test merge `f8b6e2e8d38c7a000adfc63eb455cd9c6cae112b` for PR #384 to the candidate tree on Ubuntu. Its 1,525 product IDs exactly matched the hosted Python inventory from [attempt 1](https://github.com/kburson/aitm/actions/runs/44545077293/attempts/1), with sorted-list SHA-256 `3b88af7ea9d7a6bba72f70d32e9471540307fa9bec2efbe4bef233d112b5179e`. The probe reported local advisory provenance for that input.

## Controlled graph and outcomes

For controlled tree `3abef6aed9edcad1aa48f5429e752af5935e9991`, all three modes on both hosts selected the same nine of 16 tests. The assignment included mandatory tests and graph witnesses for one direct and one transitive dependency. The clean base passed all 16. The seeded candidate failed exactly the two witnessed tests in both the nine-test selected run and the 16-test full run on each host. The dynamic edge selected all 16. Missing inventory refused assignment. The rename retained witnesses from the old and new graphs.

## Regression and custody checks

The final tools regression ran 668 tests with one platform skip on Ubuntu and 669 tests on macOS. The existing pinned #355 command replay passed 38 assigned tests and 114 observed phases on Linux, and 36 tests and 108 phases on Darwin. Both preserved the captured hook bytes, index, status, and HEAD. The workflow, path map, policy, Python gate, trusted verifier, and pinned runner bytes were compared to trunk and were identical. The independent [source review](reviews/2026-11-19-383-independent-source-review.md) passed the same candidate.

The first hosted attempt's two Python jobs, quality, and file checks passed. Its collector held because the trusted base and candidate runners used different Ubuntu image builds. Replaying the tracked evaluator on the original artifacts confirmed the trusted-base identity as the sole failure. Hosted authority is recorded separately after a successful, authenticated attempt.
