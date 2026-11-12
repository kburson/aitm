# #141 local verification · Formal source-review correction

Codex / story141, assigned implementer. Validation on 2026-11-12 UTC.

| Item | Exact identity |
| --- | --- |
| Source and target | `kburson/aitm`, `codex/aitm-wave30-141` into `trunk` |
| Accepted plan and pickup | Planning `201d21a0deca8b4a03d39a4ba8b8ba383deee4cd`; Review → Develop correction authorization `ba9b2965e738d5dd97163161393d83aea9fe23c4` |
| Pinned base | `71aa5c880fc6a1db1cf676dfc663373f02ef7b16`, tree `b4a757f106b89086a24d0e909bc259d7b5b93c88` |
| Prior reviewed head | `be8f5bff9311655fb788e597c69069c23609a341`, tree `ed4ea486732346bfaaf7d518bc91b4d13b555fd5`, retained as the new commit's parent |
| Replacement head and tree | `8a4d9d5ee81a98596b893c03f43b383fa3acab22`, `f2c045b29ed4c8f99ba8056de459d17ff340f4d3`; clean after local commit at 03:27:57 UTC |
| Source and test blobs | `tools/ci/tia/python_graph.py` `5e1657560d4f48e5d6834dfd82bef1f30be74626`; `tools/ci/tests/test_tia_python_graph.py` `d61cdbebc1ec29f9d5ec62ae62160b6fec99a0d9`; exact two regular additions from the pinned base |
| Runtime | Darwin arm64, Apple Git 2.54.0, uv 0.10.6, locked CPython 3.13.9 and Ruff 0.15.22 |

## Finding and disposition

The [formal source review](reviews/141-formal-sar-r1.md) found that
`importlib.__import__` is a functioning loader on the pinned runtime.
The detector recognized only `import_module` on the `importlib`
module, so it left both the module-alias attribute and from-import
alias cases without a dynamic-input record. I confirmed both loader
forms and reproduced the missing uncertainty before editing the module.

The fix allows both recognized loader names on `importlib`. The
provider now emits `dynamic-import` for an attribute on an aliased
module and for a directly imported loader alias. The regression
asserts that the ordinary helper import remains present and that a
reviewed exact-reader bound applies to the first form, with unbounded
reach for the second form. The public graph interface and data formats
remain as accepted.

## Local proof

Run from the assigned checkout with a private uv environment.

```bash
export PYTHONPATH="$PWD/tools/ci"
uv run --project packages/aitm-usage --locked --python 3.13.9 python -m pytest -q tools/ci/tests/test_tia_python_graph.py -k importlib_dunder_import
uv run --project packages/aitm-usage --locked --python 3.13.9 python -m pytest --collect-only -q tools/ci/tests/test_tia_python_graph.py
uv run --project packages/aitm-usage --locked --python 3.13.9 python -m pytest -q tools/ci/tests/test_tia_python_graph.py
uv run --project packages/aitm-usage --locked --python 3.13.9 python -m pytest -q tools/ci/tests/test_tia_python_graph.py tools/ci/tests/test_tia_inventory.py tools/ci/tests/test_tia_snapshot.py
uv run --project packages/aitm-usage --locked --python 3.13.9 ruff check --config packages/aitm-usage/pyproject.toml tools/ci/tia/python_graph.py tools/ci/tests/test_tia_python_graph.py
uv run --project packages/aitm-usage --locked --python 3.13.9 ruff format --check --config packages/aitm-usage/pyproject.toml tools/ci/tia/python_graph.py tools/ci/tests/test_tia_python_graph.py
git diff --check 71aa5c880fc6a1db1cf676dfc663373f02ef7b16 HEAD
```

| Observation | Result | Private log SHA-256 |
| --- | --- | --- |
| Behavior red on the prior implementation | Both cases failed at the expected empty unresolved tuple comparison, 19 deselected. Exit 1. | `813b3ebe4150bca21c0a068628113afba4546bc1c0169b4d696fe39fce53c256` |
| Behavior green after the correction | 2 passed, 19 deselected in 0.03s | `7ebefd1eeaf3691a17f430bee53870456ac778ff10bedc62e966bbea12a5722c` |
| Focused collection on replacement tree | 21 collected in 0.01s | `0be09a0c2b6ba24fb87642c4d7d33768d51ad0cd6b62674dad1c0b76eaef234e` |
| Focused execution on replacement tree | 21 passed in 0.93s | `da50f2614da3da707dea099573d9d24bd1b0a9f35ab7d0d9d000447f64302026` |
| Related T02/T03 on replacement tree | 106 passed in 23.08s | `5f4b3e59c619290083992ff6158f351a5f0eb73f68e798a435da7feebdebd8fd` |
| Ruff and whitespace on replacement | Lint passed, two files already formatted, whitespace clean | `afa20b27dacc9bf0aba3c1d265964c21e04ab42f6e39e2dd4769718ceded003a` for Ruff |

[Focused node IDs](2026-11-11-141-focused-nodeids-sar-r1.txt) are
retained in collection order, 21 lines, SHA-256
`bf8ecad04dc858be7d84e930cf78bda6ae21ca12b355e06617f2a846a03f7cdc`.
The two added IDs are
`test_importlib_dunder_import_reports_unresolved_scope[aliased-module]`
and `test_importlib_dunder_import_reports_unresolved_scope[from-import]`.

The earlier local product diagnostic, hosted #103 proof and SAR verdict
stay bound to their recorded source revisions. The replacement requires
fresh hosted validation, owner disposition, trusted verifier proof and
formal independent review on its exact applicable base and tested tree.
