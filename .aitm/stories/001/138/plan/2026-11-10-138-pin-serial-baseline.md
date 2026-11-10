# #138 Pin the serial baseline Implementation Plan

> **For agentic workers** Use Superpowers subagent-driven development or
> executing-plans after separate implementation authorization. Checkboxes
> describe the work for that authorized attempt.

**Goal** Produce a reproducible serial CI comparison for #133 from the
exact #103 PR and delivered trunk evidence pinned by T01.

**Architecture** The closure owner prepares and verifies the historical
proof inputs using protected #103 controls. A pure projection checks the
joins between those inputs and emits one canonical baseline that keeps
the PR candidate, its trusted base, and the trunk push distinguishable.

**Tech stack** Python 3.13.9, uv 0.10.6, locked pytest and coverage.py,
standard-library JSON and SHA-256, and GitHub Actions evidence from #103.

**Spec** [Accepted #138 design](../design/pin-serial-baseline-design.md),
SHA-256 `d080652606e1e177c4c79c5a9c17a98cdaf5ef8d38ce641f4b55ff89ac0efa0b`.
[Accepted #133 T01](../../133/plan/test-impact-analysis-implementation-plan.md#t01-pin-the-serial-baseline--25h-p1-no-predecessor)
at `dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84`.
[Attempt 1 pickup inputs](2026-11-10-138-jit.md).

## Global constraints

- Preserve #103 as the current PR gate. Its unrounded 90% product and
  helper floors, base outcome comparison, exact installed-wheel smoke,
  normal child exits and file checks still govern delivery.
- Project only closure-owner-verified inputs. Keep the projection offline
  and credential-free. The comparison and advisory collection carry
  no future FullProof, observer, scheduled health, merge or Stop the Line
  authority.
- Use an isolated source checkout and implicit `tia` namespace. Use only
  the owned files below. #140 has a distinct module and test. Shared
  workflow, policy, verifier, package configuration and namespace
  initializer are outside scope.
- Keep raw receipts in authenticated or private custody. The planning
  report exposes safe links, hashes, counts, timings and verification
  limits. Work here stays at Planning until the owner separately
  authorizes implementation.

## Review focus

- A plausible base, artifact shard or timing row from a different
  attempt, even with the same tree or job name, must be refused.
- A push can legitimately skip the two PR-only jobs. A failed,
  unexpectedly skipped, cancelled or missing required job holds the
  corresponding historical role.
- Validate paths before treating them as inventory or archive entries.
  A dot segment, absolute path, backslash alias or traversal is a
  refusal. Keep legitimate pytest parameter text opaque.
- A missing helper collection blocks the comparison. A collected
  helper node is advisory inventory with no hosted per-node outcome.
- Unknown cold timings retain their role and reason. They cannot
  fill missing proof or inherit a PR-base cache result.

## Files and interfaces

| Owned path | Responsibility |
| --- | --- |
| `tools/ci/tia/baseline.py` | Canonical offline baseline projection |
| `tools/ci/tests/test_tia_baseline.py` | Focused red/green tests and generated test inputs |
| `.aitm/stories/001/138/attachments/serial-baseline.md` | Sanitized verified comparison on `planning` |

The module exports `build_baseline(verified_ci103: bytes, timings: bytes) -> Baseline`,
with `Baseline` a bytes type alias for the canonical JSON output. Raise
`ValueError` with a stable reason category on malformed, incomplete or
misbound input. The closure owner supplies both envelopes from the
protected verification and custody route. This function neither
performs nor asserts independent authentication of the caller.

The envelope and output contracts below define the field names used in
focused tests and by downstream consumers. Use UTF-8 JSON with sorted
object keys, compact separators, no ASCII escaping or non-finite numbers,
and no trailing newline. Enforce unique keys at every depth before
mapping, including when decoding retained raw JSON. Hash the original
receipt bytes, independent of the envelope serializer.

| Input or output | Field contract |
| --- | --- |
| `aitm.tia-ci103-input/v1` | `schema`, `roles` keyed by `pr_candidate`, `pr_base`, `trunk_push`, and `helper_collection` |
| Role | `binding`, `jobs`, `archives`, `verification`, `raw`, `outcomes`. `binding` holds repository ID, event/ref, commit/tree, applicable PR/base/head, workflow ID/path, run/attempt and check suite, control and lock identities, and platform/toolchain. Job and archive records identify their owning run/attempt and names/IDs. Archive records bind original SHA-256 and allowed member paths. `raw` holds the original JSON receipts as UTF-8 text keyed by their approved member names within the role's archives. `outcomes` is the node-to-classification map from the trusted #103 observer/classifier. |
| `helper_collection` | Advisory kind `local_advisory`, exact shared tree, pinned lock, observer, collection command, local runner/runtime, four targets, zero deselections, sorted unique IDs and compact-array SHA-256 |
| `aitm.tia-baseline-timings/v1` | `schema`, `observations` keyed by the candidate/push role then `cold` and `warm`. Each slot includes the evidence role and exact binding, lane, boundaries, seconds and evidence reference per measured metric, plus cache profile, actual hit/miss and provenance when observed. Unavailable slots or metrics carry `status: "unknown"`, role, scope and reason. |
| `aitm.tia-baseline/v1` | `schema`, `roles` (verified bindings, exact source/test inventories and digests, classified product outcomes, scope-specific coverage, child, wheel and file proof), `helper_collection` (advisory), `timings` (separately bound observations) |

The `pr_base` role shares the PR attempt and base-lane custody with
`pr_candidate`, but records its own checkout and observer/policy,
configuration and lock identities. It carries product test outcomes only.
Any repeated reference to that archive across the two role records must
be identical. Historical job IDs, signed subject and archive identities
come from the pickup note. The implementation compares trusted receipt
bindings to the supplied inputs. The closure owner verifies that the
actual delivery report uses the frozen historical pair.

## Task 1 · Build and verify the historical comparison

### 1. Start with the attempt-binding regression

- [ ] In `tools/ci/tests/test_tia_baseline.py` write
  `test_baseline_rejects_mixed_attempts` against the public function
  imported as `from tia.baseline import build_baseline`. Start from
  one complete synthetic pair using the #103 receipt shapes below.
  Parameterize one change at a time to the required base archive,
  Python archive/member custody or timing slot. Each carries the
  same tree but an owning attempt of 2 against attempt 1. Assert
  `with pytest.raises(ValueError, match="attempt")` around the call.
- [ ] In the owned `tools/ci/tia/baseline.py` module add a minimal,
  importable `build_baseline` scaffold with the declared signature.
  Return canonical baseline-schema bytes without attempt validation
  so the unchanged public call reaches the missing-refusal assertion.
  Implement the real projection in this same function after red.
- [ ] Run the named case from the physical source root. Retain its
  nonzero exit and `DID NOT RAISE` behavior failure at the public
  call. Use the same test, parameterized fixture and public call in
  green. The fixture is offline.

  ```sh
  cd "$(pwd -P)"
  PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --locked \
    python -m pytest -q tools/ci/tests/test_tia_baseline.py \
    -k test_baseline_rejects_mixed_attempts
  ```

### 2. Project complete, bound proof

- [ ] Extend the same complete synthetic proof fixture with the tests
  below. Give each role a separate identity. Verify behavior through
  the public function.

  | Test | Required assertion |
  | --- | --- |
  | `test_baseline_projects_exact_pair` | Output is byte-identical on repeat; canonical schema is `aitm.tia-baseline/v1`; the same tree yields distinct PR and trunk role records; trusted base has its own outcomes; explicit push skips are accepted; helper IDs stay advisory; coverage, child, wheel, file and role-specific timings survive with their scope. |
  | `test_baseline_rejects_incomplete_or_conflicting_proof` | `ValueError` for a missing required archive/receipt, changed repository/ref/commit/base/head/tree/control/lock/runner, unsupported receipt schema, conflicting IDs/digests, absent or non-passing required job, expired evidence without independently verifiable retained custody, and a signed-subject digest that differs from raw PR inventory/base evidence. |
  | `test_baseline_rejects_noncanonical_or_unsafe_input` | `ValueError` for nested duplicate JSON keys, an unsupported envelope schema, non-finite JSON, or an absolute, aliased or escaping path in source inventory, archive members, coverage or the source portion of a node ID. A slash in a legitimate pytest parameter remains opaque. |
  | `test_baseline_rejects_unqualified_helper_collection` | `ValueError` for absent collection, wrong tree/lock/observer/target set, duplicate IDs, deselections or a collection digest mismatch. Presence of local IDs leaves hosted helper node outcomes absent. |
  | `test_baseline_distinguishes_unknown_and_observed_timing` | A bound cold slot with role/scope/reason serializes as Unknown and a separately proven warm hit retains seconds, cache and provenance. A mismatched profile/key or wrong attempt fails. A missing required proof still fails when a valid Unknown slot is supplied. |

- [ ] Implement `build_baseline` in the owned module. Decode the two
  canonical envelopes and support only the raw #103 receipt shapes
  enumerated in the [pickup inputs](2026-11-10-138-jit.md#historical-comparison).
  Reject unsafe paths without silently rewriting them. For pytest node
  IDs apply that check only to the source prefix before the first
  `::`. Match same-attempt job/check and archive references to
  verification evidence. Refuse conflicting or duplicate IDs, member
  paths or digest claims. The same content digest may legitimately
  recur across distinct roles, for example the wheel or common tree's
  source inventory. Bind the PR candidate's raw inventory, source
  inventory and trusted base bytes to the signed subject, including
  the base identity and policy digest. Require both proof roles and
  their independent dispositions before projecting.
- [ ] Retain the trusted classified product outcomes and their exact
  node sets, including the candidate-only CLI evidence test. Check that
  raw collection and outcome map domains agree and that the counts
  agree with the #103 results. Preserve source inventories and digests,
  approved helper source scope and local collection provenance.
  Carry product and helper coverage receipts by raw digest, line
  counts and available branch evidence with scope. Use the protected
  replay's unrounded line-floor dispositions. Validate required normal
  child, installed-wheel smoke and authenticated file-check proof
  for both tested roles. Leave the PR-base lane product-only.
- [ ] Join timing slots to their exact role, run, attempt, controls,
  lock and platform. Bind the actual cache observation to the same
  Python job. Keep queue, setup, serial test bucket, Python lane wall
  time and runner seconds, collector wait and duration, feedback and
  total non-skipped hosted job seconds distinct. Retain each available
  measured boundary and mark the finer timing/billing fields Unknown
  where unobserved. Cold and warm are separate per role.
- [ ] At two active implementation agent-hours, require the positive
  complete synthetic pair and the unchanged mixed-attempt regression
  to pass on the public function. Reassess if the remaining focused
  proof and report cannot fit the four-hour cap.
- [ ] Run all focused tests from the physical checkout, followed by
  Ruff for both owned files using the locked package config. Retain
  tree/head, runtime, collected node IDs and the first red and final
  green results.

  ```sh
  cd "$(pwd -P)"
  export PYTHONPATH="$PWD/tools/ci"
  uv run --project packages/aitm-usage --locked python -m pytest -q \
    tools/ci/tests/test_tia_baseline.py
  uv run --project packages/aitm-usage --locked python -m pytest --collect-only -q \
    tools/ci/tests/test_tia_baseline.py
  uv run --project packages/aitm-usage --locked ruff check \
    --config packages/aitm-usage/pyproject.toml \
    tools/ci/tia/baseline.py tools/ci/tests/test_tia_baseline.py
  uv run --project packages/aitm-usage --locked ruff format --check \
    --config packages/aitm-usage/pyproject.toml \
    tools/ci/tia/baseline.py tools/ci/tests/test_tia_baseline.py
  git diff --check
  ```

### 3. Reconcile the real proof and record delivery

- [ ] Reopen the historical source by Git object and authenticate the
  inputs listed in the [pickup note](2026-11-10-138-jit.md).
  Use the retained passing #115/#103 PR verifier disposition and
  independently compare the raw PR receipts to it. Replay the
  historical push with the pinned #103 `python_gate.py --mode push`
  and exact protected policy against the archived observer receipt for
  both `--inventory` and `--outcomes`, product coverage and inventory,
  helper coverage, children and capability. For PR raw replay use
  `--mode pr` with the additional exact base receipt, base policy and
  expected base. Use the pinned #103 classifier for product outcomes.
  Verify exact wheel-smoke and file-check step/job evidence in both
  attempts and the signed PR subject and base hashes. Keep replay
  inputs, command, observed output and verifier custody independently
  bound.
- [ ] Read the retained advisory observation or reproduce it in a
  separate disposable checkout of historical tree
  `c1c9bc00e7845278b805d4f2828de3663a79c18e`. Use the pinned Python,
  lock and observer and write the observer JSON to private custody.

  ```sh
  cd "$(pwd -P)"
  PYTHONPATH="$PWD/tools/ci" AITM_CI_PYTEST_EVIDENCE="$private_observer_json" \
    uv run --project packages/aitm-usage --locked --python 3.13.9 \
    python -m pytest -p pytest_evidence --rootdir "$PWD" --collect-only -q \
    tools/ci/tests/test_python_gate.py tools/ci/tests/test_pytest_evidence.py \
    tools/ci/tests/test_verify_pr.py tools/ci/tests/test_file_checks.py
  ```

  Require exit 0, exactly 182 unique IDs, zero deselections, no reports
  or children, and sorted compact JSON-array SHA-256
  `69cef362f4c87ba65846443eda6a2c8ae3dca3431f76905dcefc459c1e7200a4`.
  Hold the comparison and #139 pickup if the collection is absent or
  discrepant.
- [ ] Project the real envelopes twice and compare bytes. The PR
  candidate and trunk each reconcile to 630 product/CLI outcomes,
  22 product source files, 7,146/7,825 product and 778/821 helper
  lines, with matching child labels and available branch receipts.
  Require 592 independently bound PR-base outcomes. Verify the two
  historical warm observations and the explicit cold Unknowns.
  Write the sanitized comparison to the owned attachment on
  `planning`, with the exact receipt links/digests, baseline digest,
  inventory identities, counts, boundaries, runner/cache controls
  and limits. Keep the canonical full record and raw evidence private
  and make their authenticated custody reconcilable.
- [ ] Stage only the two owned source paths. Commit the reviewed
  work on the authorized source branch, then follow the
  [manual delivery checklist](../../../../manual-delivery-checklist.md).
  Use exact current #103 PR jobs and trusted-target verification,
  required exact tested-tree owner disposition for the new
  `tools/ci/` files, independent source review, and verified
  delivery/sign-off. Recheck the explicit four-file helper denominator
  at the exact candidate. Keep separate local focused evidence because
  the current hosted helper command uses four explicit test targets.
  Preserve red results and any required gate that holds. A changed
  base/head or validation input requires a new exact candidate check
  and applicable review before delivery.

## Estimate

**2.5 implementation agent-hours · S · P1**, with 0.5h custody readback,
0.75h projection, 0.75h focused behavior tests and verification, and
0.5h report. Hosted queue and review wait are separate. Reassess at
pickup if custody, the advisory inventory, or the historical
verification route fails. Replan if required work exceeds four
implementation agent-hours. This planning checkpoint ends at Planning.
