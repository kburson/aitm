# #147 attempt 1 replacement local validation

**Implementer** Codex / story147 · **Repository** `kburson/aitm` · **Target** `trunk`

| Identity | Value |
| --- | --- |
| Baseline | `71aa5c880fc6a1db1cf676dfc663373f02ef7b16` · tree `b4a757f106b89086a24d0e909bc259d7b5b93c88` |
| Replacement candidate | `0d8f8ea353d71ab19802e882ceecbd105e6837ae` · tree `9699130f9be8411cb2a5646197e803956b1ef1b3` |
| Superseded candidate and sole correction parent | `a9f97f937369192b6f565f6d5cec1e26340358ab` · tree `b3aef9e5f6b75aa987f443bc6133d5a243147011`. [Original local evidence](local-validation.md) |
| Branch and custody | `codex/aitm-wave30-147`. Clean after local correction commit. The tested blobs were verified again at commit. Both the correction and the cumulative diff from trunk contain only the two owned paths. |
| `tools/ci/tia/controls.py` | Git blob `b89aff93e93323749946ec5c2b40a72af9a21203` · SHA-256 `7283e2dcb149adba06ab1fd992d39f643c5b217c06d141dd1ef4a5578b541001` |
| `tools/ci/tests/test_tia_controls.py` | Git blob `4c8d0e7bce5c75cbe86abcecf4d68ba4b440db62` · SHA-256 `a33ca2a3c3ad7befc485c11b45adfdd357e5b1516eddaa793ffa58543d4bebbc` |
| Environment | macOS 26.6.2, Darwin arm64/APFS, locked CPython 3.13.9, uv 0.10.6, PATH Git 2.42.1 and Apple Git 2.54.0 for Git fixture construction. |

## Findings and correction

- Two exactly matching approvals originally cleared the disposition hold on a full workload missing its CI-helper lane. The correction requires `ControlCandidate.suite_policy` to contain the existing caller-authenticated T02 `SuitePolicy` bytes and workload. The raw suite and CI policy hashes must equal the digests in `Scope`. T02's validated policy supplies the complete required profile/platform pairs and owners. T10 verifies the exact pair set and compatible runner and capabilities before matching either approval. Missing or contradictory policy or scope holds and requires full. A separately named comparison workload retains full on changed controls and its decisions cannot satisfy a full-workload binding.
- A reference with matching raw digest originally admitted malformed nested T02 scope provenance. The correction requires exact 64-hex observer and receipt digests and a nonempty map of named 40/64-hex Git control identities in every scope. The validated reference preserves the original values. Authority and custody remain independently established by the caller.
- The two named public functions and their evidence boundaries remain as accepted. The correction adds no authority source, policy authoring, provider integration, workflow, or package changes.

The two focused refusal groups produced 11 expected failures on the original logic. After correction, 14 targeted cases passed in 4.27 seconds, including independent proof absence or mismatch, a named comparison, and both complete and omitted additional platform lanes under a reviewed suite policy.

## Exact replacement checks

```bash
PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --python 3.13.9 --locked python -m pytest -q tools/ci/tests/test_tia_controls.py
PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --python 3.13.9 --locked python -m pytest --collect-only -q tools/ci/tests/test_tia_controls.py
PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --python 3.13.9 --locked python -m pytest -q tools/ci/tests/test_tia_controls.py tools/ci/tests/test_tia_inventory.py tools/ci/tests/test_tia_snapshot.py tools/ci/tests/test_verify_pr.py
uv run --project packages/aitm-usage --python 3.13.9 --locked ruff check --config packages/aitm-usage/pyproject.toml tools/ci/tia/controls.py tools/ci/tests/test_tia_controls.py
uv run --project packages/aitm-usage --python 3.13.9 --locked ruff format --check --config packages/aitm-usage/pyproject.toml tools/ci/tia/controls.py tools/ci/tests/test_tia_controls.py
git diff --check 71aa5c880fc6a1db1cf676dfc663373f02ef7b16 0d8f8ea353d71ab19802e882ceecbd105e6837ae
```

| Check | Observed result |
| --- | --- |
| V(controls) | 55 passed in 16.41 seconds |
| Focused collection | 55 collected in 0.03 seconds. [Ordered node IDs](local-focused-nodeids-r2.txt), SHA-256 `816dacee770b0235c65b5e7af27f3be55695482e8876af895242166cd85e1e8f`. |
| T10, T02, T03 and #103 verifier | 231 passed in 38.45 seconds |
| Ruff and Git | Lint and format checks passed. Whitespace, exact two-file scope and clean checkout verified. |

Test → Develop recorded 2026-11-12T02:25:04Z. Replacement committed 2026-11-12T02:30:37Z, 333 seconds observed rework wall time. Active implementation agent-hours are Unknown. [Replacement delivery checklist addendum](delivery-checklist-r2.md)
