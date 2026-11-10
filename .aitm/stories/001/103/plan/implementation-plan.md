# GitHub CI and repository quality gates Implementation Plan

> For agentic workers, use the subagent-driven-development or executing-plans skill for each authorized leaf. This is a draft for plan review. Admission, JIT and implementation authorization are separate.

**Goal** Give a source story a trustworthy, timely GitHub Actions result for its exact candidate.

**Architecture** One ordinary PR workflow builds the Python package on macOS, with portable checks on Linux. The closure owner verifies canonical run evidence against live GitHub identities and trusted target policy. Three sequential leaves have separate delivery targets and close as soon as their own last gate passes.

**Tech stack** GitHub Actions, Python 3.13, uv, pytest and pytest-cov, coverage.py, Ruff, actionlint, markdownlint-cli2 and yamllint. TypeScript has a documented future ESLint, `tsc` and Vitest contract.

**Spec** [Accepted design](../design/github-ci-quality-gates-design.md) at SHA-256 `d48fc2bd0b1973c48a39b4b197a9ab7e97d77db7bdd34980e58022037d4c1ed0`, published at `a1a49bf101ae702e28118f0294c8c4c7d8546bed`. [Baseline observation](../attachments/local-coverage-baseline.md) · [Manual delivery checklist](../../../../manual-delivery-checklist.md).

## Global constraints

- Preserve the exact 90% line floor for each active product package and executable CI policy helpers. Compare raw counts, include unimported production code, and verify meaningful behavior, failure, recovery and invariants. A 100% result is welcome where these tests naturally reach it.
- Run the full applicable suite serially on the qualified Darwin runner. CI keeps missing required jobs, skipped required tests and missing expected subprocess coverage visible as failures. Report separately any approved optional platform capability skips. Record the full inventory and cold/warm timings before considering sharding.
- Ordinary `pull_request` with read-only hosted execution and no repository secrets, privileged execution or production state. Full action SHAs and locked runtime and tooling dependencies. Initial runner candidates are `macos-26` arm64 and `ubuntu-24.04`. Confirm availability and required Darwin capabilities before pickup. Record runner image/version and Xcode or command-line tooling version. [GitHub-hosted runner reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
- Use the observed CPython 3.13.9, uv 0.10.6, pytest-cov 7.1.0 and coverage.py 7.17.2 as initial pins, subject to a reproducible lock and supported runner. The initial planning allowance is up to 10 hosted runner-minutes per full macOS attempt, based on 1m 33s local suite time plus environment, wheel and evidence setup. Measure the actual run, including reruns after target movement. This is a forecast, not an observed cost.
- Pin protected trunk `f80f22645e2008c4cac9dc6e4003640bba976b5f` for refinement and recheck it at each pickup. Use only the named source story and its declared target. Plan review and exact JIT precede Develop. Epic #2, C01, release publishing and actual deployment stay outside this work.

## Refined delivery map

| Leaf | Estimate | Depends on | Own closure proof |
| --- | ---: | --- | --- |
| [CI1 · Bootstrap Actions and Python validation](../../104/story.md) | 4.0 h | None | Exact green bootstrap PR, verified merge and trunk check, representative integration-target proof, author sign-off |
| [CI2 · Verify canonical PR evidence](../../105/story.md) | 3.5 h | CI1 | Reviewed verifier source, 90% helper coverage, exact green PR and delivered verifier from trusted target |
| [CI3 · Lint repository files and define the TypeScript lane](../../106/story.md) | 2.5 h | CI2 | Reviewed lint policy, safe failure proofs, exact green PR, delivered checks and documented TypeScript contract |

Total **10.0 implementation agent-hours**, including source verification and review. This is a forecast, separate from CI queue time and observed local test elapsed time. Refine each leaf further if its four-hour cap becomes implausible. The 90.9551% local collector baseline clears the product floor, so there is no planned coverage remediation leaf. If hosted measurement shows a genuine behavior gap, stop and scope it under the design's conditional prerequisite before delivering a required gate.

## Review focus

- A malformed or missing gate policy or unknown required package fails closed even on a workflow that would otherwise pass. CI1.
- A real GitHub run with stale target or insufficient authenticated run-to-commit identity remains blocked. CI1 proves the live route manually, CI2 refuses it from fixtures and a controlled live readback.
- A normal CLI or service subprocess exits successfully without recorded coverage. CI1 fails on the missing measurement. A deliberate kill retains behavioral recovery evidence while unflushed lines remain uncovered.
- A passing aggregate assembled from different attempts or a lookalike workflow must fail even when GitHub's summary shows a green check. CI2.
- A deliberately malformed fixture or newly present TypeScript project may change what is applicable. CI3 keeps exceptions exact and visibly reports absent TypeScript.

## CI1 · Bootstrap Actions and Python validation

**Owns** `.github/workflows/ci.yml`, `packages/aitm-usage/pyproject.toml`, `packages/aitm-usage/uv.lock`, `tools/ci/policy.json`, `tools/ci/python_gate.py`, `tools/ci/tests/test_python_gate.py`, and `docs/ci.md`.

- [ ] Confirm the documented first-workflow route. Record any separately authorized Before Develop preflight exception for the missing existing workflow. Fix the intended source target, exact base and runner capabilities in the delivery checklist. A real passing Actions run is required for the bootstrap PR.
- [ ] Pin a small policy describing the required collector source root, tests and expected normal child subprocess data. Use the existing APFS, ACL, exclusive publication, lease and crash/restart tests to enumerate required behaviors and narrowly document permitted capability skips. Record the exact current trusted base inventory and outcomes.
- [ ] Add behavioral runner tests before the helper. Check that 179 covered of 200 fails, 9 of 10 passes, missing or malformed policy fails, and zero tests, unknown required package, missing/duplicate test IDs, unexpected skips, stale reports and missing normal subprocess data fail. A deliberate hard kill remains a real test outcome. Show the failing helper tests before implementing their policy.
- [ ] Keep the helper interface small. `python tools/ci/python_gate.py --policy <file> --inventory <file> --junit <file> --coverage <file> --base-evidence <file>` reports a sanitized disposition with exact raw counts and failures and exits zero only for an eligible result. Keep the supported outcome and count semantics in tested functions.
- [ ] Install locked test tools with uv. Run the complete collector suite with subprocess measurement, collection inventory, JUnit, coverage JSON and slow durations. Apply the raw coverage floor to the collector and the executable policy helper separately. Compare candidate outcomes with trusted exact base evidence. Keep required host-sensitive tests serial.
- [ ] Build one candidate wheel with pinned build tooling. Prepare a clean environment with locked runtime dependencies, excluding the editable project. Hash the wheel, verify it immediately before installation, install it with `--no-deps`, then check the command and import resolve inside the clean environment.
- [ ] Wire the `pull_request` activities, trunk push, unprivileged checkout, dependency caches and per-PR cancellation. Verify the two ordered parents of the raw tested commit. The stable `aitm-ci` job depends on every applicable lane and inspects every required job result. Run Ruff and pinned actionlint and document the local checks. Use the same head/base and gate-policy facts in the sanitized run summary.
- [ ] On an authorized same-repo bootstrap PR, observe authentic GitHub run and job provenance. Use controlled negative proof for the required failure routes, then reverify the exact clean current candidate. If GitHub cannot bind the run to the tested merge independently of candidate output, stop the gate and return to planning. Verify the approved merge, the trunk push run and an ordinary PR into a representative CI-enabled integration branch. Demonstrate a fresh candidate after base or target movement. Apply the manual verification procedure for this leaf and close on its own delivery and sign-off.

## CI2 · Verify canonical PR evidence

**Owns** `tools/ci/verify_pr.py`, `tools/ci/tests/test_verify_pr.py` and its sanitized API fixture directory, plus scoped workflow, policy and `docs/ci.md` extensions for the verifier.

- [ ] Write fixtures from the actual CI1 API shape. Assert one canonical complete successful attempt passes. Exercise absent fork linkage, wrong workflow or target, branch ref advanced without a new event, reversed or invalid merge parents, neutral or cancelled jobs, duplicates within the chosen attempt, partial reruns, and an undisposed gate-defining blob change. Check that an older matching run cannot mask a newer failed or pending run.
- [ ] Implement the read-only `python tools/ci/verify_pr.py --repo <owner/repo> --pr <number> --target <branch> --output <file>` command from the trusted target. Read the pull request, live target ref, canonical workflow, runs, check suite, commit objects and attempt-specific jobs using authenticated `gh api`. Require sufficient GitHub evidence for all identities and compare candidate-reported identities with it. Retain dated evidence and a bounded blocker on refusal. Enforce the reviewed gate-control diff and recorded owner disposition.
- [ ] Run independent exact review and all applicable CI on this leaf, with the 90% helper floor. Verify delivery manually while the verifier is still new, then run the delivered trusted copy on a read-only case and close CI2 with its own author sign-off. Reuse that verified copy for subsequent PRs. [GitHub workflow job attempt endpoints](https://docs.github.com/en/rest/actions/workflow-jobs)

## CI3 · Lint repository files and define the TypeScript lane

**Owns** `tools/ci/file_checks.py`, `tools/ci/tests/test_file_checks.py`, the pinned tool manifests/locks and lint configurations under `tools/ci/file-lint/`, and scoped workflow, policy and `docs/ci.md` extensions.

- [ ] Record an exact base lint baseline for tracked maintained Markdown, JSON and YAML. Make fixture, vendor, generated and immutable-history exceptions exact and reviewable. Preserve existing history. Check malformed JSON, duplicate keys, bad YAML, Actions semantic errors and lint violations with small focused fixtures before adding the checks.
- [ ] Run markdownlint-cli2 from a locked Node tool environment, yamllint from a pinned tool environment, strict JSON parsing and declared schemas, and the existing pinned actionlint. Wire the applicable file lane into `aitm-ci` without a workflow-wide filter. Verify that future product TypeScript detection cannot silently omit a real package with missing lint, typecheck or test configuration. Report the current TypeScript lane as not applicable. Document ESLint/typescript-eslint, `tsc --noEmit`, Vitest and the 90% V8 coverage floor at activation of the first product package.
- [ ] Use the trusted CI2 verifier and the manual checklist on the exact CI3 PR. Verify refusal cases, required gate success, reviewed remote delivery, retrospective and immediate story closure.

## Parent acceptance

On the exact CI3 PR candidate, compare the trusted verifier with the manual GitHub readback before merge and retain their agreement. Verify the three child closures and their evidence, then record the parent's retrospective and own terminal disposition. An Actions result and an independent agent's review remain separate. Ruleset enforcement, additional test sharding, and any CI validation for direct planning publication require their own authorized work.
