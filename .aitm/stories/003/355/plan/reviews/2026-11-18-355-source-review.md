# Independent #355 source review, round 3

**PASS for the exact source and cooperative local behavior of PR #369.** Both findings are resolved. Authenticated hosted CI, merge eligibility, delivery verification, and closure remain separate judgments.

Signed, Codex independent source reviewer `/root/review_355`, 2026-11-18 UTC.

- Base `8218a69ad6d9d9f33c6383bd5a6cd4930bef21d7`, tree `90f2cc4007a82493029799d1a1cec10a855cc4a7`.
- Head `2bd902dbd982188e00e0f21a5b5c3565699c332d`, tree `594971b04a905027b72cac36425dd34c5b16e63e`.
- Governing planning commit `bd463a59`. Owner scope decision SHA-256 `b7abb092d546a48dc9c8cc5cfec7ba689dfd2d775a1da21b80f03db49a70e97d`. Advisory delivery plan SHA-256 `f34fdc8034b3c75534d303f35260d1a2df8e58b97925fcc20147fd016bb9c4fd`.

The runner retains readable worker receipts and the observed OS exit when semantic validation refuses the run. The final checkout check also runs on those paths. Independent controls exercised incomplete phases, a mismatched exit, missing and malformed receipts, private-copy drift, and simultaneous receipt failure and checkout drift.

I reproduced the ambient cache issue on `725607f`, which returned 0 while creating 740 paths under the inspected checkout’s `.git` directory. On the exact replacement, the same `XDG_CACHE_HOME` override left the configured cache path absent. The CLI returned 0 after one pytest process matched all 30 assigned IDs and all 90 passing phase records. The run preserved the raw index, Git status, audited source bytes, and bytecode-cache inventory. Pytest took 8.86 seconds, invocation `46128983d5694db485207e7f1ea44dfe`.

All 25 runner tests passed on the exact replacement, including the real failing subprocess control. Separate CLI controls refused an unrelated untracked path and an unrelated committed path before pytest launch. Ruff and `git diff --check` passed. The base-to-head diff preserves the hosted workflows, selector, Python gate, observer, product tests, and runtime lock.
