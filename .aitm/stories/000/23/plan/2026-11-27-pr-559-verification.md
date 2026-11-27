# PR #559 verification

Base `0be7dd77f6c60e302f2c4dce1279d08f749c5a2b`, head `600828bf27a4747b44331ca8d4668dc939b9048d`, synthetic merge `606725818fcb757e9df82bc6c51a9c6eb28bd4dd`, tree `e3f55a5173482457078c2a1d6e9e8031c1192250`.

The test first failed on the absent index builder. Both completed C18 tests passed against disposable Git and real SQLite. They cover WAL rebuild under an active reader, index-versus-tree result equivalence, cold/corrupt/locked fallback, full-text story/idea/draft/lesson hits, installed read routes, explicit C08 refresh, and explicit unregistration of the explanation capability. A transport and harness shim verified warm reads do not fetch/push or execute a model. The Core macOS full unique collection is 756 unit and 64 integration out of 820. The threshold remains 92%. Ruff check and format passed. Exact draft workflows are repository #46059359677 and Core #46059359743.
