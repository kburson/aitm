# #103 local collector coverage baseline

Observed November 9, 2026, from 20:50:18 to 20:51:54 CST. Read-only planning observation using a private archive of `packages/aitm-usage` from protected trunk `f80f22645e2008c4cac9dc6e4003640bba976b5f`. Source tree `418b1d6e681f65a0377472f4392be87076b6bad4`. The archived `uv.lock` SHA-256 was `f060cb80f0826ecf6ac33d165b381fa8a1db0d340ef465099a2a94b364d00c2e` before and after measurement.

- macOS 26.6.2 arm64, Xcode 27.2 (27B52), CPython 3.13.9, uv 0.10.6, locked pytest 9.2.0. Temporary coverage tools pytest-cov 7.1.0 and coverage.py 7.17.2.
- Ran the full serial suite with the locked environment and temporary coverage tools. Coverage measured `src/aitm_usage` using relative paths and coverage.py's subprocess patch. No branch coverage was requested for this diagnostic.
- **530 passed**, zero skips reported, in **93.27 seconds** under coverage. Ruff lint and format checks passed. The slowest calls were owned LaunchAgent recovery at 13.70s, exact recovery receipt at 7.42s, and real service crash/replay at 5.50s.
- **6,285 of 6,910 executable lines across 18 files covered**. The raw ratio is **90.9551%**, above the 90% package floor. The current plan needs no product coverage uplift on this baseline.
- Private local artifact SHA-256. Coverage JSON `7d05442db4fbd6abe46a835f9b157842f113f57ecf36113f77bc0fb7cd5e4b0d`. JUnit XML `bbf2a0b775a48b43faa790f9a973c465a60d2a0fff1c7df324b9ae61a7fbdd64`.

This is a local source baseline. The required hosted runner must prove its own inventory, named subprocess coverage, package line floor and capabilities. An isolated wheel smoke and native workflow evidence are separate delivery gates. Exact active agent engagement and hosted runtime remain Unknown.
