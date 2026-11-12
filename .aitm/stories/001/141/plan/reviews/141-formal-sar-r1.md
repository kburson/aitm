# #141 formal independent source review · R1

**HOLD — one blocking finding.** Reviewed on 2026-11-12 UTC by Codex / sar141, separate from the implementer (Codex / story141), the earlier owner-disposition assessor, and the Wave 30 coordinator. This verdict is limited to the exact candidate below. The passing #103 evidence remains valid for its own attempt.

| Item | Reviewed identity |
| --- | --- |
| Story and PR | [kburson/aitm #141](https://github.com/kburson/aitm/issues/141) and [PR #262](https://github.com/kburson/aitm/pull/262), `codex/aitm-wave30-141` into `trunk` |
| Base | `71aa5c880fc6a1db1cf676dfc663373f02ef7b16` |
| Head | `be8f5bff9311655fb788e597c69069c23609a341` |
| Tested merge and tree | `95f6ebe25c6cca5c67efdc509a617842b729f276`, ordered parents base then head, tree `ed4ea486732346bfaaf7d518bc91b4d13b555fd5` (also the head tree) |
| Source blobs | `tools/ci/tia/python_graph.py`: `30d61a548a8127356f045892f40481e5593879bd`; `tools/ci/tests/test_tia_python_graph.py`: `d1d50524ae921f7a89ce0838876dadad62b0afdd` |
| Governing material | Accepted leaf design, refinement, Plan and JIT, source assessments, exact owner disposition and trusted verifier receipt read from `.aitm/stories/001/141/` at planning commit `3865e1e753c98e0e721809a7ff9575d4807185ce`. Accepted Plan/JIT publication `201d21a0deca8b4a03d39a4ba8b8ba383deee4cd`. |
| Hosted attempt | [43140853744 attempt 1](https://github.com/kburson/aitm/actions/runs/43140853744/attempts/1), completed successfully on the exact PR/base/head, with all six required jobs successful. |

## [P1] Record uncertainty for direct references to `importlib.__import__`

Location: [`tools/ci/tia/python_graph.py:181–205`](https://github.com/kburson/aitm/blob/be8f5bff9311655fb788e597c69069c23609a341/tools/ci/tia/python_graph.py#L181-L205), with the loader table at line 12.

The design requires conservative AST recognition of references to `__import__`, including aliases and from-imports of the loader. The detector maps `importlib` to just `import_module` and `builtins` to just `__import__`. Its general `__import__` check applies only to bare AST names. CPython's `importlib.__import__` is also a functioning loader, and these two direct references need no inference through runtime data flow:

```python
# src/direct.py
import importlib as il
assert il.__import__("probe_helper_141").VALUE == 42

# src/imported.py
from importlib import __import__ as load
assert load("probe_helper_141").VALUE == 42
```

On the exact reviewed source and locked CPython 3.13.9, I used the two files above, `src/probe_helper_141.py` containing `VALUE = 42`, and a positive-control reader using `from importlib import import_module as load`. The policy mapped `b"src"` and approved external `"importlib"`, with the remaining fields empty. All three reviewer-authored fixtures successfully loaded the helper when executed in isolation. The static graph returned `edges=()` and a single unbounded `dynamic-import` record for the positive control. It returned no record for either `__import__` reader.

If the helper changes and another test provides a known edge to it, a later selector can otherwise accept that positive edge while omitting consumers of these unmarked readers. The provider must expose the uncertainty so #142 can account for it. Recognize the direct attribute and from-import forms of this loader, including aliases, with the existing exact-reader bound behavior. Add a regression covering both forms and a coexisting ordinary edge. Revalidate and review the replacement against fresh exact-candidate evidence.

## Other reviewed evidence

- The live PR was open and unmerged, with the issue open and Project **In review** at readback. Live remote `trunk`, PR head and PR merge refs matched the table. GitHub's tested commit had the exact ordered parents and tree. The attempt-specific API showed success for `python-base`, `python`, `quality`, `file-checks`, `collect-evidence` and `aitm-ci`. Artifact `13909448252` was unexpired and its live archive digest matched the retained trusted verifier receipt. The retained exact-tree owner disposition and the #103 verifier pass bind the same PR, source and run attempt. I checked the receipt against live identities; this source review did not re-run the trusted verifier.
- The exact base-to-head diff contains only the two allowed regular-file additions. `git diff --check` passed, and the source checkout was clean at readback. The delivered #139 and #140 revisions are ancestors of the base. There is no change to active invocation policy, workflow, existing gate controls, runtime declarations, or selection. The two added paths require the #103 gate-control disposition. The unchanged hosted test list excludes the new graph suite and the four-helper coverage denominator excludes the module.
- Snapshot reads use the three accepted endpoint inputs and propagate bound-read refusal. I reviewed byte identity, source and policy validation, AST ownership, known-edge retention with ambiguity, relative and from-list handling, pytest cutoff/config scope and provenance, explicit package endpoints, and deterministic records against the accepted design. The earlier assessment's wildcard-package and namespace named-child corrections remain present with regressions. I found no other blocking issue within the accepted static profile.
- On an independent Git archive of the head, with a separate uv 0.10.6 locked environment, CPython 3.13.9, disabled pytest cache and dedicated basetemp, the graph, inventory and snapshot suites passed: **104 passed in 22.53 seconds**. Ruff lint passed and Ruff format confirmed both added files were already formatted. The direct-loader probe is separate from the candidate tests and identifies a case that those green results do not cover.
