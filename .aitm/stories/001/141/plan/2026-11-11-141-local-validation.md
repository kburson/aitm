# #141 local validation · Attempt 1

Codex / story141, assigned implementing agent. Validation on 2026-11-12 UTC.

## Exact candidate

| Item | Observed identity |
| --- | --- |
| Source | `kburson/aitm`, `codex/aitm-wave30-141` into `trunk` |
| Accepted Plan/JIT | Planning `201d21a0deca8b4a03d39a4ba8b8ba383deee4cd`; Plan SHA-256 `ba033428548e17f629e8f5b161a85b64b7980ebd74a05f2baba530e533e86944`; JIT SHA-256 `445e6838ac835c1ed61f75209c5e5ebec0d43e1c159a220b5f993c8147533e1c` |
| Develop checkpoint | Planning `67e9049aa4c5773720c83d65faaad3e985122e3a`, attempt 1, generation 1 |
| Base | `71aa5c880fc6a1db1cf676dfc663373f02ef7b16`, tree `b4a757f106b89086a24d0e909bc259d7b5b93c88` |
| Head and tree | `be8f5bff9311655fb788e597c69069c23609a341`, tree `ed4ea486732346bfaaf7d518bc91b4d13b555fd5`, immediate parent `39d2ef5166db04a1ae9fa3cf24d504b591a7fa18` with sole parent the pinned base. Clean after replacement commit at 02:20:05 UTC. |
| Added blobs | `tools/ci/tia/python_graph.py` `30d61a548a8127356f045892f40481e5593879bd`; `tools/ci/tests/test_tia_python_graph.py` `d1d50524ae921f7a89ce0838876dadad62b0afdd`. Both regular mode `100644`. |
| Local environment | Darwin arm64, Apple Git 2.54.0, uv 0.10.6, locked CPython 3.13.9 and Ruff 0.15.22. A private uv environment was used for the assigned worktree. |

## Behavior and exact local checks

The first behavior run put a collection-safe empty graph scaffold in an
ignored namespace overlay. The real provider module was absent. Thirteen
tests reached expected missing behavior assertions. The alias, relative,
re-export and cycle test compared an empty edge set with six expected
edges. The dynamic and ambiguity tests also reached missing-edge
assertions. The injected bound-read failure case reached the expected
exception assertion. Pytest exited 1 with 13 failures and no import or
collection failure. The first implementation passed those 13 tests.

A follow-on policy shape test reproduced three failures against the first
implementation. Mutable outer and inner sequences were accepted and an
invalid nested record escaped as `AttributeError`. Explicit record and
tuple validation now refuses those shapes with `ValueError`.

Source preflight on original local head `39d2ef5` found a possible
child import through a package's `__all__` when the graph saw
`from pkg import *`. The graph also treated a missing explicit
from-list name under a namespace-only base as covered without a source
owner. Both regressions failed for the missing uncertainty on that
head and passed after the fix. The replacement keeps the package
initializer and any known child edges, and records unbounded
`wildcard-import` or `unresolved-import` for the affected reader.
The original local candidate remains in Git history with its own
17 focused and 102 related passes. It was superseded before Test.

Run from the checkout root, with only the real module namespace on
`PYTHONPATH`:

```bash
export PYTHONPATH="$PWD/tools/ci"
uv run --project packages/aitm-usage --locked --python 3.13.9 python -m pytest --collect-only -q tools/ci/tests/test_tia_python_graph.py
uv run --project packages/aitm-usage --locked --python 3.13.9 python -m pytest -q tools/ci/tests/test_tia_python_graph.py
uv run --project packages/aitm-usage --locked --python 3.13.9 python -m pytest -q tools/ci/tests/test_tia_python_graph.py tools/ci/tests/test_tia_inventory.py tools/ci/tests/test_tia_snapshot.py
uv run --project packages/aitm-usage --locked --python 3.13.9 ruff check --config packages/aitm-usage/pyproject.toml tools/ci/tia/python_graph.py tools/ci/tests/test_tia_python_graph.py
uv run --project packages/aitm-usage --locked --python 3.13.9 ruff format --check --config packages/aitm-usage/pyproject.toml tools/ci/tia/python_graph.py tools/ci/tests/test_tia_python_graph.py
git diff --cached --check
git diff --check
```

| Command observation at committed tree | Result |
| --- | --- |
| Focused collect-only | 19 collected in 0.02s |
| Focused behavior | 19 passed in 0.82s |
| T04 with T02/T03 | 104 passed in 23.37s |
| Ruff and Git whitespace | Ruff lint passed, both files formatted, staged and unstaged whitespace checks passed. After commit, the whitespace comparison against the pinned story base passed. |

Focused node IDs use the `tools/ci/tests/test_tia_python_graph.py::` prefix.

- `test_import_alias_relative_reexport_cycle`
- `test_dynamic_scope`
- `test_ambiguous_owners_keep_possible_edges`
- `test_wildcard_package_import_preserves_initializer_and_uncertainty`
- `test_missing_namespace_from_import_preserves_known_child_and_uncertainty`
- `test_ambiguous_relative_context_keeps_valid_dependency`
- `test_pytest_scope_keeps_fixture_config_and_search_evidence`
- `test_reviewed_package_dependencies_require_exact_endpoints`
- `test_graph_binds_real_snapshot_pair`
- `test_invalid_source_retains_uncertainty`
- `test_bound_read_failure_refuses_graph`
- `test_invalid_policy_cannot_authorize_a_graph[rules0]` through `[rules7]`

Private log SHA-256 values for evidence retention:

| Observation | SHA-256 |
| --- | --- |
| Behavior red | `44600cd6a1bb1d160446b90d9e5169f194edf1372bad9f32759f703ea13ef349` |
| Policy shape red | `7a0373271b843a2ec2fd27c18de405baae497d29361bfdcfafb8edf6a55bed2e` |
| From-list behavior red | `ef0759b7c6c9d9c95b6c40a65a8835a343fdc0dc93a26b77ad12046ae9493b90` |
| From-list behavior green | `a862e8666156d3d43ea512c53b637998f087451d6c81ab3c6c3cbe099596e48d` |
| Replacement collection | `b93be638ba67b9c4cdf35a52c1ef6d6d129467d2f9c2dc270060f62f726d4e8a` |
| Focused green | `e493844ff5347c1e745841e6c8f7de85b76cd19a39c1198ce29659aaf637ac41` |
| Related green | `7d8e2f92d7b22abbfacc568d99f4293e3893f41dbdbf551a5ff74145dd30c7a8` |
| Ruff | `afa20b27dacc9bf0aba3c1d265964c21e04ab42f6e39e2dd4769718ceded003a` |

## Additional local product and helper diagnostics

This separate three-worker check ran from the source root without the
hosted observer, coverage, exact-base lane or attestation. It excluded the
new graph tests. The working-source run preceded the final policy shape
hardening. The comparison used a separate source archive at exact base
`71aa5c8`, a separate locked editable environment and the same test set,
worker count and pytest options. The archive had neither graph addition.
Both runs exited 1.

```bash
export PYTHONPATH="$PWD/tools/ci"
uv run --project packages/aitm-usage --locked --python 3.13.9 python -m pytest -q -n 3 --dist worksteal packages/aitm-usage/tests tools/ci/tests/test_cli_evidence.py tools/ci/tests/test_file_checks.py tools/ci/tests/test_pytest_evidence.py tools/ci/tests/test_python_gate.py tools/ci/tests/test_verify_pr.py
```

| Local source | Observation | Private log SHA-256 |
| --- | --- | --- |
| Working story source before final policy shape hardening | 1290 passed, 5 failed, 3 setup errors in 72.17s | `2c7b17ca20760d9ae3035e5be544968e9eb99d3d3cb53a6741a3b91687a9c576` |
| Isolated exact-trunk source archive | 1199 passed, 34 failed, 65 setup errors in 70.56s. All eight nonpassing story-run node IDs also failed or errored in this baseline run. | `6141b3bfe318656a840c40a41898c8e26d06ccf36b7fc5e8a9df0b4fab0b936d` |

The eight shared node IDs were in unchanged product test files. Failure
phase varied for four IDs. The observed traces include unavailable native
capture frontiers or positions, missing unique native streams, a changed
native scope checkpoint and unpacking missing fixture results. Root cause
of the local monitor fixture variation is unverified.

| Product node ID | Working story | Exact trunk |
| --- | --- | --- |
| `test_monitor_journal.py::test_claude_conflict_requires_distinct_usage_and_current_independent_custody[disabled]` | Failed | Failed |
| `test_monitor_journal.py::test_claude_conflict_requires_distinct_usage_and_current_independent_custody[equal-child]` | Setup error | Failed |
| `test_monitor_journal.py::test_claude_conflict_requires_distinct_usage_and_current_independent_custody[relocated]` | Setup error | Setup error |
| `test_monitor_journal.py::test_journal_holds_independently_admitted_claude_copy_with_changed_scope` | Failed | Setup error |
| `test_monitor_journal.py::test_journal_holds_keyed_grok_contradiction_without_touching_codex` | Failed | Failed |
| `test_monitor_journal.py::test_journal_holds_native_claude_agent_overlap_and_mixed_diagnostics[aggregate-overlap]` | Failed | Setup error |
| `test_monitor_scope.py::test_ordinary_mark_routes_unanchored_usage_after_native_rescan` | Failed | Setup error |
| `test_monitor_scope.py::test_queued_monitor_scope_cli_joins_only_first_native_target` | Setup error | Setup error |

The exact current [trunk push run](https://github.com/kburson/aitm/actions/runs/43138335027/attempts/1)
completed its four applicable jobs on `71aa5c8`. The story's required
PR evidence still needs the #103 full three-worker product/CLI candidate
lane and serial exact-base lane, helper and coverage checks, file/quality,
attestation and exact verifier result under the applicable base and head.
The focused graph check has its own local evidence. Hosted coverage
does not measure this module in the helper gate denominator.
