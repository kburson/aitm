# Repository CI

Ordinary same-repository PRs use a temporary merge from GitHub and the stable `aitm-ci` job. Trunk pushes verify their own tree and do not satisfy a PR gate. The Python suite runs serially on a qualified Darwin APFS runner. Each required job must pass, and a missing, cancelled or skipped required job holds delivery.

The collector and CI helpers each have an unrounded 90% line floor. Coverage includes unimported production code, records branch coverage separately, and measures normally exiting CLI and service child processes before combining raw shards. Tests added for coverage must verify a behavior, an invariant or a failure/recovery outcome.

Use the locked toolchain from the repository root.

```sh
uv sync --project packages/aitm-usage --locked --python 3.13.9
(cd packages/aitm-usage && .venv/bin/ruff check . && .venv/bin/ruff format --check .)
packages/aitm-usage/.venv/bin/ruff check --config packages/aitm-usage/pyproject.toml tools/ci
packages/aitm-usage/.venv/bin/ruff format --check --config packages/aitm-usage/pyproject.toml tools/ci
go run github.com/rhysd/actionlint/cmd/actionlint@v1.7.12
```

Local tests give local evidence. For delivery, read the authenticated PR, workflow, latest run attempt and its jobs. Verify the attempt archive and its signed subject against the ordinary PR merge ref. The signed certificate must identify the actual source SHA and exact invocation. Confirm the raw merge parents against live base and head, approved workflow and policy controls, both raw line floors, and exact review before merging. The signed artifact contains sanitized evidence and creates a public GitHub attestation and Sigstore transparency record.

The isolated base lane uses the delivered observer and policy from the exact target. On initial bootstrap it uses the independently reviewed and digest-pinned standalone blobs. The signer downloads only the exact collector archive, verifies the raw digest and allowed member, and signs the fixed evidence file without candidate checkout or executable input.

## Verify a pull request from the target

Run the delivered verifier from a clean checkout of the current declared target with GitHub CLI 2.97.0.

```sh
python tools/ci/verify_pr.py --repo kburson/aitm --pr 123 --target trunk --output /tmp/aitm-ci-readback.json
```

The verifier reads GitHub and writes the local result. For a reviewed gate-control change, pass `--reviewed-tree <tested-tree-sha>` from the existing source review. A stale run, incomplete attempt, invalid bundle or mismatched merge holds the result. The verifier does not change branch protection or merge the PR.
