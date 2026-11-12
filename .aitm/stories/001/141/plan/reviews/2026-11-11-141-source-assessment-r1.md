# #141 independent source assessment, initial candidate

Codex / story144 reviewed the immutable source on 2026-11-12 at 02:18 UTC, independently of implementer Codex / story141. This assessment informs the owner's source disposition. The formal source review follows exact passing #103 evidence.

| Item | Exact identity |
| --- | --- |
| Candidate | Commit `39d2ef5166db04a1ae9fa3cf24d504b591a7fa18`, sole parent `71aa5c880fc6a1db1cf676dfc663373f02ef7b16`, tree `699ed35f33482a3c41c84caa9f419f0bb55572e1` |
| Graph module | `tools/ci/tia/python_graph.py`, blob `ebac67dc41ed4320672722920f0a271a8c70db17`, raw SHA-256 `3033a9bb333580bab03c7da2e0c84f4eb783867a9a3100e8abe9276400c9db30`, 419 lines |
| Focused test | `tools/ci/tests/test_tia_python_graph.py`, blob `54ff178c314e1f95d1ed39c506697dd340babfee`, raw SHA-256 `2790e171cc1cd37d0a9dcceeb0763241d5505b1c9a4984ab28323d6cef028e77`, 382 lines |
| Accepted leaf design and refinement | Raw SHA-256 `0f10b0e978208480b39b304c9e513019e2f603bb1358a0b8738eff75f817d438` and `7ef160644c7374a678ad6b837507839ef886de327eeb88c0348b1400160baedc` |
| Accepted plan and JIT | Publication `201d21a0deca8b4a03d39a4ba8b8ba383deee4cd`; raw SHA-256 `ba033428548e17f629e8f5b161a85b64b7980ebd74a05f2baba530e533e86944` and `445e6838ac835c1ed61f75209c5e5ebec0d43e1c159a220b5f993c8147533e1c` |

**Verdict — revise and assess the replacement source.** One blocking gap in wildcard package imports.

**[P1] Preserve uncertainty when a wildcard import can load package children.** At `tools/ci/tia/python_graph.py:302`–`307`, an import-from retains the base and looks for a child named after each AST alias. For `from pkg import *` the alias is `*` and the child lookup contributes nothing. CPython's `importlib._bootstrap._handle_fromlist` follows a package's `__all__` and can load a child named there even if its initializer contains no import of the child. The graph can therefore retain the initializer while omitting both the child dependency and uncertainty. A changed child with another known consumer could leave the wildcard consumer out of selection. The coordinator independently reproduced the behavior and directed a red/green correction. Preserve the base edge and report conservative uncertainty where the wildcard's children cannot be established. Test the initializer-only export and require the old graph's missing evidence to fail the assertion.

The two-path diff is otherwise within scope. The graph reads snapshot membership, bound bytes and digest, validates the supplied policy and retains provenance. Named imports, relative contexts and overlapping owners preserve represented edges and explicit ambiguity. Pytest fixture/config scope, recognized dynamic loaders, unsupported source modes and parse failures record uncertainty. The tests exercise those cases, a real local T03 snapshot rename, and exact bound-read refusal. The focused suite has no wildcard-package case on this candidate. The assessment examined committed objects without executing the candidate while its author prepared the correction.

Both additions are gate controls under the protected target's `tools/ci/` predicate. The workflow, verifier and helper policy are unchanged. The four-helper hosted denominator excludes the module and its focused test. `git diff --check` passed on the exact source range, and remote trunk matched the pinned parent at readback. Keep readiness held pending an assessed replacement, its exact-tree owner disposition and the applicable #103 delivery gates.
