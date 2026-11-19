# #370 bounded production suite qualification

**Pass for the exact reviewed Grok headless decoder change.** #398 passed independent refinement as Size M with the 3.5 agent-hour estimate, then ran three exact hosted Ubuntu PR trees. The positive production change replaced positional constructor arguments with equivalent named arguments inside `_headless_tokens`. All 33 Grok replay test outcomes matched the 1,776-test full run. The suite lane took 4.316 seconds including setup and selection, versus 338.504 seconds for the full reference, a saving of 334.188 seconds or 98.7%.

[Hosted run](https://github.com/kburson/aitm/actions/runs/44622984300/attempts/1) · [Refinement](../../398/plan/2026-11-19-398-production-boundary-refine.md) · [Independent disposition](../../398/plan/2026-11-19-398-independent-refinement.md) · [Exact evidence](2026-11-19-370-bounded-production-shadow-evidence.json)

| Exact tested PR | Suite result | Full result | Suite lane seconds | Full lane seconds | Path-map lane seconds |
| --- | --- | --- | ---: | ---: | ---: |
| [#399 Equivalent named arguments](https://github.com/kburson/aitm/pull/399) | 33 passed | 1,776 passed | 4.316 | 338.504 | 338.618 |
| [#401 Seeded cache bucket swap](https://github.com/kburson/aitm/pull/401) | 32 passed, one intended failure | 1,775 passed, same failure | 4.436 | 364.201 | 364.365 |
| [#400 Shared adapter edit](https://github.com/kburson/aitm/pull/400) | Full | 1,776 passed | 359.538 | 359.444 | 359.608 |

Each comparison used the same GitHub-tested tree and one hosted Ubuntu 24.04 x64 runner. Both product lanes used three pytest workers, locked uv 0.10.6 and CPython 3.13.9, matched test-context coverage, and independent scratch. Full ran 1,525 product and CLI tests and 251 helpers. Overall lane times include locked environment sync. Selector lane times include assignment. They exclude interpreter provisioning, workflow queue and startup, post-run evidence verification, and wheel smoke. Full decisions reused the corresponding full run. The current base-owned map chose full for all three cases.

## Scope and evidence

The audited source path goes through the adapter's optional headless callback, guarded native walk, and private decoder. The full product coverage databases recorded decoder body execution only under `test_headless_projection_is_only_corroboration` in the candidate checkout's `src/aitm_usage/sources/grok.py`. The actual full helper lanes had no decoder hits. Both full lanes showed a covered subprocess console entry, and a standalone CLI canary also tied that entry to a normally exiting observed child. Subprocess coverage was configured in both phases. The raw coverage database digests and independently extracted contexts match the hosted receipts.

The selector used #383's exact Git snapshots, ordered parents, reviewed source digests, and unchanged bytes outside the declared function body. It rechecked the captured identities after execution. Wrong tested tree and stale head returned unavailable. A truncated full phase receipt failed validation. The seeded cache swap kept the token total and changed the bucket mapping. Both lanes failed the same existing assertion, with zero missed failures or differing outcomes. The related shared adapter edit selected full.

The first shadow dispatch was cancelled after review strengthened coverage evidence for the actual full lanes and added raw database retention. The completed run kept the same three PR bindings. The experiment used separate draft branches. Trunk, the required workflow, path map, evaluator, verifier, branch rules and pinned #355 runner were verified unchanged.

Qualification applies to the reviewed decoder refactor and its seeded control on the pinned base. Unreviewed source changes, shared paths and later bases take the conservative fallback. Promotion remains a separate decision.
