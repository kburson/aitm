# #141 independent source assessment, replacement candidate

Codex / story144 reviewed the replacement on 2026-11-12 at 02:22 UTC, independently of implementer Codex / story141. This assessment informs the owner's exact-tree source disposition. The formal review follows passing evidence under the existing #103 delivery gate.

| Item | Exact identity |
| --- | --- |
| Candidate | Commit `be8f5bff9311655fb788e597c69069c23609a341`, tree `ed4ea486732346bfaaf7d518bc91b4d13b555fd5`, sole parent `39d2ef5166db04a1ae9fa3cf24d504b591a7fa18`, original base `71aa5c880fc6a1db1cf676dfc663373f02ef7b16` |
| Graph module | `tools/ci/tia/python_graph.py`, blob `30d61a548a8127356f045892f40481e5593879bd`, raw SHA-256 `c826fa54bdfed0ff840e30c736906fb502841dcc558222b73796490146f6f7c0`, 431 lines |
| Focused test | `tools/ci/tests/test_tia_python_graph.py`, blob `d1d50524ae921f7a89ce0838876dadad62b0afdd`, raw SHA-256 `fd60699d33f4e707c3d124e0c5f5128411d289238436c7f1f80684e37ed7912a`, 419 lines |
| Planning authority | Accepted Plan/JIT publication `201d21a0deca8b4a03d39a4ba8b8ba383deee4cd`. The leaf design, refinement and accepted scope are the same inputs reviewed in the [initial assessment](2026-11-11-141-source-assessment-r1.md). |

**Verdict — source acceptable for the owner's exact-tree disposition.** The replacement resolves the blocking finding, and this assessment found no additional blocker.

The revised import-from resolver keeps the known initializer or module edge. It records unbounded `wildcard-import` for a local package or namespace, since a wildcard can load children through an initializer's `__all__`. It preserves the known-only behavior for a plain local module and an approved external module in the new regression. For an implicit namespace with no initializer, it retains the known child's edge and reports the missing named child as unresolved. An ambiguous candidate set continues to retain represented edges and explicit uncertainty.

I exported the two module revisions and the exact replacement tests from Git, then tested them in isolated scratch with uv 0.10.6, locked CPython 3.13.9 and pytest 9.2.0. Against the original module, both new tests failed at their missing uncertainty assertions and 17 were deselected. Against the replacement, all 19 focused tests passed in 0.72 seconds, including the existing snapshot, package and pytest scope cases. Both Ruff checks passed on the exact replacement files. The retained red and green log SHA-256 values are `3f5544684cd7ce641f51aff3f8d88b6febb43c54633855b3f38eee0019eab61f` and `e6396efe40cf15f574edb67564512af66a4c78f7447df731899bd83906e61134`.

The diff against the original candidate contains only the resolver correction and its two regressions. The diff against the pinned base contains only the two owned additions and passes `git diff --check`. The source checkout was clean. Both paths are #103 gate controls under `tools/ci/`; the hosted helper list and denominator still exclude the focused test and graph module. The exact-tree owner disposition and applicable #103 proof remain required before the formal independent source review.
