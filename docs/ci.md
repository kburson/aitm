# Repository CI

Ordinary same-repository PRs use a temporary merge from GitHub and the stable `aitm-ci` job. Trunk pushes verify their own tree and do not satisfy a PR gate. The Python suite runs serially on a qualified Darwin APFS runner. The workflow reports a pass only when all its applicable jobs pass.

The collector and CI helpers each have an unrounded 90% line floor. Coverage includes unimported production code, records branch coverage separately, and measures normally exiting CLI and service child processes before combining raw shards. Tests added for coverage must verify a behavior, an invariant or a failure/recovery outcome.

Use the locked toolchain from the repository root.

```sh
uv sync --project packages/aitm-usage --locked --python 3.13.9
(cd packages/aitm-usage && .venv/bin/ruff check . && .venv/bin/ruff format --check .)
packages/aitm-usage/.venv/bin/ruff check --config packages/aitm-usage/pyproject.toml tools/ci
packages/aitm-usage/.venv/bin/ruff format --check --config packages/aitm-usage/pyproject.toml tools/ci
go run github.com/rhysd/actionlint/cmd/actionlint@v1.7.12
```

To verify a hosted PR run, read the authenticated PR, workflow, latest attempt and jobs. Verify the attempt archive and signed subject against the ordinary PR merge ref. Compare the signed source and invocation with the live base and head, workflow and policy controls, and both raw line floors. The signed artifact contains sanitized evidence and creates a public GitHub attestation and Sigstore transparency record.

The isolated base lane uses the delivered observer and policy from the exact target. On initial bootstrap it uses the independently reviewed and digest-pinned standalone blobs. The signer downloads only the exact collector archive, verifies the raw digest and allowed member, and signs the fixed evidence file without candidate checkout or executable input.

## Verify a pull request from the target

Run the delivered verifier from a clean checkout of the current declared target with GitHub CLI 2.97.0.

```sh
python tools/ci/verify_pr.py --repo kburson/aitm --pr 123 --target trunk --output /tmp/aitm-ci-readback.json
```

The verifier reads GitHub and writes the local result. For a reviewed gate-control change, pass `--reviewed-tree <tested-tree-sha>` from the existing source review. A stale run, incomplete attempt, invalid bundle or mismatched merge holds the result. The verifier does not change branch protection or merge the PR.

## Check maintained files locally

Use Node 24.22.2 and the locked lint environments from the repository root.

```sh
npm ci --prefix tools/ci/file-lint --ignore-scripts --no-audit --no-fund
uv sync --project tools/ci/file-lint --locked --python 3.13.9
uv run --project packages/aitm-usage --locked --no-dev --python 3.13.9 \
  python tools/ci/file_checks.py --root . \
    --markdownlint tools/ci/file-lint/node_modules/.bin/markdownlint-cli2 \
    --yamllint tools/ci/file-lint/.venv/bin/yamllint
```

The file lane checks tracked Markdown and YAML with markdownlint-cli2 and yamllint. Markdown runs against a clean copy of the tracked inputs with the selected configuration. The file lane flags YAML's file-wide lint suppression. It parses tracked JSON strictly and checks the declared CI policy, rate card and activation receipt formats. The existing quality job also runs actionlint for Actions workflow semantics. JSON Lines and compressed evidence use separate formats.

TypeScript reports **not applicable** because the repository has no product TypeScript package. The tooling manifest under `tools/ci/file-lint/` only installs the Markdown checker. The first tracked product TypeScript inputs surface a hold until the product has a working ESLint and typescript-eslint check, `tsc --noEmit`, and Vitest with meaningful behavioral tests and an unrounded 90% V8 line floor.

The Python jobs retain the full applicable test inventory, slow test durations, setup and run timings, and the cold or warm cache result. Use those observations when evaluating test scheduling as the suite grows.
