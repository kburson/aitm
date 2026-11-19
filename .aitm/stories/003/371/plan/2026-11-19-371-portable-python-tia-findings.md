# #371 One Python program for affected-test selection

**Finding.** Python source analysis is sufficient for the selection calculation. Keep one CPython program for both platforms. The work under #370 is to bind exact input endpoints and qualify their affected-test evidence before any production integration. Current trunk has a usable file-level graph and conservative fallback. It does not expose standalone index, HEAD, and PR input modes in the local launcher or prove safe narrowing on the ordinary hook edit used here.

## Source, runtime, and operating-system boundaries

CPython is a platform build of the interpreter. It compiles Python source to code objects and executes their bytecode. Cached `.pyc` files carry implementation and version information and exist to avoid recompiling source. Distribute the source. A `py3-none-any` wheel can package Python modules without a platform ABI requirement. It carries neither CPython nor a guarantee that the program's dependencies and system calls work on every host. Native extensions have their own ABI and platform constraints. Node.js offers a comparable interpreter model for JavaScript. Switching runtimes would still leave Git, filesystem custody, and pytest integration to implement. [CPython bytecode](https://docs.python.org/3.13/glossary.html#term-bytecode) · [Compiled module caches](https://docs.python.org/3.13/tutorial/modules.html#compiled-python-files) · [Wheel compatibility tags](https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/) · [Node.js runtime](https://nodejs.org/en/learn/getting-started/introduction-to-nodejs).

The selector can parse captured bytes into Python ASTs and build dependency edges without importing product modules. Resolve static absolute and relative imports, package initialization, pytest configuration and fixtures, and declared resource or package relationships. Start from changed paths in the old and new trees. Walk reverse edges to consuming test files, then use the exact candidate inventory to turn those files into pytest node IDs. A file-level witness can conservatively explain an imported function through its owning module. It cannot prove which individual call sites execute or justify removing tests solely because a function appears unused. Dynamic dispatch, ambiguous imports, generated inputs, or a missing witness must preserve the applicable full fallback. [Python AST](https://docs.python.org/3.13/library/ast.html).

Use Git to resolve the selected branch parent and its divergence commit. Index mode reads the staged blobs and modes. HEAD mode reads the committed tree. A future PR probe should name its base and head and distinguish a head diff from the synthetic merge that is actually tested. The current hosted custody model binds the literal PR base, candidate head, tested commit/tree, ordered merge parents, and run/attempt. A divergence diff can inform impact, while the authenticated tested tree still binds evidence for the hosted route. Preserve unambiguous rename and deletion evidence on both endpoints, and hold on unresolvable or ambiguous inputs. [Git merge base](https://git-scm.com/docs/git-merge-base) · [Git diff](https://git-scm.com/docs/git-diff).

## What is on trunk

Audited commit `5023860969b719989575ad2a07666a91c909ec12`, tree `3fb7143978706746cebdedf31f51a98c306e16db`. [Trunk CI](https://github.com/kburson/aitm/actions/runs/44536101270).

| File | Current behavior and boundary |
| --- | --- |
| `tools/ci/tia/python_graph.py` | Portable source reader. AST import edges, package initializers, declared dependencies, and pytest input edges are file to file. Dynamic imports, unresolved/relative or wildcard context, parse failures, and plugin or fixture ambiguity retain uncertainty. |
| `tools/ci/tia/selection.py` | Portable decision logic over two snapshots and inventories. It emits path witnesses from changed inputs through reverse edges to pytest IDs. Unbounded uncertainty can force full even when concrete paths exist. A missing candidate inventory can make planning unavailable. |
| `tools/ci/path_map.py` | Portable allowlist evaluator. Hosted CI uses the reviewed base-owned map and exact tree comparison. Unknown input, control changes, incompatible file modes, and consumer digest drift select full. It does not call the dependency graph. Its Git reader is an external tool boundary. |
| `tools/ci/tia/local.py` | The CLI uses an explicit `--base` and the effective worktree for both planning and execution. It has separate staged and unstaged provenance but neither an index-only nor a HEAD-only option. Git, uv, pytest, private scratch and filesystem checks are external boundaries. `--plan` runs pytest collection in frozen private copies, so the graph’s source-only property does not extend to the entire launcher. The capability probe uses private modes, `O_NOFOLLOW`, and native no-replace rename through `renameat2` or `renameatx_np`. |
| `tools/ci/tia/snapshot.py` | Git-backed input adapter with offline Git from PATH, byte paths, object and mode checks, filesystem descriptor and identity checks, and drift detection. The local adapter captures the index and worktree. Its hosted library binds supplied commit/tree and PR merge parents, while authenticated GitHub evidence is a separate authority. No CLI dispatches all three proposed modes today. |
| `tools/ci/python_gate.py` | One Python evidence evaluator with an Ubuntu 24.04 hosted contract and pinned runtime, coverage, outcomes, child evidence, and base identity. The trusted verifier authenticates the actual hosted run. The evaluator does not derive dependency paths. |
| `tools/ci/tia/suites.json` | Portable workload data for product tests and all six current CI helper modules. It declares capability and inventory policy. It does not establish that an observed run occurred. |

The Windows follow-on question is whether an adapter can prove equivalent Git snapshot custody, private directory and file identity, no-follow handling of links and reparse points, exclusive publication, and subprocess receipt custody on Windows. The Python AST and graph logic would be shared. No Windows facility was designed or qualified here.

## Linux reference and macOS cross-check

Both hosts ran the identical scratch probes from exact trunk with CPython 3.13.9. Linux was non-root Ubuntu 24.04 in a container. macOS was the local portability cross-check. No production files changed.

| Probe | Linux | macOS |
| --- | --- | --- |
| Clean `tools.ci.tia.local --base <trunk> --plan` | Selected the same seven mandatory IDs | Selected the same seven mandatory IDs |
| Same staged ASCII Grok hook comment append | Full, 1,776 collected obligations | Full, 1,771 collected obligations |
| Git index vs effective working tree | Index had only the staged hook blob. Local snapshot also saw the unstaged documentation and later unstaged hook bytes. | Same semantic result |
| Commit and synthetic tested PR controls | HEAD and synthetic tested tree saw only the committed hook change. A mismatched tested tree was refused. | Same semantic result |
| Snapshot, graph, and selector pytest modules | 100 passed, one alias test skipped because the filesystem has no normalization aliases | 101 passed |

The five-node count difference is expected from the observed collection. Linux adds five native watch tests. Two errno-parameter IDs also differ on each platform. Compare obligations by identity and platform applicability instead of requiring identical raw totals. The stock Grok edit produced the same uncertainty counts on both platforms. There were 12 dynamic-import, 24 unresolved-import, and two relative-import-context records across the old and new sides. Both reported the direct path from `grok_scope_hook.py` to `test_grok_scope_receipts.py`, and a transitive path through `scope_admission.py`, `monitor_control.py`, `monitor_registry.py`, and `conftest.py` to `test_accounting.py`. These are import witnesses within a full decision. The unchanged hosted map also returned full for the same edit, because its audited consumer scope changed. The #354/#355 command is a separately pinned advisory assignment. [Probe readback](2026-11-19-371-probe-evidence.json).

The live checks were planning and fixture-level proof, with a synthetic PR binding used only to exercise tree shape and refusal. The separate authenticated trunk CI run passed 1,525 behavior tests and 251 tool tests. A successful scratch binding or mandatory-only clean selection does not establish that the future probe catches regressions on arbitrary edits.

## Follow-on under #370

**Implement a read-only affected-test probe for the index, HEAD, and PR trees.** Reuse the snapshot adapters, file graph and selection/inventory validation, rather than introduce another language or selector. Extend the missing input interfaces and record the exact input identities, path-to-test witnesses, remaining uncertainties and platform-scoped node IDs. Use proven bounds for a positive narrow case and retain full or unavailable dispositions when sound evidence cannot be established.

The first implementation should compare a supported direct and transitive change against an exact full Ubuntu control, including a seeded behavioral regression caught by both. Exercise staged versus unstaged edits, committed versus worktree changes, PR identity mismatch, and an unresolved dependency that calls for full fallback. Repeat the same-source probe on macOS and explain legitimate platform inventory differences. The read-only probe stays advisory. Hosted gate integration is a later reviewed change and the existing path map and #355 command retain their contracts.
