# Repository CI

Ordinary same-repository PRs use GitHub's tested merge and the stable `aitm-ci` job. The trusted base selector compares both exact Git trees and records a disposition for every changed path. Qualified source and fixture changes run the declared consumer modules. Shared inputs, unclassified paths, moves, removals and changed consumer inventories require the full applicable suite. Explicit no-impact documentation rules still run the helper checks and wheel smoke.

A narrowed PR runs the full suite on its first successful attempt for the exact PR, base, selector, policy and selected modules. The signed gate publishes a stamp only after the full run and all required checks pass. A later push with that same identity still runs the mapped check and can reuse the stamp from a completed successful run. Superseded runs are cancelled. The full product and CLI suite uses three pytest-xdist workers on Ubuntu 24.04 runners and may take up to 20 minutes. The initial bootstrap observer uses the serial path. Trunk pushes verify their own tree.

The path map qualifies a small set of inputs. Its declarations describe how each input reaches the tests and bind the audited package and CI consumer inventory. If that inventory changes, a later change to the input runs full until the mapping is reviewed again. The trusted verifier compares the signed selection with the two Git trees and checks that each selected module has a passing call.

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

The isolated Ubuntu base lane uses the delivered observer and policy from the exact target. It uses a private scratch directory under the sticky system temporary directory for custody fixtures and their pinned interpreter. The [hosted base qualification](https://github.com/kburson/aitm/actions/runs/43726916730) compares serial and parallel outcomes from the same source and runner image. On initial bootstrap it uses the independently reviewed and digest-pinned standalone blobs. The signer downloads only the exact collector archive, verifies the raw digest and allowed member, and signs the fixed evidence file without candidate checkout or executable input.

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

The native macOS ACL and FSEvents checks can be run on demand from the package directory.

```sh
cd packages/aitm-usage
uv run --locked pytest tests/test_host_watch.py native-tests
```

The Python jobs retain the full applicable test inventory, slow test durations, setup and run timings, and the cold or warm cache result. Use those observations when evaluating test scheduling as the suite grows.

## Report pinned obligations for an uncommitted change

Run the report from a trusted checkout containing the tooling. Pass the inspected
checkout separately and use its exact 40-character HEAD commit for `--base`.
Use `-B` to keep Python from writing bytecode caches in the tooling checkout.

```sh
python -B -E -s -m tools.ci.tia.working_tree_report \
  --repo /path/to/inspected/checkout \
  --base 8799c5a445dd4b51d499132e9a314b64796ae918
```

Version 1 supports an edit confined to appending LF-terminated ASCII comments
and blank lines to the audited Grok scope hook source, with the original bytes
and file mode preserved. It admits the evidence anchor shown above and a tree
whose only committed differences are this report's three new files and the CI
guide update. Other committed changes require fresh qualification. Use separate
checkouts if the inspected checkout contains edits to the tooling. Git-ignored
files are outside the effective snapshot.

A positive JSON report exits 0 with `mode: pinned-mapped-obligations`, the observed
snapshot, the admission evidence, and the 30 pinned test IDs. The candidate
inventory and impact completeness are both `unqualified`. The command reads
captured data without importing candidate Python or running tests.

An unavailable report exits 2 with a machine-readable `reason` and an empty
`node_ids` array. This includes invalid arguments, an unsupported or clean
worktree, and an observation that changed during the report. Bind any subsequent
action to the reported snapshot and revalidate it before use.
