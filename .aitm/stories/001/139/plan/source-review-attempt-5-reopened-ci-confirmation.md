# #139 source review confirmation after PR #197 reopened

**The accepted source verdict applies to the regenerated test merge commit.**
Authenticated GitHub reads showed [PR #197](https://github.com/kburson/aitm/pull/197)
open and its merge ref pointing to `cddd5d3d830769f48850a67479952df15fc18e76`.
GitHub verified both this commit and its predecessor
`59a03a1942401d2f462c11e548ad74b1d73beeaf`. Both have the same ordered
parents and tree.

| Field | Verified value |
| --- | --- |
| Literal `trunk` base and first parent | `b0f8ac79b8bd3f178b1d47dc2e66650f1f54e0d5` |
| Reviewed PR head and second parent | `dbbc729574c9b078658af310b2efa2945020224f` |
| Reviewed candidate tree | `7d93353e06c8177c19bc1f918217e2f8ccf75da7` |
| Fresh run | [43062845686, attempt 1](https://github.com/kburson/aitm/actions/runs/43062845686/attempts/1) |
| Check suite | `116615977198` |

The authenticated run and attempt records agree on their creation
timestamp and PR association. Attempt 1 was queued with no conclusion
when checked. The prior attempt's hosted evidence applies to its own
synthetic merge commit. Delivery requires successful attested evidence
for the fresh attempt, trusted-target verification, and the separate
owner disposition for the three added #103 gate-control paths on this
exact tree.

The source verdict in `source-review-attempt-5.md` has SHA-256
`b0df50fdb6ef69573bb30b8e6e078565b3227a43eb3c9dac3917ad115427065d`.
The reopen receipt `pr-reopen-receipt-43062845686.json` has SHA-256
`8e406cd6ec5e0a21935fe16b69f0032247dbd63265d7713944df97122b057112`.

Signed `codex-collaboration:/root/review197` for the source identity above.
