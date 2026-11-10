<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-2001d40a8de8ac60b2d33b424e958263"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/001/103/design/github-ci-quality-gates-design.md"
artifact_commit: "4e7d5708bb5628d7a6767d295fbf4eeacc72670b"
artifact_blob: "dd63e65951195b3f57c001186e2aca44bf1595f2"
artifact_digest: "sha256:2506b3bb129e98ca936677c825513fee65f838a65e1c7625087ec091fba5a02e"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:3bae1567c47b4a0eb7bcaa003c3fee94a2ce29d930504d00aa989d4aa5887226"
  identity_source: "runtime"
started_at: "2026-11-10T02:45:49.379Z"
submitted_at: "2026-11-10T02:48:35.337Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Read coverage: I read `.aitm/stories/001/103/design/github-ci-quality-gates-design.md` in fresh contiguous Read ranges of at most 20 lines: lines 1–20, 21–40 and 41–49. The third read asked for 41–60 and returned only through line 49, which is EOF. No range was marked truncated, and the read is complete through EOF. For context only, I also read the invitation, the author startup note and `.aitm/stories/001/103/story.md` lines 1–32. I did not edit the artifact or run Git.

The design is well grounded. It has a single fail-closed aggregate (`aitm-ci`) and it checks merge parents for PR test merges. It requires a fresh event after base drift and a whole-workflow rerun. It runs the required suite on hosted macOS and keeps Linux to portable checks. It sets a 90% gate per package, counts unimported modules and blocks on unexpected skips. It also adds shard-completeness checks before parallelization and keeps the PBI standalone. However, several gate-integrity and evidence-binding properties depend on mechanisms the design leaves unspecified, or that a PR under test can change. The most important gaps:

- the PR controls its own gate definition;
- no component is named to verify the evidence binding, and there is no rule for choosing among several runs;
- the `edited` trigger interacts badly with cancelling superseded runs;
- target coverage on integration branches is unspecified;
- the test inventory baseline is ambiguous;
- coverage.py rounding at the threshold;
- the wheel smoke does not install locked dependencies;
- the checked file sets overlap with fixtures and existing code.

Each needs a design-level decision before development is authorized.

## Findings

1. **The PR under test controls its own gate (gate integrity, lines 15–17, 29–41).** A `pull_request` run uses the workflow and config from the test merge commit. A PR can therefore weaken any of these and still get a green `aitm-ci`: `.github/workflows/ci.yml`, the coverage threshold and `source`/omit settings, the exclusion justifications, the list of known required packages, the named required test cases or inventory baseline, and the markdownlint/yamllint rule sets. A PR can also add a second workflow file with a job named `aitm-ci`. Ruleset check-source binding can name the GitHub Actions app but not a specific workflow file, so the stable name alone can be spoofed. Line 17 binds evidence to the "canonical workflow path or ID". That stops a different workflow file from passing, but it does not stop the canonical file from being edited in the same PR. The design needs a stated control so that a weakened gate cannot pass silently. For example, a guard step could compare gate-defining files and thresholds with the base ref. Any loosening, or any change to those files, would then need an explicit, recorded owner disposition in the story checklist. The evidence record would also capture the blob IDs of the workflow and gate configuration that ran.

2. **No component is named to verify the evidence binding, and there is no rule for choosing among runs (exact candidate binding, lines 17–19; acceptance 2).** The design lists the fields a passing result must bind: repository, workflow, PR, event, target, run and attempt, head/base, tested commit and per-job results. It does not say what verifies them, where that check lives, when it runs or how it is tested. A script in the repo would be product code under the 90% gate. A manual checklist procedure would not be testable for acceptance 2's refusal cases. The design also says "duplicate … aggregate evidence never qualifies". A head/base pair can legitimately have several runs: `edited` events, reruns, or both `synchronize` and `edited`. A literal reading would then block valid PRs. Define the selection rule, for example: "the most recent completed attempt of the canonical workflow whose event head and base equal the live head and base; earlier or concurrent runs are ignored, not disqualifying." Also define how the verifier proves a whole-workflow rerun. Every job in the selected attempt must belong to that attempt, so a "re-run failed jobs" attempt that reuses earlier job results is rejected. Name the verifier's inputs (`gh api` run, jobs and PR endpoints), its outputs (the "named CI evidence" in acceptance 1) and its test strategy.

3. **The `edited` trigger combined with superseded-run cancellation (lines 19, 21).** `pull_request: edited` fires on title and description edits as well as base changes. If the concurrency group is per PR with cancel-in-progress, a description edit cancels the in-flight macOS suite and restarts it. That delays evidence and doubles macOS minutes. If the design instead skips non-base `edited` runs, the skipped run produces a non-passing `aitm-ci` on the same head SHA. That could become the latest check and block the PR, or confuse the verifier. The design should state the concurrency key, for example PR number plus base ref plus head SHA, or a rule that non-retarget edits do not cancel. It should also say what a non-retarget `edited` run does: full validation, or no aggregate result at all. And it should say how finding 2's selection rule treats it.

4. **Integration targets and bootstrap (CI bootstrap, lines 15, 23).** (a) The design does not say how "declared epic integration targets" are matched. An `on.pull_request.branches` pattern that misses a newly declared target silently produces no check. If a filter is used, the design should run on all PRs or fail closed. A declared target without an `aitm-ci` result should leave the gate open, never make the check not applicable. (b) Integration branches cut before the bootstrap merges will not contain `ci.yml`. PRs into them then run no workflow. Before such a branch counts as gated, the design should name a step that brings it up to date with trunk's workflow. (c) Line 23 says "the first workflow cannot already show a passing check before it exists". For a same-repository branch, a PR that adds a `pull_request` workflow does run it on itself, so the bootstrap PR can produce its own real result, as the next sentence requires. Reword this so the actual bootstrap gap is clear: the Before Develop CI-route preflight and the trunk push and integration-target proofs, which happen only after merge.

5. **Test inventory baseline (keeping the full inventory during parallelization, lines 40–41; acceptance 2).** "Compare collected and executed IDs with a complete baseline" does not say where the baseline comes from. If it is collected from the candidate in the same run, it catches lost shards but not a PR that deletes, deselects (`-k`, `-m`, `--deselect`, `collect_ignore`) or newly skips/xfails required tests. If it is a committed file, the PR can edit it (finding 1). Specify both: (a) in-run completeness, where collected IDs on the candidate equal executed IDs across all shards with none missing or duplicated; and (b) a diff of the candidate inventory against the base-ref inventory. Removed, newly skipped, newly xfail and deselected IDs then show up for review, and removing a named required case blocks the gate without a recorded disposition. This applies to the initial serial stage as well as later sharding. Acceptance 2 shows refusal for a missing Darwin capability and for missing, skipped or cancelled jobs. It does not show refusal when a required test case is unexpectedly skipped or missing, though line 40 makes that a blocker. Add it.

6. **Coverage threshold arithmetic and scope (90% per product package, lines 38–39, 47).** Line 39 rightly requires checking covered and executable counts before display rounding. However, coverage.py's `fail_under` (which `--cov-fail-under` uses) compares `round(total, precision) < fail_under`, and `precision` defaults to 0. So 89.5% passes a 90 floor. The design should require either computing the gate from raw counts or a `precision` setting that cannot round up past the floor, and a refusal demonstration at 89.5%. Also: (a) say where each package's threshold and source roots are declared (ties to finding 1); (b) "subprocess coverage … when available" is not testable as written. Name the subprocess and CLI paths expected to produce coverage data. Missing data from an expected path should fail, not quietly count as uncovered or drop out of scope.

7. **The wheel smoke does not install locked dependencies (line 29; acceptance 1, 3).** Installing the built wheel in a clean environment resolves its runtime dependencies from the index at smoke time unless something constrains them. The smoke result can then change without any change to the candidate, and could pass with versions other than those in `uv.lock`. Specify locked dependencies for the smoke install, for example constraints exported from `uv.lock` or `--no-deps` into a locked dependency environment. Verify the installed wheel's digest against the built artifact. If build and smoke run in separate jobs, verify the digest of the downloaded artifact too.

8. **Protecting existing work, and the checked file sets (standalone scope, lines 29–34).** (a) The JSON row says "Parse tracked JSON strictly". The repository may hold deliberately malformed or duplicate-key JSON test fixtures, and tests of the parsers would need them. The exclusion rule for fixtures should be in the design itself, not left to "define the checked file sets", and it should be reviewed like other gate config. (b) The design gives Markdown a baseline policy but none for Ruff lint or format on existing Python. If `ruff format --check` or a new rule set fails on current trunk, a fix-everything bootstrap would touch unrelated files and conflict with concurrent story branches. Measure the Ruff, markdownlint, yamllint and JSON baseline on trunk first. Treat any repo-wide fix as a separately scoped, reviewed change or a named baseline, never as incidental churn in the CI PR.

## Required changes

1. Add a gate-integrity control for gate-defining files: workflow, thresholds, coverage scope and exclusions, required package and test lists, and lint rule sets. Changes to them must be detected against the base ref and need a recorded owner disposition. Record the blob IDs of the workflow and gate configuration in the evidence (finding 1).
2. Name the evidence verifier: what it is, where it runs, its inputs and outputs, and how it is tested and covered. Define the run-selection rule, replace "duplicate never qualifies" with that rule, and define how a whole-workflow attempt is detected (finding 2).
3. State the concurrency key and how non-retarget `edited` events behave, so description edits neither cancel valid runs nor leave a non-passing latest `aitm-ci` (finding 3).
4. State how declared integration targets are matched, fail closed when a declared target has no `aitm-ci` result, add a step bringing pre-existing integration branches up to date with the workflow, and reword the line 23 bootstrap sentence (finding 4).
5. Define the inventory baseline as both in-run completeness and a diff against the base-ref inventory. Add a refusal demonstration for a missing or unexpectedly skipped required test case (finding 5).
6. Require the coverage gate to be computed from raw counts, or with a precision that cannot round up past the floor, and add a refusal demonstration at 89.5%. Say where per-package thresholds and source roots live. Replace "when available" with a named set of expected subprocess coverage sources (finding 6).
7. Install locked dependencies for the wheel smoke and verify the digest of the wheel actually installed (finding 7).
8. Put the fixture exclusion rule for strict JSON in the design, and add a baseline-first policy for Ruff and other linters on existing code that bars incidental repo-wide churn (finding 8).

## Optional suggestions

1. Propose the split now instead of at refinement. Workflow, aggregate and Python lane; the evidence verifier; Markdown/JSON/YAML linting; and any coverage-to-90% remediation each look close to a leaf in their own right. Together they very likely exceed the four-agent-hour limit in acceptance 4.
2. Explicitly forbid `pull_request_target` and secrets in PR jobs, and state how fork PRs are handled, so the read-only stance on line 21 cannot be eroded.
3. `actions/checkout` defaults to a shallow depth-1 checkout, where the merge commit shows no parents through `git log`/`rev-list`. Specify `fetch-depth: 2`, or read the raw commit object, for the merge-parent check on line 19.
4. Record the pinned macOS runner label together with the runner image version and Xcode/CLT version for each run. If the repository is private, give a budget for macOS minutes, which are billed at a multiple of Linux minutes, since the full suite runs serially on macOS.
5. When enforcement is enabled (line 23), consider strict "require branches up to date" or a merge queue, so the base-drift rule on line 19 is enforced mechanically and not only by procedure.
6. Back the behavioral-test intent (lines 39, 47) with a review checklist item for coverage-raising tests: each asserts an observable outcome, with no assertion-free execution. Optionally sample mutation testing on core modules later, as a non-gating signal.
7. Track branch coverage as a trend in the evidence record even though it does not gate, so a future decision to gate it has a baseline.

## Decision

revisions-requested
