# PR #559 verification

Base `0be7dd77f6c60e302f2c4dce1279d08f749c5a2b`, head `600828bf27a4747b44331ca8d4668dc939b9048d`, synthetic merge `606725818fcb757e9df82bc6c51a9c6eb28bd4dd`, tree `e3f55a5173482457078c2a1d6e9e8031c1192250`.

The test first failed on the absent index builder. Both completed C18 tests passed against disposable Git and real SQLite. They cover WAL rebuild under an active reader, index-versus-tree result equivalence, cold/corrupt/locked fallback, full-text story/idea/draft/lesson hits, installed read routes, explicit C08 refresh, and explicit unregistration of the explanation capability. A transport and harness shim verified warm reads do not fetch/push or execute a model. The Core macOS full unique collection is 756 unit and 64 integration out of 820. The threshold remains 92%. Ruff check and format passed. Exact draft workflows are repository #46059359677 and Core #46059359743.

## Revised candidate

Head `9cc35ed3db22ae9a8a8f421ba0fe23e7a4147453`, synthetic merge `2c81b23945bdb59d3a736e8d0227332b2996e35d`, tree `50b5efcb15a7c0de9db6c7a79bb3ed6f5866c460`. The installed read regression first failed because the result did not identify the validated shared commit separately from the pinned local view. The revised tests pass, including an unpublished local change with verified shared freshness and an explicit mismatch between the commits. First candidate passed 821 locked Core product and tooling tests. New repository run #46059866606 and Core run #46059866630 were triggered for the revised draft.
