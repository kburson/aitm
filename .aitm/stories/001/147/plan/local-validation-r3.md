# #147 attempt 1 policy-reconciliation replacement local validation

**Implementer** Codex / story147 · **Repository** `kburson/aitm` · **Target** `trunk`

| Identity | Value |
| --- | --- |
| Baseline | `71aa5c880fc6a1db1cf676dfc663373f02ef7b16` · tree `b4a757f106b89086a24d0e909bc259d7b5b93c88` |
| Candidate | `96fdc4d34c3645fee7f13ef68527f9b6486c316b` · tree `8671a77850794d4de78f6c2250b75aa9bf6c5c50` |
| Previous candidate and sole parent | `0d8f8ea353d71ab19802e882ceecbd105e6837ae` · tree `9699130f9be8411cb2a5646197e803956b1ef1b3`. [Prior evidence](local-validation-r2.md) |
| Branch and custody | `codex/aitm-wave30-147`. The tests ran on the exact owned blobs and the clean committed tree contains those blobs. The correction and cumulative changes from the base each touch only the two owned files. |
| `tools/ci/tia/controls.py` | Git blob `412bd7b66b89a3638a070477640656a21e970a92` · SHA-256 `180180bc2298f9ade1d1bf40b8861b783f78f3145681046ee788e45b07620132` |
| `tools/ci/tests/test_tia_controls.py` | Git blob `43726eb56a42e3306992228f4d50aed35cab42d6` · SHA-256 `6153bdc3dcc32cbe6b84d55178dc9d8cb1203a176f216e26006c4c2b211ef8a6` |
| Environment | macOS 26.6.2, Darwin arm64/APFS, locked CPython 3.13.9, uv 0.10.6, PATH Git 2.42.1 and Apple Git 2.54.0 for fixture construction. |

## Formal review finding and correction

The independent SAR held the previous candidate because reviewed additions and changed row metadata could contradict the bound policy. A reference could also omit a fixed helper target and preserve the incomplete set through replay. An independently reproduced zero-step reference missing one fixed helper was accepted. A reviewed row naming a module absent from the suite policy was also admitted.

`InventoryTarget.policies` now carries the existing caller-authenticated T02 `SuitePolicy` records. Their raw suite/CI policy SHA-256 pairs must exactly cover all distinct points, including the reference and current target. T10 uses T02 policy validation for the fixed replay lanes and the existing obligation projection for the complete rows of each lane. It compares the projected rows against the received rows, with policy-required IDs and exact helper targets enforced at the anchor and every successor. It also preserves prior helper targets across transitions. Replay uses the projection for consistency checking and preserves the original qualified collection receipt. It creates no collection evidence or authority.

The unregistered addition, incorrect suite, incorrect isolation group, and missing anchor helper target produced four expected behavior failures on the prior logic. The corrected policy projection also exposed an error in the earlier positive fixture. It copied a test-specific override onto a new ID. The fixture now derives the valid addition directly through T02. All 49 replay-focused cases passed in 1.15 seconds, including missing or wrong policy proof and a genuine reviewed metadata replacement under a revised policy.

## Exact candidate checks

```bash
PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --python 3.13.9 --locked python -m pytest -q tools/ci/tests/test_tia_controls.py
PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --python 3.13.9 --locked python -m pytest --collect-only -q tools/ci/tests/test_tia_controls.py
PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --python 3.13.9 --locked python -m pytest -q tools/ci/tests/test_tia_controls.py tools/ci/tests/test_tia_inventory.py tools/ci/tests/test_tia_snapshot.py tools/ci/tests/test_verify_pr.py
uv run --project packages/aitm-usage --python 3.13.9 --locked ruff check --config packages/aitm-usage/pyproject.toml tools/ci/tia/controls.py tools/ci/tests/test_tia_controls.py
uv run --project packages/aitm-usage --python 3.13.9 --locked ruff format --check --config packages/aitm-usage/pyproject.toml tools/ci/tia/controls.py tools/ci/tests/test_tia_controls.py
git diff --check 71aa5c880fc6a1db1cf676dfc663373f02ef7b16 96fdc4d34c3645fee7f13ef68527f9b6486c316b
```

| Check | Observed result |
| --- | --- |
| V(controls) | 63 passed in 17.67 seconds |
| Focused collection | 63 collected in 0.03 seconds. [Ordered node IDs](local-focused-nodeids-r3.txt), SHA-256 `85618b0a8889f1f9013dca24fab3a8c714676fea05f2c7984ece29e210ccebe4`. |
| T10, T02, T03 and #103 verifier | 239 passed in 42.47 seconds |
| Ruff and Git | Lint, format and whitespace checks passed. Exact two-file scope and clean checkout verified. |

Review → Develop recorded at 2026-11-12T03:27:44Z. Replacement committed at 2026-11-12T03:32:10Z, 266 seconds observed rework wall time. Active implementation agent-hours are Unknown. [Replacement delivery checklist](delivery-checklist-r3.md)
