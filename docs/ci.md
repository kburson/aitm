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

The signed Linux receipt records the requested runner label and observed image
build for each Python job. Both requests must match the same versioned Ubuntu
label, both images must match that Ubuntu release, and both interpreters must
match the pinned runtime. Different image builds of that release can pass.
The verifier checks each request against the authenticated Actions job labels.

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
and file mode preserved. It admits the evidence anchor shown above and the
post-supervisor anchor at `4ae28dba1493c2171bd8097e58195198c4001a51`, plus
their reviewed tooling delivery shapes, including the portable launcher. Other committed changes require fresh
qualification. Use separate
checkouts if the inspected checkout contains edits to the tooling. Git-ignored
files are outside the effective snapshot.

A positive JSON report exits 0 with `mode: pinned-mapped-obligations`, the observed
snapshot, the admission evidence, and the pinned test IDs. The original anchor
assigns 30 tests. The post-supervisor inventory assigns 38 on Linux and 36 on
Darwin, and reports the platform and any excluded Linux-only IDs. The candidate
inventory and impact completeness are both `unqualified`. The command reads
captured data without importing candidate Python or running tests.

An unavailable report exits 2 with a machine-readable `reason` and an empty
`node_ids` array. This includes invalid arguments, an unsupported or clean
worktree, and an observation that changed during the report. Bind any subsequent
action to the reported snapshot and revalidate it before use.

## Run pinned obligations before committing

On Linux or macOS with `uv`, CPython 3.13.9, and Git supporting
`--no-lazy-fetch` on PATH, run this command from the trusted tooling checkout. Use the exact HEAD of the inspected checkout.

```sh
python -B -E -s -m tools.ci.tia.working_tree_run \
  --repo /path/to/inspected/checkout \
  --base "$(git -C /path/to/inspected/checkout rev-parse HEAD)"
```

The command uses the report above as its assignment. It runs only those node
IDs in a separate pytest process on a private copy of the effective snapshot.
It rechecks the report before and after execution. JSON on stdout includes the
assignment, an invocation ID, the OS process return code and the matched
pytest receipt. Exit 0 means all assigned tests passed with complete phase
evidence. Exit 1 means the worker exited 1 with a complete matching failure
receipt. Exit 2 means unavailable, including an unsupported change, drift,
or incomplete or inconsistent evidence.

The result is labeled `local_advisory`. Test phase evidence comes from a pytest
plugin inside the same-account worker. Use this manual command for cooperative
local feedback. The original report's candidate inventory and impact
completeness fields remain unqualified.

## Probe affected tests for exact Git inputs

Run the advisory probe from the tooling checkout with CPython 3.13.9, uv,
and Git supporting `--no-lazy-fetch`. The inspected checkout is explicit.

```sh
python -B -E -s -m tools.ci.tia.probe \
  --repo /path/to/checkout --parent "$parent_commit" --input index
```

Use the full commit ID of the chosen branch parent in a checkout with full
Git history. The probe resolves one merge base of that commit and HEAD.
`index` reads staged blob contents and modes, even if the same file has an unstaged edit. Use `head` to read the
committed HEAD tree independently of staged, unstaged, and untracked changes.

For `--input pr`, pass the literal PR base as `--parent`, plus the full
`--pr-head`, `--tested-commit`, and `--tested-tree`. The tested commit
must have exactly the base and head as its ordered parents. The probe records
the PR divergence point separately and compares the literal base to the
tested merge tree. This checks Git object identity. Hosted authentication is
a separate check.

The JSON plan binds the input, observed inventories, selected pytest IDs,
witnesses, and uncertainty. Run it on cooperative checkouts. It collects
pytest inventory in private copies and leaves the inspected Git inputs alone.
A full decision lists the full applicable candidate inventory. Missing or
changed inputs or an unavailable candidate inventory return exit 2 with no
assignment. An emitted plan returns exit 0. The production PR gate continues
to use the hosted path map.

## Local category sweep

Run the opt-in full sweep from a clean AITM checkout with Python 3.13, uv,
Git, and the native tools used by the suite. The checkout needs complete
Git history, including the historical planning fixture
`17761cc1928fd916cf32a9c078d4a742bfcb32b8`. Use a new output directory outside
the checkout.

```sh
python3.13 -m tools.ci.category_sweep run --output /tmp/aitm-sweep
```

The command collects five profiles, reconciles the exact IDs to the reviewed
Darwin or Linux catalog, and runs the nonempty categories concurrently. The
catalog includes the known platform differences and leaves an empty category
visible in the plan. A changed inventory requires a reviewed catalog update
before the full sweep can pass.

Each category gets a standalone checkout, locked environment, private temporary
state and separate output. Linux keeps the workspace, custody fixtures and
managed Python under a private directory in `/var/tmp`. The coordinator checks
every phase and both required child results before writing `result.json`. If a
run fails, inspect its category and profile logs. Rerun into a new directory. Add
`--serial` for the unsharded reference on the same committed source.

The ordinary affected-test command and the hosted PR path-map check remain the
usual entry points for validating a change.

## Hosted category sweep

**Category full sweep** runs daily at 23:23 UTC on `trunk`. You can also dispatch
it manually on `trunk`. The two triggers share one concurrency group. An
active run finishes, and GitHub can replace the one pending run with a newer
request. To disable the daily trigger, remove the `schedule` block through a
PR and keep `workflow_dispatch`.

The workflow publishes one separate job per nonempty category and host
assignment, then verifies the exact union. Ubuntu owns shared IDs and
Linux-only IDs. Darwin owns the opt-in native cases and Darwin-only IDs. Each
job collects its full host inventory to detect drift before running its
assigned profile slices. Workers retain the same pinned historical planning
fixture used by the local sweep.

The reconcile job requires every planned receipt for its source and workflow
attempt. A passing run uploads `category-verdict.json`, including the empty
categories and per-job timings. A failed or incomplete worker prevents a passing
verdict. Re-run all jobs for a fresh attempt.

Use Actions job timestamps for queue delays and workflow bootstrap. Each shard
receipt separates collection and environment setup from test execution and
receipt sealing. Failed test output is available in the shard's Actions log.

Check the scheduled event history against the expected UTC slot.

```sh
gh run list --workflow category-full-sweep.yml --event schedule --branch trunk \
  --json databaseId,createdAt,startedAt,headSha,status,conclusion,url
```

GitHub may register a scheduled event after the expected slot. Compare the
slot with the run's registration and start timestamps. Record an absent slot
when there is no corresponding scheduled run and note any later arrival. For a
registered run, use its run ID and attempt to find the expected worker
artifacts and `category-verdict-a<attempt>`. A failed, cancelled or incomplete
attempt has no passing verdict. A manual run has its own event and receipts.
