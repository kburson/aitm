# #147 attempt 1 local validation

**Implementer** Codex / story147 · **Repository** `kburson/aitm` · **Target** `trunk`

| Identity | Value |
| --- | --- |
| Baseline | `71aa5c880fc6a1db1cf676dfc663373f02ef7b16` · tree `b4a757f106b89086a24d0e909bc259d7b5b93c88` |
| Candidate | `a9f97f937369192b6f565f6d5cec1e26340358ab` · tree `b3aef9e5f6b75aa987f443bc6133d5a243147011` |
| Branch and custody | `codex/aitm-wave30-147`. Exact two-file diff and clean worktree verified after local commit. The same raw blob IDs were verified before the test and at commit. |
| `tools/ci/tia/controls.py` | Git blob `55c0de689374eed8e8c4787391e27f3a32c4aa06` · SHA-256 `dbd056f07842e245d09c02a1feee72d5ad79b0cd5d03957881adc12b76f00b4e` |
| `tools/ci/tests/test_tia_controls.py` | Git blob `c1da9558c7f36ea94fb25353640de2b09e4b1a15` · SHA-256 `282dffff9172b001dd6158338d116bf8d8824a07155f42ed546e46f2d9080d50` |
| Environment | macOS 26.6.2, Darwin arm64/APFS, locked CPython 3.13.9, uv 0.10.6, PATH Git 2.42.1 and Apple Git 2.54.0 for Git fixture construction. |

## Behavior red and green

- `test_control_edit_requires_full_and_independent_disposition` produced five expected behavior failures against the collection-safe scaffold. The scaffold did not set the full requirement for any changed control. After implementation, all seven control cases passed. The final proof also checks inexact change endpoints and invalid target refs, and treats semantically identical lane ordering as equal. The added regressions each failed before correction and passed after it.
- The required `test_reference_inventory_requires_intervening_dispositions` failed first because the scaffold returned no derived inventory. All 32 replay and refusal cases failed against the scaffold, then passed after implementation. The cases use the delivered T02 classifier with an independently supplied hosted-shaped fixture, keep the original reference collection data, and bind both required lanes to review and delivery evidence.
- The new source and fixtures exercise control qualification and applicable inventory comparison. The trusted caller still establishes actor authority, review currency, delivery and collection custody, and actual runtime outcomes.

## Exact candidate checks

From the repository root, with the pinned Python/uv environment:

```bash
PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --python 3.13.9 --locked python -m pytest -q tools/ci/tests/test_tia_controls.py
PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --python 3.13.9 --locked python -m pytest --collect-only -q tools/ci/tests/test_tia_controls.py
PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --python 3.13.9 --locked python -m pytest -q tools/ci/tests/test_tia_controls.py tools/ci/tests/test_tia_inventory.py tools/ci/tests/test_tia_snapshot.py tools/ci/tests/test_verify_pr.py
uv run --project packages/aitm-usage --python 3.13.9 --locked ruff check --config packages/aitm-usage/pyproject.toml tools/ci/tia/controls.py tools/ci/tests/test_tia_controls.py
uv run --project packages/aitm-usage --python 3.13.9 --locked ruff format --check --config packages/aitm-usage/pyproject.toml tools/ci/tia/controls.py tools/ci/tests/test_tia_controls.py
git diff --check 71aa5c880fc6a1db1cf676dfc663373f02ef7b16 a9f97f937369192b6f565f6d5cec1e26340358ab
```

| Check | Observed result |
| --- | --- |
| V(controls) | 41 passed in 12.24 seconds |
| Focused collection | 41 collected in 0.04 seconds. [Ordered node IDs](local-focused-nodeids.txt), SHA-256 `ee2a4e2374bf57a6bf194623ee069e8a2fa51132b1c2eef659cc7b80b9dd7c1a`. |
| T10, T02, T03 and #103 verifier | 217 passed in 34.27 seconds |
| Ruff and Git | All lint checks passed, two files formatted, clean whitespace and exact two-file diff. |

Recorded Dev at 2026-11-12T02:06:23Z and local commit at 2026-11-12T02:18:53Z, 750 seconds observed wall time. Active implementation agent-hours are Unknown. Hosted validation and independent exact-source review remain pending for this candidate. [Delivery checklist](delivery-checklist.md)
