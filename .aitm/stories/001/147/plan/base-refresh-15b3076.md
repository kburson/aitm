# #147 base refresh after #141 delivery

**Attempt 1 · Implementer Codex / story147**

At 2026-11-12T03:39:53Z the assigned branch `codex/aitm-wave30-147` merged exact protected trunk `15b3076848e726c3fed62c2725621106a04246ef`, tree `f2c045b29ed4c8f99ba8056de459d17ff340f4d3`, in a local non-rewriting merge. The result is clean head `26e8ba1aa41eb8eb1c26d963a189c5cc43771a85`, tree `cab945d1c8bdd14bab3b1f7aa06fde7b023f9357`. Its ordered parents are `96fdc4d34c3645fee7f13ef68527f9b6486c316b` then the exact trunk commit above. Remote trunk read back at the same identity after local validation.

The old-to-new base diff contains exactly the #141 additions `tools/ci/tia/python_graph.py` and `tools/ci/tests/test_tia_python_graph.py`. The canonical workflow, CI helpers and verifier, package configuration/lock, CI and suite policies, and T02/T03 provider inputs have identical blobs. The exact new-base diff has only the two #147 additions. The owned blobs are unchanged from the R3 validation: `412bd7b66b89a3638a070477640656a21e970a92` for `controls.py` and `43726eb56a42e3306992228f4d50aed35cab42d6` for its tests. [#141 delivery PR](https://github.com/kburson/aitm/pull/262) · [R3 local proof](local-validation-r3.md)

Locked CPython 3.13.9 and uv 0.10.6 on macOS 26.6.2 Darwin arm64/APFS. All commands ran on the clean refreshed head.

```bash
PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --python 3.13.9 --locked python -m pytest -q tools/ci/tests/test_tia_controls.py
PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --python 3.13.9 --locked python -m pytest --collect-only -q tools/ci/tests/test_tia_controls.py
PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --python 3.13.9 --locked python -m pytest -q tools/ci/tests/test_tia_controls.py tools/ci/tests/test_tia_inventory.py tools/ci/tests/test_tia_snapshot.py tools/ci/tests/test_verify_pr.py
uv run --project packages/aitm-usage --python 3.13.9 --locked ruff check --config packages/aitm-usage/pyproject.toml tools/ci/tia/controls.py tools/ci/tests/test_tia_controls.py
uv run --project packages/aitm-usage --python 3.13.9 --locked ruff format --check --config packages/aitm-usage/pyproject.toml tools/ci/tia/controls.py tools/ci/tests/test_tia_controls.py
git diff --check 15b3076848e726c3fed62c2725621106a04246ef 26e8ba1aa41eb8eb1c26d963a189c5cc43771a85
```

Focused 63 passed in 17.71 seconds. Collection found the same 63 ordered nodes byte-for-byte, SHA-256 `85618b0a8889f1f9013dca24fab3a8c714676fea05f2c7984ece29e210ccebe4`. Combined regression 239 passed in 41.87 seconds. Ruff lint/format and exact diff whitespace checks passed. [Focused node IDs](local-focused-nodeids-r3.txt)

The coordinator uses the refreshed head/base for the new hosted run, exact owner disposition, protected verifier and independent source review.
