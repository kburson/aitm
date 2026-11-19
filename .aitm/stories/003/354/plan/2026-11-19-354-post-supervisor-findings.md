# #354 post-supervisor qualification findings

The evidence anchor is AITM trunk `4ae28dba1493c2171bd8097e58195198c4001a51`, tree `06aecaada0792e8ad38bce2b261e1c1ccd5529dd`. The audited hook is regular mode 100644, Git blob `1acb264edbb10ba55a9d5b1ac57520e5b1094832` and SHA-256 `cacd4a9bfb08ad74e6a601ef1824922fa3a4edc57d3d3c5a887ecf1a5a262e61`. Its assigned receipt module SHA-256 is `f7e20ab6ab353572fc8ed9238acda51612241c8ece52aa93566866c0b5fa5d43`.

The locked module collection produced 38 IDs. Its canonical sorted, repo-relative JSON inventory hashes to `7262ead5d97060cb789d9c17efb87952747313d4ea82f36c32c7cc9ef7ace3c3`. Two procfs integration IDs apply only on Linux and the other 36 apply on both systems. The covered behavior includes native input, attempt ownership, process ancestry and executable rechecks, scope binding and first publication. The evidence assigns the exact module for a same-mode ASCII comment append and leaves candidate inventory and impact completeness unqualified.

The current consumer digest is `709aa6dce1bd3f25d169b8cbde4af009275cfe226e9a752c0260ea8e58e8560f`. The unchanged hosted map correctly selects full testing because its audited consumer changed. For this separate local assignment, keep the pinned source map and selector, compare the exact consumer inventory against the fresh digest, and run the selector with only the existing Grok rule digest refreshed in memory. The prior #354 anchor and assignment retain their original evidence.

The [exact Ubuntu anchor run](https://github.com/kburson/aitm/actions/runs/44460849859/attempts/1) passed. The independent Darwin module run returned 36 passed and two platform skips. See the companion independent verdict for the exact selection replay.
